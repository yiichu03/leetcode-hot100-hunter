import json
import os
from pathlib import Path
import urllib.error
import urllib.request
from typing import Any, Dict, List, Tuple


def call_openai_compatible(
    messages: List[Dict[str, str]],
    model: str,
    base_url: str,
    api_key: str,
    timeout: int = 60,
) -> Tuple[bool, str]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            body: Dict[str, Any] = json.loads(raw)
    except urllib.error.HTTPError as exc:
        return False, f"API 错误: {exc.code} {exc.reason}"
    except Exception as exc:
        return False, f"请求失败: {exc}"

    try:
        return True, body["choices"][0]["message"]["content"]
    except Exception:
        return False, "返回格式无法解析。"


def get_ai_config() -> Dict[str, str]:
    file_cfg = _load_local_config()
    return {
        "base_url": os.getenv(
            "AI_BASE_URL",
            file_cfg.get("AI_BASE_URL", "https://api.deepseek.com/v1"),
        ),
        "model": os.getenv("AI_MODEL", file_cfg.get("AI_MODEL", "deepseek-chat")),
        "api_key": os.getenv("AI_API_KEY", file_cfg.get("AI_API_KEY", "")),
    }


def _load_local_config() -> Dict[str, str]:
    path = Path(__file__).resolve().parents[1] / "ai_config.txt"
    if not path.exists():
        return {}
    data: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        data[key.strip()] = value.strip()
    return data
