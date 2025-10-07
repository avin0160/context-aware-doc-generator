# Quick Terminal Commands Reference

## 🚀 Essential Commands

### Start the Advanced Documentation Server
```bash
cd context-aware-doc-generator
python3 repo_fastapi_server.py
```

### Generate Documentation (CLI)
```bash
# Current directory with Google style
python3 main.py --directory . --style google

# Specific project with different styles
python3 main.py --directory /path/to/project --style numpy
python3 main.py --directory /path/to/project --style technical_md
python3 main.py --directory /path/to/project --style opensource
python3 main.py --directory /path/to/project --style comprehensive

# From GitHub URL
python3 main.py --url https://github.com/user/repo --style google
```

### Quick Setup
```bash
# Clone and setup
git clone https://github.com/avin0160/context-aware-doc-generator.git
cd context-aware-doc-generator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start server immediately
python3 repo_fastapi_server.py
```

### Test Server
```bash
# Check if server is running
curl http://localhost:8000/test

# Test documentation generation
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "repo_url=.&context=test&doc_style=google"
```

### Git Operations
```bash
git status
git add .
git commit -m "Your commit message"
git push origin main
```

## 🎯 Available Documentation Styles
- `google` - Google-style docstrings
- `numpy` - NumPy/SciPy style
- `technical_md` - Technical markdown
- `opensource` - Open source projects
- `api` - API reference
- `comprehensive` - Complete analysis

## 🔧 Troubleshooting
```bash
# Check Python version
python3 --version

# Install missing packages
pip install python-multipart datasets transformers torch

# Kill running server
pkill -f repo_fastapi_server.py

# Check what's running on port 8000
lsof -i :8000
```