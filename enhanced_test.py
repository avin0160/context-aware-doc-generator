#!/usr/bin/env python3
"""
Enhanced system test with real parsing and better debugging
"""

import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, 'src')

def test_parser_with_real_code():
    """Test parser with actual code files"""
    from src.parser import create_parser
    
    print("🧪 Testing Parser with Real Code")
    print("-" * 40)
    
    # Create temporary files with actual code
    test_files = {
        'test_python.py': '''
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
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
''',
        'test_js.js': '''
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
    results = {}
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Created temp directory: {temp_dir}")
    
    try:
        for filename, content in test_files.items():
            # Write file
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content.strip())
            
            # Parse file
            print(f"\\n📄 Parsing {filename}...")
            result = parser.parse_file(file_path)
            
            if result:
                results[filename] = result
                print(f"   Language: {result.get('language', 'unknown')}")
                print(f"   Functions: {len(result.get('functions', []))}")
                print(f"   Classes: {len(result.get('classes', []))}")
                
                # Print function names
                func_names = [f.get('name', 'unknown') for f in result.get('functions', [])]
                if func_names:
                    print(f"   Function names: {func_names}")
                
                # Print class names  
                class_names = [c.get('name', 'unknown') for c in result.get('classes', [])]
                if class_names:
                    print(f"   Class names: {class_names}")
            else:
                print(f"   ❌ Failed to parse {filename}")
        
        return results, temp_dir
        
    except Exception as e:
        print(f"❌ Parser test error: {e}")
        return {}, temp_dir

def test_rag_with_parsed_data(parsed_results):
    """Test RAG system with real parsed data"""
    from src.rag import create_rag_system
    
    print("\\n🧠 Testing RAG with Parsed Data")
    print("-" * 40)
    
    if not parsed_results:
        print("❌ No parsed data to test with")
        return False
    
    try:
        rag_system = create_rag_system()
        print("✅ RAG system created")
        
        # Convert parsed results to codebase format
        codebase = {
            'files': parsed_results,
            'summary': {
                'total_files': len(parsed_results),
                'languages': list(set(f.get('language', 'unknown') for f in parsed_results.values())),
                'total_functions': sum(len(f.get('functions', [])) for f in parsed_results.values()),
                'total_classes': sum(len(f.get('classes', [])) for f in parsed_results.values())
            }
        }
        
        print(f"📊 Codebase summary:")
        print(f"   Files: {codebase['summary']['total_files']}")
        print(f"   Languages: {codebase['summary']['languages']}")
        print(f"   Functions: {codebase['summary']['total_functions']}")
        print(f"   Classes: {codebase['summary']['total_classes']}")
        
        # Prepare chunks
        print("\\n📦 Preparing code chunks...")
        chunks = rag_system.prepare_code_chunks(codebase)
        print(f"   Created {len(chunks)} chunks")
        
        if chunks:
            # Show chunk details
            for i, chunk in enumerate(chunks[:3]):
                print(f"   Chunk {i+1}: {chunk['type']} - {chunk['metadata'].get('name', 'N/A')}")
        
        # Build index
        print("\\n🔨 Building index...")
        rag_system.build_index(chunks)
        print("✅ Index built")
        
        # Test search
        if chunks:
            test_queries = [
                "fibonacci recursive function",
                "calculator class",
                "email validation"
            ]
            
            print("\\n🔍 Testing searches:")
            for query in test_queries:
                print(f"\\n   Query: '{query}'")
                try:
                    results = rag_system.search(query, k=2)
                    if results:
                        for j, result in enumerate(results, 1):
                            chunk = result['chunk']
                            score = result['score']
                            name = chunk['metadata'].get('name', 'N/A')
                            print(f"     {j}. {chunk['type']} '{name}' (score: {score:.3f})")
                    else:
                        print("     No results found")
                except Exception as e:
                    print(f"     Search error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG test error: {e}")
        return False

def cleanup_temp_dir(temp_dir):
    """Clean up temporary directory"""
    import shutil
    try:
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up {temp_dir}")
    except:
        pass

def main():
    print("🚀 Enhanced System Test")
    print("=" * 50)
    
    # Test parser
    parsed_results, temp_dir = test_parser_with_real_code()
    
    # Test RAG
    rag_success = test_rag_with_parsed_data(parsed_results)
    
    # Cleanup
    cleanup_temp_dir(temp_dir)
    
    # Summary
    print("\\n" + "=" * 50)
    if parsed_results and rag_success:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)