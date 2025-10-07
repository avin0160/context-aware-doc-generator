#!/usr/bin/env python3
"""
Complete solution: Start both Streamlit and API with full compatibility
"""

import os
import sys
import subprocess
import time
import signal

def setup_full_environment():
    """Setup complete environment"""
    # Colab compatibility
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    # Detect environment
    try:
        import google.colab
        print("🔍 Google Colab detected - optimized for cloud")
        os.environ['COLAB_ENV'] = '1'
    except ImportError:
        print("🔍 Local environment detected")
        os.environ['COLAB_ENV'] = '0'

def start_both_servers():
    """Start both Streamlit and API servers"""
    print("🚀 Starting Complete Documentation Generator")
    print("=" * 60)
    
    setup_full_environment()
    
    # Start API server in background
    print("🔗 Starting API server (port 8000)...")
    api_cmd = [
        sys.executable, "-m", "uvicorn", 
        "src.api:app", "--host", "0.0.0.0", "--port", "8000"
    ]
    
    try:
        api_process = subprocess.Popen(api_cmd, 
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        time.sleep(3)  # Give API time to start
        print("✅ API server starting...")
    except Exception as e:
        print(f"⚠️  API server issue: {e}")
        print("🔄 Continuing with Streamlit only...")
        api_process = None
    
    # Start Streamlit
    print("🌐 Starting Streamlit interface (port 8501)...")
    streamlit_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend.py", "--server.port", "8501"
    ]
    
    try:
        # Register signal handler for cleanup
        def cleanup(signum, frame):
            print("\n🛑 Shutting down servers...")
            if api_process:
                api_process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, cleanup)
        subprocess.run(streamlit_cmd)
        
    except KeyboardInterrupt:
        if api_process:
            api_process.terminate()
        print("\n✅ Servers stopped")

def main():
    start_both_servers()

if __name__ == "__main__":
    main()