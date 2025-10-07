#!/usr/bin/env python3
"""
FastAPI Server for Generic Documentation Generator
Uses semantic analysis and CodeSearchNet principles
"""

import os
import sys
import subprocess
import tempfile
import uvicorn
from fastapi import FastAPI, Form, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
from fastapi import UploadFile as UploadedFile

try:
    from comprehensive_docs_advanced import DocumentationGenerator
    DOCS_AVAILABLE = True
    print("Advanced documentation system loaded successfully")
    # Initialize the generator
    doc_generator = DocumentationGenerator()
except ImportError as e:
    print(f"Warning: {e}")
    print("Running in demo mode")
    DOCS_AVAILABLE = False
    doc_generator = None

app = FastAPI(title="Generic Documentation Generator", version="2.0.0")

def install_deps():
    """Install required dependencies"""
    try:
        import fastapi
        import uvicorn
        print("FastAPI dependencies already available")
        return True
    except ImportError:
        print("Installing FastAPI dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                 "fastapi", "uvicorn[standard]", "python-multipart"])
            print("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False

def install_ngrok():
    """Install pyngrok for tunneling"""
    try:
        import pyngrok
        print("pyngrok already available")
        return True
    except ImportError:
        print("Installing pyngrok...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
            print("pyngrok installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pyngrok: {e}")
            return False

def setup_ngrok():
    """Setup ngrok tunnel"""
    try:
        from pyngrok import ngrok
        auth_token = "33dHcz0qHINoRMVnD8COCZ2Vnfp_4dkFqzWa3KeWrLCSKmARW"
        ngrok.set_auth_token(auth_token)
        print("ngrok authentication configured")
        return True
    except Exception as e:
        print(f"Failed to setup ngrok: {e}")
        return False

def create_tunnel(port=8000):
    """Create ngrok tunnel"""
    try:
        from pyngrok import ngrok
        print("Creating ngrok tunnel...")
        tunnel = ngrok.connect(port)
        print(f"SUCCESS: ngrok tunnel created: {tunnel.public_url}")
        print("Click the URL above to access the documentation generator!")
        return tunnel
    except Exception as e:
        print(f"Failed to create tunnel: {e}")
        print("Server will run on localhost:8000")
        return None

@app.get("/", response_class=HTMLResponse)
async def home():
    """Main interface"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Generic Documentation Generator</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            background: white; padding: 40px; border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 900px; margin: 0 auto;
        }
        .header { text-align: center; margin-bottom: 30px; }
        h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #7f8c8d; font-size: 1.2em; margin-bottom: 20px; }
        .info { 
            background: linear-gradient(45deg, #2ecc71, #27ae60);
            color: white; padding: 15px; border-radius: 8px; 
            margin-bottom: 30px; text-align: center;
        }
        .form-group { margin: 25px 0; }
        label { 
            display: block; margin-bottom: 8px; font-weight: 600; 
            color: #34495e; font-size: 1.1em;
        }
        textarea { 
            width: 100%; padding: 15px; border: 2px solid #e0e6ed; 
            border-radius: 8px; font-size: 14px; font-family: 'Monaco', monospace;
            resize: vertical; transition: border-color 0.3s; min-height: 250px;
        }
        textarea:focus { border-color: #3498db; outline: none; }
        input[type="text"] {
            width: 100%; padding: 12px; border: 2px solid #e0e6ed; 
            border-radius: 8px; font-size: 14px; transition: border-color 0.3s;
        }
        input[type="text"]:focus { border-color: #3498db; outline: none; }
        select {
            width: 100%; padding: 12px; border: 2px solid #e0e6ed; 
            border-radius: 8px; font-size: 14px; background: white;
        }
        .btn { 
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white; padding: 15px 40px; border: none; 
            border-radius: 8px; cursor: pointer; font-size: 18px;
            font-weight: 600; transition: transform 0.2s;
            width: 100%; margin: 20px 0;
        }
        .btn:hover { transform: translateY(-2px); }
        .status { 
            background: #d4edda; border: 1px solid #c3e6cb;
            color: #155724; padding: 15px; border-radius: 8px;
            margin: 20px 0; display: none;
        }
        .error {
            background: #f8d7da; border: 1px solid #f5c6cb;
            color: #721c24;
        }
        pre { 
            background: #f8f9fa; padding: 20px; border-radius: 8px;
            border-left: 4px solid #3498db; overflow-x: auto;
            white-space: pre-wrap; max-height: 500px; overflow-y: auto;
        }
        .features {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin: 20px 0;
        }
        .feature {
            background: #f8f9fa; padding: 15px; border-radius: 8px;
            text-align: center; border-left: 4px solid #3498db;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Advanced Documentation Generator</h1>
            <p class="subtitle">CodeSearchNet-inspired semantic analysis with multiple input support</p>
        </div>
        
        <div class="info">
            <strong>Semantic Analysis Powered</strong><br>
            Analyzes your code structure and generates documentation specific to your project type
        </div>
        
        <div class="features">
            <div class="feature">
                <strong>Web Apps</strong><br>
                Flask, Django, FastAPI
            </div>
            <div class="feature">
                <strong>Data Science</strong><br>
                Pandas, NumPy, ML models
            </div>
            <div class="feature">
                <strong>CLI Tools</strong><br>
                Command-line interfaces
            </div>
            <div class="feature">
                <strong>Libraries</strong><br>
                General purpose utilities
            </div>
        </div>
        
        <form id="docForm">
            <div class="form-group">
                <label for="code_input">Python Code:</label>
                <textarea id="code_input" name="code_input" 
                    placeholder="Paste your Python code here...&#10;&#10;Example:&#10;from flask import Flask&#10;&#10;app = Flask(__name__)&#10;&#10;@app.route('/api/users')&#10;def get_users():&#10;    return {'users': []}" 
                    required></textarea>
            </div>
            
            <div class="form-group">
                <label for="context">Project Context (Optional):</label>
                <input type="text" id="context" name="context" 
                    placeholder="Brief description: e.g., 'User management web application'">
            </div>
            
                        <div class="form-group">
                <label for="style">Documentation Style:</label>
                <select id="style" name="style" required>
                    <option value="comprehensive">Comprehensive</option>
                    <option value="google">Google Style</option>
                    <option value="numpy">NumPy Style</option>
                    <option value="technical_md">Technical Markdown</option>
                    <option value="opensource">Open Source</option>
                    <option value="technical">Technical</option>
                    <option value="api">API Documentation</option>
                    <option value="user_guide">User Guide</option>
                    <option value="tutorial">Tutorial</option>
                </select>
            </div>
            
            <button type="submit" class="btn">Generate Documentation</button>
        </form>
        
        <div id="status" class="status"></div>
        <div id="result" style="display: none;">
            <h3>Generated Documentation:</h3>
            <pre id="documentation"></pre>
        </div>
    </div>

    <script>
        document.getElementById('docForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const statusDiv = document.getElementById('status');
            const resultDiv = document.getElementById('result');
            const docDiv = document.getElementById('documentation');
            
            // Show loading
            statusDiv.style.display = 'block';
            statusDiv.className = 'status';
            statusDiv.innerHTML = 'Analyzing code and generating documentation...';
            resultDiv.style.display = 'none';
            
            const formData = new FormData(e.target);
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = `Error: ${data.error}`;
                } else {
                    statusDiv.innerHTML = `Success: ${data.status}`;
                    docDiv.textContent = data.documentation;
                    resultDiv.style.display = 'block';
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.innerHTML = `Network error: ${error.message}`;
            }
        });
    </script>
</body>
</html>
    """)

@app.post("/generate")
async def generate_documentation(
    context: str = Form(...),
    doc_style: str = Form(default="comprehensive"),
    files: List[UploadedFile] = File(...)
):
    """Generate documentation from uploaded files"""
    
    try:
        # Process uploaded files
        file_contents = {}
        
        for file in files:
            if file.filename.endswith(('.py', '.pyx', '.pyi')):
                content = await file.read()
                file_contents[file.filename] = content.decode('utf-8', errors='ignore')
        
        if not file_contents:
            raise HTTPException(status_code=400, detail="No Python files provided")
        
        # Try advanced generation first
        try:
            from comprehensive_docs_advanced import DocumentationGenerator
            
            generator = DocumentationGenerator()
            analysis = generator.analyzer.analyze_repository_comprehensive(file_contents)
            repo_name = "Uploaded Project"
            
            # Generate documentation using advanced methods
            if doc_style == 'google':
                documentation = generator._generate_google_style(analysis, context, repo_name)
            elif doc_style == 'numpy':
                documentation = generator._generate_numpy_style(analysis, context, repo_name)
            elif doc_style == 'technical_md':
                documentation = generator._generate_technical_markdown(analysis, context, repo_name)
            elif doc_style == 'opensource':
                documentation = generator._generate_opensource_style(analysis, context, repo_name)
            elif doc_style == 'api':
                documentation = generator._generate_api_documentation(analysis, context, repo_name)
            else:
                documentation = generator._generate_comprehensive_style(analysis, context, repo_name)
                
        except ImportError:
            # Fallback to basic generation using new method
            if doc_generator:
                # Convert file_contents dict to single string for the new API
                combined_content = ""
                for file_path, content in file_contents.items():
                    combined_content += f"# File: {file_path}\n{content}\n\n"
                
                documentation = doc_generator.generate_documentation(
                    input_data=combined_content,
                    context=context,
                    doc_style=doc_style,
                    input_type='code',
                    repo_name=""
                )
            else:
                documentation = "Documentation generator not available"
        
        return {
            "success": True,
            "documentation": documentation,
            "files_processed": len(file_contents),
            "style_used": doc_style,
            "features_used": "advanced" if 'comprehensive_docs_advanced' in locals() else "basic"
        }
        
    except Exception as e:
        print(f"Error generating documentation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating documentation: {str(e)}")

@app.post("/generate_from_repo")
async def generate_from_repo(
    repo_url: str = Form(...),
    context: str = Form(...),
    doc_style: str = Form(default="comprehensive")
):
    """Generate documentation from a git repository"""
    
    if not DOCS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Documentation generation not available")
    
    try:
        # Try using advanced multi-input handler first
        try:
            from comprehensive_docs_advanced import DocumentationGenerator
            
            print(f"Processing repository with advanced handler: {repo_url}")
            
            generator = DocumentationGenerator()
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            
            documentation = generator.generate_documentation(
                input_data=repo_url,
                context=context,
                doc_style=doc_style,
                input_type='git',
                repo_name=repo_name
            )
            
            return {
                "success": True,
                "documentation": documentation,
                "repo_url": repo_url,
                "style_used": doc_style,
                "features_used": "advanced_multi_input"
            }
            
        except ImportError:
            print("Advanced features not available, using basic git processing")
            
            # Fallback to basic git processing
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Clone repository
                result = subprocess.run(
                    ['git', 'clone', repo_url, temp_dir],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    raise Exception(f"Git clone failed: {result.stderr}")
                
                # Process the cloned repository
                file_contents = {}
                
                for root, dirs, files in os.walk(temp_dir):
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                    
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    relative_path = os.path.relpath(file_path, temp_dir)
                                    file_contents[relative_path] = f.read()
                            except Exception:
                                continue
                
                if not file_contents:
                    raise Exception("No Python files found in repository")
                
                # Generate documentation using enhanced system
                if doc_generator:
                    # Convert file_contents dict to single string for the new API
                    combined_content = ""
                    for file_path, content in file_contents.items():
                        combined_content += f"# File: {file_path}\n{content}\n\n"
                    
                    documentation = doc_generator.generate_documentation(
                        input_data=combined_content,
                        context=context,
                        doc_style=doc_style,
                        input_type='code',
                        repo_name=os.path.basename(temp_dir)
                    )
                else:
                    documentation = "Documentation generator not available"
                
                return {
                    "success": True,
                    "documentation": documentation,
                    "files_processed": len(file_contents),
                    "repo_url": repo_url,
                    "features_used": "basic_git"
                }
                
            finally:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Repository cloning timed out")
    except Exception as e:
        print(f"Error processing repository: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing repository: {str(e)}")

@app.get("/test")
async def test_system():
    """Test the documentation system"""
    test_code = '''
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    """Get all users"""
    return jsonify([{"id": 1, "name": "John"}])

class UserService:
    """Service for managing users"""
    
    def create_user(self, name, email):
        """Create a new user"""
        return {"name": name, "email": email}
    
    def delete_user(self, user_id):
        """Delete a user by ID"""
        pass

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    try:
        if DOCS_AVAILABLE:
            if doc_generator:
                result = doc_generator.generate_documentation(
                    input_data=test_code,
                    context="Flask web application for user management",
                    doc_style="technical",
                    input_type='code',
                    repo_name=""
                )
            else:
                result = "Documentation generator not available"
            return JSONResponse({
                "test_code": test_code,
                "generated_docs": result,
                "status": "System working correctly"
            })
        else:
            return JSONResponse({
                "test_code": test_code,
                "status": "Demo mode - documentation generation not available"
            })
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "Test failed"
        })

def start_server():
    """Start the FastAPI server with ngrok tunnel"""
    print("Generic Documentation Generator")
    print("=" * 50)
    
    # Install dependencies
    if not install_deps():
        return
    
    tunnel = None
    if install_ngrok():
        if setup_ngrok():
            tunnel = create_tunnel(8000)
    
    print("\nStarting server...")
    if tunnel:
        print(f"Public URL: {tunnel.public_url}")
    print("Local URL: http://localhost:8000")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\nShutting down...")
        if tunnel:
            tunnel.close()
        print("Server stopped")

if __name__ == "__main__":
    start_server()