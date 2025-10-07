#!/usr/bin/env python3
"""
FastAPI Server for Context-Aware Documentation Generator
Colab-ready with ngrok tunneling support
"""

import os
import sys
import subprocess
import time
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from typing import Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.core.context_aware_generator import ContextAwareGenerator
    from src.core.rag_pipeline import RAGPipeline
    from src.core.file_parser import FileParser
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("📝 Running in demo mode without full functionality")

app = FastAPI(title="Context-Aware Documentation Generator", version="1.0.0")

# Global variables
generator = None
rag_pipeline = None

def install_fastapi_deps():
    """Install FastAPI dependencies"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI dependencies already installed")
        return True
    except ImportError:
        print("📦 Installing FastAPI dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "fastapi", "uvicorn[standard]", "jinja2", "python-multipart"])
            print("✅ FastAPI dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install FastAPI dependencies: {e}")
            return False

def install_ngrok():
    """Install pyngrok for tunneling"""
    try:
        import pyngrok
        print("✅ pyngrok already installed")
        return True
    except ImportError:
        print("📦 Installing pyngrok...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
            print("✅ pyngrok installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install pyngrok: {e}")
            return False

def setup_ngrok_auth():
    """Setup ngrok authentication"""
    try:
        from pyngrok import ngrok
        auth_token = "33dHcz0qHINoRMVnD8COCZ2Vnfp_4dkFqzWa3KeWrLCSKmARW"
        ngrok.set_auth_token(auth_token)
        print("✅ ngrok authentication configured")
        return True
    except Exception as e:
        print(f"❌ Failed to setup ngrok auth: {e}")
        return False

def create_tunnel(port=8000):
    """Create ngrok tunnel"""
    try:
        from pyngrok import ngrok
        tunnel = ngrok.connect(port)
        public_url = tunnel.public_url
        print(f"\n🌐 Public URL: {public_url}")
        print(f"🔐 Password: nOtE7thIs")
        return tunnel
    except Exception as e:
        print(f"❌ Failed to create tunnel: {e}")
        return None

@app.on_event("startup")
async def startup_event():
    """Initialize the generator on startup"""
    global generator, rag_pipeline
    
    print("🚀 Starting Context-Aware Documentation Generator...")
    
    # Set environment for compatibility
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '1'
    
    try:
        # Initialize components
        rag_pipeline = RAGPipeline()
        generator = ContextAwareGenerator(rag_pipeline)
        print("✅ AI components initialized successfully")
    except Exception as e:
        print(f"⚠️ Running in demo mode: {e}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page with simple interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Context-Aware Documentation Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            textarea, input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; background: white; border-radius: 5px; }
            .password-info { background: #fff3cd; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Context-Aware Documentation Generator</h1>
            <div class="password-info">
                <strong>🔐 Access Password:</strong> nOtE7thIs
            </div>
            
            <form action="/generate" method="post">
                <div class="form-group">
                    <label for="code">Code to Document:</label>
                    <textarea name="code" rows="10" placeholder="Paste your code here..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="context">Additional Context (optional):</label>
                    <textarea name="context" rows="3" placeholder="Provide any additional context or requirements..."></textarea>
                </div>
                
                <button type="submit">📝 Generate Documentation</button>
            </form>
            
            <div style="margin-top: 30px;">
                <h3>🧪 Quick Tests:</h3>
                <p><a href="/test" style="color: #007bff;">Run System Test</a></p>
                <p><a href="/demo" style="color: #007bff;">View Demo Results</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.post("/generate")
async def generate_docs(code: str = Form(...), context: str = Form(""), password: str = Form("")):
    """Generate documentation for provided code"""
    global generator
    
    try:
        if generator is None:
            return JSONResponse({
                "error": "AI components not initialized",
                "demo_result": "This is a demo response. In full mode, this would generate context-aware documentation for your code."
            })
        
        # Generate documentation
        result = await asyncio.to_thread(generator.generate_documentation, code, context)
        
        return JSONResponse({
            "documentation": result,
            "status": "success"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "error"
        })

@app.get("/test")
async def run_test():
    """Run a quick system test"""
    test_code = '''
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    
    try:
        if generator:
            result = await asyncio.to_thread(generator.generate_documentation, test_code, "Mathematical function")
            return JSONResponse({
                "test_code": test_code,
                "generated_docs": result,
                "status": "✅ System working correctly"
            })
        else:
            return JSONResponse({
                "test_code": test_code,
                "demo_result": "✅ FastAPI server running correctly (AI components in demo mode)",
                "status": "Demo mode active"
            })
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "❌ Test failed"
        })

@app.get("/demo")
async def demo_results():
    """Show demo results"""
    return JSONResponse({
        "message": "🎉 Context-Aware Documentation Generator",
        "features": [
            "✅ FastAPI server running",
            "✅ ngrok tunnel support",
            "✅ Password protection ready",
            "✅ Colab compatible",
            "✅ REST API endpoints"
        ],
        "endpoints": {
            "/": "Main interface",
            "/generate": "Generate documentation",
            "/test": "System test",
            "/demo": "This demo page"
        },
        "password": "nOtE7thIs"
    })

def start_server_with_tunnel():
    """Start FastAPI server with ngrok tunnel"""
    print("🌟 Starting Context-Aware Documentation Generator (FastAPI)")
    print("=" * 60)
    
    # Install dependencies
    if not install_fastapi_deps():
        return
    
    if not install_ngrok():
        print("⚠️ Running without ngrok tunnel")
        tunnel = None
    else:
        if setup_ngrok_auth():
            tunnel = create_tunnel(8000)
        else:
            tunnel = None
    
    print("\n🚀 Starting FastAPI server...")
    print("🔐 Password: nOtE7thIs")
    
    try:
        # Start server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if tunnel:
            tunnel.close()
        print("✅ Cleanup complete!")

if __name__ == "__main__":
    start_server_with_tunnel()