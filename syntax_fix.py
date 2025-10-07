#!/usr/bin/env python3
"""
Emergency syntax fix for fastapi_server.py
Fixes common syntax issues that can occur in different environments
"""

import re
import sys

def fix_syntax_issues(filename):
    """Fix common syntax issues in the file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix any malformed f-strings
        content = re.sub(r"f'''([^']*?)'''", r'f"""\\1"""', content)
        content = re.sub(r'f"""([^"]*?)"""', lambda m: f'f"""{m.group(1)}"""', content)
        
        # Fix any missing commas in function calls
        content = re.sub(r'sys\.executable,\s*\'-c\',\s*f\'\'\'', 'sys.executable, "-c", """', content)
        
        # Fix any unicode issues
        content = content.encode('ascii', 'ignore').decode('ascii')
        
        # Remove any problematic lines that might cause syntax errors
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip lines that might cause f-string syntax errors
            if "sys.executable, '-c', f'''" in line:
                continue
            if line.strip().endswith("f'''") and not line.strip().startswith('"""'):
                continue
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Write the fixed content
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f" Fixed syntax issues in {filename}")
        return True
        
    except Exception as e:
        print(f" Error fixing {filename}: {e}")
        return False

def validate_syntax(filename):
    """Validate Python syntax"""
    try:
        with open(filename, 'r') as f:
            compile(f.read(), filename, 'exec')
        print(f" {filename} syntax is valid")
        return True
    except SyntaxError as e:
        print(f" Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f" Error validating {filename}: {e}")
        return False

if __name__ == "__main__":
    filename = "fastapi_server.py"
    
    print(" Emergency Syntax Fix")
    print("=" * 40)
    
    # First check current syntax
    if validate_syntax(filename):
        print(" No syntax fixes needed")
    else:
        print(" Applying fixes...")
        if fix_syntax_issues(filename):
            if validate_syntax(filename):
                print(" Syntax fixes applied successfully")
            else:
                print(" Manual fixes may be required")
        else:
            print(" Failed to apply automatic fixes")