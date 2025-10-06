#!/usr/bin/env python3
"""
Colab-compatible web interface startup
Disables problematic dependencies and uses CPU-only mode
"""

import os
import sys
import subprocess
import time

def setup_colab_environment():
    """Configure environment for Colab compatibility"""
    # Disable problematic features
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU
    
    print("✅ Environment configured for Colab compatibility")
    print("   - Quantization: DISABLED")
    print("   - Device: CPU only")
    print("   - Tokenizers: Single-threaded")

def start_streamlit():
    """Start Streamlit web interface"""
    print("\n🌐 Starting Streamlit Web Interface...")
    print("🔗 Once running, you'll see URLs to access the interface")
    print("=" * 60)
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    subprocess.run(cmd)

def main():
    print("🚀 Context-Aware Documentation Generator - Web UI")
    print("=" * 60)
    
    setup_colab_environment()
    start_streamlit()

if __name__ == "__main__":
    main()