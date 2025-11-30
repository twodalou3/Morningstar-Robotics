import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine.memory_store import (
    save_reflection,
    list_recent_reflections,
    save_question,
    list_recent_episodes
)

def test_memory_store():
    print("Testing Memory Store...")

    # Test Reflections
    print("\n--- Testing Reflections ---")
    ref1 = save_reflection("This is a test reflection.", linked_episode_ids=["ep1", "ep2"])
    print(f"Saved reflection: {ref1}")
    
    ref2 = save_reflection("Another reflection without links.")
    print(f"Saved reflection: {ref2}")

    recent_refs = list_recent_reflections(limit=5)
    print(f"Recent reflections ({len(recent_refs)}):")
    for r in recent_refs:
        print(r)
    
    # Test Questions
    print("\n--- Testing Questions ---")
    q1 = save_question("What is the meaning of life?", context_episode_id="ep3")
    print(f"Saved question: {q1}")

    q2 = save_question("Why is the sky blue?", status="answered")
    print(f"Saved question: {q2}")

    # Test Episodes (assuming empty or existing)
    print("\n--- Testing Episodes ---")
    episodes = list_recent_episodes()
    print(f"Recent episodes ({len(episodes)}):")
    for e in episodes:
        print(e)

if __name__ == "__main__":
    test_memory_store()
