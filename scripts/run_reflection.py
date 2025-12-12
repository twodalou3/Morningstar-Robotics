# scripts/run_reflection.py

import os
import sys

# Allow importing engine.*
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.reflection_engine import run_reflection


def main() -> None:
    result = run_reflection()
    reflection = result["reflection"]
    questions = result["questions"]

    reflection_id = reflection.get("id", "N/A")
    reflection_ts = reflection.get("timestamp", "N/A")
    reflection_text = reflection.get("text", "")

    print("=== Morningstar Reflection ===\n")
    print(f"Reflection ID: {reflection_id}")
    print(f"Timestamp:     {reflection_ts}\n")
    print(reflection_text)
    print("\nQuestions:")

    if not questions:
        print("(no questions)")
    else:
        for q in questions:
            q_text = q.get("text", "")
            q_ts = q.get("timestamp", "N/A")
            print(f"- [{q_ts}] {q_text}")


if __name__ == "__main__":
    main()
