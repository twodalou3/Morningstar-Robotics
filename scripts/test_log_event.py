import sys
import os

# Add project root to path so we can import engine
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine.event_logger import log_event

if __name__ == "__main__":
    event = log_event(
        event_type="system_boot",
        summary="Test boot event",
        source="system",
        tags=["test", "boot"],
    )
    print(event["id"])
