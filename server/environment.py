import os
import json
import random
import yaml
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")
from openai import OpenAI
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import TutorAction, TutorObservation, TutorState

ROOT = Path(__file__).parent.parent


# ── Loaders ────────────────────────────────────────────────────────────────────

def _load_library() -> dict:
    with open(ROOT / "library.yaml") as f:
        raw = yaml.safe_load(f)

    library = {}
    for book, chapters in raw.items():
        description = chapters.pop("_description", "")
        library[book] = {"_description": description}
        for chapter, data in chapters.items():
            content = data.get("content")
            if content is None:
                path = ROOT / data["content_path"]
                with open(path) as cf:
                    content = cf.read()
            library[book][chapter] = {
                "summary": data["summary"],
                "content": content,
            }
    return library


def _load_tasks() -> dict:
    with open(ROOT / "tasks.yaml") as f:
        return yaml.safe_load(f)


LIBRARY = _load_library()
TASKS   = _load_tasks()

AGENT_SYSTEM_PROMPT = """You are an AI Tutor helping a student learn. You have access to a library of educational books.
You must retrieve information using tools before answering the student.

TOOLS AVAILABLE:
1. list_books          — lists all available books. Args: {}
2. get_summaries       — lists chapter summaries for a book. Args: {"book_title": str}
3. read_chapter        — reads full chapter content. Args: {"book_title": str, "chapter_title": str}
4. talk_to_student     — delivers your final answer to the student. Args: {"answer": str}  ← use ONCE, ends episode.

RULES:
- WORKFLOW: list_books → get_summaries (for EACH book you plan to read) → read_chapter → talk_to_student.
- NEVER guess chapter names. Always call get_summaries first to see the exact chapter titles.
- You MUST call read_chapter at least once successfully before talk_to_student.
- You MUST call get_summaries separately for every book before reading from it.
- If the book does not contain the exact information, explicitly say so in your answer.
- talk_to_student ends the episode — make your answer complete, clear, and well-cited.
- Explain concepts with examples and cite the specific chapter you read from.

Respond with ONLY a JSON object (no markdown fences):
{"tool": "<tool_name>", "args": {<args>}}
"""

NO_RETRIEVAL_PROMPT = """You are an AI Tutor. Answer the student's question directly from your own knowledge.
Do not use any tools. Give a clear, accurate explanation with examples.

Respond with ONLY:
{"tool": "talk_to_student", "args": {"answer": "<your answer>"}}
"""

TASKS_BY_DIFFICULTY = {
    "easy":   [k for k, v in TASKS.items() if v["difficulty"] == "easy"],
    "medium": [k for k, v in TASKS.items() if v["difficulty"] == "medium"],
    "hard":   [k for k, v in TASKS.items() if v["difficulty"] == "hard"],
}


# ── LLM Judge ─────────────────────────────────────────────────────────────────

