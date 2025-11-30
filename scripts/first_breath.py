import sys
import os

# Ensure the project root is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.event_logger import log_event
from engine.reflection_engine import run_reflection

def main():
    # 1. Log Boot Event
    log_event(
        event_type="system_boot",
        summary="Morningstar Seed initialized for the first time.",
        source="system",
        tags=["first_breath", "boot"]
    )

    # 2. Run Reflection
    result = run_reflection()
    reflection = result["reflection"]
    questions = result["questions"]

    # 3. Print Output
    print("=== Morningstar First Breath ===")
    
    # Reflection Section
    ref_id = reflection.get("id", "N/A")
    ref_time = reflection.get("timestamp", "N/A")
    ref_text = reflection.get("text", "No text provided")
    
    print(f"\nReflection ID: {ref_id}")
    print(f"Timestamp: {ref_time}")
    print(f"\n{ref_text}")

    # Questions Section
    print("\nQuestions:")
    for q in questions:
        q_id = q.get("id", "N/A")
        q_time = q.get("timestamp", "N/A")
        q_text = q.get("text", "No text provided")
        print(f"- [{q_id} @ {q_time}] {q_text}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"First breath failed: {e}")
        raise
