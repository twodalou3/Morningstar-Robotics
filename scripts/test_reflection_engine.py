import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine import reflection_engine

class TestReflectionEngine(unittest.TestCase):
    
    @patch('engine.reflection_engine.config_loader')
    @patch('engine.reflection_engine.memory_store')
    @patch('engine.reflection_engine.llm_client')
    def test_run_reflection_success(self, mock_llm, mock_memory, mock_config):
        # Setup mocks
        mock_config.load_mind_seed.return_value = {
            "name": "TestBot",
            "stage": "Alpha",
            "core_values": ["Helpfulness"],
            "constraints": ["No harm"],
            "relational_style": {
                "role": "Mentor",
                "tone": "Warm"
            }
        }
        mock_config.load_constitution_text.return_value = "Be good."
        
        mock_memory.list_recent_episodes.return_value = [
            {"id": "ep1", "timestamp": "2023-01-01", "event_type": "test", "summary": "Something happened\nover multiple lines"}
        ]
        mock_memory.list_recent_reflections.return_value = []
        
        mock_llm.call_llm.return_value = '{"reflection_text": "I am thinking.", "insights": ["Aha!"], "questions": ["Why?"]}'
        
        mock_memory.save_reflection.return_value = {"id": "ref1", "text": "I am thinking."}
        mock_memory.save_question.side_effect = lambda text, context_episode_id, status: {"text": text}
        
        # Run
        result = reflection_engine.run_reflection()
        
        # Verify
        mock_config.load_mind_seed.assert_called_once()
        mock_memory.list_recent_episodes.assert_called_once()
        mock_llm.call_llm.assert_called_once()
        
        # Check prompts passed to LLM (basic check)
        args, _ = mock_llm.call_llm.call_args
        system_prompt, user_prompt = args
        self.assertIn("TestBot", system_prompt)
        self.assertIn("Be good", system_prompt)
        self.assertIn("Role: Mentor", system_prompt)
        self.assertIn("Tone: Warm", system_prompt)
        self.assertIn("Something happened over multiple lines", user_prompt)
        
        # Check persistence
        mock_memory.save_reflection.assert_called_once_with(
            text="I am thinking.",
            linked_episode_ids=["ep1"]
        )
        mock_memory.save_question.assert_called_once_with(
            text="Why?",
            context_episode_id="ep1",
            status="open"
        )
        
        self.assertEqual(result["reflection"]["text"], "I am thinking.")
        self.assertEqual(len(result["questions"]), 1)

    @patch('engine.reflection_engine.config_loader')
    @patch('engine.reflection_engine.memory_store')
    @patch('engine.reflection_engine.llm_client')
    def test_run_reflection_bad_json(self, mock_llm, mock_memory, mock_config):
        # Setup mocks
        mock_config.load_mind_seed.return_value = {}
        mock_config.load_constitution_text.return_value = None
        mock_memory.list_recent_episodes.return_value = []
        mock_memory.list_recent_reflections.return_value = []
        
        # Return invalid JSON
        mock_llm.call_llm.return_value = "This is not JSON."
        
        mock_memory.save_reflection.return_value = {"text": "This is not JSON."}
        
        # Run
        result = reflection_engine.run_reflection()
        
        # Verify fallback behavior
        mock_memory.save_reflection.assert_called_once_with(
            text="This is not JSON.",
            linked_episode_ids=[]
        )
        mock_memory.save_question.assert_not_called()
        
        self.assertEqual(result["reflection"]["text"], "This is not JSON.")
        self.assertEqual(result["questions"], [])

if __name__ == '__main__':
    unittest.main()
