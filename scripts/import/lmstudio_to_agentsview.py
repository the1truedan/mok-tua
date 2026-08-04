#!/usr/bin/env python3
"""Convert LM Studio .conversation.json files to AgentsView ChatGPT-import JSON.

LM Studio stores each message as a list of alternate ``versions`` plus a
``currentlySelected`` index. Only the selected version is exported, preserving
the conversation as it was last displayed without mutating the source files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path, help="LM Studio conversations directory or one JSON file")
    p.add_argument("output", type=Path, help="AgentsView-compatible conversations.json")
    p.add_argument("--limit", type=int, help="Export at most N newest files")
    return p.parse_args()


def parts(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                out.append(item["text"])
        return out
    return []


def selected_version(record: dict[str, Any]) -> dict[str, Any] | None:
    versions = record.get("versions")
    if not isinstance(versions, list) or not versions:
        return None
    index = record.get("currentlySelected", 0)
    if not isinstance(index, int) or not 0 <= index < len(versions):
        index = 0
    selected = versions[index]
    return selected if isinstance(selected, dict) else None


def convert(path: Path) -> dict[str, Any] | None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(record, dict):
        return None
    mapping: dict[str, Any] = {}
    previous: str | None = None
    for index, raw in enumerate(record.get("messages", [])):
        if not isinstance(raw, dict):
            continue
        msg = selected_version(raw)
        if not msg:
            continue
        text = parts(msg.get("content"))
        role = msg.get("role") or "assistant"
        if not text and role not in ("system", "user", "assistant", "tool"):
            continue
        node_id = f"{path.stem}:{index}"
        mapping[node_id] = {
            "id": node_id,
            "message": {
                "id": node_id,
                "author": {"role": role},
                "content": {"content_type": "text", "parts": text},
                "status": "finished_successfully",
            },
            "parent": previous,
            "children": [],
        }
        if previous:
            mapping[previous]["children"].append(node_id)
        previous = node_id
    if not mapping:
        return None
    created = record.get("createdAt")
    title = record.get("name") or path.stem
    return {
        "title": title,
        "create_time": created,
        "update_time": record.get("assistantLastMessagedAt") or record.get("userLastMessagedAt") or created,
        "mapping": mapping,
        "current_node": previous,
        "conversation_id": f"lmstudio:{path.stem}",
        "source": "lm-studio",
        "metadata": {"preset": record.get("preset"), "system_prompt": record.get("systemPrompt")},
    }


def main() -> int:
    args = parse_args()
    files = [args.source] if args.source.is_file() else sorted(args.source.glob("*.conversation.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if args.limit:
        files = files[: args.limit]
    exported: list[dict[str, Any]] = []
    skipped = 0
    for path in files:
        item = convert(path)
        if item is None:
            skipped += 1
        else:
            exported.append(item)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(exported, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"exported={len(exported)} skipped={skipped} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
