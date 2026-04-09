---
title: Hierarchical RAG AI Tutor
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

# AI Tutor Environment

An OpenEnv RL environment where an LLM agent acts as an AI Tutor. The agent must navigate a structured library of educational books to answer  questions — it cannot answer from memory alone.

## Why This Environment?

Most QA benchmarks let models answer directly from training knowledge. This environment forces grounded retrieval: the agent must locate the right book, find the right chapter, read it, and only then answer. This tests multi-step planning, tool use, and citation accuracy — skills critical for trustworthy AI tutors.

## How It Works

The agent follows a strict hierarchical retrieval workflow:

1. `list_books` — discover what books are available
2. `get_summaries` — see chapter summaries for a book
3. `read_chapter` — read the full chapter content
4. `talk_to_student` — deliver the final answer (ends the episode)

Skipping retrieval and answering directly is penalized. The agent must read before it can teach.

## Tools

| Tool | Args | What it does |
|------|------|--------------|
| `list_books` | none | Lists all books with descriptions |
| `get_summaries` | `book_title` | Returns chapter summaries for a book |
| `read_chapter` | `book_title`, `chapter_title` | Returns full chapter content |
| `talk_to_student` | `answer` | Submits final answer — triggers LLM judge |

## Reward — LLM as Judge

This environment uses an LLM as the judge for the final `talk_to_student` action. Every final answer is scored strictly in `(0, 1)` using a task-specific rubric. The judge checks:

- Factual correctness against a ground truth answer
- Required concepts are explained (e.g. eigenvalues, Kraus operators)
- Correct citations to specific books and chapters
- Working code examples where required

Partial credit is given for incomplete but partially correct answers. Hard tasks require citing two different books — missing either citation costs points.

### Reward Shaping and Anti-Hacking Design

Intermediate tool steps (`list_books`, `get_summaries`, `read_chapter`) return `0.0`. This keeps retrieval behavior neutral: the agent is not rewarded for simply calling tools, and meaningful reward only comes from the judged final answer.

Reward hacking is further prevented by:
- `max_steps` per task (easy: 5–6, medium: 8, hard: 12) — episode terminates on timeout
- Protocol enforcement: `talk_to_student` without a successful `read_chapter` returns `reward=0.0, done=False`, so the agent cannot skip retrieval and still collect reward
- LLM judge scores are clamped to `[0.01, 0.99]` — no exact `0` or `1` possible
- Timeout returns `0.01`, which stays validator-safe while still acting as a near-failure score

## Task Format

Each task in `tasks.yaml` follows this structure:

```yaml
hard_3:
  difficulty: hard
  student_question: "Explain the physical cost of resetting a quantum computer's memory..."
  required_books: ["Quantum Computation and Quantum Information", "Thermodynamics of Computation"]
  max_steps: 12
  ground_truth_answer: "..."
  grading_rubric: |
    - Must define qubit erasure using Kraus operators
    - Must state Landauer's formula E = kT ln(2)
    - Must cite BOTH books
```

## Setup

### Environment Variables

Create a `.env` file in the project root:

```
HF_TOKEN=your_huggingface_token
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
ENV_BASE_URL=http://localhost:8000
```

`ENV_BASE_URL` points inference.py at your local Docker container. If omitted, it defaults to the live HF Space.

### Run with Docker (Hackathon-style evaluation)

This replicates exactly how the hackathon evaluates the submission:

```bash
# Step 1 — build the Docker image
docker build -t hierarchical-rag-tutor .

# Step 2 — start the environment server
docker run -p 8000:8000 --env-file .env hierarchical-rag-tutor

# Step 3 — in a second terminal, run the agent inside Docker
docker run --rm \
  -e HF_TOKEN=your_huggingface_token \
  -e API_BASE_URL=https://router.huggingface.co/v1 \
  -e MODEL_NAME=Qwen/Qwen2.5-72B-Instruct \
  -e ENV_BASE_URL=http://host.docker.internal:8000 \
  hierarchical-rag-tutor python inference.py
```

### Run locally (without Docker)

```bash
pip install -r requirements.txt

# Terminal 1
cd server && python -m uvicorn app:app --port 8000

# Terminal 2
python inference.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Start a new episode |
| `/step` | POST | Execute one action |
| `/state/{session_id}` | GET | Inspect session state |
| `/health` | GET | Health check |
