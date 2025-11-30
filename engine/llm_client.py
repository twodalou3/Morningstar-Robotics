import os
from dotenv import load_dotenv
from openai import OpenAI, APIError

# Load environment variables from .env file
load_dotenv()

# Initialize module-level client
# We delay the check for API key presence to the function call or client initialization
# However, the requirement says "Initialize the OpenAI client" at module level.
# OpenAI client automatically looks for OPENAI_API_KEY, but we are using LLM_API_KEY.
# So we need to pass it explicitly.

_api_key = os.getenv("LLM_API_KEY")
_client = None

if _api_key:
    _client = OpenAI(api_key=_api_key)

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Send a chat-completion request with the given system and user prompts
    and return the assistant's text content.

    Raises:
        ValueError: If LLM_API_KEY or LLM_MODEL_NAME are missing.
        RuntimeError: If the API call fails or returns an invalid response.
    """
    api_key = os.getenv("LLM_API_KEY")
    model_name = os.getenv("LLM_MODEL_NAME")

    if not api_key:
        raise ValueError("Missing environment variable: LLM_API_KEY")
    if not model_name:
        raise ValueError("Missing environment variable: LLM_MODEL_NAME")

    # Ensure client is initialized if it wasn't at module level (though we tried)
    # If _client is None here, it means api_key was missing at import time.
    # But we just checked api_key again. If it's present now (e.g. set dynamically),
    # we should use it. But for simplicity and adhering to "module-level client",
    # we rely on the global _client.
    
    global _client
    if _client is None:
         # Try to initialize again in case env var was set after import
         _client = OpenAI(api_key=api_key)

    try:
        response = _client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except APIError as e:
        raise RuntimeError(f"LLM API call failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"LLM API call failed with unexpected error: {e}") from e

    if not response.choices or not response.choices[0].message.content:
        raise RuntimeError("LLM API returned an empty response or no content.")

    return response.choices[0].message.content
