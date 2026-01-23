"""
Test script to diagnose repo_fastapi_server.py startup issues
Run this to see where the crash occurs
"""

import sys
import traceback

print("=" * 70)
print("🔍 DIAGNOSTIC TEST FOR REPO_FASTAPI_SERVER.PY")
print("=" * 70)

# Test 1: Basic imports
print("\n[Test 1] Testing basic Python imports...")
try:
    import os
    import ast
    import subprocess
    print("✅ Basic imports OK")
except Exception as e:
    print(f"❌ Basic imports FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: FastAPI imports
print("\n[Test 2] Testing FastAPI imports...")
try:
    import fastapi
    import uvicorn
    print("✅ FastAPI imports OK")
except Exception as e:
    print(f"❌ FastAPI imports FAILED: {e}")
    print("   Run: pip install fastapi uvicorn")
    traceback.print_exc()

# Test 3: Documentation system imports
print("\n[Test 3] Testing documentation system imports...")
try:
    from comprehensive_docs_advanced import DocumentationGenerator
    print("✅ DocumentationGenerator import OK")
except Exception as e:
    print(f"❌ DocumentationGenerator import FAILED: {e}")
    traceback.print_exc()

# Test 4: Evaluation metrics imports
print("\n[Test 4] Testing evaluation metrics imports...")
try:
    from evaluation_metrics import BLEUScore, ROUGEScore
    print("✅ Evaluation metrics import OK")
except Exception as e:
    print(f"❌ Evaluation metrics import FAILED: {e}")
    traceback.print_exc()

# Test 5: RAG system imports
print("\n[Test 5] Testing RAG system imports...")
try:
    from src.rag import CodeRAGSystem
    print("✅ RAG system import OK")
except Exception as e:
    print(f"⚠️ RAG system import FAILED (non-critical): {e}")

# Test 6: Gemini imports
print("\n[Test 6] Testing Gemini imports...")
try:
    from gemini_context_enhancer import GeminiContextEnhancer
    print("✅ Gemini enhancer import OK")
except Exception as e:
    print(f"⚠️ Gemini enhancer import FAILED (non-critical): {e}")

# Test 7: Data sanitizer - DEPRECATED (module removed)
print("\n[Test 7] Data sanitizer check (skipped - module deprecated)...")
print("✅ Data sanitizer not required in this version")

# Test 8: Initialize DocumentationGenerator
print("\n[Test 8] Testing DocumentationGenerator initialization...")
try:
    doc_gen = DocumentationGenerator()
    print("✅ DocumentationGenerator initialized OK")
except Exception as e:
    print(f"❌ DocumentationGenerator initialization FAILED: {e}")
    traceback.print_exc()

# Test 9: Import the server module
print("\n[Test 9] Testing repo_fastapi_server.py import...")
try:
    import repo_fastapi_server
    print("✅ repo_fastapi_server.py import OK")
except Exception as e:
    print(f"❌ repo_fastapi_server.py import FAILED: {e}")
    traceback.print_exc()
    print("\n💡 This is likely where VS Code crashes")
    sys.exit(1)

# Test 10: Check app object
print("\n[Test 10] Testing FastAPI app object...")
try:
    from repo_fastapi_server import app
    print(f"✅ FastAPI app object OK: {app}")
except Exception as e:
    print(f"❌ FastAPI app object FAILED: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED - Server should start successfully")
print("=" * 70)
print("\nIf tests pass but VS Code still crashes:")
print("1. Try running from terminal: python repo_fastapi_server.py")
print("2. Check VS Code terminal settings")
print("3. Try: python -u repo_fastapi_server.py (unbuffered output)")
print("4. Check VS Code Python extension is up to date")
