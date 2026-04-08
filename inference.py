"""
Inference script for the Hierarchical RAG AI Tutor environment.
Drives Easy / Medium / Hard tasks via HTTP and outputs [START]/[STEP]/[END] logs.
"""

import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
HF_TOKEN     = os.environ["HF_TOKEN"]
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_ID     = os.getenv("MODEL_NAME") or os.getenv("MODEL_ID", "Qwen/Qwen2.5-72B-Instruct")
ENV_NAME     = "hierarchical-rag-tutor"

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

# One representative task per difficulty for validation
EVAL_TASKS = [
    {"difficulty": "easy",   "task_id": "easy_1"},
    {"difficulty": "medium", "task_id": "medium_1"},
    {"difficulty": "hard",   "task_id": "hard_1"},
]

# System prompt is provided by the environment on reset() via observation.system_prompt
# Kept here as fallback only
_FALLBACK_SYSTEM_PROMPT = "You are an AI Tutor. Use tools to retrieve information before answering. Respond with only JSON: {\"tool\": \"<name>\", \"args\": {}}"


def call_agent(messages: list[dict]) -> tuple[str, dict]:
    resp = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages,
        max_tokens=2000,
        temperature=0.2,
    )
    raw = resp.choices[0].message.content.strip()
    clean = raw.strip("`").removeprefix("json").strip()
    try:
        parsed = json.loads(clean)
    except Exception:
        # Fallback: treat raw text as the answer
        parsed = {"tool": "talk_to_student", "args": {"answer": raw}}
    return raw, parsed


def run_episode(task_cfg: dict) -> dict:
    difficulty = task_cfg["difficulty"]
    task_id    = task_cfg["task_id"]

    # ── Reset ──────────────────────────────────────────────────────────────────
    r = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"difficulty": difficulty, "task_id": task_id},
    )
    r.raise_for_status()
    data       = r.json()
    session_id = data.get("session_id", "")
    obs        = data.get("observation", data)

    print(f"[START] task={task_id} env={ENV_NAME} model={MODEL_ID}")

    system_prompt = obs.get("system_prompt") or _FALLBACK_SYSTEM_PROMPT

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": obs.get("feedback", str(obs))},
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
            err = step_resp.text
            print(f"[STEP] step={step_num} action={action_dict} reward=0.0 done=True error={err}")
            rewards.append(0.0)
            break

        step_data = step_resp.json()
        obs_data  = step_data.get("observation", step_data)
        reward    = step_data.get("reward", obs_data.get("reward", 0.0))
        done      = step_data.get("done",   obs_data.get("done", False))
        feedback  = obs_data.get("feedback", "")

        error_str = ""
        if "[System Error]" in feedback or "[Protocol Error]" in feedback or "[TIMEOUT]" in feedback:
            error_str = feedback

        print(
            f"[STEP] step={step_num} "
            f"action={json.dumps(action_dict)} "
            f"reward={reward:.4f} "
            f"done={done} "
            f"error={error_str!r}"
        )
        rewards.append(reward)
        if done:
            final_score = reward

        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": feedback})

    success = final_score >= 0.7
    print(
        f"[END] success={success} "
        f"steps={step_num} "
        f"score={final_score:.4f} "
        f"rewards={[round(r, 4) for r in rewards]}"
    )
    return {"task_id": task_id, "success": success, "score": final_score, "steps": step_num}


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = []
    for task in EVAL_TASKS:
        result = run_episode(task)
        results.append(result)
        print()

    passed = sum(1 for r in results if r["success"])
    print(f"=== Results: {passed}/{len(results)} tasks passed ===")
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        print(f"  [{status}] {r['task_id']} — score={r['score']:.4f} steps={r['steps']}")
