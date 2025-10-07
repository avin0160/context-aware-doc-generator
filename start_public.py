#!/usr/bin/env python3
"""
Create public tunnel for Colab using ngrok or cloudflared
"""

import os
import sys
import subprocess
import time
import threading

def install_tunnel_tool():
    """Install and setup tunnel tool"""
    print("🔧 Setting up public tunnel...")
    
    # Try to install pyngrok
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyngrok'], 
                      capture_output=True, check=True)
        print("✅ pyngrok installed")
        return 'pyngrok'
    except:
        print("⚠️  pyngrok installation failed, trying alternative...")
    
    # Try cloudflared (more reliable)
    try:
        # Install cloudflared
        subprocess.run(['wget', '-q', 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'], 
                      capture_output=True)
        subprocess.run(['chmod', '+x', 'cloudflared-linux-amd64'], capture_output=True)
        subprocess.run(['mv', 'cloudflared-linux-amd64', '/usr/local/bin/cloudflared'], 
                      capture_output=True)
        print("✅ cloudflared installed")
        return 'cloudflared'
    except:
        print("❌ Could not install tunnel tools")
        return None

def start_with_ngrok():
    """Start Streamlit with ngrok tunnel"""
    try:
        from pyngrok import ngrok
        
        # Start Streamlit in background
        streamlit_cmd = [sys.executable, '-m', 'streamlit', 'run', 'src/frontend.py', 
                        '--server.port', '8501', '--server.headless', 'true']
        streamlit_process = subprocess.Popen(streamlit_cmd)
        
        time.sleep(5)  # Wait for Streamlit to start
        
        # Create ngrok tunnel
        public_url = ngrok.connect(8501)
        print(f"\n🎯 PUBLIC URL: {public_url}")
        print(f"🌐 Access your app at: {public_url}")
        print("=" * 60)
        
        # Keep running
        streamlit_process.wait()
        
    except Exception as e:
        print(f"❌ ngrok failed: {e}")
        return False
    return True

def start_with_cloudflared():
    """Start Streamlit with cloudflared tunnel"""
    try:
        # Start Streamlit in background
        streamlit_cmd = [sys.executable, '-m', 'streamlit', 'run', 'src/frontend.py', 
                        '--server.port', '8501', '--server.headless', 'true']
        streamlit_process = subprocess.Popen(streamlit_cmd)
        
        time.sleep(5)  # Wait for Streamlit to start
        
        # Start cloudflared tunnel
        print("🌐 Creating public tunnel...")
        tunnel_cmd = ['cloudflared', 'tunnel', '--url', 'http://localhost:8501']
        tunnel_process = subprocess.Popen(tunnel_cmd, stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE, universal_newlines=True)
        
        # Monitor tunnel output for public URL
        for line in iter(tunnel_process.stdout.readline, ''):
            print(line.rstrip())
            if 'https://' in line and 'trycloudflare.com' in line:
                url = line.strip()
                print(f"\n🎯 PUBLIC URL FOUND: {url}")
                print(f"🌐 Access your app at: {url}")
                print("=" * 60)
                break
        
        # Keep both processes running
        try:
            tunnel_process.wait()
        except KeyboardInterrupt:
            tunnel_process.terminate()
            streamlit_process.terminate()
            
    except Exception as e:
        print(f"❌ cloudflared failed: {e}")
        return False
    return True

def main():
    print("🚀 Context-Aware Documentation Generator - Public Access")
    print("=" * 70)
    
    # Setup environment
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    
    # Install dependencies
    print("📦 Installing project dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                  capture_output=True)
    
    # Install tunnel tool
    tunnel_tool = install_tunnel_tool()
    
    if tunnel_tool == 'pyngrok':
        print("🔗 Using ngrok for public access...")
        if not start_with_ngrok():
            print("❌ ngrok failed, trying cloudflared...")
            start_with_cloudflared()
    elif tunnel_tool == 'cloudflared':
        print("🔗 Using cloudflared for public access...")
        start_with_cloudflared()
    else:
        print("❌ No tunnel tools available")
        print("💡 Try running Streamlit directly and use Colab's port forwarding:")
        print("   !python3 -m streamlit run src/frontend.py --server.port 8501")

if __name__ == "__main__":
    main()