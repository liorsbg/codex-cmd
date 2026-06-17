"""Parse Codex JSONL output."""

import json
from typing import Any, List, Optional


def extract_final_message(stdout: str) -> str:
    candidates: List[str] = []

    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
        except json.JSONDecodeError:
            candidates.append(stripped)
            continue
        candidate = _event_text(event)
        if candidate:
            candidates.append(candidate)

    if not candidates:
        raise ValueError("Codex output did not include a final message")
    return candidates[-1].strip()


def _event_text(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        if value.get("type") == "agent_message" and isinstance(value.get("text"), str):
            return value["text"]
        if value.get("type") == "agent_message" and isinstance(value.get("message"), str):
            return value["message"]
        if value.get("type") in {"final_message", "final_response"} and isinstance(
            value.get("content"), str
        ):
            return value["content"]
        for nested in value.values():
            candidate = _event_text(nested)
            if candidate:
                return candidate
    if isinstance(value, list):
        for item in value:
            candidate = _event_text(item)
            if candidate:
                return candidate
    return None
