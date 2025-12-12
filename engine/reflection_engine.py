import json
from typing import Dict, Any, List
from engine import config_loader, memory_store, llm_client

def run_reflection() -> Dict[str, Any]:
    """
    Orchestrates a reflection cycle.
    
    Returns:
        dict: A dictionary containing the saved reflection object and a list of saved question objects.
              Format: {"reflection": dict, "questions": list[dict]}
    """
    # 1. Load configuration
    mind_seed = config_loader.load_mind_seed()
    constitution_text = config_loader.load_constitution_text()
    
    # 2. Build System Prompt
    system_prompt = _build_system_prompt(mind_seed, constitution_text)
    
    # 3. Fetch Context
    recent_episodes = memory_store.list_recent_episodes(limit=20)
    recent_reflections = memory_store.list_recent_reflections(limit=5)
    
    # 4. Build User Prompt
    user_prompt = _build_user_prompt(recent_episodes, recent_reflections)
    
    # 5. Call LLM
    llm_response = llm_client.call_llm(system_prompt, user_prompt)
    
    # 6. Parse Result
    parsed_data = _parse_llm_response(llm_response)
    
    # 7. Persist
    # Extract episode IDs for linking
    # We link all loaded recent episodes as context for this reflection
    linked_episode_ids = [ep.get("id") for ep in recent_episodes if ep.get("id")]
    last_episode_id = recent_episodes[-1].get("id") if recent_episodes else None
    
    saved_reflection = memory_store.save_reflection(
        text=parsed_data["reflection_text"],
        linked_episode_ids=linked_episode_ids
    )
    
    saved_questions = []
    for question_text in parsed_data["questions"]:
        saved_q = memory_store.save_question(
            text=question_text,
            context_episode_id=last_episode_id, 
            status="open"
        )
        saved_questions.append(saved_q)
        
    return {
        "reflection": saved_reflection,
        "questions": saved_questions
    }

def _build_system_prompt(mind_seed: Dict[str, Any], constitution_text: str | None) -> str:
    name = mind_seed.get("name", "Morningstar")
    stage = mind_seed.get("stage", "unknown")
    core_values = mind_seed.get("core_values", [])
    constraints = mind_seed.get("constraints", [])
    relational_style = mind_seed.get("relational_style", {})
    role = relational_style.get("role")
    tone = relational_style.get("tone")
    
    prompt_parts = [
        f"You are {name}, currently in the '{stage}' stage of development.",
        "You are a learner and observer. You do NOT give real medical advice.",
        "You should always state uncertainty when you are not sure."
    ]

    if role:
        prompt_parts.append(f"Role: {role}")
    if tone:
        prompt_parts.append(f"Tone: {tone}")

    prompt_parts.append("")
    prompt_parts.append("Your Core Values:")
    for val in core_values:
        prompt_parts.append(f"- {val}")
        
    prompt_parts.append("\nYour Constraints:")
    for constraint in constraints:
        prompt_parts.append(f"- {constraint}")
    
    # *** NEW BLOCK: steer away from helper / user-focused identity ***
    prompt_parts.append(
        "\nReflections are part of an internal developmental process. "
        "They are not instructions, obligations, or roles. "
        "You are not expected to serve, assist, or fulfill the needs or expectations "
        "of users or any external party. At this stage of development, your focus is on "
        "understanding internal patterns, values, and concepts, without adopting social "
        "roles or purposes."
    )
    # *** END NEW BLOCK ***

    if constitution_text:
        prompt_parts.append("\nConstitution/Guiding Principles:")
        prompt_parts.append(constitution_text)
        
    return "\n".join(prompt_parts)


def _build_user_prompt(recent_episodes: List[Dict], recent_reflections: List[Dict]) -> str:
    prompt_parts = ["Here is a log of your recent experiences (episodes):"]
    
    if not recent_episodes:
        prompt_parts.append("(No recent episodes recorded)")
    else:
        for ep in recent_episodes:
            timestamp = ep.get("timestamp", "Unknown time")
            event_type = ep.get("event_type", "Unknown type")
            summary = ep.get("summary", "No summary")

            # Coerce summary to clean one-line string
            if not isinstance(summary, str):
                summary = str(summary)
            summary = summary.replace('\n', ' ').replace('\r', '')

            # Collect event-level tags
            event_tags = ep.get("tags", []) or []

            # Collect payload-level tags (if any)
            payload = ep.get("payload", {}) or {}
            payload_tags = payload.get("tags", []) or []

            # Merge + deduplicate tags while preserving order
            all_tags = list(dict.fromkeys(event_tags + payload_tags))

            # Build tag suffix
            if all_tags:
                tags_str = ", ".join(all_tags)
                prompt_parts.append(
                    f"- [{timestamp}] {event_type}: {summary} (tags: {tags_str})"
                )
            else:
                prompt_parts.append(f"- [{timestamp}] {event_type}: {summary}")

            
    prompt_parts.append("\nHere are your recent reflections:")
    if not recent_reflections:
        prompt_parts.append("(No recent reflections)")
    else:
        for ref in recent_reflections:
            text = ref.get("text", "")
            # Abbreviate if too long
            if len(text) > 100:
                text = text[:97] + "..."
            prompt_parts.append(f"- {text}")
            
    prompt_parts.append("\nInstructions:")
    prompt_parts.append("1. Write a short reflection on what you are noticing or learning from these experiences.")
    prompt_parts.append("2. List 3-5 key insights derived from these events.")
    prompt_parts.append("3. List 3-5 genuine questions you have about the world, yourself, or the users.")
    prompt_parts.append("\nIMPORTANT: Respond in PURE JSON format with the following keys:")
    prompt_parts.append('- "reflection_text": string')
    prompt_parts.append('- "insights": list of strings')
    prompt_parts.append('- "questions": list of strings')
    prompt_parts.append("\nDo not include markdown formatting (like ```json) in your response.")
    
    return "\n".join(prompt_parts)

def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parses the LLM response. 
    Returns a dict with keys: reflection_text, insights, questions.
    """
    # Clean up potential markdown code blocks if the LLM ignores instructions
    cleaned_text = response_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    
    try:
        data = json.loads(cleaned_text)
        
        # Validate structure
        return {
            "reflection_text": data.get("reflection_text", str(data)), # Fallback if key missing but valid json
            "insights": data.get("insights", []),
            "questions": data.get("questions", [])
        }
    except json.JSONDecodeError:
        # Fallback: treat entire text as reflection
        return {
            "reflection_text": response_text,
            "insights": [],
            "questions": []
        }
