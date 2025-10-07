# Terminal Commands Guide for Context-Aware Documentation Generator

## 🚀 Quick Start Commands

### 1. Setup Environment
```bash
# Clone repository
git clone https://github.com/avin0160/context-aware-doc-generator.git
cd context-aware-doc-generator

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install fastapi uvicorn python-multipart pyngrok requests datasets transformers torch GitPython markdown beautifulsoup4 pygments jinja2
```

### 2. Run FastAPI Server
```bash
# Start the main server (repo_fastapi_server.py)
python3 repo_fastapi_server.py

# Or with specific Python path
/path/to/your/python repo_fastapi_server.py

# Start with custom port
uvicorn repo_fastapi_server:app --host 0.0.0.0 --port 8080

# Start in development mode with auto-reload
uvicorn repo_fastapi_server:app --reload --host 0.0.0.0 --port 8000
```

### 3. CLI Documentation Generation
```bash
# Basic usage - document current directory
python3 main.py --directory . --style google

# Document specific directory
python3 main.py --directory /path/to/project --style numpy --context "My project docs"

# Document from GitHub URL
python3 main.py --url https://github.com/user/repo --style technical_md

# All available styles
python3 main.py --directory . --style google
python3 main.py --directory . --style numpy  
python3 main.py --directory . --style technical_md
python3 main.py --directory . --style opensource
python3 main.py --directory . --style api
python3 main.py --directory . --style comprehensive

# With custom output file
python3 main.py --directory . --style google --output my_docs.md

# Help command
python3 main.py --help
```

### 4. Testing Commands
```bash
# Test the advanced documentation system
python3 -c "from comprehensive_docs_advanced import DocumentationGenerator; print('✅ Advanced system working')"

# Test server endpoint
curl -X GET "http://localhost:8000/test"

# Test with specific repository
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "repo_url=https://github.com/user/repo&context=test&doc_style=google"

# Check server health
curl -X GET "http://localhost:8000/health"
```

### 5. Environment Management
```bash
# Check Python environment
which python3
python3 --version

# Check installed packages
pip list | grep -E "fastapi|transformers|datasets"

# Install missing dependencies
pip install python-multipart  # For FastAPI forms
pip install datasets transformers torch  # For CodeSearchNet

# Update requirements
pip freeze > requirements.txt
```

### 6. Process Management
```bash
# Run server in background
nohup python3 repo_fastapi_server.py > server.log 2>&1 &

# Check running processes
ps aux | grep python
ps aux | grep fastapi

# Kill server process
pkill -f repo_fastapi_server.py
# Or find PID and kill
lsof -i :8000
kill -9 <PID>

# Monitor server logs
tail -f server.log
```

### 7. Git Operations
```bash
# Check current status
git status

# Stage all changes
git add .

# Commit changes
git commit -m "Add advanced documentation system with CodeSearchNet integration"

# Push to main branch
git push origin main

# Create and push new branch
git checkout -b feature/advanced-docs
git push -u origin feature/advanced-docs

# Pull latest changes
git pull origin main
```

### 8. Docker Commands (Optional)
```bash
# Build Docker image
docker build -t context-aware-docs .

# Run container
docker run -p 8000:8000 context-aware-docs

# Run with volume mount
docker run -p 8000:8000 -v $(pwd):/app context-aware-docs
```

### 9. Debugging Commands
```bash
# Check imports
python3 -c "
try:
    from comprehensive_docs_advanced import DocumentationGenerator
    print('✅ Advanced system imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
"

# Test specific functionality
python3 -c "
from comprehensive_docs_advanced import DocumentationGenerator
gen = DocumentationGenerator()
result = gen.generate_documentation('print(\"hello world\")', 'Test code')
print('✅ Generation successful')
print(f'Result length: {len(result)} characters')
"

# Check file permissions
ls -la *.py
chmod +x main.py repo_fastapi_server.py

# Check disk space
df -h
du -sh .
```

### 10. Performance Monitoring
```bash
# Monitor CPU and memory usage
top -p $(pgrep -f repo_fastapi_server.py)
htop

# Monitor network connections
netstat -tlnp | grep :8000
ss -tlnp | grep :8000

# Check system resources
free -h
uptime
```

## 🔧 Common Issues & Solutions

### Issue: "python: command not found"
```bash
# Solution: Use python3
python3 --version
which python3
```

### Issue: "ModuleNotFoundError"
```bash
# Solution: Install missing packages
pip install -r requirements.txt
# Or activate virtual environment
source .venv/bin/activate
```

### Issue: "Port already in use"
```bash
# Solution: Kill existing process or use different port
lsof -i :8000
kill -9 <PID>
# Or change port
uvicorn repo_fastapi_server:app --port 8080
```

### Issue: "Permission denied"
```bash
# Solution: Fix file permissions
chmod +x *.py
# Or run with sudo (not recommended)
sudo python3 repo_fastapi_server.py
```

## 📊 Monitoring & Logs

### View application logs
```bash
# Real-time logs
tail -f server.log

# Search logs
grep "ERROR" server.log
grep -i "documentation" server.log

# Log rotation
logrotate -f /path/to/logrotate.conf
```

### System monitoring
```bash
# Resource usage
ps aux | grep python
iostat 1 5
sar -u 1 5
```

## 🚀 Production Deployment

### Using systemd (Linux)
```bash
# Create service file
sudo tee /etc/systemd/system/context-docs.service > /dev/null <<EOF
[Unit]
Description=Context-Aware Documentation Generator
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/context-aware-doc-generator
Environment=PATH=/path/to/context-aware-doc-generator/.venv/bin
ExecStart=/path/to/context-aware-doc-generator/.venv/bin/python repo_fastapi_server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable context-docs
sudo systemctl start context-docs
sudo systemctl status context-docs
```

### Using screen/tmux
```bash
# Using screen
screen -S docs-server
python3 repo_fastapi_server.py
# Detach: Ctrl+A, D
# Reattach: screen -r docs-server

# Using tmux
tmux new-session -d -s docs 'python3 repo_fastapi_server.py'
tmux attach-session -t docs
```

## 🌐 Network & Security

### Firewall setup
```bash
# Allow port 8000
sudo ufw allow 8000/tcp
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

### SSL/HTTPS setup
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Run with HTTPS
uvicorn repo_fastapi_server:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

## 📁 File Operations

### Backup and restore
```bash
# Create backup
tar -czf context-docs-backup-$(date +%Y%m%d).tar.gz .

# Restore backup
tar -xzf context-docs-backup-20241007.tar.gz

# Sync with remote
rsync -avz . user@server:/path/to/context-aware-doc-generator/
```