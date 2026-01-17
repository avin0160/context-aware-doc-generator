#!/usr/bin/env python3
"""
Test script for inline Sphinx documentation injection with evaluation metrics
Focus: Injection quality and metrics display ONLY
"""

import os
import sys

def test_injection():
    """Test inline injection"""
    
    print("="*70)
    print("🧪 INLINE SPHINX INJECTION TEST")
    print("="*70)
    
    # Test file
    test_file = "test_undocumented.py"
    output_file = "TEMP/test_undocumented_documented.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Create output directory
    os.makedirs("TEMP", exist_ok=True)
    
    print(f"\n📄 Input: {test_file}")
    print(f"📝 Output: {output_file}")
    print(f"🎨 Style: Sphinx/reST (official standard)")
    
    # Run injection
    print("\n" + "="*70)
    print("🔧 INLINE INJECTION")
    print("="*70)
    
    cmd = f'venv\\Scripts\\python.exe inject_docs.py {test_file} -o {output_file} -s sphinx'
    print(f"\nCommand: {cmd}\n")
    
    result = os.system(cmd)
    
    if result != 0:
        print(f"\n❌ Injection failed with exit code: {result}")
        return False
    
    # Check output exists
    if not os.path.exists(output_file):
        print(f"\n❌ Output file not created: {output_file}")
        return False
    
    print(f"\n✅ Injection completed successfully")
    return True

def show_output_sample():
    """Show a sample of the generated documentation"""
    output_file = "TEMP/test_undocumented_documented.py"
    
    if not os.path.exists(output_file):
        return
    
    print("\n" + "="*70)
    print("📖 SAMPLE OUTPUT (First 40 lines)")
    print("="*70)
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:40]
            for i, line in enumerate(lines, 1):
                print(f"{i:3d} | {line.rstrip()}")
                
        # Count sphinx directives
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            param_count = content.count(':param')
            type_count = content.count(':type')
            return_count = content.count(':return')
            rtype_count = content.count(':rtype')
            
        print("\n" + "="*70)
        print("📊 SPHINX DIRECTIVES FOUND:")
        print("="*70)
        print(f"   :param directives: {param_count}")
        print(f"   :type directives: {type_count}")
        print(f"   :return directives: {return_count}")
        print(f"   :rtype directives: {rtype_count}")
        print(f"   Total Sphinx tags: {param_count + type_count + return_count + rtype_count}")
        
    except Exception as e:
        print(f"❌ Error reading output: {e}")

if __name__ == "__main__":
    print("\n🚀 Starting inline injection test...\n")
    
    success = test_injection()
    
    if success:
        show_output_sample()
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
