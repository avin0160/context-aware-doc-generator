# VS Code Crash Fix Guide

## Problem
VS Code closes/crashes when running `repo_fastapi_server.py`

## Quick Fixes (Try These First)

### Option 1: Run Test Diagnostic
```bash
python test_server_startup.py
```
This will show exactly where the crash occurs.

### Option 2: Use Safe Start
```bash
python start_safe_server.py
```
This starts with minimal dependencies and maximum error handling.

### Option 3: Run from Terminal (Not VS Code)
```bash
# Windows PowerShell
.\venv\Scripts\python.exe repo_fastapi_server.py

# Windows CMD
venv\Scripts\python.exe repo_fastapi_server.py
```

### Option 4: Use Unbuffered Output
```bash
python -u repo_fastapi_server.py
```
The `-u` flag forces unbuffered output, which can help see error messages before crash.

---

## Common Causes & Solutions

### 1. Import Error (Most Common)

**Symptom:** VS Code closes immediately with no error message

**Diagnosis:**
```bash
python test_server_startup.py
```

**Solution:**
If test shows missing dependencies:
```bash
pip install fastapi uvicorn google-genai
```

---

### 2. Memory Issue

**Symptom:** VS Code freezes then closes when Phi-3 model loads

**Solution:** Use safe start which delays model loading:
```bash
python start_safe_server.py
```

---

### 3. VS Code Terminal Buffer Issue

**Symptom:** Works in external terminal but crashes in VS Code

**Solution 1:** Change VS Code terminal settings

File → Preferences → Settings → Search "terminal.integrated.scrollback"
- Increase to 10000

**Solution 2:** Use external terminal
- Right-click `repo_fastapi_server.py` → "Run in External Terminal"

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python test_server_startup.py` | Diagnose startup issues |
| `python start_safe_server.py` | Start with minimal dependencies |
| `python -u repo_fastapi_server.py` | Start with unbuffered output |
| `.\venv\Scripts\python.exe repo_fastapi_server.py` | Use venv Python directly |

---

**Most Common Fix:** Run `python test_server_startup.py` to see the exact error.
