# 🚀 GOOGLE COLAB TERMINAL QUICK START

## ⚡ ONE-COMMAND SETUP
```bash
# Run this single command to set everything up
curl -sSL https://raw.githubusercontent.com/avin0160/context-aware-doc-generator/main/setup_colab.sh | bash
```

## 📝 INSTANT DOCUMENTATION GENERATION

### Memory-Safe Commands (Works on any Colab instance)
```bash
# Clone if not already done
git clone https://github.com/avin0160/context-aware-doc-generator.git
cd context-aware-doc-generator

# Google Style - Inline code walkthrough
python main.py --directory . --style google --context "Code walkthrough documentation" --output google_docs.md

# NumPy Style - Scientific with visuals  
python main.py --directory . --style numpy --context "Scientific analysis documentation" --output numpy_docs.md

# Technical Style - Comprehensive analysis
python main.py --directory . --style technical_md --context "Technical architecture documentation" --output technical_docs.md

# Open Source Style - Contributor guide
python main.py --directory . --style opensource --context "Open source project documentation" --output opensource_docs.md
```

### Document External Repositories
```bash
# Document any GitHub repo
python main.py --url https://github.com/user/repo --style google --context "External repository analysis"

# Example with popular repo
python main.py --url https://github.com/fastapi/fastapi --style technical_md --context "FastAPI framework analysis"
```

### View Results
```bash
# Preview generated documentation
head -30 google_docs.md
head -30 numpy_docs.md  
head -30 technical_docs.md

# Download in Colab
from google.colab import files
files.download('google_docs.md')
files.download('numpy_docs.md')
```

## 🌐 WEB INTERFACE (if RAM allows)
```bash
# Start web server
python repo_fastapi_server.py

# Or with ngrok for public access
python -c "
from pyngrok import ngrok
import subprocess
import threading
import time

def start_server():
    subprocess.run(['python', 'repo_fastapi_server.py'])

# Start server in background
threading.Thread(target=start_server, daemon=True).start()
time.sleep(10)

# Create public tunnel
public_url = ngrok.connect(8000)
print(f'🌐 Public URL: {public_url}')
print('🔐 Password: nOtE7thIs')
"
```

## 💾 MEMORY MANAGEMENT
```bash
# Check RAM usage
free -h

# Monitor while running
watch -n 2 'free -h && ps aux | grep python | head -3'

# Clear memory if needed
pkill -f python
python -c "import gc; gc.collect()"
```

## 🎯 WHAT MAKES THIS DIFFERENT

### 🔍 Google Style - Code Detective
- **What it does**: Walks through your code like a detective explaining what each piece actually does
- **Perfect for**: Understanding unfamiliar codebases, code reviews, onboarding new developers
- **Output**: "This function does X, calls Y to achieve Z, and handles edge case W"

### 📊 NumPy Style - Visual Scientist  
- **What it does**: Creates ASCII diagrams, complexity matrices, scientific analysis
- **Perfect for**: Technical documentation, academic projects, data science workflows
- **Output**: Dependency graphs, performance charts, mathematical documentation structure

### 🏗️ Technical MD - System Architect
- **What it does**: Deep-dive into architecture, security, performance, scalability
- **Perfect for**: System design docs, technical reviews, enterprise documentation
- **Output**: Architecture diagrams, security analysis, deployment recommendations

### 🤝 Open Source - Community Builder
- **What it does**: Contributors guide, maintainer checklist, project health dashboard
- **Perfect for**: GitHub projects, community building, project governance
- **Output**: Contribution areas, coding standards, release processes

## 🚨 TROUBLESHOOTING

### Memory Issues
```bash
# If you get OOM errors, use basic mode:
pip install fastapi uvicorn python-multipart requests markdown --only
python main.py --directory . --style google --context "Basic mode"
```

### Import Errors
```bash
# Reinstall core dependencies
pip install --force-reinstall fastapi uvicorn python-multipart
```

### Slow Performance
```bash
# Process smaller chunks
mkdir small_test
cp *.py small_test/ 2>/dev/null || echo "No .py files found"
python main.py --directory small_test --style google --context "Small test"
```

---

## 🎉 SUCCESS! 
**You now have a world-class documentation generator that creates truly insightful, distinctive documentation for each style - optimized for Google Colab's memory constraints!**