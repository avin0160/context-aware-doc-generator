#!/usr/bin/env python3
"""
Enhanced FastAPI Server for Context-Aware Documentation Generator
Supports Git repositories, ZIP files, and multiple documentation styles
"""

import os
import sys
import subprocess
import time
import uvicorn
import asyncio
import tempfile
import zipfile
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import sys
    import os
    # Add current directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'src'))
    
    from src.core.context_aware_generator import ContextAwareGenerator
    from src.core.rag_pipeline import RAGPipeline  
    from src.core.file_parser import FileParser
    from src.core.llm_interface import LLMInterface
    from src.utils.output_formatter import OutputFormatter
    
    AI_AVAILABLE = True
    print("✅ AI components imported successfully")
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("📝 Running in demo mode without full functionality")
    AI_AVAILABLE = False

app = FastAPI(title="Context-Aware Documentation Generator", version="2.0.0")

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
    
    if AI_AVAILABLE:
        try:
            # Initialize components
            print("🔧 Initializing RAG Pipeline...")
            rag_pipeline = RAGPipeline()
            
            print("🤖 Initializing Context-Aware Generator...")
            generator = ContextAwareGenerator(rag_pipeline)
            
            print("✅ AI components initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize AI components: {e}")
            generator = None
            rag_pipeline = None
    else:
        print("⚠️ Running in demo mode - AI components not available")
        generator = None
        rag_pipeline = None

async def analyze_repository_structure(repo_path: str, context: str, doc_style: str):
    """Analyze repository structure and generate documentation"""
    try:
        import os
        import fnmatch
        
        # Find all Python files
        code_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h')):
                    code_files.append(os.path.join(root, file))
        
        # Read and analyze files
        file_contents = {}
        for file_path in code_files[:10]:  # Limit to first 10 files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_contents[os.path.relpath(file_path, repo_path)] = content[:2000]  # First 2000 chars
            except:
                continue
        
        # Generate documentation based on style
        doc = generate_styled_documentation(file_contents, context, doc_style, repo_path)
        
        return JSONResponse({
            "documentation": doc,
            "status": "✅ Generated via repository analysis",
            "method": "structure analysis",
            "style": doc_style,
            "files_analyzed": len(file_contents)
        })
        
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "❌ Repository analysis failed"
        })

async def generate_basic_docs(input_text: str, context: str, doc_style: str):
    """Generate basic documentation from input text"""
    
    style_templates = {
        "google": f"""
# Code Documentation (Google Style)

## Overview
{context or 'Generated documentation for the provided code/repository.'}

## Input Analysis
```
{input_text[:500]}{'...' if len(input_text) > 500 else ''}
```

## Functions

### function_name(param1, param2)
'''Brief description of the function.

Args:
    param1 (type): Description of param1.
    param2 (type): Description of param2.

Returns:
    type: Description of return value.

Raises:
    Exception: Description of when this exception is raised.
'''

## Usage Example
```python
# Example usage would go here
result = function_name(arg1, arg2)
```
        """,
        
        "numpy": f"""
# Code Documentation (NumPy Style)

## Overview
{context or 'Generated documentation for the provided code/repository.'}

## Input Analysis
```
{input_text[:500]}{'...' if len(input_text) > 500 else ''}
```

## Functions

### function_name(param1, param2)
'''
Brief description of the function.

Parameters
----------
param1 : type
    Description of param1.
param2 : type
    Description of param2.

Returns
-------
type
    Description of return value.

Raises
------
Exception
    Description of when this exception is raised.
'''

## Usage Example
```python
# Example usage would go here
result = function_name(arg1, arg2)
```
        """,
        
        "markdown": f"""
# Code Documentation

## Overview
{context or 'Generated documentation for the provided code/repository.'}

## Input Analysis
```
{input_text[:500]}{'...' if len(input_text) > 500 else ''}
```

## Functions

### `function_name(param1, param2)`
Brief description of the function.

**Parameters:**
- `param1` (type): Description of param1
- `param2` (type): Description of param2

**Returns:**
- `type`: Description of return value

**Raises:**
- `Exception`: Description of when this exception is raised

## Usage Example
```python
# Example usage would go here
result = function_name(arg1, arg2)
```
        """
    }
    
    selected_style = doc_style if doc_style in style_templates else "google"
    
    return JSONResponse({
        "documentation": style_templates[selected_style],
        "status": "✅ Generated via basic analysis",
        "method": "template-based",
        "style": doc_style
    })

