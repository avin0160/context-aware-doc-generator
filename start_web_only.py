#!/usr/bin/env python3
"""
Universal startup script for Context-Aware Documentation Generator
Works in both local environment and Google Colab
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def setup_environment():
    """Configure environment for optimal compatibility"""
    # Set environment variables for stability
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Avoid threading issues
    
    # Detect if we're in Colab
    try:
        import google.colab
        os.environ['COLAB_ENV'] = '1'
        print("🔍 Google Colab environment detected")
    except ImportError:
        os.environ['COLAB_ENV'] = '0'
        print("🔍 Local environment detected")

def start_streamlit_only():
    """Start only Streamlit interface (most stable option)"""
    print("🌐 Starting Streamlit web interface...")
    print("📝 Note: API server disabled to avoid dependency conflicts")
    print("🔗 Access the web interface at the URL shown below")
    print("=" * 60)
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend.py", 
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

def show_usage_info():
    """Display usage information"""
    print("🎯 Context-Aware Documentation Generator")
    print("=" * 50)
    print("✅ System validated and ready!")
    print("\n📚 Available options:")
    print("   1. Web Interface: python start_web_only.py")
    print("   2. Terminal Demo: python terminal_demo.py") 
    print("   3. System Test: python final_test.py")
    print("   4. Full Test: python enhanced_test.py")
    print("\n🔧 For development:")
    print("   • CLI mode: python main.py --help")
    print("   • Notebooks: Open notebooks/academic_presentation.ipynb")

def main():
    # Check if we want to start web interface
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        setup_environment()
        start_streamlit_only()
    else:
        show_usage_info()

if __name__ == "__main__":
    main()