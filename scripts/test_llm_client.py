import os
import sys

# Ensure we can import from engine
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.llm_client import call_llm

def main():
    print("Testing llm_client...")

    # Check if env vars are present to decide what to expect
    api_key = os.getenv("LLM_API_KEY")
    model_name = os.getenv("LLM_MODEL_NAME")

    if not api_key or not model_name:
        print("Environment variables missing. Expecting configuration error...")
        try:
            call_llm("System", "User")
        except ValueError as e:
            print(f"Caught expected error: {e}")
        except Exception as e:
            print(f"Caught unexpected error type: {type(e).__name__}: {e}")
            sys.exit(1)
    else:
        print(f"Found API key and model ({model_name}). Attempting real call...")
        try:
            response = call_llm(
                "You are a test system.",
                "Reply with the single word: hello.",
            )
            print(f"Response: {response}")
            if "hello" in response.lower():
                print("SUCCESS: Received expected response.")
            else:
                print("WARNING: Response did not contain 'hello'.")
        except Exception as e:
            print(f"FAILURE: API call failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Ensure we can import from engine
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    main()
