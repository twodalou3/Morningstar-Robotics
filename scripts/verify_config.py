import sys
import os
import unittest

# Add project root to path so we can import engine
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine.config_loader import load_mind_seed, load_constitution_text

class TestConfigLoader(unittest.TestCase):
    def test_load_mind_seed_structure(self):
        print("\nTesting load_mind_seed structure...")
        config = load_mind_seed()
        self.assertIsInstance(config, dict)
        
        required_keys = ['name', 'stage', 'core_values', 'orientation', 'constraints', 'relational_style']
        for key in required_keys:
            self.assertIn(key, config)
            
        self.assertIsInstance(config['core_values'], list)
        self.assertTrue(all(isinstance(x, str) for x in config['core_values']))
        
        self.assertIsInstance(config['constraints'], list)
        self.assertTrue(all(isinstance(x, str) for x in config['constraints']))
        
        self.assertIsInstance(config['relational_style'], dict)
        self.assertIn('role', config['relational_style'])
        self.assertIn('tone', config['relational_style'])
        print("PASS: load_mind_seed structure is correct.")

    def test_load_constitution_text_exists(self):
        print("\nTesting load_constitution_text with existing file...")
        text = load_constitution_text()
        self.assertIsInstance(text, str)
        self.assertTrue(len(text) > 0)
        print("PASS: load_constitution_text returned content.")

    def test_load_constitution_text_missing(self):
        print("\nTesting load_constitution_text with missing file...")
        # Rename constitution.md temporarily
        constitution_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'constitution.md')
        temp_path = constitution_path + ".bak"
        
        if os.path.exists(constitution_path):
            os.rename(constitution_path, temp_path)
            
        try:
            text = load_constitution_text()
            self.assertIsNone(text)
            print("PASS: load_constitution_text returned None for missing file.")
        finally:
            # Restore file
            if os.path.exists(temp_path):
                os.rename(temp_path, constitution_path)

if __name__ == '__main__':
    unittest.main()
