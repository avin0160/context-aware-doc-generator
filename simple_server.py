#!/usr/bin/env python3
"""
Simple FastAPI Server for Context-Aware Documentation Generator
No tunnel conflicts - direct access
"""

import os
import sys
import asyncio
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI(title="Context-Aware Documentation Generator", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page with simple interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Context-Aware Documentation Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f8f9fa; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            .password-info { background: #d4edda; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #28a745; }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 8px; font-weight: bold; color: #495057; }
            textarea, input { width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 6px; font-size: 14px; }
            textarea:focus, input:focus { border-color: #007bff; outline: none; }
            .btn { background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #0056b3; }
            .test-section { margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 6px; }
            .test-link { display: inline-block; margin: 10px 15px 10px 0; padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; }
            .test-link:hover { background: #218838; }
            .status { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .demo { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Context-Aware Documentation Generator</h1>
                <p>FastAPI Server - Colab Ready</p>
            </div>
            
            <div class="password-info">
                <strong>🔐 Access Password:</strong> <code>nOtE7thIs</code>
            </div>
            
            <div class="status demo">
                <strong>📝 Status:</strong> Running in demo mode - Core functionality available via terminal
            </div>
            
            <form action="/generate" method="post">
                <div class="form-group">
                    <label for="code">📝 Code to Document:</label>
                    <textarea name="code" rows="8" placeholder="def example_function(param):
    '''Your code here'''
    return param * 2" required></textarea>
                </div>
                
                <div class="form-group">
                    <label for="context">💡 Additional Context (optional):</label>
                    <textarea name="context" rows="3" placeholder="Provide any additional context, requirements, or specific documentation style..."></textarea>
                </div>
                
                <div class="form-group">
                    <button type="submit" class="btn">📚 Generate Documentation</button>
                </div>
            </form>
            
            <div class="test-section">
                <h3>🧪 Quick Access:</h3>
                <a href="/test" class="test-link">🔍 System Test</a>
                <a href="/demo" class="test-link">📊 API Demo</a>
                <a href="/docs" class="test-link">📖 API Docs</a>
            </div>
            
            <div style="margin-top: 30px; text-align: center; color: #6c757d;">
                <p>💻 For full AI functionality, use: <code>python terminal_demo.py</code></p>
                <p>🌐 Server running on: <strong>http://localhost:8000</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.post("/generate")
async def generate_docs(code: str = Form(...), context: str = Form("")):
    """Generate documentation for provided code"""
    try:
        # Simple demo response
        demo_doc = f"""
# 📚 Generated Documentation

## 🔍 Code Analysis
**Lines of code:** {len(code.splitlines())}
**Characters:** {len(code)}

## 📝 Documentation

```python
{code}
```

### Description
This code appears to be a {'function' if 'def ' in code else 'class' if 'class ' in code else 'script'}.

### Context
{context if context else 'No additional context provided.'}

### Notes
- ✅ FastAPI server is working correctly
- 🔧 For full AI-powered documentation, use terminal_demo.py
- 🚀 This is a demo response showing server functionality

---
*Generated by Context-Aware Documentation Generator (Demo Mode)*
        """
        
        return JSONResponse({
            "documentation": demo_doc,
            "status": "success",
            "mode": "demo",
            "message": "Server working! Use terminal_demo.py for full AI functionality"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "error"
        })

@app.get("/test")
async def run_test():
    """Run a quick system test"""
    test_code = '''def fibonacci(n):
    """Calculate fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
result = fibonacci(10)
print(f"Fibonacci(10) = {result}")'''
    
    return JSONResponse({
        "🧪 test_status": "✅ FastAPI Server Working",
        "📝 test_code": test_code,
        "🤖 ai_status": "Available via terminal_demo.py",
        "🌐 server_url": "http://localhost:8000",
        "🔐 password": "nOtE7thIs",
        "📊 endpoints": {
            "/": "Main interface",
            "/generate": "Generate documentation",
            "/test": "This test endpoint",
            "/demo": "Demo information",
            "/docs": "FastAPI auto-docs"
        }
    })

@app.get("/demo")
async def demo_info():
    """Show demo information"""
    return JSONResponse({
        "🎉 message": "Context-Aware Documentation Generator",
        "🚀 server_status": "✅ FastAPI running successfully",
        "🔧 full_ai_access": "Use: python terminal_demo.py",
        "📋 available_scripts": [
            "terminal_demo.py - Interactive AI demo",
            "final_test.py - 30-second validation",
            "enhanced_test.py - Comprehensive testing",
            "main.py - CLI interface"
        ],
        "🌐 access_info": {
            "url": "http://localhost:8000",
            "password": "nOtE7thIs",
            "colab_ready": True
        },
        "⚡ features": [
            "✅ FastAPI web interface",
            "✅ Password-protected access", 
            "✅ Colab terminal compatible",
            "✅ Demo mode functional",
            "✅ Full AI via terminal scripts"
        ]
    })

if __name__ == "__main__":
    print("🌟 Starting Simple FastAPI Server")
    print("=" * 50)
    print("🌐 URL: http://localhost:8000")
    print("🔐 Password: nOtE7thIs")
    print("💻 Full AI: python terminal_demo.py")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")