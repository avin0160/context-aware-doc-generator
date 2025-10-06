#!/usr/bin/env python3
"""
Colab-optimized startup script
Sets up environment and starts services without quantization issues
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def setup_colab_environment():
    """Set up Colab-specific environment variables."""
    print("🔧 Setting up Colab environment...")
    
    # Disable problematic features for Colab
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['BITSANDBYTES_NOWELCOME'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
    
    print("✅ Environment configured for Colab compatibility")

def run_final_test():
    """Run the final test to validate system."""
    print("\n🎯 Running System Validation...")
    result = subprocess.run([sys.executable, "final_test.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ System validation successful!")
        print(result.stdout)
        return True
    else:
        print("❌ System validation failed:")
        print(result.stderr)
        return False

def start_streamlit():
    """Start Streamlit web interface."""
    print("\n🌐 Starting Streamlit web interface...")
    
    try:
        # Start Streamlit in background
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "src/frontend.py", 
            "--server.port", "8501",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(3)  # Give it time to start
        
        if process.poll() is None:  # Still running
            print("✅ Streamlit started successfully!")
            print("   🌐 Access at: http://localhost:8501")
            return process
        else:
            print("❌ Streamlit failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return None

def start_api_server():
    """Start FastAPI server without quantization."""
    print("\n🚀 Starting FastAPI server...")
    
    try:
        # Start API server in background  
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.api:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload", "false"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(5)  # Give it more time to start
        
        if process.poll() is None:  # Still running
            print("✅ API server started successfully!")
            print("   🔗 API docs at: http://localhost:8000/docs")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ API server failed to start:")
            print(f"   STDOUT: {stdout.decode()}")
            print(f"   STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None

def main():
    """Main startup sequence for Colab."""
    print("🎓 Context-Aware Documentation Generator")
    print("=" * 50)
    print("🧪 Colab-Optimized Startup")
    
    # Setup environment
    setup_colab_environment()
    
    # Run validation test
    if not run_final_test():
        print("⚠️  System validation failed, but continuing...")
    
    # Start services
    streamlit_process = start_streamlit()
    api_process = start_api_server()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Startup Complete!")
    
    if streamlit_process:
        print("✅ Web Interface: http://localhost:8501")
    else:
        print("❌ Web Interface: Failed to start")
        
    if api_process:
        print("✅ API Server: http://localhost:8000/docs")
    else:
        print("❌ API Server: Failed to start")
    
    print("\n📚 Alternative Usage:")
    print("   • Terminal Demo: python terminal_demo.py")
    print("   • Enhanced Test: python enhanced_test.py")
    print("   • Final Test: python final_test.py")
    
    # Keep processes alive
    try:
        if streamlit_process or api_process:
            print("\n⏰ Services running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
                
                # Check if processes are still alive
                if streamlit_process and streamlit_process.poll() is not None:
                    print("⚠️  Streamlit process stopped")
                    streamlit_process = None
                    
                if api_process and api_process.poll() is not None:
                    print("⚠️ API process stopped")
                    api_process = None
                    
                if not streamlit_process and not api_process:
                    print("All services stopped")
                    break
        else:
            print("\n💡 Use the terminal demo instead:")
            print("   python terminal_demo.py")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        if streamlit_process:
            streamlit_process.terminate()
        if api_process:
            api_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()