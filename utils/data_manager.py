import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "problems.json"
SOLUTIONS_DIR = Path(__file__).resolve().parents[1] / "solutions"


def load_questions() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    content = DATA_PATH.read_text(encoding="utf-8").strip()
    if not content:
        return []
    return json.loads(content)


def save_questions(questions: List[Dict[str, Any]]) -> None:
    DATA_PATH.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_random_question() -> Optional[Dict[str, Any]]:
    questions = load_questions()
    unsolved = [q for q in questions if q.get("status") == "unsolved"]
    if not unsolved:
        return None
    return random.choice(unsolved)


def update_status(question_id: str, code: str, notes: str) -> Optional[Dict[str, Any]]:
    questions = load_questions()
    updated_question = None
    for question in questions:
        if str(question.get("id")) == str(question_id):
            question["status"] = "solved"
            question["my_code"] = code
            question["notes"] = notes
            updated_question = question
            break
    if updated_question is None:
        return None
    save_questions(questions)
    return updated_question


def save_solution(question_id: str, code: str) -> Path:
    SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{question_id}_solution.py"
    path = SOLUTIONS_DIR / filename
    path.write_text(code, encoding="utf-8")
    return path
