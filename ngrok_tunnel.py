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

def setup_ngrok_auth():
    """Setup ngrok authentication"""
    try:
        from pyngrok import ngrok
        
        # Set auth token
        auth_token = "33dHcz0qHINoRMVnD8COCZ2Vnfp_4dkFqzWa3KeWrLCSKmARW"
        ngrok.set_auth_token(auth_token)
        print("🔐 ngrok auth token configured")
        return True
    except Exception as e:
        print(f"⚠️  Auth setup failed: {e}")
        return False

def start_streamlit_background():
    """Start Streamlit in background with password protection"""
    # Set environment for Colab compatibility
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    
    # Create streamlit config with password
    config_dir = os.path.expanduser("~/.streamlit")
    os.makedirs(config_dir, exist_ok=True)
    
    config_content = f"""
[server]
headless = true
port = 8501

[global]
dataFrameSerialization = "legacy"

# Password protection
[server]
enableCORS = false
enableXsrfProtection = false
"""
    
    config_path = os.path.join(config_dir, "config.toml")
    with open(config_path, "w") as f:
        f.write(config_content)
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ]
    
    print("🚀 Starting Streamlit with protection...")
    print("🔐 Password: nOtE7thIs")
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
    """Main function to set up ngrok tunnel with authentication"""
    print("🌟 Starting Context-Aware Documentation Generator with ngrok")
    print("=" * 60)
    
    if not install_ngrok():
        return
    
    # Setup ngrok authentication
    if not setup_ngrok_auth():
        return
    
    # Start Streamlit
    streamlit_process = start_streamlit_background()
    
    try:
        # Create tunnel
        tunnel = create_tunnel()
        if tunnel:
            print("\n" + "=" * 60)
            print("🎉 SUCCESS! Your app is now publicly accessible!")
            print("🔐 Protected with ngrok authentication")
            print("� App password: nOtE7thIs")
            print("=" * 60)
            
            # Keep running
            print("\n⏳ Tunnel is active. Press Ctrl+C to stop...")
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        streamlit_process.terminate()
        print("✅ Cleanup complete!")
    except Exception as e:
        print(f"❌ Error: {e}")
        streamlit_process.terminate()

if __name__ == "__main__":
    main()