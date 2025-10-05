#!/usr/bin/env python3
"""
Google Colab setup script for Context-Aware Code Documentation Generator.
Run this in a Colab cell to set up the environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and print the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} failed with error: {e}")
        return False

def setup_colab_environment():
    """Set up the Colab environment for the documentation generator."""
    
    print("🚀 Setting up Context-Aware Code Documentation Generator in Google Colab")
    print("=" * 70)
    
    # Check if we're in Colab
    try:
        import google.colab
        print("✅ Google Colab environment detected")
    except ImportError:
        print("⚠️  Warning: Not running in Google Colab")
    
    # Install system dependencies if needed
    print("\n📦 Installing system dependencies...")
    
    # Install the packages from requirements.txt
    print("\n📚 Installing Python packages...")
    success = run_command(
        "pip install -q fastapi uvicorn[standard] streamlit pydantic",
        "Installing web framework dependencies"
    )
    
    if success:
        success = run_command(
            "pip install -q tree-sitter tree-sitter-python tree-sitter-javascript tree-sitter-java tree-sitter-go tree-sitter-cpp",
            "Installing tree-sitter and language parsers"
        )
    
    if success:
        success = run_command(
            "pip install -q gitpython sentence-transformers faiss-cpu",
            "Installing Git and RAG dependencies"
        )
    
    if success:
        success = run_command(
            "pip install -q transformers torch peft bitsandbytes accelerate",
            "Installing LLM and fine-tuning dependencies"
        )
    
    if success:
        success = run_command(
            "pip install -q python-multipart aiofiles python-dotenv loguru tqdm pathlib2",
            "Installing utility dependencies"
        )
    
    # Create necessary directories
    print("\n📁 Creating project directories...")
    directories = ['models', 'temp', 'output', 'logs', 'indexes']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created: {directory}/")
    
    # Check GPU availability
    print("\n🖥️  Checking compute environment...")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✅ CUDA GPU available: {gpu_name}")
            print(f"   GPU Memory: {gpu_memory:.1f} GB")
        else:
            print("⚠️  CUDA not available, using CPU")
    except ImportError:
        print("⚠️  PyTorch not installed yet")
    
    # Test imports
    print("\n🧪 Testing imports...")
    test_imports = [
        ("tree_sitter", "Tree-sitter"),
        ("sentence_transformers", "Sentence Transformers"),
        ("transformers", "HuggingFace Transformers"),
        ("fastapi", "FastAPI"),
        ("streamlit", "Streamlit")
    ]
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} imported successfully")
        except ImportError as e:
            print(f"❌ {name} import failed: {e}")
    
    # Final setup
    print("\n🎯 Final setup...")
    
    # Set environment variables for Colab
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Avoid warnings
    os.environ['HF_HOME'] = './models'  # Cache models locally
    
    print("\n🎉 Setup completed!")
    print("\n📖 Next steps:")
    print("1. Import the modules: from src.parser import create_parser")
    print("2. Try the examples in notebooks/examples.ipynb")
    print("3. For web interface, use: !streamlit run src/frontend.py --server.port 8501")
    print("4. For API, use: !uvicorn src.api:app --host 0.0.0.0 --port 8000")
    
    return success

if __name__ == "__main__":
    setup_colab_environment()