import json
import os
from datetime import datetime, timezone

# Constants for file paths
MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory")
EPISODES_FILE = os.path.join(MEMORY_DIR, "episodes.jsonl")
REFLECTIONS_FILE = os.path.join(MEMORY_DIR, "reflections.jsonl")
QUESTIONS_FILE = os.path.join(MEMORY_DIR, "questions.jsonl")

def _ensure_file_exists(filepath: str):
    """Ensures that the given file exists. If not, creates an empty file."""
    if not os.path.exists(filepath):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                pass
        except OSError as e:
            # Re-raise or handle appropriately depending on strictness requirements.
            # For now, we'll let it bubble up if we can't create the file.
            raise e

def _append_entry(filepath: str, data: dict) -> dict:
    """Appends a dictionary as a JSON line to the file."""
    _ensure_file_exists(filepath)
    try:
        json_line = json.dumps(data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize data to JSON: {e}")

    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(json_line + '\n')
    
    return data

def _read_last_n(filepath: str, n: int) -> list[dict]:
    """Reads the last N entries from a JSONL file."""
    if not os.path.exists(filepath):
        return []

    entries = []
    with open(filepath, 'r', encoding='utf-8') as f:
        # This is a simple implementation. For very large files, 
        # reading the whole file might be inefficient, but for this scope it's fine.
        # A more robust solution would use `seek` from the end.
        lines = f.readlines()
        for line in lines[-n:]:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines or log them
                    continue
    
    return entries

def list_recent_episodes(limit: int = 20) -> list[dict]:
    """Returns a list of recent episodes."""
    return _read_last_n(EPISODES_FILE, limit)

def save_reflection(text: str, linked_episode_ids: list[str] | None = None) -> dict:
    """Saves a reflection object."""
    if linked_episode_ids is None:
        linked_episode_ids = []
    
    reflection = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "linked_episodes": linked_episode_ids
    }
    return _append_entry(REFLECTIONS_FILE, reflection)

def list_recent_reflections(limit: int = 20) -> list[dict]:
    """Returns a list of recent reflections."""
    return _read_last_n(REFLECTIONS_FILE, limit)

def save_question(text: str, context_episode_id: str | None = None, status: str = "open") -> dict:
    """Saves a question object."""
    question = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "context_episode_id": context_episode_id,
        "status": status
    }
    return _append_entry(QUESTIONS_FILE, question)
