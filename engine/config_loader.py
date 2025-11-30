import json
import os
from typing import Dict, Any, Optional

def load_mind_seed() -> Dict[str, Any]:
    """
    Loads and parses config/mind_seed.json.
    
    Returns:
        dict: The configuration dictionary.
        
    Raises:
        FileNotFoundError: If the config file is missing.
        json.JSONDecodeError: If the config file is invalid JSON.
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'mind_seed.json')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Failed to parse mind_seed.json: {e.msg}", e.doc, e.pos)

def load_constitution_text() -> Optional[str]:
    """
    Loads config/constitution.md if it exists.
    
    Returns:
        str | None: The content of the constitution file, or None if it does not exist.
    """
    constitution_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'constitution.md')
    
    if not os.path.exists(constitution_path):
        return None
        
    with open(constitution_path, 'r', encoding='utf-8') as f:
        return f.read()
