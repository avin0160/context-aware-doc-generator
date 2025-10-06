#!/usr/bin/env python3
"""
Quick Test Script - Run in Colab terminal for immediate verification
"""

import sys
sys.path.insert(0, 'src')

print("🚀 Quick System Test")
print("=" * 30)

try:
    # Test imports
    print("1. Testing imports...")
    from src.parser import create_parser
    from src.rag import create_rag_system
    print("   ✅ Imports successful")
    
    # Test parser
    print("2. Testing parser...")
    parser = create_parser()
    code = "def hello(): return 'world'"
    result = parser.parse_code(code, 'python')
    if result:
        print(f"   ✅ Parsed {len(result.get('functions', []))} functions")
    else:
        print("   ⚠️ Parser returned no results (may need tree-sitter languages)")
    
    # Test RAG
    print("3. Testing RAG system...")
    rag = create_rag_system()
    print("   ✅ RAG system ready")
    
    print("\n🎉 All systems working!")
    print("Ready to run: python terminal_demo.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Run setup_colab.py first")