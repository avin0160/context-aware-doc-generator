#!/usr/bin/env python3
"""
Final comprehensive test with improved name extraction
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, 'src')

def main():
    print("🎯 Final System Validation")
    print("=" * 50)
    
    from src.parser import create_parser
    from src.rag import create_rag_system
    
    # Test code samples
    test_code = {
        'python': '''
def calculate_fibonacci(n):
    """Calculate fibonacci number recursively."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class Calculator:
    """A simple calculator class."""
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        return a + b
''',
        'javascript': '''
class UserManager {
    constructor() {
        this.users = [];
    }
    
    addUser(name, email) {
        this.users.push({name, email});
        return this.users.length;
    }
}

function validateEmail(email) {
    const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return regex.test(email);
}
'''
    }
    
    parser = create_parser()
    all_results = {}
    
    # Test parsing
    print("🔍 Testing Code Parsing:")
    for lang, code in test_code.items():
        print(f"\\n📝 {lang.title()} Code:")
        result = parser.parse_code(code, lang)
        
        if result:
            all_results[f'test.{lang[:2]}'] = result
            functions = result.get('functions', [])
            classes = result.get('classes', [])
            
            print(f"   Functions: {len(functions)}")
            for func in functions:
                print(f"     - {func.get('name', 'unknown')}")
            
            print(f"   Classes: {len(classes)}")
            for cls in classes:
                print(f"     - {cls.get('name', 'unknown')}")
        else:
            print(f"   ❌ Failed to parse {lang}")
    
    # Test RAG system
    if all_results:
        print("\\n🧠 Testing RAG System:")
        rag_system = create_rag_system()
        
        # Create proper codebase structure
        codebase = {
            'files': all_results,
            'summary': {
                'total_files': len(all_results),
                'languages': list(test_code.keys()),
                'total_functions': sum(len(f.get('functions', [])) for f in all_results.values()),
                'total_classes': sum(len(f.get('classes', [])) for f in all_results.values())
            }
        }
        
        print(f"   Files: {codebase['summary']['total_files']}")
        print(f"   Total functions: {codebase['summary']['total_functions']}")
        print(f"   Total classes: {codebase['summary']['total_classes']}")
        
        # Build index
        chunks = rag_system.prepare_code_chunks(codebase)
        rag_system.build_index(chunks)
        
        print(f"   Created {len(chunks)} searchable chunks")
        
        # Test searches
        queries = [
            "fibonacci recursive algorithm",
            "calculator mathematical operations", 
            "user management system",
            "email validation function"
        ]
        
        print("\\n🔎 Search Results:")
        for query in queries:
            print(f"\\n   '{query}':")
            results = rag_system.search(query, k=2)
            for i, result in enumerate(results, 1):
                chunk = result['chunk']
                score = result['score']
                name = chunk['metadata'].get('name', 'N/A')
                chunk_type = chunk['type']
                print(f"     {i}. {chunk_type} '{name}' (relevance: {score:.2f})")
    
    print("\\n" + "=" * 50)
    print("✅ System validation complete!")
    print("🎉 Your Context-Aware Documentation Generator is ready!")
    
    print("\\n📚 Usage:")
    print("  • Web UI: streamlit run src/frontend.py --server.port 8501")
    print("  • API: uvicorn src.api:app --host 0.0.0.0 --port 8000") 
    print("  • CLI: python main.py --help")
    print("  • Notebooks: Open notebooks/examples.ipynb")

if __name__ == "__main__":
    main()