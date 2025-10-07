#!/usr/bin/env python3
"""
Simple ngrok tunnel for Colab - get localhost access from anywhere
"""

import subprocess
import sys
import time
import threading
import signal
import os

def install_ngrok():
    """Install pyngrok in Colab"""
    print("📦 Installing ngrok...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyngrok'], 
                      capture_output=True, check=True)
        print("✅ ngrok installed")
        return True
    except:
        print("❌ Failed to install ngrok")
        return False

def start_streamlit_background():
    """Start Streamlit in background"""
    # Set environment for Colab compatibility
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ]
    
    print("🚀 Starting Streamlit...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # Give Streamlit time to start
    return process

def create_tunnel():
    """Create ngrok tunnel"""
    try:
        from pyngrok import ngrok
        
        print("🌐 Creating public tunnel...")
        public_url = ngrok.connect(8501)
        
        print("\n" + "="*60)
        print("🎯 SUCCESS! Your app is now publicly accessible:")
        print(f"🔗 Public URL: {public_url}")
        print("🌍 Access from anywhere: Copy the URL above")
        print("="*60)
        
        return public_url, ngrok
        
    except ImportError:
        print("❌ pyngrok not available")
        return None, None
    except Exception as e:
        print(f"❌ Tunnel creation failed: {e}")
        return None, None

def main():
    print("🚀 Context-Aware Documentation Generator - ngrok Tunnel")
    print("=" * 70)
    print("💡 Perfect for Colab - creates public URL for localhost")
    print()
    
    # Install ngrok
    if not install_ngrok():
        return
    
    # Start Streamlit
    streamlit_process = start_streamlit_background()
    
    # Create tunnel
    public_url, ngrok_module = create_tunnel()
    
    if public_url:
        try:
            print("\n🔄 Tunnel active. Press Ctrl+C to stop.")
            print("💡 Keep this cell running to maintain the tunnel")
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            if ngrok_module:
                ngrok_module.disconnect(public_url)
                ngrok_module.kill()
            streamlit_process.terminate()
            print("✅ Tunnel closed")
    else:
        print("❌ Could not create tunnel")
        streamlit_process.terminate()

if __name__ == "__main__":
    main()