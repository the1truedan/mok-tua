#!/usr/bin/env python3
"""Convert Open WebUI SQLite chats to AgentsView's ChatGPT import format.

Read-only by design: the source database is opened with SQLite's immutable URI
mode and only a JSON export is written.  Open WebUI stores conversation turns
inside chat.chat.history.messages; the separate message table is not required.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("database", type=Path, help="Open WebUI webui.db")
    p.add_argument("output", type=Path, help="AgentsView-compatible conversations.json")
    p.add_argument("--user-id", help="Only export chats belonging to this Open WebUI user")
    p.add_argument("--limit", type=int, help="Export at most N chats (newest first)")
    return p.parse_args()


def text_parts(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    out.append(item["text"])
                elif isinstance(item.get("content"), str):
                    out.append(item["content"])
        return out
    if isinstance(value, dict):
        if isinstance(value.get("parts"), list):
            return text_parts(value["parts"])
        if isinstance(value.get("content"), (str, list)):
            return text_parts(value["content"])
    return [json.dumps(value, ensure_ascii=False, sort_keys=True)]


def convert_message(node_id: str, node: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    role = node.get("role") or (node.get("message") or {}).get("role") or "assistant"
    content = node.get("content")
    if content is None and isinstance(node.get("message"), dict):
        content = node["message"].get("content")
    created = node.get("timestamp") or node.get("created_at") or node.get("create_time")
    msg: dict[str, Any] = {
        "id": node.get("id") or node_id,
        "author": {"role": role},
        "content": {"content_type": "text", "parts": text_parts(content)},
        "status": "finished_successfully",
    }
    if created is not None:
        msg["create_time"] = created
    if node.get("model"):
        msg["metadata"] = {"model_slug": node["model"]}
    parent = node.get("parentId") or node.get("parent_id") or node.get("parent")
    return msg, parent


def convert_chat(chat_id: str, title: str | None, created: Any, updated: Any, raw: str) -> dict[str, Any] | None:
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return None
    history = data.get("history") if isinstance(data, dict) else None
    nodes = (history or {}).get("messages") if isinstance(history, dict) else None
    if not isinstance(nodes, dict):
        nodes = data.get("messages") if isinstance(data, dict) else None
    if not isinstance(nodes, dict) or not nodes:
        return None
    mapping: dict[str, Any] = {}
    for node_id, node in nodes.items():
        if not isinstance(node, dict):
            continue
        msg, parent = convert_message(node_id, node)
        children = node.get("childrenIds") or node.get("children_ids") or node.get("children") or []
        mapping[node_id] = {
            "id": node_id,
            "message": msg,
            "parent": parent,
            "children": children if isinstance(children, list) else [],
        }
    if not mapping:
        return None
    current = (history or {}).get("currentId") if isinstance(history, dict) else None
    return {
        "title": title or "Open WebUI chat",
        "create_time": created,
        "update_time": updated,
        "mapping": mapping,
        "current_node": current or next(reversed(mapping)),
        "conversation_id": chat_id,
        "source": "open-webui",
    }


def main() -> int:
    args = parse_args()
    uri = f"file:{args.database.resolve()}?mode=ro&immutable=1"
    conn = sqlite3.connect(uri, uri=True)
    query = "SELECT id,title,created_at,updated_at,chat FROM chat WHERE chat IS NOT NULL"
    params: list[Any] = []
    if args.user_id:
        query += " AND user_id = ?"
        params.append(args.user_id)
    query += " ORDER BY updated_at DESC"
    if args.limit:
        query += " LIMIT ?"
        params.append(args.limit)
    exported: list[dict[str, Any]] = []
    skipped = 0
    for row in conn.execute(query, params):
        item = convert_chat(*row)
        if item is None:
            skipped += 1
        else:
            exported.append(item)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(exported, ensure_ascii=False, indent=2) + "\n")
    print(f"exported={len(exported)} skipped={skipped} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