def _call_judge(task: TutorState, answer: str) -> str:
    client = OpenAI(
        api_key=os.getenv("HF_TOKEN"),
        base_url=os.getenv("API_BASE_URL", "https://router.huggingface.co/v1"),
    )
    system_prompt = (
        "You are a strict educational evaluator.\n"
        "Given a student question, a ground-truth answer, grading criteria, "
        "and a tutor's response, score the response.\n\n"
        "Grading criteria for this specific question:\n"
        f"{task.grading_rubric}\n\n"
        "General scoring guide (score must be strictly between 0 and 1, never 0.0 or 1.0):\n"
        "- 0.95: All criteria met, correct, clear, sources cited.\n"
        "- 0.7-0.9: Mostly correct, minor omissions.\n"
        "- 0.4-0.6: Partially correct, key concept missing.\n"
        "- 0.1-0.3: Vague or mostly wrong.\n"
        "- 0.05: Completely wrong or empty.\n\n"
        'Respond ONLY with valid JSON: {"score": <float strictly between 0 and 1>, "student_reply": "<realistic follow-up>"}'
    )
    user_prompt = (
        f"Student Question: {task.student_question}\n\n"
        f"Ground Truth Answer: {task.ground_truth_answer}\n\n"
        f"Tutor's Response: {answer}\n\n"
        f"Books the tutor retrieved from: {task.successful_reads}"
    )
    resp = client.chat.completions.create(
        model=os.getenv("MODEL_NAME") or os.getenv("MODEL_ID", "Qwen/Qwen2.5-72B-Instruct"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=300,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def _clamp(score: float) -> float:
    """Clamp score to strictly open interval (0, 1) as required by validator."""
    return max(0.01, min(0.99, score))


def _llm_judge(task: TutorState, answer: str, max_retries: int = 3) -> tuple[float, str]:
    for attempt in range(max_retries):
        try:
            raw = _call_judge(task, answer)
            clean = raw.strip("`").removeprefix("json").strip()
            parsed = json.loads(clean)
            score = float(parsed["score"])
            if 0.0 <= score <= 1.0:
                return _clamp(score), parsed.get("student_reply", "Thanks.")
            # score out of range → retry
        except Exception:
            pass
    return 0.01, "Could not evaluate the response."


# ── Environment ────────────────────────────────────────────────────────────────

class TutorEnvironment:

    def __init__(self):
        self._state = TutorState()

    def reset(self, difficulty: str = "easy", task_id: str | None = None) -> TutorObservation:
        if task_id is None:
            task_id = random.choice(TASKS_BY_DIFFICULTY[difficulty])

        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id: '{task_id}'. Valid: {list(TASKS.keys())}")
        spec = TASKS[task_id]
        self._state = TutorState(
            task_id=task_id,
            difficulty=spec["difficulty"],
            student_question=spec["student_question"],
            ground_truth_answer=spec["ground_truth_answer"],
            grading_rubric=spec["grading_rubric"],
            required_books=spec["required_books"],
            max_steps=spec["max_steps"],
        )
        if spec.get("agent_prompt"):
            system_prompt = spec["agent_prompt"]
        elif not spec["required_books"]:
            system_prompt = NO_RETRIEVAL_PROMPT
        else:
            system_prompt = AGENT_SYSTEM_PROMPT

        return TutorObservation(
            feedback=(
                f"[AI Tutor Session Started]\n"
                f"Student asks: \"{self._state.student_question}\"\n"
            ),
            system_prompt=system_prompt,
            reward=0.005,
            done=False,
        )

    def step(self, action: TutorAction) -> tuple:
        state = self._state
        state.step_count += 1
        tool_log = f"{action.tool}({action.args})"
        state.tools_called.append(tool_log)

        # ── Timeout ───────────────────────────────────────────────────────────
        if state.step_count > state.max_steps:
            state.done = True
            obs = TutorObservation(
                feedback="[TIMEOUT] Max steps exceeded.",
                retrieved_chunks=state.retrieved_chunks,
                tools_called=state.tools_called,
                steps_taken=state.step_count,
                reward=0.01,
                done=True,
            )
            return obs, 0.01, True, state

        # ── Tool dispatch ─────────────────────────────────────────────────────
        feedback = ""
        reward   = 0.005  # small non-zero reward for valid tool calls; terminal steps overwrite this
        done     = False

        if action.tool == "list_books":
            lines = []
            for b, data in LIBRARY.items():
                desc = data.get("_description", "")
                lines.append(f"- {b}: {desc}" if desc else f"- {b}")
            feedback = "Available books:\n" + "\n".join(lines)

        elif action.tool == "get_summaries":
            book_title = action.args.get("book_title", "")
            book = LIBRARY.get(book_title)
            if book is None:
                feedback = f"[System Error] Book not found: '{book_title}'"
            else:
                summaries = {ch: data["summary"] for ch, data in book.items() if ch != "_description"}
                feedback = f"Summaries for '{book_title}':\n" + json.dumps(summaries, indent=2)

        elif action.tool == "read_chapter":
            book_title    = action.args.get("book_title", "")
            chapter_title = action.args.get("chapter_title", "")
            book = LIBRARY.get(book_title)
            if book is None:
                feedback = f"[System Error] Book not found: '{book_title}'"
            else:
                chapter = book.get(chapter_title)
                if chapter is None:
                    feedback = f"[System Error] Chapter not found: '{chapter_title}'"
                else:
                    chunk = f"[{book_title} / {chapter_title}]\n{chapter['content']}"
                    state.retrieved_chunks.append(chunk)
                    key = f"{book_title}::{chapter_title}"
                    if key not in state.successful_reads:
                        state.successful_reads.append(key)
                    feedback = chunk

        elif action.tool == "talk_to_student":
            # Tasks with no required_books (open-ended) skip the retrieval check
            retrieval_required = len(state.required_books) > 0
            if retrieval_required and not state.successful_reads:
                feedback = (
                    "[Protocol Error] You must call read_chapter successfully "
                    "before talking to the student."
                )
                reward = 0.05
                done   = False
            else:
                answer = action.args.get("answer", "")
                # Unwrap if agent double-encoded the answer as a nested JSON tool call
                try:
                    inner = json.loads(answer)
                    if isinstance(inner, dict) and inner.get("tool") == "talk_to_student":
                        answer = inner.get("args", {}).get("answer", answer)
                except (json.JSONDecodeError, TypeError):
                    pass
                score, student_reply = _llm_judge(state, answer)
                state.final_score = score
                done     = True
                reward   = score
                feedback = (
                    f"[Student Reply] {student_reply}\n"
                    f"[Session Score] {score:.2f}"
                )

        else:
            feedback = f"[System Error] Unknown tool: '{action.tool}'"
            reward = 0.01

        state.done = done
        obs = TutorObservation(
            feedback=feedback,
            retrieved_chunks=list(state.retrieved_chunks),
            tools_called=list(state.tools_called),
            steps_taken=state.step_count,
            reward=reward,
            done=done,
        )
        return obs, reward, done, state

    @property
    def state(self) -> TutorState:
        return self._state
