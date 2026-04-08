import json
import gradio as gr
import requests

_BASE = "http://localhost:8000"
_session_id: list = [None]


def do_reset(difficulty: str, task_id: str) -> tuple[str, str]:
    payload: dict = {"difficulty": difficulty}
    if task_id.strip():
        payload["task_id"] = task_id.strip()
    try:
        r = requests.post(f"{_BASE}/reset", json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return f"Error: {e}", "—"
    data = r.json()
    _session_id[0] = data["session_id"]
    obs = data["observation"]
    status = f"reward=0.00  done=false  session={_session_id[0][:8]}..."
    return obs.get("feedback", ""), status


def do_step(tool: str, args_raw: str) -> tuple[str, str]:
    if not _session_id[0]:
        return "No active session. Click Reset first.", "—"
    try:
        args = json.loads(args_raw) if args_raw.strip() else {}
    except json.JSONDecodeError as e:
        return f"Invalid JSON in args: {e}", "—"
    try:
        r = requests.post(
            f"{_BASE}/step",
            json={"session_id": _session_id[0], "action": {"tool": tool, "args": args}},
            timeout=30,
        )
        r.raise_for_status()
    except Exception as e:
        return f"Error: {e}", "—"
    data = r.json()
    obs = data["observation"]
    status = f"reward={data['reward']:.2f}  done={str(data['done']).lower()}"
    return obs.get("feedback", ""), status


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="AI Tutor RL Environment", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# Hierarchical RAG AI Tutor\n"
            "An OpenEnv RL environment. The agent navigates a book library to answer student questions.\n\n"
            "**Workflow:** `list_books` → `get_summaries` → `read_chapter` → `talk_to_student`"
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Reset Episode")
                difficulty = gr.Dropdown(
                    choices=["easy", "medium", "hard"],
                    value="easy",
                    label="Difficulty",
                )
                task_id_input = gr.Textbox(
                    label="Task ID (optional)",
                    placeholder="e.g. easy_3, medium_1, hard_3",
                )
                reset_btn = gr.Button("Reset", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("### Take a Step")
                tool_input = gr.Dropdown(
                    choices=["list_books", "get_summaries", "read_chapter", "talk_to_student"],
                    value="list_books",
                    label="Tool",
                )
                args_input = gr.Textbox(
                    label="Args (JSON)",
                    value="{}",
                    placeholder='{"book_title": "Python Basics"}',
                )
                step_btn = gr.Button("Step", variant="secondary")

        observation_box = gr.Textbox(label="Observation / Feedback", lines=12, interactive=False)
        status_box = gr.Textbox(label="Reward & Status", lines=1, interactive=False)

        reset_btn.click(
            do_reset,
            inputs=[difficulty, task_id_input],
            outputs=[observation_box, status_box],
        )
        step_btn.click(
            do_step,
            inputs=[tool_input, args_input],
            outputs=[observation_box, status_box],
        )

    return demo
