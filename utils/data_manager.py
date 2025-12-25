import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "problems.json"
SOLUTIONS_DIR = Path(__file__).resolve().parents[1] / "solutions"
BEST_DIR = SOLUTIONS_DIR / "best"
NOTES_DIR = Path(__file__).resolve().parents[1] / "notes"


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
    if not questions:
        return None
    weights = [3 if q.get("status") == "unsolved" else 1 for q in questions]
    return random.choices(questions, weights=weights, k=1)[0]


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


def save_solution(question_id: str, title: str, code: str, is_best: bool) -> Path:
    SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
    if is_best:
        BEST_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{_format_id(question_id)}_{_slugify_title(title)}.py"
        target_dir = BEST_DIR
    else:
        filename = (
            f"{_format_id(question_id)}_{_slugify_title(title)}_{_timestamp()}.py"
        )
        target_dir = SOLUTIONS_DIR
    path = target_dir / filename
    path.write_text(code, encoding="utf-8")
    return path


def save_notes(question_id: str, title: str, notes: str) -> Optional[Path]:
    if not notes.strip():
        return None
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{_format_id(question_id)}_{_slugify_title(title)}.md"
    path = NOTES_DIR / filename
    header = f"[{_timestamp()}]\n"
    content = header + notes.rstrip() + "\n\n"
    path.write_text(
        (path.read_text(encoding="utf-8") if path.exists() else "") + content,
        encoding="utf-8",
    )
    return path


def read_notes(question_id: str, title: str) -> str:
    filename = f"{_format_id(question_id)}_{_slugify_title(title)}.md"
    path = NOTES_DIR / filename
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def reset_question_data(question_id: str) -> Optional[Dict[str, Any]]:
    questions = load_questions()
    updated_question = None
    for question in questions:
        if str(question.get("id")) == str(question_id):
            question["status"] = "unsolved"
            question["my_code"] = ""
            question["notes"] = ""
            updated_question = question
            break
    if updated_question is None:
        return None
    save_questions(questions)
    return updated_question


def reset_all_questions() -> int:
    questions = load_questions()
    for question in questions:
        question["status"] = "unsolved"
        question["my_code"] = ""
        question["notes"] = ""
    save_questions(questions)
    return len(questions)


def clear_question_files(question_id: str, title: str) -> None:
    prefix = f"{_format_id(question_id)}_{_slugify_title(title)}"
    if SOLUTIONS_DIR.exists():
        for path in SOLUTIONS_DIR.glob(f"{prefix}_*.py"):
            if path.is_file():
                path.unlink()
    best_path = BEST_DIR / f"{prefix}.py"
    if best_path.exists():
        best_path.unlink()
    notes_path = NOTES_DIR / f"{prefix}.md"
    if notes_path.exists():
        notes_path.unlink()


def clear_all_files() -> None:
    if SOLUTIONS_DIR.exists():
        for path in SOLUTIONS_DIR.rglob("*"):
            if path.is_file():
                path.unlink()
    if NOTES_DIR.exists():
        for path in NOTES_DIR.rglob("*"):
            if path.is_file():
                path.unlink()


def _format_id(question_id: str) -> str:
    digits = re.sub(r"\D+", "", str(question_id))
    return digits.zfill(3) if digits else str(question_id)


def _slugify_title(title: str) -> str:
    base = re.sub(r"^\s*\d+\.\s*", "", title.strip())
    ascii_only = base.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_only).strip("_").lower()
    return slug or "solution"


def format_commit_message(question_id: str, title: str) -> str:
    return f"Solve {_format_id(question_id)} {_slugify_title(title)}"


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")