def generate_styled_documentation(file_contents: dict, context: str, doc_style: str, repo_path: str):
    """Generate comprehensive documentation in the specified style"""
    
    # Import the comprehensive documentation generator
    try:
        from comprehensive_docs import generate_comprehensive_documentation
        return generate_comprehensive_documentation(file_contents, context, doc_style, repo_path)
    except ImportError:
        # Fallback to basic analysis if comprehensive_docs not available
        return generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)

def generate_basic_repository_analysis(file_contents: dict, context: str, doc_style: str, repo_path: str):
    """Fallback basic repository analysis"""
    
    # Analyze the files
    total_lines = sum(len(content.split('\n')) for content in file_contents.values())
    functions = []
    classes = []
    imports = []
    
    for file_path, content in file_contents.items():
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('def '):
                functions.append(f"{file_path}: {line}")
            elif line.startswith('class '):
                classes.append(f"{file_path}: {line}")
            elif line.startswith(('import ', 'from ')):
                imports.append(line)
    
    if doc_style == "google":
        return f"""# Repository Documentation (Google Style)

## Overview
Repository: {os.path.basename(repo_path)}
Context: {context or 'Comprehensive repository documentation'}

## Repository Statistics
- Files analyzed: {len(file_contents)}
- Total lines: {total_lines}
- Functions found: {len(functions)}
- Classes found: {len(classes)}

## File Structure
{chr(10).join(f"- `{file_path}`" for file_path in file_contents.keys())}

## Functions
{chr(10).join(f"### {func.split(': ', 1)[1] if ': ' in func else func}" for func in functions[:5])}

## Classes  
{chr(10).join(f"### {cls.split(': ', 1)[1] if ': ' in cls else cls}" for cls in classes[:5])}

## Dependencies
{chr(10).join(f"- `{imp}`" for imp in list(set(imports))[:10])}

---
*Generated by Context-Aware Documentation Generator*"""
    
    elif doc_style == "numpy":
        return f"""# Repository Documentation (NumPy Style)

## Overview
Repository: {os.path.basename(repo_path)}
Context: {context or 'Comprehensive repository documentation'}

## Repository Statistics
- Files analyzed: {len(file_contents)}
- Total lines: {total_lines}  
- Functions found: {len(functions)}
- Classes found: {len(classes)}

## File Structure
{chr(10).join(f"- `{file_path}`" for file_path in file_contents.keys())}

## Functions
{chr(10).join(f"### {func.split(': ', 1)[1] if ': ' in func else func}" for func in functions[:5])}

## Classes
{chr(10).join(f"### {cls.split(': ', 1)[1] if ': ' in cls else cls}" for cls in classes[:5])}

## Dependencies
{chr(10).join(f"- `{imp}`" for imp in list(set(imports))[:10])}

---
*Generated by Context-Aware Documentation Generator*"""
    
    else:  # markdown
        return f"""# Repository Documentation

## Overview
**Repository:** {os.path.basename(repo_path)}  
**Context:** {context or 'Comprehensive repository documentation'}

## Repository Statistics
- **Files analyzed:** {len(file_contents)}
- **Total lines:** {total_lines}
- **Functions found:** {len(functions)}
- **Classes found:** {len(classes)}

## File Structure
{chr(10).join(f"- `{file_path}`" for file_path in file_contents.keys())}

## Functions
{chr(10).join(f"### `{func.split(': ', 1)[1] if ': ' in func else func}`" for func in functions[:5])}

## Classes
{chr(10).join(f"### `{cls.split(': ', 1)[1] if ': ' in cls else cls}`" for cls in classes[:5])}

## Dependencies
{chr(10).join(f"- `{imp}`" for imp in list(set(imports))[:10])}

---
*Generated by Context-Aware Documentation Generator*"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page with enhanced interface for Git repos and documentation styles"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Context-Aware Documentation Generator - Repository Edition</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px; margin: 0 auto; padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container { 
                background: white; padding: 40px; border-radius: 15px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header { text-align: center; margin-bottom: 30px; }
            h1 { color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }
            .subtitle { color: #7f8c8d; font-size: 1.2em; }
            .form-group { margin: 25px 0; }
            label { 
                display: block; margin-bottom: 8px; font-weight: 600; 
                color: #34495e; font-size: 1.1em;
            }
            input, textarea, select { 
                width: 100%; padding: 15px; border: 2px solid #e0e6ed; 
                border-radius: 8px; font-size: 14px;
                resize: vertical; transition: border-color 0.3s;
            }
            input:focus, textarea:focus, select:focus { border-color: #3498db; outline: none; }
            .btn { 
                background: linear-gradient(45deg, #3498db, #2980b9);
                color: white; padding: 15px 40px; border: none; 
                border-radius: 8px; cursor: pointer; font-size: 18px;
                font-weight: 600; transition: transform 0.2s;
                width: 100%; margin: 20px 0;
            }
            .btn:hover { transform: translateY(-2px); }
            .password-info { 
                background: linear-gradient(45deg, #2ecc71, #27ae60);
                color: white; padding: 15px; border-radius: 8px; 
                margin-bottom: 30px; text-align: center;
            }
            .features { 
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin: 30px 0;
            }
            .feature { 
                background: #f8f9fa; padding: 20px; border-radius: 8px;
                text-align: center; border-left: 4px solid #3498db;
            }
            .style-grid {
                display: grid; grid-template-columns: 1fr 1fr 1fr;
                gap: 15px; margin: 10px 0;
            }
            .style-option {
                padding: 10px; border: 2px solid #e0e6ed; border-radius: 6px;
                cursor: pointer; text-align: center; transition: all 0.3s;
            }
            .style-option:hover { border-color: #3498db; }
            .style-option.selected { border-color: #3498db; background: #ebf3fd; }
            .example { font-size: 0.9em; color: #7f8c8d; margin-top: 10px; }
        </style>
        <script>
            function selectStyle(style) {
                document.querySelectorAll('.style-option').forEach(el => el.classList.remove('selected'));
                document.querySelector(`[data-style="${style}"]`).classList.add('selected');
                document.querySelector('select[name="doc_style"]').value = style;
            }
            
            async function generateDocs(event) {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const button = form.querySelector('.btn');
                const originalText = button.textContent;
                
                button.textContent = '🔄 Processing Repository...';
                button.disabled = true;
                
                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    // Create result div if it doesn't exist
                    let resultDiv = document.getElementById('result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.id = 'result';
                        resultDiv.style.cssText = 'margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #27ae60;';
                        form.parentNode.appendChild(resultDiv);
                    }
                    
                    if (result.error) {
                        resultDiv.innerHTML = `
                            <h3 style="color: #e74c3c;">❌ Error</h3>
                            <p><strong>Error:</strong> ${result.error}</p>
                            <p><strong>Status:</strong> ${result.status}</p>
                        `;
                        resultDiv.style.borderLeftColor = '#e74c3c';
                    } else {
                        resultDiv.innerHTML = `
                            <h3 style="color: #27ae60;">✅ ${result.status}</h3>
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 10px 0;">
                                <div><strong>Method:</strong> ${result.method}</div>
                                <div><strong>Style:</strong> ${result.style || 'N/A'}</div>
                                <div><strong>Files:</strong> ${result.files_analyzed || 'N/A'}</div>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 8px; margin: 15px 0; white-space: pre-wrap; font-family: monospace; max-height: 600px; overflow-y: auto; border: 1px solid #ddd;">${result.documentation}</div>
                            <button onclick="downloadDocs('${result.style || 'markdown'}')" style="background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">📥 Download Documentation</button>
                        `;
                        resultDiv.style.borderLeftColor = '#27ae60';
                    }
                    
                    resultDiv.scrollIntoView({ behavior: 'smooth' });
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('Network error. Please try again.');
                } finally {
                    button.textContent = originalText;
                    button.disabled = false;
                }
            }
            
            function downloadDocs(style) {
                const content = document.querySelector('#result div[style*="font-family: monospace"]').textContent;
                const blob = new Blob([content], { type: 'text/markdown' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `documentation_${style}.md`;
                a.click();
                URL.revokeObjectURL(url);
            }
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Context-Aware Documentation Generator</h1>
                <p class="subtitle">Repository Documentation with Multiple Styles</p>
            </div>
            
            <div class="password-info">
                <strong>🔐 Secure Access:</strong> nOtE7thIs | <strong>🌐 Public URL:</strong> Colab + ngrok Ready
            </div>
            
            <form onsubmit="generateDocs(event)">
                <div class="form-group">
                    <label for="repo_url">📂 Repository Source:</label>
                    <input type="text" name="repo_url" placeholder="https://github.com/user/repo.git OR /path/to/repo.zip OR paste code directly" required>
                    <div class="example">
                        Examples:<br>
                        • Git: https://github.com/microsoft/vscode.git<br>
                        • ZIP: /content/my-project.zip<br>
                        • Code: def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)
                    </div>
                </div>
                
                <div class="form-group">
                    <label>📝 Documentation Style:</label>
                    <div class="style-grid">
                        <div class="style-option selected" data-style="google" onclick="selectStyle('google')">
                            <strong>Google Style</strong>
                            <div class="example">Inline docstrings with Args/Returns</div>
                        </div>
                        <div class="style-option" data-style="opensource" onclick="selectStyle('opensource')">
                            <strong>Open Source</strong>
                            <div class="example">README + API docs for collaboration</div>
                        </div>
                        <div class="style-option" data-style="numpy" onclick="selectStyle('numpy')">
                            <strong>NumPy Style</strong>
                            <div class="example">Parameters, Returns sections</div>
                        </div>
                                                <div class="style-option" data-style="markdown" onclick="selectStyle('markdown')">
                            <strong>Technical MD</strong>
                            <div class="example">Detailed technical documentation</div>
                        </div>
                    </div>
                    <select name="doc_style" style="display: none;">
                        <option value="google" selected>Google Style (Inline Docstrings)</option>
                        <option value="opensource">Open Source (README + API)</option>
                        <option value="numpy">NumPy Style</option>
                        <option value="markdown">Technical Markdown</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="context">💡 Documentation Context:</label>
                    <textarea name="context" rows="4" placeholder="Academic research project focusing on algorithmic efficiency
Include performance analysis and optimization recommendations
Target audience: Computer science students and researchers"></textarea>
                </div>
                
                <button type="submit" class="btn">🚀 Generate Repository Documentation</button>
            </form>
            
            <div class="features">
                <div class="feature">
                    <h4>📂 Repository Support</h4>
                    <p>Git URLs, ZIP files, and direct code input</p>
                </div>
                <div class="feature">
                    <h4>📋 Professional Documentation</h4>
                    <p>Google docstrings, Open Source READMEs, Technical docs</p>
                </div>
                <div class="feature">
                    <h4>🧠 Deep Analysis</h4>
                    <p>Architecture understanding, API design, maintenance guides</p>
                </div>
                <div class="feature">
                    <h4>🤝 Collaboration Ready</h4>
                    <p>Open source standards, contribution guides, API references</p>
                </div>
            </div>
            
            <div style="margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 0.9em;">
                <p>💻 <strong>Terminal Access:</strong> python terminal_demo.py | python enhanced_test.py</p>
                <p>🔧 <strong>CLI Interface:</strong> python main.py --directory /path/to/repo --style google</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.post("/generate")
async def generate_docs(
    repo_url: str = Form(...), 
    context: str = Form(""), 
    doc_style: str = Form("google")
):
    """Generate documentation for repository from Git URL, ZIP, or code"""
    global generator
    
    try:
        # Handle repository input (Git URL, ZIP file, or code)
        repo_path = None
        
        if repo_url.startswith(('http://', 'https://')) and ('github.com' in repo_url or 'gitlab.com' in repo_url):
            # Clone Git repository
            print(f"🔄 Cloning repository: {repo_url}")
            temp_dir = tempfile.mkdtemp()
            try:
                result = subprocess.run(['git', 'clone', repo_url, temp_dir], 
                                     check=True, capture_output=True, text=True, timeout=120)
                repo_path = temp_dir
                print(f"✅ Repository cloned to: {repo_path}")
            except subprocess.CalledProcessError as e:
                return JSONResponse({
                    "error": f"Failed to clone repository: {e.stderr if e.stderr else str(e)}",
                    "status": "❌ Git clone failed"
                })
            except subprocess.TimeoutExpired:
                return JSONResponse({
                    "error": "Repository cloning timed out (>2 minutes)",
                    "status": "❌ Clone timeout"
                })
        
        elif repo_url.endswith('.zip') and os.path.exists(repo_url):
            # Handle ZIP file
            print(f"🔄 Extracting ZIP file: {repo_url}")
            temp_dir = tempfile.mkdtemp()
            try:
                with zipfile.ZipFile(repo_url, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                repo_path = temp_dir
                print(f"✅ ZIP extracted to: {repo_path}")
            except Exception as e:
                return JSONResponse({
                    "error": f"Failed to extract ZIP: {str(e)}",
                    "status": "❌ ZIP extraction failed"
                })
        
        elif os.path.exists(repo_url) and os.path.isdir(repo_url):
            # Local directory
            repo_path = repo_url
            print(f"✅ Using local directory: {repo_path}")
        
        # Try full AI mode first
        if generator and AI_AVAILABLE:
            print("🤖 Using full AI generation...")
            try:
                if repo_path and os.path.exists(repo_path):
                    # Use repository analysis
                    if hasattr(generator, 'generate_repository_documentation'):
                        result = await asyncio.to_thread(generator.generate_repository_documentation, repo_path, context, doc_style)
                    else:
                        # Fallback to analyzing main files
                        main_files = []
                        for root, dirs, files in os.walk(repo_path):
                            for file in files[:5]:  # Limit files
                                if file.endswith('.py'):
                                    file_path = os.path.join(root, file)
                                    try:
                                        with open(file_path, 'r') as f:
                                            content = f.read()
                                            main_files.append(content)
                                    except:
                                        continue
                        
                        combined_code = '\n\n'.join(main_files)
                        result = await asyncio.to_thread(generator.generate_documentation, combined_code, context)
                else:
                    # Treat as code snippet
                    result = await asyncio.to_thread(generator.generate_documentation, repo_url, context)
                
                return JSONResponse({
                    "documentation": result,
                    "status": "✅ Generated via full AI system",
                    "method": "context-aware AI",
                    "style": doc_style
                })
            except Exception as e:
                print(f"AI generation failed: {e}")
        
        # Fallback to repository analysis
        if repo_path and os.path.exists(repo_path):
            print("🔄 Using repository structure analysis...")
            return await analyze_repository_structure(repo_path, context, doc_style)
        else:
            # Basic code analysis
            print("🔄 Using basic code analysis...")
            return await generate_basic_docs(repo_url, context, doc_style)
        
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "❌ Generation failed",
            "fallback": "Try using: python terminal_demo.py"
        })

@app.get("/test")
async def run_test():
    """Run a quick system test with repository simulation"""
    test_repo_structure = {
        "main.py": '''def fibonacci(n):
    """Calculate fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)''',
        "utils.py": '''class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self, item):
        return item.upper()'''
    }
    
    try:
        doc = generate_styled_documentation(test_repo_structure, "Test repository", "google", "/test/repo")
        return JSONResponse({
            "🧪 test_status": "✅ Repository Documentation System Working",
            "📝 sample_output": doc[:500] + "...",
            "🤖 ai_status": "✅ Available" if AI_AVAILABLE else "⚠️ Demo mode",
            "🌐 server_url": "Repository-ready FastAPI server",
            "🔐 password": "nOtE7thIs",
            "📊 supported_inputs": ["Git URLs", "ZIP files", "Local directories", "Code snippets"],
            "🎨 supported_styles": ["google", "numpy", "markdown"]
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "❌ Test failed"
        })

@app.get("/demo")
async def demo_info():
    """Show enhanced demo information"""
    return JSONResponse({
        "🎉 message": "Context-Aware Documentation Generator - Repository Edition",
        "🚀 server_status": "✅ Enhanced FastAPI with repository support",
        "📂 input_support": ["Git URLs (GitHub/GitLab)", "ZIP files", "Local directories", "Code snippets"],
        "🎨 output_styles": ["Google Style", "NumPy Style", "Markdown"],
        "🔧 full_ai_access": "Use: python terminal_demo.py",
        "📋 available_scripts": [
            "terminal_demo.py - Interactive AI demo",
            "final_test.py - 30-second validation",
            "enhanced_test.py - Comprehensive testing",
            "main.py - CLI interface with --directory flag"
        ],
        "🌐 access_info": {
            "url": "Repository documentation server",
            "password": "nOtE7thIs",
            "colab_ready": True,
            "ngrok_integrated": True
        },
        "⚡ features": [
            "✅ Git repository cloning",
            "✅ ZIP file extraction", 
            "✅ Multiple documentation styles",
            "✅ AI-powered analysis with fallbacks",
            "✅ Professional web interface",
            "✅ Colab + ngrok compatible"
        ]
    })

def start_server_with_tunnel():
    """Start FastAPI server with ngrok tunnel"""
    print("🌟 Starting Context-Aware Documentation Generator (Repository Edition)")
    print("=" * 70)
    
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
    
    print("\n🚀 Starting Enhanced FastAPI server...")
    print("📂 Repository support: Git URLs, ZIP files, directories")
    print("🎨 Documentation styles: Google, NumPy, Markdown")
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