import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

def log_event(
    event_type: str,
    summary: str,
    source: str = "system",
    payload: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Logs an event to memory/episodes.jsonl.

    Args:
        event_type: Short string describing the event type.
        summary: Human-readable summary of the event.
        source: The source of the event (default: "system").
        payload: Optional dictionary containing event details.
        tags: Optional list of tags associated with the event.

    Returns:
        dict: The created event dictionary.

    Raises:
        TypeError: If the payload is not JSON serializable.
    """
    
    # Resolve paths
    project_root = os.path.dirname(os.path.dirname(__file__))
    memory_dir = os.path.join(project_root, "memory")
    episodes_path = os.path.join(memory_dir, "episodes.jsonl")

    # Ensure directory exists
    os.makedirs(memory_dir, exist_ok=True)

    # Construct event
    event = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "event_type": event_type,
        "summary": summary,
        "payload": payload if payload is not None else {},
        "tags": tags if tags is not None else [],
    }

    # Serialize to JSON line
    try:
        json_line = json.dumps(event)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Failed to serialize event to JSON: {e}")

    # Append to file
    with open(episodes_path, "a", encoding="utf-8") as f:
        f.write(json_line + "\n")

    return event
