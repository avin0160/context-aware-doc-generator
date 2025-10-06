#!/usr/bin/env python3
"""
Smart web interface launcher that handles port conflicts
"""

import os
import sys
import subprocess
import socket
import time

def check_port(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def find_available_port(start_port=8501):
    """Find the next available port starting from start_port"""
    for port in range(start_port, start_port + 10):
        if check_port(port):
            return port
    return None

def kill_port_process(port):
    """Kill process using the specified port"""
    try:
        result = subprocess.run(['lsof', '-t', f'-i:{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pid = result.stdout.strip()
            subprocess.run(['kill', pid])
            time.sleep(2)
            print(f"✅ Killed existing process on port {port}")
            return True
    except:
        pass
    return False

def setup_environment():
    """Setup environment for compatibility"""
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    print("✅ Environment configured for stability")

def start_streamlit(port=8501):
    """Start Streamlit on specified port"""
    print(f"🌐 Starting Streamlit on port {port}...")
    print(f"🔗 Access at: http://localhost:{port}")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/frontend.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0"
    ]
    
    subprocess.run(cmd)

def main():
    print("🚀 Context-Aware Documentation Generator - Smart Launcher")
    print("=" * 60)
    
    setup_environment()
    
    # Try to use port 8501, handle conflicts
    target_port = 8501
    
    if not check_port(target_port):
        print(f"⚠️  Port {target_port} is in use")
        
        # Try to kill existing process
        if kill_port_process(target_port):
            if check_port(target_port):
                print(f"✅ Port {target_port} is now available")
            else:
                print(f"❌ Could not free port {target_port}")
                target_port = find_available_port(8502)
        else:
            # Find alternative port
            target_port = find_available_port(8502)
    
    if target_port:
        start_streamlit(target_port)
    else:
        print("❌ No available ports found in range 8501-8510")
        print("💡 Try: pkill -f streamlit")
        print("💡 Then run this script again")

if __name__ == "__main__":
    main()