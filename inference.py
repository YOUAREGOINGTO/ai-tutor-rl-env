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
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "https://Yaswanth123-rl-env-hierarchical-rag-tutor.hf.space")
HF_TOKEN     = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME") or os.getenv("MODEL_ID", "Qwen/Qwen2.5-72B-Instruct")
ENV_NAME     = "hierarchical-rag-tutor"

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)

# Representative tasks covering all difficulties
EVAL_TASKS = [
    {"difficulty": "easy",   "task_id": "easy_3"},    # Alien Flora — hallucination prevention
    {"difficulty": "medium", "task_id": "medium_1"},  # KeyError debugging + citation
    {"difficulty": "medium", "task_id": "medium_3"},  # RNN exploding gradients (ML)
    {"difficulty": "hard",   "task_id": "hard_1"},    # Compound interest — multi-book
    {"difficulty": "hard",   "task_id": "hard_3"},    # Qubit erasure — Quantum + Thermodynamics
]

# System prompt is provided by the environment on reset() via observation.system_prompt
# Kept here as fallback only
_FALLBACK_SYSTEM_PROMPT = "You are an AI Tutor. Use tools to retrieve information before answering. Respond with only JSON: {\"tool\": \"<name>\", \"args\": {}}"


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

    print(f"[START] task={task_id} env={ENV_NAME} model={MODEL_NAME}", flush=True)

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
            print(f"[STEP] step={step_num} action={json.dumps(action_dict)} reward=0.00 done=true error={err}", flush=True)
            rewards.append(0.0)
            break

        step_data = step_resp.json()
        obs_data  = step_data.get("observation", step_data)
        reward    = step_data.get("reward", obs_data.get("reward", 0.0))
        done      = step_data.get("done",   obs_data.get("done", False))
        feedback  = obs_data.get("feedback", "")

        error_str = "null"
        if "[System Error]" in feedback or "[Protocol Error]" in feedback or "[TIMEOUT]" in feedback:
            error_str = feedback

        print(
            f"[STEP] step={step_num} "
            f"action={json.dumps(action_dict)} "
            f"reward={reward:.2f} "
            f"done={str(done).lower()} "
            f"error={error_str}",
            flush=True,
        )
        rewards.append(reward)
        if done:
            final_score = reward

        messages.append({"role": "assistant", "content": raw})
        messages.append({"role": "user", "content": feedback})

    success      = final_score >= 0.3
    rewards_str  = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} "
        f"steps={step_num} "
        f"score={final_score:.2f} "
        f"rewards={rewards_str}",
        flush=True,
    )
    return {"task_id": task_id, "score": final_score, "steps": step_num}


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    results = []
    for task in EVAL_TASKS:
        result = run_episode(task)
        results.append(result)
        print(flush=True)

    print(f"=== Results: {len(results)} tasks completed ===", flush=True)
    for r in results:
        print(f"  {r['task_id']} — score={r['score']:.2f} steps={r['steps']}", flush=True)
