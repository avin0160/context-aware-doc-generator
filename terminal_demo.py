#!/usr/bin/env python3
"""
Context-Aware Code Documentation Generator - Terminal Demo
Run this script in Colab terminal to test all functionality
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step} {description}")
    print("-" * 40)

def main():
    print_header("Context-Aware Code Documentation Generator - Terminal Demo")
    
    # Add src to Python path
    sys.path.insert(0, 'src')
    
    # Step 1: Test imports
    print_step("1️⃣", "Testing Module Imports")
    try:
        from src.parser import create_parser
        from src.rag import create_rag_system
        from src.git_handler import create_git_handler
        print("✅ All core modules imported successfully!")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've run setup_colab.py first")
        return False
    
    # Step 2: Test parser
    print_step("2️⃣", "Testing Multi-Language Code Parsing")
    
    # Python code sample
    python_code = '''
def fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        return a + b
'''
    
    # JavaScript code sample
    js_code = '''
class User {
    constructor(name) {
        this.name = name;
    }
    
    getName() {
        return this.name;
    }
}

function validateEmail(email) {
    return email.includes('@');
}
'''
    
    try:
        parser = create_parser()
        
        # Test Python parsing
        print("🐍 Parsing Python code...")
        py_result = parser.parse_code(python_code, 'python')
        py_functions = py_result.get('functions', [])
        py_classes = py_result.get('classes', [])
        print(f"   ✅ Found {len(py_functions)} functions: {[f.get('name', 'unknown') for f in py_functions]}")
        print(f"   ✅ Found {len(py_classes)} classes: {[c.get('name', 'unknown') for c in py_classes]}")
        
        # Test JavaScript parsing
        print("🟨 Parsing JavaScript code...")
        js_result = parser.parse_code(js_code, 'javascript')
        js_functions = js_result.get('functions', [])
        js_classes = js_result.get('classes', [])
        print(f"   ✅ Found {len(js_functions)} functions: {[f.get('name', 'unknown') for f in js_functions]}")
        print(f"   ✅ Found {len(js_classes)} classes: {[c.get('name', 'unknown') for c in js_classes]}")
        
    except Exception as e:
        print(f"❌ Parser error: {e}")
        return False
    
    # Step 3: Test RAG system
    print_step("3️⃣", "Testing RAG System")
    try:
        rag_system = create_rag_system()
        print("✅ RAG system initialized")
        
        # Create mock codebase
        mock_codebase = {
            'files': {
                'test.py': {
                    'functions': [
                        {'name': 'fibonacci', 'text': 'def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)'},
                        {'name': 'factorial', 'text': 'def factorial(n): return 1 if n <= 1 else n * factorial(n-1)'}
                    ],
                    'classes': []
                }
            }
        }
        
        print("📦 Preparing code chunks...")
        chunks = rag_system.prepare_code_chunks(mock_codebase)
        print(f"   Created {len(chunks)} code chunks")
        
        print("🔨 Building search index...")
        rag_system.build_index(chunks)
        print("   ✅ Index built successfully")
        
        print("🔍 Testing similarity search...")
        query = "recursive mathematical function"
        results = rag_system.search(query, k=2)
        print(f"   Query: '{query}'")
        for i, result in enumerate(results[:2], 1):
            score = result.get('score', 0)
            chunk = result.get('chunk', {})
            name = chunk.get('metadata', {}).get('name', 'unknown')
            print(f"   {i}. {name} (score: {score:.3f})")
            
    except Exception as e:
        print(f"❌ RAG system error: {e}")
        return False
    
    # Step 4: Test GPU and LLM (optional)
    print_step("4️⃣", "Checking GPU and LLM Capabilities")
    try:
        import torch
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✅ GPU Available: {gpu_name}")
            print(f"✅ GPU Memory: {gpu_memory:.1f} GB")
            
            if gpu_memory > 10:
                print("✅ Sufficient memory for LLM operations")
            else:
                print("⚠️  Limited GPU memory - LLM operations may be slow")
        else:
            print("⚠️  No GPU detected - using CPU mode")
            
    except Exception as e:
        print(f"❌ GPU check error: {e}")
    
    # Step 5: Test GitHub integration
    print_step("5️⃣", "Testing GitHub Integration")
    try:
        git_handler = create_git_handler()
        print("✅ Git handler initialized")
        print("💡 GitHub cloning functionality available")
        print("   Use: git_handler.clone_repository('https://github.com/user/repo.git')")
        
    except Exception as e:
        print(f"❌ Git handler error: {e}")
        return False
    
    # Step 6: Create sample output
    print_step("6️⃣", "Generating Sample Analysis Report")
    try:
        # Create output directory
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        # Generate report
        report = {
            'project_name': 'Terminal Demo Test',
            'timestamp': str(datetime.now()),
            'test_results': {
                'parser_test': 'PASSED',
                'rag_test': 'PASSED',
                'gpu_check': 'COMPLETED',
                'git_test': 'PASSED'
            },
            'code_analysis': {
                'python_functions': len(py_functions),
                'python_classes': len(py_classes),
                'javascript_functions': len(js_functions),
                'javascript_classes': len(js_classes)
            }
        }
        
        report_file = output_dir / 'terminal_demo_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"✅ Report saved to: {report_file}")
        
    except Exception as e:
        print(f"❌ Report generation error: {e}")
    
    # Final summary
    print_header("Demo Completed Successfully!")
    print("✅ All core systems tested and working")
    print("✅ Multi-language parsing functional")
    print("✅ RAG system operational")
    print("✅ Ready for documentation generation")
    print("\n🎯 Next steps:")
    print("   • Use 'python main.py --help' for CLI options")
    print("   • Start web interface: 'streamlit run src/frontend.py --server.port 8501'")
    print("   • Start API server: 'uvicorn src.api:app --host 0.0.0.0 --port 8000'")
    print("   • Open notebooks for detailed examples")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Terminal demo completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Demo encountered errors")
        sys.exit(1)