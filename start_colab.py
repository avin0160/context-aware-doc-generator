#!/usr/bin/env python3
"""
Colab-specific web interface launcher with public URL access
"""

import os
import sys
import subprocess
import time

def setup_colab_environment():
    """Configure environment for Google Colab"""
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    
    print("🔍 Google Colab Environment Detected")
    print("✅ Environment configured for Colab compatibility")
    print("   - Quantization: DISABLED")
    print("   - Device: CPU only")
    print("   - Tokenizers: Single-threaded")

def install_dependencies():
    """Install required packages for Colab"""
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                  capture_output=True)
    print("✅ Dependencies installed")

def start_colab_streamlit():
    """Start Streamlit with Colab-specific configuration"""
    print("\n🌐 Starting Streamlit for Google Colab...")
    print("🔗 Colab will show public URLs below")
    print("=" * 60)
    
    # Use subprocess.Popen to capture and redirect output
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    
    # Start Streamlit
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                              universal_newlines=True)
    
    # Print output in real-time and look for URLs
    print("🚀 Starting server...")
    for line in iter(process.stdout.readline, ''):
        print(line.rstrip())
        if "External URL:" in line or "Network URL:" in line:
            print("🎯 Use the External/Network URL above to access from your browser!")
        if "You can now view your Streamlit app in your browser" in line:
            print("\n💡 IMPORTANT: In Colab, use the 'External URL' shown above")
            print("   The localhost URL won't work from your local browser")

def main():
    print("🚀 Context-Aware Documentation Generator - Colab Edition")
    print("=" * 70)
    
    # Check if we're in Colab
    try:
        import google.colab
        print("✅ Google Colab detected")
        setup_colab_environment()
        install_dependencies()
        start_colab_streamlit()
    except ImportError:
        print("❌ This script is designed for Google Colab")
        print("💡 For local use, try: python3 start_smart.py")
        print("💡 For Colab, make sure you're running in a Colab notebook")

if __name__ == "__main__":
    main()