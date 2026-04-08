from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TutorAction:
    tool: str = ""
    args: dict = field(default_factory=dict)


@dataclass
class TutorObservation:
    feedback: str = ""
    system_prompt: str = ""
    retrieved_chunks: list = field(default_factory=list)
    tools_called: list = field(default_factory=list)
    steps_taken: int = 0
    reward: float = 0.01
    done: bool = False


@dataclass
class TutorState:
    task_id: str = ""
    difficulty: str = ""
    student_question: str = ""
    ground_truth_answer: str = ""
    grading_rubric: str = ""
    required_books: list = field(default_factory=list)
    max_steps: int = 10

    # Runtime tracking
    step_count: int = 0
    retrieved_chunks: list = field(default_factory=list)
    tools_called: list = field(default_factory=list)
    successful_reads: list = field(default_factory=list)
    done: bool = False
    final_score: Optional[float] = None
