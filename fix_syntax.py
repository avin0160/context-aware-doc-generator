#!/usr/bin/env python3
"""
Fix all string and syntax issues in Python files
"""

import os
import re
import ast

def fix_string_issues(content):
    """Fix common string and syntax issues"""
    
    # Fix multiline strings that might be malformed
    lines = content.split('\n')
    fixed_lines = []
    in_multiline_string = False
    current_quote = None
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Skip lines that are clearly documentation (markdown-style)
        stripped = line.strip()
        if (stripped.startswith('#') or 
            stripped.startswith('##') or 
            stripped.startswith('###') or
            stripped.startswith('- ') or
            stripped.startswith('* ') or
            stripped == '' or
            'Args:' in stripped or
            'Returns:' in stripped or
            'Raises:' in stripped or
            'Example:' in stripped or
            'Examples:' in stripped or
            'Note:' in stripped):
            fixed_lines.append(original_line)
            continue
            
        # Fix any remaining formatting issues
        line = line.replace('**', '')  # Remove markdown bold
        line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)  # Remove markdown links
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def validate_and_fix_file(filepath):
    """Validate and fix a Python file"""
    try:
        print(f"Fixing: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # First try to compile to check for syntax errors
        try:
            ast.parse(content)
            print(f"  ✓ {filepath} is valid")
            return True
        except SyntaxError as e:
            print(f"  ! Syntax error in {filepath} at line {e.lineno}: {e.msg}")
            
            # Try to fix common issues
            fixed_content = fix_string_issues(content)
            
            try:
                ast.parse(fixed_content)
                # If parsing succeeds, write the fixed content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"  ✓ Fixed {filepath}")
                return True
            except SyntaxError:
                print(f"  ✗ Could not automatically fix {filepath}")
                return False
                
    except Exception as e:
        print(f"  ✗ Error processing {filepath}: {e}")
        return False

def main():
    """Fix all Python files"""
    print("Fixing syntax issues in all Python files")
    print("=" * 50)
    
    # Focus on key files first
    key_files = ['comprehensive_docs.py', 'fastapi_server.py', 'generic_docs.py', 'complete_test.py']
    
    for filepath in key_files:
        if os.path.exists(filepath):
            validate_and_fix_file(filepath)
    
    print("\n" + "=" * 50)
    print("✓ Key files processed")

if __name__ == "__main__":
    main()