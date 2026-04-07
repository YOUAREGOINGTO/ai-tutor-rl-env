import requests
from dataclasses import asdict
from models import TutorAction, TutorObservation, TutorState


class TutorEnvClient:

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session_id = None

    def reset(self, difficulty: str = "easy", task_id: str | None = None) -> TutorObservation:
        r = requests.post(f"{self.base_url}/reset", json={"difficulty": difficulty, "task_id": task_id})
        r.raise_for_status()
        data = r.json()
        self.session_id = data["session_id"]
        return self._parse_obs(data["observation"])

    def step(self, action: TutorAction) -> tuple:
        r = requests.post(f"{self.base_url}/step", json={
            "session_id": self.session_id,
            "action": {"tool": action.tool, "args": action.args},
        })
        r.raise_for_status()
        data = r.json()
        obs = self._parse_obs(data["observation"])
        return obs, data["reward"], data["done"]

    def get_state(self) -> TutorState:
        r = requests.get(f"{self.base_url}/state/{self.session_id}")
        r.raise_for_status()
        return self._parse_state(r.json()["state"])

    def _parse_obs(self, payload: dict) -> TutorObservation:
        return TutorObservation(
            feedback=payload.get("feedback", ""),
            system_prompt=payload.get("system_prompt", ""),
            retrieved_chunks=payload.get("retrieved_chunks", []),
            tools_called=payload.get("tools_called", []),
            steps_taken=payload.get("steps_taken", 0),
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> TutorState:
        return TutorState(
            task_id=payload.get("task_id", ""),
            difficulty=payload.get("difficulty", ""),
            student_question=payload.get("student_question", ""),
            ground_truth_answer=payload.get("ground_truth_answer", ""),
            grading_rubric=payload.get("grading_rubric", ""),
            required_books=payload.get("required_books", []),
            max_steps=payload.get("max_steps", 10),
            step_count=payload.get("step_count", 0),
            done=payload.get("done", False),
            final_score=payload.get("final_score"),
        )
