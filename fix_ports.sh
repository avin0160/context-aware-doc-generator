#!/bin/bash
# Quick fix for port conflicts

echo "🔧 Port Conflict Resolver"
echo "========================"

# Kill all Streamlit processes
echo "🛑 Stopping all Streamlit processes..."
pkill -f streamlit 2>/dev/null || echo "No Streamlit processes found"

# Kill processes on common ports
for port in 8501 8502 8503; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo "🔫 Killing process $pid on port $port"
        kill $pid
    fi
done

sleep 2
echo "✅ Ports cleared!"
echo ""
echo "🚀 Now you can run:"
echo "   python3 start_smart.py"
echo "   python3 start_web.py"  
echo "   python3 what_next.py"