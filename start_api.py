#!/usr/bin/env python3
"""
Start API server with Colab compatibility
"""

import os
import sys
import subprocess

def setup_api_environment():
    """Configure environment for API compatibility"""
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    print("✅ API environment configured for compatibility")

def start_api():
    """Start FastAPI server"""
    print("🔗 Starting FastAPI server on port 8000...")
    print("🌐 API will be available at: http://localhost:8000")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "src.api:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ]
    
    subprocess.run(cmd)

def main():
    print("🚀 Context-Aware Documentation Generator - API Server")
    print("=" * 60)
    
    setup_api_environment()
    start_api()

if __name__ == "__main__":
    main()