# scripts/upload_episode_from_file.py

import os
import sys
import json
import argparse
from typing import Any, Dict

# Make sure engine modules import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.event_logger import log_event


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log a new episode into Morningstar's memory from a JSON file."
    )
    parser.add_argument(
        "json_path",
        type=str,
        help="Path to a JSON file describing the episode.",
    )
    return parser.parse_args()


def load_episode_spec(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required = ["event_type", "source", "summary", "content"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Episode JSON missing required keys: {', '.join(missing)}")

    # Tags can be missing — that’s fine
    data.setdefault("event_tags", [])
    data.setdefault("payload_tags", [])

    if not isinstance(data["event_tags"], list):
        raise ValueError("'event_tags' must be a list.")

    if not isinstance(data["payload_tags"], list):
        raise ValueError("'payload_tags' must be a list.")

    return data


def main() -> None:
    args = parse_args()

    # 1. Load JSON
    ep = load_episode_spec(args.json_path)

    event_type = ep["event_type"]
    source = ep["source"]
    summary = ep["summary"]
    content = ep["content"]
    event_tags = ep["event_tags"]
    payload_tags = ep["payload_tags"]

    # 2. Build payload object (payload-level tags stay inside it)
    payload: Dict[str, Any] = {
        "summary": summary,
        "content": content,
        "tags": payload_tags,
    }

    # Allow optional "type"
    if "type" in ep:
        payload["type"] = ep["type"]

    # 3. Log the episode
    event = log_event(
        event_type=event_type,
        summary=summary,
        source=source,
        payload=payload,
        tags=event_tags,     # ← EVENT-level tags
    )

    print("=== Logged Episode ===")
    print(f"ID:        {event['id']}")
    print(f"Timestamp: {event['timestamp']}")
    print(f"Source:    {event['source']}")
    print(f"Type:      {event['event_type']}")
    print(f"Summary:   {event['summary']}")
    print(f"Event Tags: {', '.join(event['tags']) if event['tags'] else '(none)'}")
    print(f"Payload Tags: {', '.join(payload_tags) if payload_tags else '(none)'}")


if __name__ == "__main__":
    main()
