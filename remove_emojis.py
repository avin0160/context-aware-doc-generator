#!/usr/bin/env python3
"""
Remove all emojis from Python files to fix Unicode syntax errors
"""

import os
import re
import sys

def remove_emojis_from_text(text):
    """Remove emoji characters from text"""
    # Unicode ranges for emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def clean_file(filepath):
    """Remove emojis from a single file"""
    try:
        print(f"Cleaning: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove emojis
        clean_content = remove_emojis_from_text(content)
        
        # Check if any changes were made
        if content != clean_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            print(f"   Cleaned emojis from {filepath}")
            return True
        else:
            print(f"  - No emojis found in {filepath}")
            return False
            
    except Exception as e:
        print(f"   Error cleaning {filepath}: {e}")
        return False

def main():
    """Main function to clean all Python files"""
    print(" Removing emojis from all Python files")
    print("=" * 50)
    
    # Get all Python files in current directory
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    cleaned_count = 0
    for filepath in python_files:
        if clean_file(filepath):
            cleaned_count += 1
    
    print("\n" + "=" * 50)
    print(f" Processed {len(python_files)} Python files")
    print(f" Cleaned {cleaned_count} files")
    print(" All files should now be emoji-free!")

if __name__ == "__main__":
    main()