import sys
import uuid
from pathlib import Path
from dataclasses import asdict

# Add both server/ and root to path
SERVER_DIR = Path(__file__).parent
ROOT_DIR   = SERVER_DIR.parent
sys.path.insert(0, str(SERVER_DIR))
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from environment import TutorEnvironment
from models import TutorAction

app = FastAPI(title="Hierarchical RAG AI Tutor Environment")
env = TutorEnvironment()

# In-memory session store { session_id -> TutorState }
_sessions: dict = {}


# ── Request models ─────────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    difficulty: str = "easy"
    task_id: str | None = None

class ActionRequest(BaseModel):
    tool: str
    args: dict = {}

class StepRequest(BaseModel):
    session_id: str
    action: ActionRequest


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "hierarchical-rag-tutor",
        "description": "Hierarchical RAG AI Tutor RL Environment",
        "endpoints": ["/reset", "/step", "/state", "/health", "/metadata", "/schema"],
    }


@app.get("/metadata")
def metadata():
    return {
        "name": "hierarchical-rag-tutor",
        "description": "An AI Tutor RL environment where an agent navigates a library of educational books using hierarchical RAG to answer student questions. Tasks range from easy (single-book lookup) to hard (multi-book synthesis).",
        "version": "1.0.0",
    }


@app.get("/schema")
def schema():
    return {
        "action": {
            "type": "object",
            "properties": {
                "tool": {"type": "string", "description": "Tool name to call"},
                "args": {"type": "object", "description": "Tool arguments"},
            },
            "required": ["tool"],
        },
        "observation": {
            "type": "object",
            "properties": {
                "feedback": {"type": "string"},
                "system_prompt": {"type": "string"},
                "retrieved_chunks": {"type": "array"},
                "tools_called": {"type": "array"},
                "steps_taken": {"type": "integer"},
                "reward": {"type": "number"},
                "done": {"type": "boolean"},
            },
        },
        "state": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "difficulty": {"type": "string"},
                "step_count": {"type": "integer"},
                "done": {"type": "boolean"},
            },
        },
    }


@app.post("/mcp")
def mcp():
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": [
                {"name": "search_book", "description": "Search a specific book for relevant content"},
                {"name": "list_books", "description": "List available books in the library"},
                {"name": "talk_to_student", "description": "Send final answer to the student"},
            ]
        },
        "id": None,
    }


@app.get("/state")
def get_state_list():
    return {"sessions": list(_sessions.keys())}


@app.post("/reset")
def reset(req: ResetRequest):
    sid = str(uuid.uuid4())
    try:
        obs = env.reset(difficulty=req.difficulty, task_id=req.task_id)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    _sessions[sid] = env.state
    return {"session_id": sid, "observation": asdict(obs), "reward": 0.0, "done": False}


@app.post("/step")
def step(req: StepRequest):
    state = _sessions.get(req.session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")
    if state.done:
        raise HTTPException(status_code=400, detail="Episode already finished.")

    env._state = state
    action = TutorAction(tool=req.action.tool, args=req.action.args)
    obs, reward, done, state = env.step(action)
    _sessions[req.session_id] = state
    return {"session_id": req.session_id, "observation": asdict(obs), "reward": reward, "done": done}


@app.get("/state/{session_id}")
def get_state(session_id: str):
    state = _sessions.get(session_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": session_id, "state": asdict(state)}


@app.get("/health")
def health():
    return {"status": "healthy"}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
