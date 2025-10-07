#!/usr/bin/env python3
"""
Lightweight local tester - minimal dependencies
Tests core functionality without heavy ML libraries
"""

import sys
import os
import tempfile

def check_basic_python():
    """Test basic Python functionality"""
    print("🐍 Testing Basic Python...")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print("✅ Python working")

def test_file_operations():
    """Test file I/O without external dependencies"""
    print("\n📁 Testing File Operations...")
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def hello_world():
    '''Simple test function'''
    return "Hello, World!"

class TestClass:
    '''Simple test class'''
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
""")
        temp_file = f.name
    
    print(f"   Created test file: {temp_file}")
    
    # Read file back
    with open(temp_file, 'r') as f:
        content = f.read()
        lines = len(content.split('\n'))
        print(f"   File contains {lines} lines")
        print(f"   Found 'def' keywords: {content.count('def')}")
        print(f"   Found 'class' keywords: {content.count('class')}")
    
    # Cleanup
    os.unlink(temp_file)
    print("✅ File operations working")

def test_basic_parsing():
    """Test basic string parsing without tree-sitter"""
    print("\n🔍 Testing Basic Code Analysis...")
    
    sample_code = """
def fibonacci(n):
    '''Calculate fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    '''Simple calculator class'''
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

def main():
    calc = Calculator()
    result = calc.add(5, 3)
    print(f"Result: {result}")
"""
    
    # Simple regex-based analysis
    import re
    
    # Find functions
    func_pattern = r'def\s+(\w+)\s*\('
    functions = re.findall(func_pattern, sample_code)
    
    # Find classes  
    class_pattern = r'class\s+(\w+)\s*[:(]'
    classes = re.findall(class_pattern, sample_code)
    
    print(f"   Functions found: {functions}")
    print(f"   Classes found: {classes}")
    print(f"   Total functions: {len(functions)}")
    print(f"   Total classes: {len(classes)}")
    print("✅ Basic parsing working")

def test_memory_usage():
    """Check current memory usage"""
    print("\n💾 Memory Check...")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"   Total RAM: {memory.total / (1024**3):.1f} GB")
        print(f"   Available: {memory.available / (1024**3):.1f} GB")
        print(f"   Used: {memory.percent}%")
        
        if memory.percent > 85:
            print("⚠️  High memory usage detected!")
            print("💡 Recommend closing other applications")
        else:
            print("✅ Memory usage looks good")
            
    except ImportError:
        print("   psutil not available - skipping memory check")
        print("✅ Continuing without memory monitoring")

def test_core_modules():
    """Test availability of core modules"""
    print("\n📦 Testing Core Module Availability...")
    
    core_modules = [
        'json', 'os', 'sys', 'tempfile', 're', 
        'pathlib', 'subprocess', 'time'
    ]
    
    available = []
    missing = []
    
    for module in core_modules:
        try:
            __import__(module)
            available.append(module)
        except ImportError:
            missing.append(module)
    
    print(f"   Available modules: {len(available)}/{len(core_modules)}")
    print(f"   Available: {', '.join(available)}")
    
    if missing:
        print(f"   Missing: {', '.join(missing)}")
    else:
        print("✅ All core modules available")

def main():
    print("🚀 Context-Aware Documentation Generator - Local Test")
    print("=" * 60)
    print("💡 Lightweight testing without heavy dependencies")
    print()
    
    try:
        check_basic_python()
        test_core_modules()
        test_memory_usage()
        test_file_operations()
        test_basic_parsing()
        
        print("\n" + "=" * 60)
        print("🎉 LOCAL TEST COMPLETE!")
        print("✅ Your system can handle the basic functionality")
        print()
        print("💡 Next steps (when memory allows):")
        print("   1. Install minimal deps: pip install streamlit")
        print("   2. Test web interface: python3 start_web.py")
        print("   3. Or stick with terminal: python3 final_test.py")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("💡 This might indicate system resource constraints")

if __name__ == "__main__":
    main()