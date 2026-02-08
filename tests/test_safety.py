#!/usr/bin/env python3
"""
Safety test: ensure no prohibited Ansible modules are used.
"""

import os
import re
import unittest


class TestSafety(unittest.TestCase):
    """Test that no dangerous modules are present in YAML files."""
    
    def test_no_prohibited_modules(self):
        """Scan all YAML files for prohibited modules."""
        prohibited = [
            r'\bapt:\s',
            r'\byum:\s',
            r'\blineinfile:\s',
            r'\bfile:\s.*state=',
            r'\bcopy:\s',
            r'\bshell:\s.*rm\s',
            r'\bshell:\s.*delete\s',
            r'\bshell:\s.*uninstall\s',
            r'\bcommand:\s.*rm\s',
            r'\bcommand:\s.*delete\s',
            r'\bcommand:\s.*uninstall\s',
        ]
        
        root_dir = os.path.dirname(os.path.dirname(__file__))
        yaml_files = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Skip hidden directories
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for filename in filenames:
                if filename.endswith('.yml') or filename.endswith('.yaml'):
                    full_path = os.path.join(dirpath, filename)
                    yaml_files.append(full_path)
        
        failures = []
        for yaml_file in yaml_files:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in prohibited:
                    if re.search(pattern, content, re.IGNORECASE):
                        failures.append(f"{yaml_file}: matches {pattern}")
        
        if failures:
            self.fail("Prohibited modules found:\n" + "\n".join(failures))
        
        print(f"Safety check passed. Scanned {len(yaml_files)} YAML files.")


if __name__ == '__main__':
    unittest.main()