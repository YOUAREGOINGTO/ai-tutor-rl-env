---
title: Hierarchical RAG AI Tutor
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

# Hierarchical RAG AI Tutor Environment

An OpenEnv-compatible RL environment where an LLM agent acts as an AI Tutor. The agent navigates a structured library of educational books using a hierarchical RAG tool chain to answer student questions. Graded by an LLM-as-judge with per-task rubrics.

## Environment Description

The agent is given a student question and must:
1. Browse the library (`list_books`) to discover available books
2. Retrieve chapter summaries (`get_summaries`) to find the relevant chapter
3. Read the specific chapter (`read_chapter`) to retrieve content
4. Answer the student (`talk_to_student`) — scored by LLM judge on accuracy and citations

Tasks range from single-book lookups (easy) to multi-book synthesis requiring citations from two different sources (hard).

## Action Space

The agent outputs a JSON action with one tool call per step:

```json
{"tool": "list_books", "args": {}}
{"tool": "get_summaries", "args": {"book_title": "Python Basics"}}
{"tool": "read_chapter", "args": {"book_title": "Python Basics", "chapter_title": "Chapter 4: For Loops"}}
{"tool": "talk_to_student", "args": {"answer": "For loops iterate over sequences..."}}
```

**Available tools:**
| Tool | Args | Description |
|------|------|-------------|
| `list_books` | none | Lists all books with descriptions |
| `get_summaries` | `book_title` | Returns chapter summaries for a book |
| `read_chapter` | `book_title`, `chapter_title` | Returns full chapter content |
| `talk_to_student` | `answer` | Submits final answer; triggers LLM grading |

## Observation Space

Each step returns a `TutorObservation`:

```json
{
  "feedback": "Here are the available books: ...",
  "system_prompt": "You are an AI Tutor...",
  "retrieved_chunks": ["chunk1", "chunk2"],
  "tools_called": ["list_books", "get_summaries"],
  "steps_taken": 2,
  "reward": 0.0,
  "done": false
}
```

## Reward

- `0.0–1.0` continuous score from LLM-as-judge
- Partial credit for incomplete but partially correct answers
- Protocol violations (skipping required steps) penalized
- Episode ends when `talk_to_student` is called or `max_steps` is reached

## Tasks

| Task ID | Difficulty | Books Required | Description |
|---------|-----------|---------------|-------------|
| `easy_1` | Easy | Python Basics | For loops explanation |
| `easy_2` | Easy | Python Basics | Variable declaration |
| `easy_3` | Easy | Alien Flora of Exoplanet Zephyr-9 | Why plants look black |
| `medium_1` | Medium | Python Basics | KeyError diagnosis and fix |
| `medium_2` | Medium | Python Algorithms | Bubble sort vs merge sort |
| `medium_3` | Medium | Deep Learning | RNN exploding gradients + gradient clipping |
| `hard_1` | Hard | Math Fundamentals + Python Algorithms | Compound interest formula + Python function |
| `hard_2` | Hard | Math Fundamentals + Python Algorithms | Geometric sequences + sum function |
| `hard_3` | Hard | Quantum Computation + Thermodynamics | Qubit erasure — Kraus operators + Landauer's Principle |

## Setup & Running

### Prerequisites

- Python 3.11+
- A HuggingFace token with inference API access

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```
HF_TOKEN=your_huggingface_token_here
API_BASE_URL=https://router.huggingface.co/v1
MODEL_ID=Qwen/Qwen2.5-72B-Instruct
ENV_BASE_URL=http://localhost:8000
```

### Run with Docker (recommended)

```bash
docker compose up --build
python inference.py
```

### Run locally

```bash
pip install -r requirements.txt

# Terminal 1: start server
cd server
python -m uvicorn app:app --port 8000

# Terminal 2: run inference
python inference.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Start a new episode |
| `/step` | POST | Execute one action |
| `/state` | GET | Inspect current session state |
| `/health` | GET | Health check (returns 200) |

## Baseline Scores

Running `python inference.py` produces reproducible scores:

```
[START] task=easy_1 env=hierarchical-rag-tutor model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action={"tool": "list_books", "args": {}} reward=0.0000 done=False error=''
...
[END] success=True steps=4 score=0.9000 rewards=[0.0, 0.0, 0.0, 0.9]

[START] task=medium_1 ...
[END] success=True steps=5 score=0.8500 ...

[START] task=hard_1 ...
[END] success=True steps=7 score=0.7500 ...

=== Results: 3/3 tasks passed ===
```
