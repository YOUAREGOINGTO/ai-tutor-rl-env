"""
Inference script for the Hierarchical RAG AI Tutor environment.
Outputs exactly: [START] / one-or-more [STEP] / [END]
"""

import os
import json
import requests
from openai import OpenAI

# ── Environment variables ─────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN environment variable is required")

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "https://Yaswanth123-rl-env-hierarchical-rag-tutor.hf.space")

ENV_NAME = "hierarchical-rag-tutor"

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

_FALLBACK_SYSTEM_PROMPT = (
    'You are an AI Tutor. Use tools to retrieve information before answering. '
    'Respond with only JSON: {"tool": "<name>", "args": {}}'
)


def call_agent(messages: list[dict]) -> tuple[str, dict]:
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        max_tokens=2000,
        temperature=0.2,
    )
    raw = resp.choices[0].message.content.strip()
    clean = raw.strip("`").removeprefix("json").strip()
    try:
        parsed = json.loads(clean)
    except Exception:
        parsed = {"tool": "talk_to_student", "args": {"answer": raw}}
    return raw, parsed


def run_episode(difficulty: str = "easy", task_id: str | None = None) -> None:
    r = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"difficulty": difficulty, "task_id": task_id},
    )
    r.raise_for_status()
    data       = r.json()
    session_id = data["session_id"]
    obs        = data.get("observation", data)

    print(f"[START] task={task_id or difficulty} env={ENV_NAME} model={MODEL_NAME}", flush=True)

    messages = [
        {"role": "system", "content": obs.get("system_prompt") or _FALLBACK_SYSTEM_PROMPT},
        {"role": "user",   "content": obs.get("feedback", "")},
    ]

    step_num    = 0
    rewards     = []
    done        = False
    final_score = 0.0

    while not done:
        step_num += 1
        raw, action_dict = call_agent(messages)

        step_resp = requests.post(
            f"{ENV_BASE_URL}/step",
            json={"session_id": session_id, "action": action_dict},
        )

        if step_resp.status_code != 200:
            print(
                f"[STEP] step={step_num} action={json.dumps(action_dict)} "
                f"reward=0.00 done=true error={step_resp.text}",
                flush=True,
            )
            rewards.append(0.0)
            break

        step_data = step_resp.json()
        obs_data  = step_data.get("observation", step_data)
        reward    = float(step_data.get("reward", obs_data.get("reward", 0.0)))
        done      = bool(step_data.get("done", obs_data.get("done", False)))
        feedback  = obs_data.get("feedback", "")

        error_str = "null"
        if any(tag in feedback for tag in ("[System Error]", "[Protocol Error]", "[TIMEOUT]")):
            error_str = feedback

        print(
            f"[STEP] step={step_num} action={json.dumps(action_dict)} "
            f"reward={reward:.2f} done={str(done).lower()} error={error_str}",
            flush=True,
        )
        rewards.append(reward)
        if done:
            final_score = reward

        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user",      "content": feedback})

    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success     = final_score >= 0.3
    print(
        f"[END] success={str(success).lower()} steps={step_num} rewards={rewards_str}",
        flush=True,
    )


EVAL_TASKS = [
    {"difficulty": "easy",   "task_id": "easy_3"},
    {"difficulty": "medium", "task_id": "medium_1"},
    {"difficulty": "medium", "task_id": "medium_3"},
    {"difficulty": "hard",   "task_id": "hard_1"},
    {"difficulty": "hard",   "task_id": "hard_3"},
]

if __name__ == "__main__":
    for task in EVAL_TASKS:
        run_episode(difficulty=task["difficulty"], task_id=task["task_id"])
