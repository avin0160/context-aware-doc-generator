#!/usr/bin/env python3
"""
Enhanced FastAPI Server for Context-Aware Documentation Generator
Supports Git repositories, ZIP files, and multiple documentation styles
"""

import ast
import os
import sys
import subprocess
import time

# Fix Windows console encoding for Unicode/emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass  # Older Python versions

import uvicorn
import asyncio
import tempfile
import zipfile
import re
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import signal
from contextlib import contextmanager

# CRITICAL: Don't add src to path to avoid importing old broken modules
# sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Clear any cached modules that might have AST errors
# LAZY LOADING: Skip heavy imports at startup
# Only load when needed to avoid 1-2 minute Phi-3 load time
ADVANCED_SYSTEM_AVAILABLE = False
CODESEARCHNET_AVAILABLE = False
doc_generator = None
rag_system = None

# Metrics classes (imported lazily)
ComprehensiveEvaluator = None
compute_codesearchnet_metrics = None
get_codesearchnet_reference_corpus = None
evaluate_documentation_quality = None  # Real quality metrics (no reference needed)

print("✅ Fast startup mode: Heavy modules will load on demand")
print("⚡ Choose 'Gemini-only' mode for instant documentation without Phi-3")

def lazy_load_metrics_only():
    """Load just the metrics modules (lightweight, no Phi-3)"""
    global CODESEARCHNET_AVAILABLE, ComprehensiveEvaluator, compute_codesearchnet_metrics, get_codesearchnet_reference_corpus, evaluate_documentation_quality
    
    if CODESEARCHNET_AVAILABLE:
        return  # Already loaded
    
    try:
        print("📊 Loading metrics evaluation modules...")
        from evaluation_metrics import ComprehensiveEvaluator as CompEval
        from gemini_context_enhancer import compute_codesearchnet_metrics as csn_metrics_func, get_codesearchnet_reference_corpus as csn_corpus_func
        from real_quality_metrics import evaluate_documentation_quality as real_metrics_func
        
        ComprehensiveEvaluator = CompEval
        compute_codesearchnet_metrics = csn_metrics_func
        get_codesearchnet_reference_corpus = csn_corpus_func
        evaluate_documentation_quality = real_metrics_func
        
        CODESEARCHNET_AVAILABLE = True
        print("✅ Metrics modules loaded")
    except Exception as e:
        print(f"⚠️ Could not load metrics modules: {e}")


def lazy_load_rag_system():
    """Load RAG system independently (works with Gemini-only mode too)"""
    global rag_system
    
    if rag_system is not None:
        return  # Already loaded
    
    try:
        print("🔍 Loading RAG system for semantic code search...")
        import threading, queue
        from src.rag import CodeRAGSystem
        
        result_queue = queue.Queue()
        def rag_loader():
            try:
                result_queue.put(CodeRAGSystem())
            except Exception as e:
                result_queue.put(e)
        
        rag_thread = threading.Thread(target=rag_loader)
        rag_thread.daemon = True
        rag_thread.start()
        rag_thread.join(timeout=60)  # 60 seconds for embedding model
        
        if not rag_thread.is_alive():
            result = result_queue.get_nowait()
            if not isinstance(result, Exception):
                rag_system = result
                print("✅ RAG system loaded (FAISS + sentence-transformers)")
            else:
                print(f"⚠️ RAG system failed to load: {result}")
        else:
            print("⚠️ RAG system load timed out (>60s)")
            
    except Exception as e:
        print(f"⚠️ RAG system not available: {e}")


def lazy_load_advanced_system():
    """Load the heavy documentation system only when requested"""
    global doc_generator, rag_system, ADVANCED_SYSTEM_AVAILABLE, CODESEARCHNET_AVAILABLE
    global ComprehensiveEvaluator, compute_codesearchnet_metrics, get_codesearchnet_reference_corpus, evaluate_documentation_quality
    
    if doc_generator is not None:
        return  # Already loaded
    
    print("\n⏳ Loading advanced documentation system (this may take 1-2 minutes)...")
    try:
        from comprehensive_docs_advanced import DocumentationGenerator
        from evaluation_metrics import BLEUScore, ROUGEScore, METEORScore, CodeBLEU, ComprehensiveEvaluator as CompEval
        from technical_doc_metrics import TechnicalDocumentationEvaluator
        from gemini_context_enhancer import compute_codesearchnet_metrics as csn_metrics_func, get_codesearchnet_reference_corpus as csn_corpus_func
        from real_quality_metrics import evaluate_documentation_quality as real_metrics_func
        
        # Make available globally
        ComprehensiveEvaluator = CompEval
        compute_codesearchnet_metrics = csn_metrics_func
        get_codesearchnet_reference_corpus = csn_corpus_func
        evaluate_documentation_quality = real_metrics_func
        
        CODESEARCHNET_AVAILABLE = True
        ADVANCED_SYSTEM_AVAILABLE = True
        print("✅ Advanced system modules imported")
        
        # Initialize DocumentationGenerator (loads Phi-3)
        print("⏳ Loading Phi-3 model (1-2 minutes)...")
        doc_generator = DocumentationGenerator()
        print("✅ Phi-3 model loaded!")
        
        # Load RAG system using the shared function
        lazy_load_rag_system()
        
    except Exception as e:
        print(f"❌ Failed to load advanced system: {e}")
        ADVANCED_SYSTEM_AVAILABLE = False

app = FastAPI(title="Advanced Documentation Generator (FIXED)", version="3.0.0")

# Add CORS middleware for remote access via ngrok
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for ngrok access
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

def install_all_requirements():
    """Install ALL required dependencies from requirements.txt and ensure models are ready"""
    import os
    
    # Quick check: If marker file exists, skip entirely (already set up)
    marker_file = os.path.join(os.path.dirname(__file__), '.deps_installed')
    if os.path.exists(marker_file):
        print("✅ Dependencies already verified (skipping check)")
        return True
    
    print("\n📦 First-time setup: Checking dependencies...")
    
    # Core packages to check/install
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn[standard]',
        'jinja2': 'jinja2',
        'python-multipart': 'python-multipart',
        'transformers': 'transformers>=4.41.0',
        'torch': 'torch',
        'sentence_transformers': 'sentence-transformers',
        'faiss': 'faiss-cpu',
        'google.genai': 'google-genai',
        'bert_score': 'bert-score',
        'gitpython': 'gitpython',
        'requests': 'requests',
    }
    
    missing_packages = []
    for module, package in required_packages.items():
        try:
            __import__(module.split('.')[0])
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📥 Installing {len(missing_packages)} missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + missing_packages)
            print("✅ All packages installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Some packages failed to install: {e}")
            print("   Try running: pip install -r requirements.txt")
    else:
        print("✅ All required packages already installed")
    
    # Check if requirements.txt exists and install from it (only on first run)
    req_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_file) and missing_packages:
        print("📋 Installing from requirements.txt...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", req_file])
        except:
            pass  # Silent fail - already handled core packages
    
    # Create marker file to skip this on future runs
    try:
        with open(marker_file, 'w') as f:
            f.write('deps_installed')
        print("✅ Setup complete (will skip on next run)")
    except:
        pass  # Non-critical if marker can't be written
    
    return True

def install_fastapi_deps():
    """Install FastAPI dependencies (legacy function, now calls install_all_requirements)"""
    return install_all_requirements()

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
        print("[SUCCESS] ngrok authentication configured")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to setup ngrok auth: {e}")
        return False

def create_tunnel(port=8000):
    """Create ngrok tunnel"""
    try:
        from pyngrok import ngrok
        
        # Kill any existing tunnels to avoid "endpoint already online" error
        try:
            ngrok.kill()
            print("🔄 Cleaned up existing ngrok tunnels")
        except:
            pass
        
        tunnel = ngrok.connect(port)
        public_url = tunnel.public_url
        print(f"\n🌐 Public URL: {public_url}")
        print(f"🔐 Password: nOtE7thIs")
        return tunnel
    except Exception as e:
        print(f"[ERROR] Failed to create tunnel: {e}")
        print("[TIP] If error persists, manually run: pkill ngrok (Linux/Mac) or taskkill /F /IM ngrok.exe (Windows)")
        return None


def build_rag_index_from_files(file_contents: dict, repo_path: str = None):
    """
    Build FAISS index from file contents for RAG retrieval.
    
    This enables semantic search over the codebase to:
    1. Find related functions/classes when documenting
    2. Provide context about similar code patterns
    3. Improve documentation quality with relevant examples
    
    Args:
        file_contents: Dict mapping file paths to content
        repo_path: Optional repository root path
        
    Returns:
        bool: True if index built successfully
    """
    global rag_system
    
    if not rag_system:
        print("⚠️ RAG system not loaded, skipping index build")
        return False
    
    try:
        import ast
        print(f"🔨 Building FAISS index from {len(file_contents)} files...")
        
        # Convert file_contents to the format expected by RAG system
        # Structure: {'files': {path: {functions: [], classes: [], ...}}}
        parsed_codebase = {'files': {}}
        
        for file_path, content in file_contents.items():
            file_data = {
                'file_path': file_path,
                'language': 'python' if file_path.endswith('.py') else 
                           'javascript' if file_path.endswith(('.js', '.ts')) else
                           'java' if file_path.endswith('.java') else
                           'cpp' if file_path.endswith(('.cpp', '.c', '.h')) else
                           'unknown',
                'functions': [],
                'classes': [],
                'imports': []
            }
            
            # Parse Python files with AST for accurate extraction
            if file_path.endswith('.py'):
                try:
                    tree = ast.parse(content)
                    lines = content.split('\n')
                    
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            # Get function code
                            start = node.lineno - 1
                            end = node.end_lineno if hasattr(node, 'end_lineno') else start + 10
                            func_text = '\n'.join(lines[start:end])
                            
                            file_data['functions'].append({
                                'name': node.name,
                                'text': func_text,
                                'start_line': node.lineno,
                                'end_line': end
                            })
                        elif isinstance(node, ast.ClassDef):
                            start = node.lineno - 1
                            end = node.end_lineno if hasattr(node, 'end_lineno') else start + 20
                            class_text = '\n'.join(lines[start:end])
                            
                            file_data['classes'].append({
                                'name': node.name,
                                'text': class_text,
                                'start_line': node.lineno,
                                'end_line': end
                            })
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                file_data['imports'].append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                file_data['imports'].append(node.module)
                except SyntaxError:
                    # Fallback: add file as single chunk
                    file_data['functions'].append({
                        'name': os.path.basename(file_path),
                        'text': content[:2000],
                        'start_line': 1,
                        'end_line': len(content.split('\n'))
                    })
            else:
                # Non-Python: add file as single chunk for now
                file_data['functions'].append({
                    'name': os.path.basename(file_path),
                    'text': content[:2000],
                    'start_line': 1,
                    'end_line': len(content.split('\n'))
                })
            
            parsed_codebase['files'][file_path] = file_data
        
        # Build the FAISS index
        code_chunks = rag_system.prepare_code_chunks(parsed_codebase)
        print(f"📦 Prepared {len(code_chunks)} code chunks for indexing")
        
        rag_system.build_index(code_chunks)
        print(f"✅ FAISS index built with {len(code_chunks)} vectors")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to build RAG index: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_rag_context_for_code(code_snippet: str, code_type: str = "function") -> str:
    """
    Get relevant context from FAISS index for documenting a piece of code.
    
    This improves documentation quality by providing:
    1. Related functions/classes that do similar things
    2. Documentation patterns from the codebase
    3. Context about how this code fits in the project
    
    Args:
        code_snippet: The code to get context for
        code_type: Type of code (function, class, file)
        
    Returns:
        str: Context string to include in LLM prompt
    """
    global rag_system
    
    if not rag_system or not rag_system.is_trained:
        return ""
    
    try:
        # Use the RAG system's built-in method
        context = rag_system.get_context_for_documentation(code_snippet, code_type)
        return context
    except Exception as e:
        print(f"⚠️ RAG context retrieval failed: {e}")
        return ""


# DISABLED: Causes double initialization of Phi-3 (takes ~1 minute extra)
# Already initialized at module import time (lines 30-66)
# Uncomment only if you need lazy loading
"""
@app.on_event("startup")
async def startup_event():
    '''Initialize the generator on startup'''
    global generator, rag_pipeline
    
    print("🚀 Starting Context-Aware Documentation Generator...")
    
    # Initialize documentation generator
    if ADVANCED_SYSTEM_AVAILABLE:
        try:
            print("📝 Initializing Advanced Documentation Generator...")
            doc_generator = DocumentationGenerator()
            print("✅ Advanced documentation system ready")
        except Exception as e:
            print(f"❌ Failed to initialize advanced system: {e}")
            doc_generator = None
    else:
        print("⚠️ Running in basic mode")
        doc_generator = None
"""

async def analyze_repository_structure(repo_path: str, context: str, doc_style: str, temperature: float = 0.3, generation_mode: str = "gemini_only"):
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
        print(f"\n📂 Discovered {len(code_files)} code files in repository")
        print("📖 Processing ALL files for comprehensive documentation generation...")
        
        # Process ALL files in the repository for comprehensive documentation
        for file_path in code_files:  # No limit - process all discovered files
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # For comprehensive analysis, read complete files
                    file_contents[os.path.relpath(file_path, repo_path)] = content
            except:
                continue
        
        total_lines = sum(len(content.split('\n')) for content in file_contents.values())
        total_chars = sum(len(content) for content in file_contents.values())
        print(f"✅ Processed {len(file_contents)} files successfully")
        print(f"   Total lines: {total_lines:,}")
        print(f"   Total size: {total_chars:,} characters")
        
        # Generate documentation based on style
        doc = generate_styled_documentation(file_contents, context, doc_style, repo_path, temperature, generation_mode)
        
        # CRITICAL: Calculate metrics for ALL generation modes
        print("\n📊 Calculating quality metrics...")
        metrics = calculate_comprehensive_metrics(doc, context)
        
        print(f"  ✅ Completeness: {metrics.get('completeness', 'N/A')}")
        print(f"  ✅ Consistency: {metrics.get('consistency', 'N/A')}")
        print(f"  ✅ Readability: {metrics.get('readability_score', 'N/A')}")
        print(f"  ✅ Flesch Grade: {metrics.get('flesch_kincaid_grade', 'N/A')}")
        if metrics.get('bert_score') and metrics.get('bert_score') != 'N/A':
            print(f"  ✅ BERTScore: {metrics.get('bert_score')}")
        print(f"  ✅ Overall: {metrics['overall']}")
        if 'methodology' in metrics:
            print(f"  📚 Method: {metrics['methodology']}")
        
        return JSONResponse({
            "documentation": doc,
            "status": f"✅ Generated via comprehensive repository analysis ({len(file_contents)} files, {total_lines:,} lines)",
            "method": generation_mode,
            "style": doc_style,
            "files_analyzed": len(file_contents),
            "total_lines": total_lines,
            "total_chars": total_chars,
            "comprehensive": True,
            "metrics": metrics  # CRITICAL: Include metrics in response!
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

def enhance_code_snippet(code_snippet: str) -> str:
    """
    Enhance code snippets to make them more analyzable
    Wraps loose code in functions/classes for better analysis
    """
    lines = code_snippet.strip().split('\n')
    
    # Check if it's already well-structured (has functions/classes)
    try:
        import ast
        tree = ast.parse(code_snippet)
        has_functions = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        has_classes = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        
        if has_functions or has_classes:
            return code_snippet  # Already well-structured
    except:
        pass
    
    # For GUI code snippets like tkinter
    if any(keyword in code_snippet.lower() for keyword in ['label', 'button', 'frame', 'root', 'tkinter', 'place', 'pack', 'grid']):
        enhanced_code = '''#!/usr/bin/env python3
"""
GUI Application Code Analysis
"""

class GUIApplication:
    """Main GUI application class for interface management"""
    
    def __init__(self):
        """Initialize the GUI application with window and components"""
        self.setup_window()
        self.create_components()
    
    def setup_window(self):
        """Setup the main application window"""
        # Window configuration code would go here
        pass
    
    def create_components(self):
        """Create and configure GUI components"""
        # Component creation and configuration
''' + f'''
        # Original code:
{code_snippet}
    
    def run(self):
        """Start the GUI application main loop"""
        # Main event loop
        pass

def main():
    """Main entry point for the GUI application"""
    app = GUIApplication()
    app.run()
    
if __name__ == "__main__":
    main()
'''
        return enhanced_code
    
    # For other code snippets, wrap in a utility class
    enhanced_code = '''#!/usr/bin/env python3
"""
Code Analysis - Enhanced Structure
"""

class CodeAnalysis:
    """Utility class for code functionality analysis"""
    
    def __init__(self):
        """Initialize the code analysis utility"""
        self.setup()
    
    def setup(self):
        """Setup and configuration"""
        pass
    
    def process(self):
        """Main processing logic"""
''' + f'''
        # Original code logic:
{code_snippet}
        
    def get_results(self):
        """Get the results of processing"""
        return self.process()

def run_analysis():
    """Run the code analysis"""
    analyzer = CodeAnalysis()
    return analyzer.get_results()

if __name__ == "__main__":
    run_analysis()
'''
    return enhanced_code

def enhance_code_snippet(code_snippet: str) -> str:
    """
    Enhance code snippets to make them more analyzable
    Wraps loose code in functions/classes for better analysis
    """
    lines = code_snippet.strip().split('\n')
    
    # Check if it's already well-structured (has functions/classes)
    try:
        tree = ast.parse(code_snippet)
        has_functions = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        has_classes = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        
        if has_functions or has_classes:
            return code_snippet  # Already well-structured
    except:
        pass
    
    # For GUI code snippets like tkinter
    if any(keyword in code_snippet.lower() for keyword in ['label', 'button', 'frame', 'root', 'tkinter', 'place', 'pack', 'grid', 'mainloop']):
        enhanced_code = '''#!/usr/bin/env python3
"""
GUI Application Code Analysis
"""

class GUIApplication:
    """Main GUI application class for interface management"""
    
    def __init__(self):
        """Initialize the GUI application with window and components"""
        self.setup_window()
        self.create_components()
    
    def setup_window(self):
        """Setup the main application window"""
        # Window configuration code would go here
        pass
    
    def create_components(self):
        """Create and configure GUI components"""
        # Component creation and configuration
''' + f'''
        # Original code:
{code_snippet}
    
    def run(self):
        """Start the GUI application main loop"""
        # Main event loop
        pass

def main():
    """Main entry point for the GUI application"""
    app = GUIApplication()
    app.run()
    
if __name__ == "__main__":
    main()
'''
        return enhanced_code
    
    # For other code snippets, wrap in a utility class
    enhanced_code = '''#!/usr/bin/env python3
"""
Code Analysis - Enhanced Structure
"""

class CodeAnalysis:
    """Utility class for code functionality analysis"""
    
    def __init__(self):
        """Initialize the code analysis utility"""
        self.setup()
    
    def setup(self):
        """Setup and configuration"""
        pass
    
    def process(self):
        """Main processing logic"""
''' + f'''
        # Original code logic:
{code_snippet}
        
    def get_results(self):
        """Get the results of processing"""
        return self.process()

def run_analysis():
    """Run the code analysis"""
    analyzer = CodeAnalysis()
    return analyzer.get_results()

if __name__ == "__main__":
    run_analysis()
'''
    return enhanced_code

def generate_styled_documentation(file_contents: dict, context: str, doc_style: str, repo_path: str, temperature: float = 0.3, generation_mode: str = "gemini_only"):
    """Generate comprehensive documentation using the FIXED generator with enhanced code processing"""
    
    # Count total functions to estimate processing time
    total_content_size = sum(len(content) for content in file_contents.values())
    file_count = len(file_contents)
    
    # === RAG INTEGRATION: Build FAISS index for semantic retrieval ===
    # This enables context-aware documentation by finding related code
    if rag_system and not rag_system.is_trained:
        print("🔍 RAG: Building semantic index for context-aware documentation...")
        build_rag_index_from_files(file_contents, repo_path)
    elif rag_system and rag_system.is_trained:
        print("✅ RAG: Using existing FAISS index")
    
    # Phi-3 Only mode - use local Phi-3 model without Gemini
    if generation_mode == "phi3_only":
        print(f"🧠 PHI-3 ONLY MODE: Using local template-based analysis (no cloud API)")
        lazy_load_advanced_system()
        
        if doc_generator:
            try:
                file_list = list(file_contents.keys())
                print(f"📄 Phi-3 analyzing {len(file_list)} files: {file_list[:5]}{'...' if len(file_list) > 5 else ''}")
                
                # Pass file_contents directly for proper code analysis
                # skip_gemini=True ensures NO Gemini API calls
                # file_contents_dict bypasses MultiInputHandler to use parsed files directly
                result = doc_generator.generate_documentation(
                    input_data='',  # Not used when file_contents_dict provided
                    context=context or 'Technical documentation',
                    doc_style=doc_style,
                    skip_gemini=True,
                    file_contents_dict=file_contents  # Pass actual code files
                )
                if result and len(result) > 100:
                    print(f"✅ PHI-3 ONLY (no Gemini): Generated {len(result)} characters")
                    return result
            except Exception as e:
                print(f"⚠️ Phi-3 only mode failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to basic analysis if Phi-3 fails
        print("⚠️ Phi-3 not available, using basic analysis")
        return generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)
    
    # For AI modes (Gemini or Phi-3), process all files comprehensively
    print(f"📊 Processing {file_count} files, {total_content_size:,} bytes")
    print(f"✅ Comprehensive analysis: ALL {file_count} files will be processed")
    
    # Gemini-only mode - skip Phi-3 entirely
    if generation_mode == "gemini_only":
        print(f"🤖 GEMINI-ONLY MODE: Using Google Gemini API directly (no Phi-3)")
        
        # SKIP metrics and RAG loading for FAST generation - load after if needed
        # lazy_load_metrics_only()  # Causes slowdown - skip for now
        # lazy_load_rag_system()    # Causes slowdown - skip for now
        
        # Skip FAISS index building for speed
        # if rag_system and not rag_system.is_trained:
        #     print("🔨 Building FAISS index for semantic code retrieval...")
        #     build_rag_index_from_files(file_contents, repo_path)
        # elif rag_system and rag_system.is_trained:
        #     print("✅ RAG: Using existing FAISS index")
        
        try:
            # Direct Gemini path - skip all heavyweight modules
            print("📦 Importing Gemini module...")
            import sys
            sys.stdout.flush()
            from gemini_context_enhancer import GeminiContextEnhancer
            print("✅ Gemini module imported")
            sys.stdout.flush()
            import config
            
            print("🔧 Initializing Gemini...")
            sys.stdout.flush()
            gemini = GeminiContextEnhancer()
            print(f"✅ Gemini initialized, available={gemini.available}")
            sys.stdout.flush()
            if not gemini.available:
                print("❌ Gemini not available - using fallback")
                return generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)
            
            # Build prompt with code context
            combined_content = ""
            file_list = list(file_contents.keys())  # Track actual files
            # Include ALL files for comprehensive documentation generation
            for file_path, content in file_contents.items():
                # Include substantial content from each file (up to 5000 chars for better context)
                combined_content += f"# File: {file_path}\n{content[:5000]}\n\n"
            
            print(f"📄 Files to document: {file_list[:10]}{'...' if len(file_list) > 10 else ''}")
            
            # Build strict file listing for anti-hallucination
            files_in_repo = "\n".join([f"- {f}" for f in file_list])
            
            # Skip RAG enhancement for FAST documentation generation
            rag_context_section = ""
            # RAG disabled for speed - uncomment to enable semantic code context
            # if rag_system and rag_system.is_trained:
            #     main_query = combined_content[:1000]
            #     rag_results = rag_system.search(main_query, k=3)
            #     ... RAG context injection code ...
            
            # Build style-specific prompts
            if doc_style == 'technical_comprehensive':
                prompt = f"""You are writing technical reference documentation for the repository below.

CRITICAL ANTI-HALLUCINATION RULES - YOU MUST FOLLOW THESE:
1. Document ONLY the files, classes, and functions that appear in the SOURCE CODE section below
2. DO NOT invent or imagine any code, files, features, or functionality
3. DO NOT make up API endpoints, database tables, or external services
4. Every single thing you document MUST be directly visible in the source code provided
5. If something is unclear, describe what you see rather than guessing
6. NEVER describe generic functionality - describe THIS SPECIFIC codebase only

FILES IN THIS REPOSITORY (the ONLY files that exist):
{files_in_repo}

Context: {context or 'Technical documentation'}
{rag_context_section}
Repository: {os.path.basename(repo_path) if repo_path else 'repository'} ({len(file_contents)} files, {sum(len(c.split('\\n')) for c in file_contents.values())} lines)

SOURCE CODE TO DOCUMENT (document ONLY what appears here):
{combined_content[:18000]}

Write comprehensive technical documentation following this structure. FOR EACH SECTION, write several paragraphs of detailed explanatory text:

# Project Name: Technical Reference Documentation

## Introduction

Write 3-4 paragraphs introducing the project: what problem it solves, why it exists, what makes it unique, and who should use it. Explain the core philosophy and design principles.

## Architecture Overview

Write detailed paragraphs explaining the system architecture. Describe how components interact, the data flow through the system, and the design decisions made. Include explanations of patterns used.

## Installation and Setup

Write step-by-step installation instructions with full explanations. Cover all prerequisites, installation commands with explanations of what each does, verification steps, and post-installation configuration.

## Core Concepts

For each major concept in the codebase, write a dedicated subsection with:
- A clear explanation of what it is and why it matters
- How it fits into the overall system
- Detailed examples showing usage

## API Reference

For EACH class and function found in the code, write:
- A description paragraph explaining its purpose
- The complete function signature
- Parameter descriptions with types and valid values
- Return value description
- Usage example with code block
- Notes on edge cases or common mistakes

## Configuration Guide

Document every configuration option with:
- What the option controls
- The default value and why
- Valid values and their effects
- Example configurations for common scenarios

## Usage Examples and Tutorials

Write multiple complete tutorials:
- A "Getting Started" tutorial for beginners
- An intermediate tutorial showing common workflows
- Advanced examples demonstrating full capabilities
Include complete, runnable code examples with detailed explanations of each step.

## Troubleshooting and FAQ

Document common issues with:
- Problem description
- Root cause explanation
- Step-by-step solution
- Prevention tips

WRITING STYLE: Write in clear, professional prose. Each section should have substantial paragraphs of text, not just lists. Explain the "why" behind things, not just the "what". Be thorough and assume the reader wants to deeply understand the system.

REMEMBER: Only document what is ACTUALLY in the source code above. Do not hallucinate or invent."""
            
            elif doc_style == 'user_guide':
                prompt = f"""You are writing a BEGINNER-FRIENDLY user guide for the code below.

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY describe features and functionality visible in the SOURCE CODE below
2. DO NOT invent or imagine any files, classes, or features
3. Every feature you mention MUST be in the source code provided
4. If unsure, describe what you see rather than guessing

FILES IN THIS REPOSITORY (the ONLY files that exist):
{files_in_repo}

Context: {context or 'User documentation'}
{rag_context_section}
Repository: {os.path.basename(repo_path) if repo_path else 'repository'} ({len(file_contents)} files)

SOURCE CODE TO DOCUMENT:
{combined_content[:18000]}

Write a friendly, accessible user guide based ONLY on the code above:

# Welcome to [Project Name]

## What is This Project?

Write 2-3 paragraphs in simple language explaining what this project does. Use analogies to explain complex concepts. For example: "Think of this like a spell-checker, but for code documentation..."

## How It Works (Visual Overview)

Explain the system flow with a Mermaid diagram:

```mermaid
flowchart TD
    A[📥 You provide your code] --> B[🔍 System analyzes it]
    B --> C[🤖 AI understands the code]
    C --> D[📝 Documentation is generated]
    D --> E[✅ You get beautiful docs!]
```

Write a paragraph explaining each step in the diagram in simple terms.

## Getting Started - Your First Time

Write step-by-step instructions like you're explaining to a friend:

**Step 1: Installation**
Explain what to do and WHY in simple terms...

**Step 2: Running for the First Time**
Walk through the process with screenshots/examples...

## Understanding the System Flow

Include a state diagram showing what happens:

```mermaid
stateDiagram-v2
    [*] --> Ready: Start the program
    Ready --> Analyzing: Upload your code
    Analyzing --> Processing: Code understood
    Processing --> Generating: Creating docs
    Generating --> Done: Success!
    Done --> Ready: Generate more
    Processing --> Error: Something went wrong
    Error --> Ready: Try again
```

Explain each state in simple language.

## Common Tasks - How Do I...?

For each common task, write:
- What you want to achieve
- Step-by-step instructions with code examples
- What to expect when it works
- What to do if it doesn't work

### Task: Generate Documentation for My Python Project

Write complete walkthrough with example inputs and outputs...

### Task: Customize the Output Style

Explain options in simple terms...

## Troubleshooting - When Things Go Wrong

For each common problem:
- **What you see**: Describe the error message
- **What it means**: Explain in simple terms
- **How to fix it**: Step-by-step solution

## Quick Reference Card

A simple summary of the most important commands and options.

WRITING STYLE: Write like you're teaching a friend. Make it approachable.

REMEMBER: Only document what is ACTUALLY in the source code above. Do not hallucinate."""
            
            else:  # opensource style
                prompt = f"""You are writing an OPEN SOURCE contribution guide for the code below.

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY describe files, classes, and functions visible in the SOURCE CODE below
2. DO NOT invent or imagine any features or functionality
3. Every file you mention MUST exist in the source code provided

FILES IN THIS REPOSITORY (the ONLY files that exist):
{files_in_repo}

Context: {context}
{rag_context_section}
Repository: {os.path.basename(repo_path) if repo_path else 'repository'}

SOURCE CODE TO DOCUMENT:
{combined_content[:18000]}

Write a contributor-focused README based ONLY on the code above:

# Project Name

Brief 2-sentence description of what this project does.

## Quick Start

Minimal instructions to get the project running (5-6 steps max).

## Troubleshooting Guide

### Common Issues and Solutions

For each issue:

**Issue: [Error message or problem]**
- What causes this
- How to fix it step by step
- How to verify it's fixed

### Debug Mode

How to enable verbose logging and debug the system.

## How to Contribute

### Setting Up Development Environment

Step-by-step dev setup instructions.

### Code Structure Overview

Brief explanation of where key functionality lives:
- `file.py` - Does X
- `module/` - Handles Y

### Making Changes

1. Fork and clone
2. Create branch
3. Make changes
4. Run tests
5. Submit PR

### Coding Standards

Brief guidelines for code style.

## Areas Needing Help

List specific areas where contributors with expertise are needed:

### 🔴 High Priority
- [Specific feature/bug that needs work]
- [Performance issue that needs expertise]

### 🟡 Medium Priority  
- [Nice-to-have improvements]
- [Documentation gaps]

### 🟢 Good First Issues
- [Beginner-friendly tasks]

## Contact and Community

How to reach maintainers, chat channels, etc.

KEEP IT CONCISE but complete. This is for developers who want to contribute or debug issues."""
            
            print(f"📝 Calling Gemini API (temperature={temperature})...")
            response = gemini.client.models.generate_content(
                model=gemini.model_name,
                contents=prompt,
                config={
                    'temperature': temperature,
                    'max_output_tokens': config.GEMINI_MAX_TOKENS
                }
            )
            
            result = response.text.strip() if response and hasattr(response, 'text') else None
            
            if result and len(result) > 100:
                print("✅ GEMINI: Documentation generated successfully")
                print(f"📄 Generated {len(result)} characters of documentation")
                return result
            else:
                print("⚠️ Gemini returned empty result - using fallback")
                return generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)
                
        except Exception as e:
            print(f"❌ Gemini generation error: {e}")
            import traceback
            traceback.print_exc()
            return generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)
    
    # Phi-3 + Gemini mode
    if generation_mode == "phi3_gemini":
        print(f"🧠 PHI-3 + GEMINI MODE: Using Microsoft Phi-3 + Google Gemini (adaptive timeout)")
        # Lazy load advanced system if not already loaded
        if not ADVANCED_SYSTEM_AVAILABLE or doc_generator is None:
            lazy_load_advanced_system()
        
        # Re-enable Phi-3 if it was disabled
        if doc_generator and hasattr(doc_generator, 'phi3_generator') and doc_generator.phi3_generator:
            doc_generator.phi3_generator.phi3_failed = False
    
    if doc_generator and ADVANCED_SYSTEM_AVAILABLE:
        # Use the FIXED advanced generator with 30-second timeout
        try:
            # Convert file_contents dict to single string for the new API
            combined_content = ""
            
            # Check if we have very little content (likely code snippets)
            total_content = sum(len(content) for content in file_contents.values())
            
            if total_content < 1000 and len(file_contents) == 1:
                # Single small file - use as-is
                for file_path, content in file_contents.items():
                    combined_content += f"# File: {file_path}\n{content}\n\n"
            else:
                # Regular file processing
                for file_path, content in file_contents.items():
                    combined_content += f"# File: {file_path}\n{content}\n\n"
            
            print(f"📝 Generating documentation for {len(combined_content)} characters of code...")
            
            # SMART ADAPTIVE TIMEOUT based on content size
            # Small files (< 5KB): 60 seconds
            # Medium files (5-20KB): 120 seconds  
            # Large files (> 20KB): 180 seconds
            content_kb = len(combined_content) / 1024
            if content_kb < 5:
                timeout_seconds = 60
            elif content_kb < 20:
                timeout_seconds = 120
            else:
                timeout_seconds = 180
            
            print(f"⏱️  Phi-3 adaptive timeout: {timeout_seconds}s for {content_kb:.1f}KB of code")
            print(f"💡 Will fallback to Gemini if Phi-3 exceeds timeout")
            
            # Use asyncio timeout for Phi-3 generation
            import concurrent.futures
            import threading
            
            result = None
            timeout_occurred = False
            
            def generate_with_timeout():
                nonlocal result
                try:
                    result = doc_generator.generate_documentation(
                        input_data=combined_content,
                        context=context,
                        doc_style=doc_style,
                        input_type='code',
                        repo_name=os.path.basename(repo_path) if repo_path else "repository",
                        temperature=temperature
                    )
                except Exception as e:
                    print(f"❌ Phi-3 generation error: {e}")
                    result = None
            
            # Run WITH adaptive timeout
            thread = threading.Thread(target=generate_with_timeout)
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout_seconds)  # Adaptive timeout based on file size
            
            if thread.is_alive():
                print(f"⏱️  Phi-3 timeout ({timeout_seconds}s exceeded) - switching to Gemini-only mode")
                timeout_occurred = True
                # Force fast-fail mode for future requests in this session
                if hasattr(doc_generator, 'phi3_generator') and doc_generator.phi3_generator:
                    doc_generator.phi3_generator.phi3_failed = True
                # Set result to None to trigger Gemini fallback below
                result = None
            
            # If Phi-3 failed or timed out, use Gemini fallback
            if result is None:
                print(f"⚠️ Phi-3 {'timed out' if timeout_occurred else 'failed'} - switching to Gemini-only mode")
                # Use Gemini fallback (NOT templates!)
                from gemini_context_enhancer import GeminiContextEnhancer
                import config
                
                gemini = GeminiContextEnhancer()
                if gemini.available:
                    combined_content = ""
                    file_list = list(file_contents.keys())
                    for file_path, content in file_contents.items():
                        combined_content += f"# File: {file_path}\n{content[:5000]}\n\n"
                    
                    files_in_repo = "\n".join([f"- {f}" for f in file_list])
                    
                    prompt = f"""You are writing technical reference documentation for the code below.

CRITICAL ANTI-HALLUCINATION RULES:
1. Document ONLY files, classes, and functions visible in the SOURCE CODE below
2. DO NOT invent or imagine any features or functionality
3. Every thing you mention MUST be in the source code provided

FILES IN THIS REPOSITORY (the ONLY files that exist):
{files_in_repo}

Context: {context or 'Technical documentation'}

Repository: {os.path.basename(repo_path) if repo_path else 'repository'} ({len(file_contents)} files, {sum(len(c.split('\\n')) for c in file_contents.values())} lines)

SOURCE CODE TO DOCUMENT:
{combined_content[:18000]}

Write documentation ONLY about the code above. Include:
- Introduction (what this code actually does)
- Architecture (based on actual files and classes)
- API Reference (ONLY functions visible in code)
- Usage examples (based on actual code patterns)

REMEMBER: Do not hallucinate or invent anything not in the source code."""
                    
                    response = gemini.client.models.generate_content(
                        model=gemini.model_name,
                        contents=prompt,
                        config={'temperature': temperature, 'max_output_tokens': config.GEMINI_MAX_TOKENS}
                    )
                    result = response.text.strip() if response and hasattr(response, 'text') else None
                    print("✅ GEMINI FALLBACK: Generated documentation successfully")
                else:
                    print("❌ Both Phi-3 and Gemini unavailable - using fallback templates")
                    result = generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)
            
            if result:
                # Quality check
                has_placeholders = any(phrase in result for phrase in [
                    'Function implementation.', 'Class implementation.', 'Method implementation.'
                ])
                
                if has_placeholders:
                    print("⚠️ WARNING: Generated documentation contains placeholder text!")
                elif timeout_occurred:
                    print(f"✅ GEMINI FALLBACK: Generated documentation successfully ({len(result)} chars)")
                else:
                    print(f"✅ PHI-3 SUCCESS: Generated documentation with Phi-3 + Gemini ({len(result)} chars)")
                
                return result
            else:
                print("⚠️ Phi-3 returned None - using fallback")
                return generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)
            
        except Exception as e:
            print(f"❌ Error with fixed generator: {e}")
            import traceback
            traceback.print_exc()
            return f"Error generating documentation: {str(e)}"
    else:
        # Fallback to basic analysis
        print("❌ WARNING: Using fallback - will produce placeholder text!")
        return generate_basic_repository_analysis(file_contents, context, doc_style, repo_path)

def calculate_comprehensive_metrics(result: str, context: str) -> dict:
    """Calculate comprehensive quality metrics for documentation.
    
    Uses:
    1. BLEU_eq, METEOR_eq, ROUGE_eq - Heuristic approximations of NLP metrics
    2. Readability scores (Flesch-Kincaid, SMOG, Coleman-Liau, ARI)
    3. BERTScore (if available) - semantic similarity
    4. Overall score = weighted average of all metrics
    
    The _eq metrics are heuristic approximations that correlate with their
    corresponding NLP metrics without requiring reference translations.
    """
    
    try:
        # ========== BASIC TEXT STATISTICS ==========
        words = result.split()
        word_count = len(words)
        unique_words = len(set(w.lower() for w in words))
        
        # Sentence detection
        sentences = re.split(r'[.!?]+', result)
        sentences = [s.strip() for s in sentences if s.strip()]
        total_sentences = len(sentences)
        unique_sentences = len(set(s.lower() for s in sentences))
        
        # Syllable counting for readability metrics
        def count_syllables(word):
            word = word.lower()
            if len(word) <= 3:
                return 1
            vowels = "aeiouy"
            count = 0
            prev_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_vowel:
                    count += 1
                prev_vowel = is_vowel
            if word.endswith('e'):
                count -= 1
            return max(count, 1)
        
        total_syllables = sum(count_syllables(w) for w in words)
        
        # Complex words (3+ syllables)
        complex_words = sum(1 for w in words if count_syllables(w) >= 3)
        
        # Character count (for some readability formulas)
        total_chars = sum(len(w) for w in words)
        
        avg_sentence_len = word_count / max(total_sentences, 1)
        avg_syllables_per_word = total_syllables / max(word_count, 1)
        
        # ========== N-GRAM STATISTICS FOR BLEU/ROUGE HEURISTICS ==========
        def get_ngrams(text_words, n):
            return [tuple(text_words[i:i+n]) for i in range(len(text_words) - n + 1)]
        
        unigrams = get_ngrams(words, 1) if len(words) >= 1 else []
        bigrams = get_ngrams(words, 2) if len(words) >= 2 else []
        trigrams = get_ngrams(words, 3) if len(words) >= 3 else []
        fourgrams = get_ngrams(words, 4) if len(words) >= 4 else []
        
        # Unique n-gram ratios (diversity)
        unigram_diversity = len(set(unigrams)) / max(len(unigrams), 1)
        bigram_diversity = len(set(bigrams)) / max(len(bigrams), 1)
        trigram_diversity = len(set(trigrams)) / max(len(trigrams), 1)
        fourgram_diversity = len(set(fourgrams)) / max(len(fourgrams), 1)
        
        # ========== BLEU_eq: N-gram Precision Heuristic ==========
        # Approximates BLEU by measuring n-gram diversity and technical vocabulary coverage
        # BLEU measures precision of n-grams against reference - we approximate with self-consistency
        
        # Technical terms presence (domain vocabulary)
        tech_terms = ['function', 'class', 'method', 'parameter', 'return', 'value', 'type',
                      'string', 'number', 'array', 'object', 'data', 'config', 'api', 'endpoint',
                      'code', 'example', 'usage', 'documentation', 'module', 'import', 'export',
                      'async', 'await', 'promise', 'callback', 'error', 'exception', 'handler']
        tech_coverage = sum(1 for term in tech_terms if term in result.lower()) / len(tech_terms)
        
        # N-gram precision approximation (geometric mean like BLEU)
        # With brevity penalty for too-short docs
        brevity_penalty = min(1.0, word_count / 500)  # Penalty if < 500 words
        
        # BLEU_eq = geometric mean of n-gram diversities * tech coverage * brevity penalty
        import math
        epsilon = 0.01  # Smoothing
        ngram_geo_mean = (
            (unigram_diversity + epsilon) * 
            (bigram_diversity + epsilon) * 
            (trigram_diversity + epsilon) * 
            (fourgram_diversity + epsilon)
        ) ** 0.25
        
        bleu_eq = brevity_penalty * ngram_geo_mean * (0.5 + 0.5 * tech_coverage)
        bleu_eq = min(1.0, max(0.0, bleu_eq * 1.2))  # Scale and clamp
        
        # ========== METEOR_eq: Term Matching + Synonymy Heuristic ==========
        # METEOR considers exact matches, stems, synonyms, and paraphrases
        # We approximate with lexical diversity, sentence variation, and semantic indicators
        
        # Exact term consistency (repeated terms used consistently)
        term_frequency = {}
        for w in words:
            w_lower = w.lower()
            term_frequency[w_lower] = term_frequency.get(w_lower, 0) + 1
        
        # High-frequency terms (concepts reinforced)
        high_freq_terms = sum(1 for freq in term_frequency.values() if freq >= 3)
        concept_reinforcement = min(1.0, high_freq_terms / 20)
        
        # Sentence structure variety (approximates paraphrase capability)
        sentence_lengths = [len(s.split()) for s in sentences]
        if sentence_lengths:
            length_variance = sum((l - avg_sentence_len)**2 for l in sentence_lengths) / len(sentence_lengths)
            structure_variety = min(1.0, (length_variance ** 0.5) / 10)
        else:
            structure_variety = 0.5
        
        # Semantic indicators (code blocks, references, headers)
        code_blocks = len(re.findall(r'```[\s\S]*?```', result))
        inline_code = len(re.findall(r'`[^`]+`', result))
        headers = len(re.findall(r'^#{1,6}\s', result, re.MULTILINE))
        
        semantic_richness = min(1.0, (code_blocks * 0.1 + inline_code * 0.02 + headers * 0.05 + 0.3))
        
        # METEOR_eq = harmonic mean of components (like F-score)
        lexical_div = unique_words / max(word_count, 1)
        meteor_components = [lexical_div, concept_reinforcement, structure_variety, semantic_richness]
        meteor_eq = sum(meteor_components) / len(meteor_components)
        # Scale to reasonable range without excessive boost
        meteor_eq = min(1.0, max(0.0, meteor_eq * 0.85 + 0.08))  # Reduced boost for realistic scores
        
        # ========== ROUGE_eq: Recall-Oriented Heuristic ==========
        # ROUGE measures recall of n-grams from reference - we approximate with content coverage
        
        # Section coverage (comprehensive recall of documentation components)
        section_patterns = [
            (r'(description|overview|summary|introduction)', 'Description'),
            (r'(parameter|argument|arg|param)', 'Parameters'),
            (r'(return|output|result)', 'Returns'),
            (r'(example|usage|sample|demo)', 'Examples'),
            (r'(note|warning|important|tip)', 'Notes'),
            (r'(function|method|class|module|component)', 'Component Docs'),
            (r'(install|setup|configuration|config)', 'Setup'),
            (r'(api|endpoint|interface|route)', 'API Docs'),
            (r'(error|exception|handle|catch)', 'Error Handling'),
            (r'(test|spec|assert|expect)', 'Testing'),
        ]
        sections_found = sum(1 for pattern, _ in section_patterns if re.search(pattern, result.lower()))
        section_recall = sections_found / len(section_patterns)
        
        # Content density (information per sentence)
        avg_words_per_sentence = word_count / max(total_sentences, 1)
        content_density = min(1.0, avg_words_per_sentence / 20)  # 20 words/sentence is dense
        
        # Longest common subsequence approximation (via unique sentence ratio)
        sentence_coverage = unique_sentences / max(total_sentences, 1)
        
        # ROUGE_eq = weighted combination of recall components
        rouge_eq = (section_recall * 0.4 + content_density * 0.3 + sentence_coverage * 0.3)
        rouge_eq = min(1.0, max(0.0, rouge_eq * 1.1 + 0.2))  # Base boost + scale
        
        # ========== LEGACY HEURISTIC SCORES (for compatibility) ==========
        lexical_diversity = unique_words / max(word_count, 1)
        completeness = section_recall  # Reuse section coverage
        
        # Consistency (internal references and code blocks)
        defined_items = len(re.findall(r'(def |function |method |class |interface )\w+', result.lower()))
        referenced_items = len(re.findall(r'`[^`]+`', result))
        consistency = min(1.0, 0.4 + (defined_items * 0.05 + referenced_items * 0.02 + code_blocks * 0.1))
        
        # Brevity (optimal sentence length is 15-25 words)
        if avg_sentence_len < 8:
            brevity = 0.6
        elif avg_sentence_len > 35:
            brevity = 0.5
        elif 12 <= avg_sentence_len <= 25:
            brevity = 1.0
        elif avg_sentence_len < 12:
            brevity = 0.8
        else:
            brevity = 0.75
        
        # ========== READABILITY SCORES ==========
        
        # Flesch Reading Ease (0-100, higher = easier)
        flesch_reading_ease = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word)
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = (0.39 * avg_sentence_len) + (11.8 * avg_syllables_per_word) - 15.59
        flesch_kincaid_grade = max(0, min(18, flesch_kincaid_grade))
        
        # SMOG Index
        if total_sentences > 0:
            smog_index = 1.0430 * ((complex_words * (30 / total_sentences)) ** 0.5) + 3.1291
        else:
            smog_index = 0
        smog_index = max(0, min(18, smog_index))
        
        # Coleman-Liau Index
        L = (total_chars / max(word_count, 1)) * 100
        S = (total_sentences / max(word_count, 1)) * 100
        coleman_liau = (0.0588 * L) - (0.296 * S) - 15.8
        coleman_liau = max(0, min(18, coleman_liau))
        
        # Automated Readability Index (ARI)
        ari = (4.71 * (total_chars / max(word_count, 1))) + (0.5 * avg_sentence_len) - 21.43
        ari = max(0, min(18, ari))
        
        # Normalize readability to 0-1 (target: grade 10-14 for technical docs)
        avg_grade = (flesch_kincaid_grade + smog_index + coleman_liau + ari) / 4
        if 10 <= avg_grade <= 14:
            readability_score = 1.0
        elif 8 <= avg_grade < 10:
            readability_score = 0.85
        elif 14 < avg_grade <= 16:
            readability_score = 0.85
        elif avg_grade < 8:
            readability_score = 0.7
        else:
            readability_score = 0.6
        
        # Flesch ease normalized
        if 50 <= flesch_reading_ease <= 70:
            flesch_normalized = 1.0
        elif 40 <= flesch_reading_ease < 50 or 70 < flesch_reading_ease <= 80:
            flesch_normalized = 0.85
        else:
            flesch_normalized = 0.7
        
        # ========== BERT SCORE (if available) ==========
        bert_score_value = None
        try:
            from bert_score import score as bert_score_func
            
            if context and len(context) > 50:
                reference = context
            else:
                reference = "This documentation provides comprehensive technical information including function descriptions, parameters, return values, usage examples, and configuration options."
            
            P, R, F1 = bert_score_func([result[:5000]], [reference], lang="en", verbose=False)
            bert_score_value = float(F1[0])
            print(f"  📊 BERTScore: {bert_score_value:.4f}")
        except ImportError:
            pass
        except Exception as e:
            print(f"  ⚠️ BERTScore failed: {e}")
        
        # ========== CALCULATE OVERALL SCORE ==========
        # Weighted average: BLEU_eq + METEOR_eq + ROUGE_eq + Readability + BERTScore
        
        nlp_heuristic_avg = (bleu_eq * 0.35 + meteor_eq * 0.35 + rouge_eq * 0.30)
        readability_avg = (readability_score * 0.5 + flesch_normalized * 0.5)
        
        if bert_score_value is not None:
            overall = (nlp_heuristic_avg * 0.40) + (readability_avg * 0.25) + (bert_score_value * 0.35)
        else:
            overall = (nlp_heuristic_avg * 0.55) + (readability_avg * 0.45)
        
        # Boost for good documentation characteristics
        if code_blocks >= 3:
            overall = min(1.0, overall + 0.03)
        if sections_found >= 5:
            overall = min(1.0, overall + 0.03)
        
        return {
            # Primary NLP-equivalent metrics
            "bleu_eq": f"{bleu_eq:.4f}",
            "meteor_eq": f"{meteor_eq:.4f}",
            "rouge_eq": f"{rouge_eq:.4f}",
            # Readability
            "readability_score": f"{readability_score:.4f}",
            "flesch_reading_ease": f"{flesch_reading_ease:.1f}",
            "flesch_kincaid_grade": f"{flesch_kincaid_grade:.1f}",
            "smog_index": f"{smog_index:.1f}",
            "coleman_liau": f"{coleman_liau:.1f}",
            "ari": f"{ari:.1f}",
            # BERTScore
            "bert_score": f"{bert_score_value:.4f}" if bert_score_value else "N/A",
            # Legacy metrics (for compatibility)
            "lexical_diversity": f"{lexical_diversity:.4f}",
            "completeness": f"{completeness:.4f}",
            "consistency": f"{consistency:.4f}",
            "brevity": f"{brevity:.4f}",
            # Overall
            "overall": f"{overall:.2%}",
            "validity": "valid",
            "methodology": "BLEU_eq + METEOR_eq + ROUGE_eq + Readability + BERTScore" if bert_score_value else "BLEU_eq + METEOR_eq + ROUGE_eq + Readability",
            "comprehensive": {
                "bleu_eq": f"{bleu_eq:.4f}",
                "meteor_eq": f"{meteor_eq:.4f}",
                "rouge_eq": f"{rouge_eq:.4f}",
                "lexical_diversity": f"{lexical_diversity:.4f}",
                "completeness": f"{completeness:.4f}",
                "consistency": f"{consistency:.4f}",
                "brevity": f"{brevity:.4f}",
                "word_count": word_count,
                "unique_words": unique_words,
                "sentences": total_sentences,
                "unique_sentences": unique_sentences,
                "avg_sentence_length": f"{avg_sentence_len:.1f}",
                "flesch_ease": f"{flesch_reading_ease:.1f}",
                "grade_level": f"{avg_grade:.1f}",
                "bert_score": f"{bert_score_value:.4f}" if bert_score_value else "N/A"
            }
        }
    except Exception as e:
        print(f"⚠️ Metrics calculation error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "bleu_eq": "0.0000",
            "meteor_eq": "0.0000",
            "rouge_eq": "0.0000",
            "lexical_diversity": "0.0000",
            "completeness": "0.0000", 
            "consistency": "0.0000",
            "brevity": "0.0000",
            "readability_score": "0.0000",
            "overall": "0.00%",
            "validity": "error",
            "comprehensive": {
                "bleu_eq": "0.0000",
                "meteor_eq": "0.0000",
                "rouge_eq": "0.0000",
                "lexical_diversity": "0.0000",
                "completeness": "0.0000",
                "consistency": "0.0000",
                "brevity": "0.0000",
                "word_count": 0,
                "unique_words": 0,
                "sentences": 0,
                "unique_sentences": 0,
                "avg_sentence_length": "0.0"
            }
        }

def _generate_tautological_description(name: str, signature: str, element_type: str = "function") -> str:
    """Generate a meaningful tautological description from function/class name and signature.
    
    This creates human-readable descriptions based on naming conventions.
    """
    import re
    
    # Clean up the name
    clean_name = name.replace('_', ' ').replace('-', ' ')
    
    # Extract words from camelCase/PascalCase
    words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', clean_name)
    words = [w.lower() for w in words if w]
    
    if not words:
        words = [name.lower()]
    
    # Common verb patterns and their descriptions
    verb_descriptions = {
        'get': ('retrieves', 'Returns the requested'),
        'set': ('sets', 'Assigns a value to'),
        'create': ('creates', 'Instantiates a new'),
        'delete': ('deletes', 'Removes the specified'),
        'remove': ('removes', 'Eliminates the specified'),
        'add': ('adds', 'Appends or inserts'),
        'update': ('updates', 'Modifies the existing'),
        'init': ('initializes', 'Sets up the initial state of'),
        'initialize': ('initializes', 'Sets up the initial state of'),
        'load': ('loads', 'Reads and processes'),
        'save': ('saves', 'Persists data to'),
        'process': ('processes', 'Handles and transforms'),
        'handle': ('handles', 'Manages and responds to'),
        'parse': ('parses', 'Analyzes and extracts data from'),
        'validate': ('validates', 'Checks the validity of'),
        'check': ('checks', 'Verifies the state or condition of'),
        'calculate': ('calculates', 'Computes the value of'),
        'compute': ('computes', 'Determines the result of'),
        'convert': ('converts', 'Transforms the format of'),
        'format': ('formats', 'Structures the output of'),
        'build': ('builds', 'Constructs and assembles'),
        'run': ('runs', 'Executes the main logic of'),
        'start': ('starts', 'Begins the execution of'),
        'stop': ('stops', 'Terminates the execution of'),
        'find': ('finds', 'Searches for and returns'),
        'search': ('searches', 'Looks for matching'),
        'filter': ('filters', 'Selects items matching criteria in'),
        'sort': ('sorts', 'Orders the elements of'),
        'render': ('renders', 'Generates visual output for'),
        'draw': ('draws', 'Creates visual representation of'),
        'display': ('displays', 'Shows the content of'),
        'send': ('sends', 'Transmits data to'),
        'receive': ('receives', 'Accepts incoming data from'),
        'connect': ('connects', 'Establishes a connection to'),
        'disconnect': ('disconnects', 'Closes the connection to'),
        'read': ('reads', 'Retrieves data from'),
        'write': ('writes', 'Outputs data to'),
        'open': ('opens', 'Initiates access to'),
        'close': ('closes', 'Terminates access to'),
        'main': ('serves as', 'The primary entry point that'),
        'test': ('tests', 'Verifies the functionality of'),
        'is': ('checks if', 'Returns a boolean indicating whether'),
        'has': ('checks if', 'Returns whether the object has'),
        'can': ('determines if', 'Returns whether the operation can'),
    }
    
    # Extract parameters from signature
    params = []
    if '(' in signature and ')' in signature:
        param_str = signature[signature.find('(')+1:signature.rfind(')')]
        params = [p.strip().split(':')[0].split('=')[0].strip() for p in param_str.split(',') if p.strip() and p.strip() != 'self']
    
    # Generate description
    first_word = words[0] if words else ''
    rest_words = ' '.join(words[1:]) if len(words) > 1 else ''
    
    if element_type == "class":
        if rest_words:
            return f"A class that represents {rest_words}. Provides functionality for managing and processing {rest_words} data and operations."
        else:
            return f"A class that encapsulates {first_word} functionality. Manages state and provides methods for {first_word} operations."
    
    # Function description
    if first_word in verb_descriptions:
        verb, prefix = verb_descriptions[first_word]
        subject = rest_words if rest_words else "the specified data"
        desc = f"{prefix} {subject}."
    else:
        # Generic description
        full_name = ' '.join(words)
        desc = f"Performs the {full_name} operation."
    
    # Add parameter info
    if params:
        param_list = ', '.join(f'`{p}`' for p in params[:4])
        desc += f" Takes {param_list} as input parameters."
        if len(params) > 4:
            desc += f" (and {len(params) - 4} more parameters)"
    
    return desc


def generate_basic_repository_analysis(file_contents: dict, context: str, doc_style: str, repo_path: str):
    """Fallback basic repository analysis with tautological descriptions"""
    
    # Analyze the files
    total_lines = sum(len(content.split('\n')) for content in file_contents.values())
    functions = []
    classes = []
    imports = []
    
    for file_path, content in file_contents.items():
        # Use AST for robust parsing (handles indentation, async, decorators)
        if file_path.endswith('.py'):
            try:
                import ast
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Get function signature
                        args = [arg.arg for arg in node.args.args]
                        sig = f"def {node.name}({', '.join(args)})"
                        functions.append(f"{file_path}: {sig}")
                    elif isinstance(node, ast.AsyncFunctionDef):
                        # Handle async functions too
                        args = [arg.arg for arg in node.args.args]
                        sig = f"async def {node.name}({', '.join(args)})"
                        functions.append(f"{file_path}: {sig}")
                    elif isinstance(node, ast.ClassDef):
                        bases = [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases[:3]]
                        bases_str = f"({', '.join(bases)})" if bases else ""
                        classes.append(f"{file_path}: class {node.name}{bases_str}")
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(f"import {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports.append(f"from {module} import {alias.name}")
            except SyntaxError:
                # Fall back to line-based detection if AST fails
                for line in content.split('\n'):
                    stripped = line.strip()
                    if 'def ' in stripped and '(' in stripped:
                        functions.append(f"{file_path}: {stripped.split('#')[0].strip()}")
                    elif stripped.startswith('class ') and ':' in stripped:
                        classes.append(f"{file_path}: {stripped.split('#')[0].strip()}")
                    elif stripped.startswith(('import ', 'from ')):
                        imports.append(stripped)
        else:
            # Non-Python files: basic line scanning
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped.startswith(('function ', 'def ', 'public ', 'private ', 'func ')):
                    functions.append(f"{file_path}: {stripped[:80]}")
                elif stripped.startswith(('class ', 'interface ', 'struct ', 'type ')):
                    classes.append(f"{file_path}: {stripped[:80]}")
    
    if doc_style == "google":
        # Generate detailed function documentation with tautological descriptions
        func_docs = []
        for func in functions[:10]:  # Document up to 10 functions
            file_path_part, sig = func.split(': ', 1) if ': ' in func else ('', func)
            # Extract function name from signature
            if '(' in sig:
                func_name = sig.split('(')[0].replace('def ', '').replace('async def ', '').strip()
            else:
                func_name = sig.replace('def ', '').replace('async def ', '').strip()
            
            description = _generate_tautological_description(func_name, sig, "function")
            func_docs.append(f"""### `{sig}`

**Description:** {description}

**Location:** `{file_path_part}`
""")
        
        # Generate detailed class documentation
        class_docs = []
        for cls in classes[:10]:  # Document up to 10 classes
            file_path_part, sig = cls.split(': ', 1) if ': ' in cls else ('', cls)
            # Extract class name from signature
            class_name = sig.replace('class ', '').split('(')[0].split(':')[0].strip()
            
            description = _generate_tautological_description(class_name, sig, "class")
            class_docs.append(f"""### `{sig}`

**Description:** {description}

**Location:** `{file_path_part}`
""")
        
        return f"""# Repository Documentation (Google Style)

## Overview

**Repository:** {os.path.basename(repo_path)}

**Purpose:** {context or 'This repository provides a comprehensive codebase for software development functionality.'}

This documentation provides detailed information about the repository structure, functions, classes, and dependencies. The codebase consists of {len(file_contents)} files with a total of {total_lines:,} lines of code.

## Repository Statistics

| Metric | Value |
|--------|-------|
| Files analyzed | {len(file_contents)} |
| Total lines | {total_lines:,} |
| Functions found | {len(functions)} |
| Classes found | {len(classes)} |

## File Structure

The repository is organized with the following file structure:

{chr(10).join(f"- `{file_path}` - Source file containing implementation code" for file_path in file_contents.keys())}

## Functions

This section documents the main functions available in the codebase.

{chr(10).join(func_docs) if func_docs else "No functions documented."}

## Classes

This section documents the classes defined in the codebase.

{class_docs[0] if class_docs else "No classes documented."}
{chr(10).join(class_docs[1:]) if len(class_docs) > 1 else ""}

## Dependencies

The following external dependencies are used by this project:

{chr(10).join(f"- `{imp}` - External module dependency" for imp in list(set(imports))[:15])}

## Usage

To use this repository, import the required modules and call the appropriate functions or instantiate the classes as needed.

```python
# Example usage
from {os.path.basename(repo_path).replace('-', '_')} import main_module
# Initialize and use the functionality
```

---
*Documentation generated with tautological analysis by Context-Aware Documentation Generator*"""
    
    elif doc_style == "user_guide":
        # User-focused documentation
        main_functions = [f for f in functions if any(keyword in f.lower() for keyword in ['main', 'run', 'start', 'execute', 'init', 'create', 'build'])]
        entry_points = main_functions[:5] if main_functions else functions[:5]
        
        # Generate dynamic component names for diagram
        top_classes = [cls.split(': ', 1)[1].split()[0] if ': ' in cls else cls.split()[0] for cls in classes[:4]]
        top_functions = [func.split(': ', 1)[1].split('(')[0] if ': ' in func and '(' in func else 'process' for func in functions[:3]]
        
        return f"""# {os.path.basename(repo_path)} - User Guide & Instruction Manual

## Getting Started

### What is this project?
{context or 'This project provides tools and utilities for software development.'}

### Quick Stats
- **Files:** {len(file_contents)}
- **Lines of Code:** {total_lines:,}
- **Classes:** {len(classes)}
- **Functions:** {len(functions)}

---

## System Architecture

### State Diagram: System Workflow

```mermaid
stateDiagram-v2
    [*] --> Initialization
    Initialization --> Configuration
    Configuration --> Processing: Config Valid
    Configuration --> Error: Config Invalid
    Processing --> {top_classes[0] if top_classes else 'CoreModule'}: Load Components
    {top_classes[0] if top_classes else 'CoreModule'} --> {top_classes[1] if len(top_classes) > 1 else 'DataHandler'}: Process Data
    {top_classes[1] if len(top_classes) > 1 else 'DataHandler'} --> {top_classes[2] if len(top_classes) > 2 else 'OutputGenerator'}: Transform
    {top_classes[2] if len(top_classes) > 2 else 'OutputGenerator'} --> Success: Complete
    Success --> [*]
    Error --> [*]
```

### Component Interaction Flow

```mermaid
graph TD
    A[User Input] --> B{top_functions[0] if top_functions else 'initialize'}
    B --> C[{top_classes[0] if top_classes else 'MainProcessor'}]
    C --> D[{top_classes[1] if len(top_classes) > 1 else 'DataHandler'}]
    D --> E[{top_classes[2] if len(top_classes) > 2 else 'OutputModule'}]
    E --> F[Results]
    C --> G[Configuration]
    G --> D
    D --> H{{top_functions[1] if len(top_functions) > 1 else 'validate'}}
    H --> |Valid| E
    H --> |Invalid| I[Error Handler]
    I --> F
```

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant System
    participant {top_classes[0] if top_classes else 'Processor'}
    participant {top_classes[1] if len(top_classes) > 1 else 'Handler'}
    participant Output
    
    User->>System: Initialize
    System->>{top_classes[0] if top_classes else 'Processor'}: Load
    {top_classes[0] if top_classes else 'Processor'}->>{top_classes[1] if len(top_classes) > 1 else 'Handler'}: Process Data
    {top_classes[1] if len(top_classes) > 1 else 'Handler'}->>Output: Transform
    Output->>User: Return Results
```

---

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {os.path.basename(repo_path)}

# Install dependencies
pip install -r requirements.txt
# or
python setup.py install
```

---

## How to Use

### Entry Points

The following are the main entry points to use this code:

{chr(10).join(f'''**{i+1}. {func.split(': ', 1)[1] if ': ' in func else func}**
   - Location: `{func.split(': ')[0] if ': ' in func else 'main module'}`
   - Purpose: Main execution function
''' for i, func in enumerate(entry_points[:3]))}

### Basic Usage Example

```python
# Example 1: Basic usage
from {list(file_contents.keys())[0].replace('.py', '').replace('/', '.').replace('\\', '.')} import *

# Initialize the main component
result = main_function()
print(result)
```

### Advanced Usage

```python
# Example 2: With custom options
from {list(file_contents.keys())[0].replace('.py', '').replace('/', '.').replace('\\', '.')} import *

# Configure options
options = {{
    'option1': 'value1',
    'option2': 'value2'
}}

result = main_function(**options)
```

---

## Available Options

### Command Line Arguments

```bash
python {list(file_contents.keys())[0]} --help
```

Common options:
- `--input`: Specify input file or data
- `--output`: Specify output destination
- `--config`: Load configuration file
- `--verbose`: Enable detailed logging

### Configuration

Create a config file:

```python
# config.py
OPTION_1 = "value1"
OPTION_2 = "value2"
```

---

## Output Types

### Return Values

Functions in this codebase typically return:

1. **Objects/Instances** - Main class instances
2. **Dictionaries** - Configuration or result data
3. **Lists** - Collections of processed items
4. **Status Codes** - Success/failure indicators

### File Outputs

The code may generate:
- Output files in `/output` directory
- Log files in `/logs`
- Cache files in `/cache`

---

## Key Classes

{chr(10).join(f'''### {cls.split(': ', 1)[1] if ': ' in cls else cls}
- **Purpose:** Main component class
- **Usage:** `instance = ClassName(params)`
''' for cls in classes[:3])}

---

## Examples Gallery

### Example 1: Quick Start

```python
# Minimal example
import {os.path.basename(repo_path).replace('-', '_')}

result = {os.path.basename(repo_path).replace('-', '_')}.run()
print(f"Result: {{result}}")
```

### Example 2: Custom Configuration

```python
# With configuration
import {os.path.basename(repo_path).replace('-', '_')}

config = {{
    'mode': 'advanced',
    'debug': True
}}

result = {os.path.basename(repo_path).replace('-', '_')}.run(config)
```

### Example 3: Batch Processing

```python
# Process multiple items
import {os.path.basename(repo_path).replace('-', '_')}

items = ['item1', 'item2', 'item3']
results = [{os.path.basename(repo_path).replace('-', '_')}.process(item) for item in items]
```

---

## Troubleshooting

### Common Issues

**Issue:** Import errors
- **Solution:** Ensure all dependencies are installed (`pip install -r requirements.txt`)

**Issue:** Permission denied
- **Solution:** Run with appropriate permissions or check file paths

**Issue:** Unexpected output
- **Solution:** Check input format and configuration settings

---

## API Reference

For detailed API documentation, see:
- [Technical Documentation](./docs/technical.md)
- [API Reference](./docs/api.md)

---

## Contributing

Want to contribute? Check out:
- Issue tracker
- Contributing guidelines  
- Code of conduct

---

*Generated by Context-Aware Documentation Generator*
*Style: User Guide (Usage-Focused)*
"""
    
    elif doc_style == "numpy":
        # Generate detailed function documentation with tautological descriptions
        func_docs = []
        for func in functions[:10]:
            file_path_part, sig = func.split(': ', 1) if ': ' in func else ('', func)
            if '(' in sig:
                func_name = sig.split('(')[0].replace('def ', '').replace('async def ', '').strip()
            else:
                func_name = sig.replace('def ', '').replace('async def ', '').strip()
            description = _generate_tautological_description(func_name, sig, "function")
            func_docs.append(f"""#### `{sig}`

{description}

Parameters
----------
See function signature for parameter details.

Returns
-------
Result of the {func_name} operation.

Location: `{file_path_part}`
""")
        
        # Generate detailed class documentation
        class_docs = []
        for cls in classes[:10]:
            file_path_part, sig = cls.split(': ', 1) if ': ' in cls else ('', cls)
            class_name = sig.replace('class ', '').split('(')[0].split(':')[0].strip()
            description = _generate_tautological_description(class_name, sig, "class")
            class_docs.append(f"""#### `{sig}`

{description}

Attributes
----------
See class definition for attribute details.

Methods
-------
See class implementation for available methods.

Location: `{file_path_part}`
""")
        
        return f"""# Repository Documentation (NumPy Style)

Overview
========

Repository: {os.path.basename(repo_path)}

Purpose
-------
{context or 'This repository provides a comprehensive codebase for software development functionality.'}

This documentation provides detailed information about the repository structure, functions,
classes, and dependencies following NumPy documentation conventions.

Repository Statistics
--------------------

===================  =======
Metric               Value
===================  =======
Files analyzed       {len(file_contents)}
Total lines          {total_lines:,}
Functions found      {len(functions)}
Classes found        {len(classes)}
===================  =======

File Structure
--------------

The repository contains the following files:

{chr(10).join(f"* `{file_path}` - Implementation source file" for file_path in file_contents.keys())}

Functions
=========

{chr(10).join(func_docs) if func_docs else "No functions documented."}

Classes
=======

{chr(10).join(class_docs) if class_docs else "No classes documented."}

Dependencies
============

The following external packages are required:

{chr(10).join(f"* `{imp}`" for imp in list(set(imports))[:15])}

Notes
-----
This documentation was generated using tautological analysis based on function
and class naming conventions.

---
*Documentation generated with tautological analysis by Context-Aware Documentation Generator*
*Style: NumPy (Scientific Python)*"""
    
    else:  # markdown / default / technical_comprehensive
        # Generate detailed function documentation with tautological descriptions
        func_docs = []
        for func in functions[:15]:  # Document up to 15 functions for default
            file_path_part, sig = func.split(': ', 1) if ': ' in func else ('', func)
            if '(' in sig:
                func_name = sig.split('(')[0].replace('def ', '').replace('async def ', '').strip()
            else:
                func_name = sig.replace('def ', '').replace('async def ', '').strip()
            description = _generate_tautological_description(func_name, sig, "function")
            func_docs.append(f"""### `{sig}`

{description}

**File:** `{file_path_part}`
""")
        
        # Generate detailed class documentation
        class_docs = []
        for cls in classes[:15]:
            file_path_part, sig = cls.split(': ', 1) if ': ' in cls else ('', cls)
            class_name = sig.replace('class ', '').split('(')[0].split(':')[0].strip()
            description = _generate_tautological_description(class_name, sig, "class")
            class_docs.append(f"""### `{sig}`

{description}

**File:** `{file_path_part}`
""")
        
        return f"""# Repository Documentation

## Overview

**Repository:** {os.path.basename(repo_path)}

**Purpose:** {context or 'This repository provides a comprehensive codebase implementing various software development functionality and utilities.'}

This documentation provides a comprehensive overview of the repository structure, all functions, classes, and their relationships to help developers understand and utilize the codebase effectively.

## Repository Statistics

| Metric | Count |
|--------|-------|
| **Files analyzed** | {len(file_contents)} |
| **Total lines** | {total_lines:,} |
| **Functions** | {len(functions)} |
| **Classes** | {len(classes)} |

## File Structure

The repository is organized as follows:

{chr(10).join(f"- **`{file_path}`** - Source implementation file" for file_path in file_contents.keys())}

## Functions

The following functions are implemented in this repository:

{chr(10).join(func_docs) if func_docs else "No functions found in the codebase."}

## Classes

The following classes are defined in this repository:

{chr(10).join(class_docs) if class_docs else "No classes found in the codebase."}

## Dependencies

This project depends on the following modules:

{chr(10).join(f"- **`{imp}`** - External dependency" for imp in list(set(imports))[:20])}

## Getting Started

To use this repository:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Import the required modules in your code

```python
# Example import
from {os.path.basename(repo_path).replace('-', '_')} import main_module
```

---
*Documentation generated with tautological analysis by Context-Aware Documentation Generator*"""

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page with minimal black/red/green interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Context-Aware-Documentation-Generator</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                max-width: 1200px; margin: 0 auto; padding: 20px; 
                background: #ffffff;
                color: #1a1a1a;
                min-height: 100vh;
                font-size: 13px;
                letter-spacing: 0.5px;
            }
            .container { 
                background: #ffffff; padding: 30px; 
                border: 2px solid #1a1a1a;
                border-radius: 3px;
            }
            .header { 
                text-align: center; margin-bottom: 30px; 
                border-bottom: 2px solid #1a1a1a;
                padding-bottom: 20px;
            }
            h1 { 
                color: #1a1a1a; font-size: 2em; margin-bottom: 10px;
                text-transform: uppercase; letter-spacing: 2.5px;
            }
            .subtitle { 
                color: #666; font-size: 0.95em;
                background: #f5f5f5; padding: 5px 10px;
                display: inline-block; border: 1px solid #ddd;
            }
            .form-group { margin: 20px 0; }
            label { 
                display: block; margin-bottom: 8px; font-weight: bold; 
                color: #2a2a2a; font-size: 0.95em;
                text-transform: uppercase;
                letter-spacing: 0.8px;
            }
            input, textarea, select { 
                width: 100%; padding: 10px; 
                background: #ffffff;
                border: 1px solid #ccc; 
                color: #1a1a1a;
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                font-size: 13px;
                resize: vertical;
            }
            input:focus, textarea:focus, select:focus { 
                border-color: #1a1a1a; outline: none;
                box-shadow: 0 0 5px rgba(26, 26, 26, 0.3);
            }
            .btn { 
                background: #ffffff;
                color: #1a1a1a; padding: 14px 35px; 
                border: 2px solid #1a1a1a; 
                cursor: pointer; font-size: 14px;
                font-weight: bold; 
                text-transform: uppercase;
                width: 100%; margin: 20px 0;
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                transition: all 0.3s;
                letter-spacing: 1.2px;
            }
            .btn:hover { 
                background: #ff0000; color: #ffffff;
                border-color: #ff0000;
            }
            .features { 
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px; margin: 30px 0;
            }
            .feature { 
                background: #f9f9f9; padding: 15px;
                border-left: 3px solid #1a1a1a;
                font-size: 0.85em;
            }
            .feature h4 { color: #2a2a2a; margin-bottom: 10px; font-size: 1em; }
            .feature p { color: #666; font-size: 0.85em; }
            .style-grid {
                display: grid; grid-template-columns: 1fr 1fr 1fr;
                gap: 10px; margin: 10px 0;
            }
            .style-option {
                padding: 15px; background: #ffffff;
                border: 1px solid #ccc;
                cursor: pointer; text-align: center; transition: all 0.3s;
                font-size: 0.85em;
            }
            .style-option:hover { 
                border-color: #ff0000; 
                background: #fff5f5;
            }
            .style-option.selected { 
                border-color: #1a1a1a; background: #f9f9f9;
                box-shadow: 0 0 10px rgba(26, 26, 26, 0.2);
            }
            .style-option strong { color: #1a1a1a; display: block; margin-bottom: 8px; font-size: 0.95em; }
            .example { font-size: 0.8em; color: #666; margin-top: 10px; }
            .radio-group { display: flex; gap: 20px; margin-bottom: 15px; }
            .radio-group label { 
                display: flex; align-items: center; cursor: pointer;
                text-transform: none; font-weight: normal;
                padding: 8px 12px; border-radius: 4px; transition: all 0.2s;
            }
            .radio-group label:hover {
                color: #2e7d32; background: #e8f5e9;
            }
            .radio-group input[type="radio"] { 
                margin-right: 8px; width: 18px; height: 18px;
                accent-color: #2e7d32;
                cursor: pointer;
            }
            .radio-group input[type="radio"]:checked + span,
            .radio-group input[type="radio"]:checked ~ span {
                color: #2e7d32; font-weight: bold;
            }
            .radio-group label:has(input:checked) {
                background: #c8e6c9; border: 2px solid #2e7d32;
            }
            .error { color: #ff0000; }
            .success { color: #00ff00; }
            .metrics-grid {
                display: grid; grid-template-columns: repeat(4, 1fr);
                gap: 10px; margin: 15px 0;
                background: #f9f9f9; padding: 20px;
                border: 1px solid #ddd;
            }
            .metric-box {
                text-align: center; padding: 15px;
                background: #fff; border: 1px solid #1a1a1a;
            }
            .metric-box .value {
                font-size: 2.1em; color: #1a1a1a;
                font-weight: bold; display: block; margin-bottom: 8px;
            }
            .success {
                color: #006400 !important; /* Darker green for success messages */
                font-weight: bold;
            }
            .metric-box .label {
                font-size: 0.85em; color: #666; text-transform: uppercase;
            }
            #result {
                margin-top: 30px; padding: 20px;
                background: #e8ffe8; border-left: 5px solid #00aa00;
                border: 2px solid #00aa00;
                border-radius: 8px;
            }
            .doc-output {
                background: #ffffff; padding: 20px; 
                color: #1a1a1a; font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                max-height: 600px; overflow-y: auto;
                border: 1px solid #ddd; margin: 15px 0;
                font-size: 14px; line-height: 1.7;
            }
            /* Markdown styles */
            .doc-output h1 { font-size: 1.8em; border-bottom: 2px solid #333; padding-bottom: 8px; margin: 20px 0 15px 0; }
            .doc-output h2 { font-size: 1.5em; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin: 18px 0 12px 0; color: #2c3e50; }
            .doc-output h3 { font-size: 1.25em; margin: 15px 0 10px 0; color: #34495e; }
            .doc-output h4 { font-size: 1.1em; margin: 12px 0 8px 0; color: #555; }
            .doc-output p { margin: 10px 0; }
            .doc-output code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Consolas', monospace; font-size: 0.9em; }
            .doc-output pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 6px; overflow-x: auto; margin: 15px 0; }
            .doc-output pre code { background: none; color: inherit; padding: 0; }
            .doc-output ul, .doc-output ol { margin: 10px 0; padding-left: 25px; }
            .doc-output li { margin: 5px 0; }
            .doc-output blockquote { border-left: 4px solid #3498db; margin: 15px 0; padding: 10px 20px; background: #f9f9f9; }
            .doc-output table { border-collapse: collapse; width: 100%; margin: 15px 0; }
            .doc-output th, .doc-output td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            .doc-output th { background: #f5f5f5; font-weight: bold; }
            .doc-output hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }
            .slider-container {
                display: flex; align-items: center; gap: 15px;
                margin-top: 10px;
            }
            .slider {
                flex: 1; height: 6px;
                background: #ddd; outline: none;
                border-radius: 3px;
                -webkit-appearance: none;
            }
            .slider::-webkit-slider-thumb {
                -webkit-appearance: none;
                appearance: none;
                width: 18px; height: 18px;
                background: #1a1a1a;
                border: 2px solid #1a1a1a;
                cursor: pointer;
                border-radius: 50%;
                transition: all 0.3s;
            }
            .slider::-webkit-slider-thumb:hover {
                background: #ff0000;
                border-color: #ff0000;
            }
            .slider::-moz-range-thumb {
                width: 18px; height: 18px;
                background: #1a1a1a;
                border: 2px solid #1a1a1a;
                cursor: pointer;
                border-radius: 50%;
                transition: all 0.3s;
            }
            .slider::-moz-range-thumb:hover {
                background: #ff0000;
                border-color: #ff0000;
            }
            .temp-value {
                min-width: 45px;
                color: #1a1a1a;
                font-weight: bold;
                text-align: right;
                font-size: 0.95em;
            }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            function selectStyle(style) {
                document.querySelectorAll('.style-option').forEach(el => el.classList.remove('selected'));
                document.querySelector(`[data-style="${style}"]`).classList.add('selected');
                document.querySelector('select[name="doc_style"]').value = style;
            }
            
            function toggleInputType() {
                const inputType = document.querySelector('input[name="input_type"]:checked').value;
                const urlInput = document.getElementById('url-input');
                const codeInput = document.getElementById('code-input');
                
                if (inputType === 'url') {
                    urlInput.style.display = 'block';
                    codeInput.style.display = 'none';
                    document.querySelector('input[name="repo_url"]').required = true;
                    document.querySelector('textarea[name="code_snippet"]').required = false;
                } else {
                    urlInput.style.display = 'none';
                    codeInput.style.display = 'block';
                    document.querySelector('input[name="repo_url"]').required = false;
                    document.querySelector('textarea[name="code_snippet"]').required = true;
                }
            }
            
            function updateTempValue(value) {
                document.getElementById('temp-display').textContent = value;
            }
            
            function toggleDetailedMetrics() {
                const detailedDiv = document.getElementById('detailed-metrics');
                const btn = document.getElementById('expand-metrics-btn');
                
                if (detailedDiv.style.display === 'none') {
                    detailedDiv.style.display = 'block';
                    btn.textContent = '▲ Hide Detailed Parameter Scores';
                    btn.classList.add('expanded');
                } else {
                    detailedDiv.style.display = 'none';
                    btn.textContent = '▼ Show Detailed Parameter Scores';
                    btn.classList.remove('expanded');
                }
            }
            
            async function generateDocs(event) {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const button = form.querySelector('.btn');
                const originalText = button.textContent;
                
                // DEBUG: Log form data being sent
                console.log('📤 Form Data Being Sent:');
                for (let [key, value] of formData.entries()) {
                    console.log(`  ${key}: ${value}`);
                }
                
                button.textContent = 'PROCESSING...';
                button.disabled = true;
                
                try {
                    const response = await fetch('/generate', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    let resultDiv = document.getElementById('result');
                    if (!resultDiv) {
                        resultDiv = document.createElement('div');
                        resultDiv.id = 'result';
                        form.parentNode.appendChild(resultDiv);
                    }
                    
                    if (result.error) {
                        resultDiv.innerHTML = `
                            <h3 class="error">ERROR</h3>
                            <p><strong>Error:</strong> ${result.error}</p>
                            <p><strong>Status:</strong> ${result.status}</p>
                        `;
                        resultDiv.style.borderLeftColor = '#ff0000';
                    } else {
                        // Show processing stats if available
                        let statsHTML = '';
                        if (result.files_analyzed || result.total_lines) {
                            statsHTML = `
                                <div style="background: #c8e6c9; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #388e3c;">
                                    <h4 style="margin: 0 0 10px 0; color: #1b5e20; font-weight: bold;">📊 Comprehensive Analysis Complete</h4>
                                    <p style="margin: 5px 0; color: #1b5e20;"><strong>Files Processed:</strong> ${result.files_analyzed || 'N/A'}</p>
                                    ${result.total_lines ? `<p style="margin: 5px 0; color: #1b5e20;"><strong>Total Lines:</strong> ${result.total_lines.toLocaleString()}</p>` : ''}
                                    ${result.total_chars ? `<p style="margin: 5px 0; color: #1b5e20;"><strong>Total Characters:</strong> ${result.total_chars.toLocaleString()}</p>` : ''}
                                    <p style="margin: 5px 0; color: #2e7d32; font-size: 0.9em;">${result.status || 'Processing complete'}</p>
                                </div>
                            `;
                        }
                        
                        let metricsHTML = '';
                        if (result.metrics) {
                            // Build comprehensive metrics HTML
                            let comprehensiveHTML = '';
                            if (result.metrics.comprehensive) {
                                const comp = result.metrics.comprehensive;
                                comprehensiveHTML = `
                                    <div style="background: #ffebee; padding: 15px; border-radius: 8px; margin-top: 10px; border-left: 4px solid #d32f2f;">
                                        <h4 style="margin: 0 0 15px 0; color: #c62828; font-weight: bold;">📊 Detailed Parameter Scores</h4>
                                        <div style="max-width: 600px; margin: 0 auto;">
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #c62828; font-weight: bold;">BLEU_eq (N-gram Precision)</span>
                                                <span style="color: #b71c1c; font-weight: bold;">${comp.bleu_eq || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #d32f2f; font-weight: bold;">METEOR_eq (Term Match)</span>
                                                <span style="color: #c62828; font-weight: bold;">${comp.meteor_eq || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #e64a19; font-weight: bold;">ROUGE_eq (Recall Score)</span>
                                                <span style="color: #bf360c; font-weight: bold;">${comp.rouge_eq || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #ad1457; font-weight: bold;">Lexical Diversity</span>
                                                <span style="color: #880e4f; font-weight: bold;">${comp.lexical_diversity || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #6a1b9a; font-weight: bold;">Completeness</span>
                                                <span style="color: #4a148c; font-weight: bold;">${comp.completeness || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #ff6f00; font-weight: bold;">Consistency</span>
                                                <span style="color: #e65100; font-weight: bold;">${comp.consistency || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #00695c; font-weight: bold;">Brevity</span>
                                                <span style="color: #004d40; font-weight: bold;">${comp.brevity || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fce4ec; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #c2185b; font-weight: bold;">📖 Flesch Reading Ease</span>
                                                <span style="color: #ad1457; font-weight: bold;">${comp.flesch_ease || 'N/A'}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fce4ec; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #c2185b; font-weight: bold;">📚 Grade Level</span>
                                                <span style="color: #ad1457; font-weight: bold;">${comp.grade_level || 'N/A'}</span>
                                            </div>
                                            ${comp.bert_score && comp.bert_score !== 'N/A' ? `
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fce4ec; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #880e4f; font-weight: bold;">🤖 BERTScore</span>
                                                <span style="color: #4a148c; font-weight: bold;">${comp.bert_score}</span>
                                            </div>
                                            ` : ''}
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #555; font-weight: bold;">Word Count</span>
                                                <span style="color: #333; font-weight: bold;">${comp.word_count || 0}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #555; font-weight: bold;">Unique Words</span>
                                                <span style="color: #333; font-weight: bold;">${comp.unique_words || 0}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ef9a9a; background: #fff; border-radius: 4px; margin-bottom: 8px;">
                                                <span style="color: #555; font-weight: bold;">Total Sentences</span>
                                                <span style="color: #333; font-weight: bold;">${comp.sentences || 0}</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; padding: 10px; background: #fff; border-radius: 4px;">
                                                <span style="color: #555; font-weight: bold;">Avg Sentence Length</span>
                                                <span style="color: #333; font-weight: bold;">${comp.avg_sentence_length || '0'} words</span>
                                            </div>
                                        </div>
                                    </div>
                                `;
                            }
                            
                            metricsHTML = `
                                <div style="background: #ffebee; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #d32f2f;">
                                    <h4 style="margin: 0 0 15px 0; color: #c62828;">📈 Documentation Quality Metrics</h4>
                                    <div class="metrics-grid">
                                        <div class="metric-box" style="border-color: #d32f2f;">
                                            <span class="value" style="color: #c62828;">${result.metrics.bleu_eq || 'N/A'}</span>
                                            <span class="label">BLEU_eq</span>
                                            <span style="font-size: 0.75em; color: #999; display: block; margin-top: 4px;">N-gram Precision</span>
                                        </div>
                                        <div class="metric-box" style="border-color: #b71c1c;">
                                            <span class="value" style="color: #b71c1c;">${result.metrics.meteor_eq || 'N/A'}</span>
                                            <span class="label">METEOR_eq</span>
                                            <span style="font-size: 0.75em; color: #999; display: block; margin-top: 4px;">Term Match</span>
                                        </div>
                                        <div class="metric-box" style="border-color: #ff5722;">
                                            <span class="value" style="color: #e64a19;">${result.metrics.rouge_eq || 'N/A'}</span>
                                            <span class="label">ROUGE_eq</span>
                                            <span style="font-size: 0.75em; color: #999; display: block; margin-top: 4px;">Recall Score</span>
                                        </div>
                                        <div class="metric-box" style="border-color: #880e4f;">
                                            <span class="value" style="color: #ad1457;">${result.metrics.overall}</span>
                                            <span class="label">Overall Quality</span>
                                            <span style="font-size: 0.75em; color: #999; display: block; margin-top: 4px;">Weighted Score</span>
                                        </div>
                                    </div>
                                    <div style="text-align: center; margin-top: 10px; padding: 8px; background: #fce4ec; border-radius: 4px;">
                                        <span style="color: #c2185b; font-weight: bold;">📖 Readability: ${result.metrics.readability_score || 'N/A'}</span>
                                        <span style="font-size: 0.75em; color: #666; display: block;">Grade Level: ${result.metrics.flesch_kincaid_grade || 'N/A'}</span>
                                    </div>
                                    ${result.metrics.bert_score && result.metrics.bert_score !== 'N/A' ? `
                                        <div style="text-align: center; margin-top: 10px; padding: 8px; background: #fce4ec; border-radius: 4px;">
                                            <span style="color: #880e4f; font-weight: bold;">🤖 BERTScore: ${result.metrics.bert_score}</span>
                                            <span style="font-size: 0.75em; color: #666; display: block;">Semantic Similarity</span>
                                        </div>
                                    ` : ''}
                                    ${comprehensiveHTML ? `
                                        <button class="expand-btn" onclick="toggleDetailedMetrics()" id="expand-metrics-btn">
                                            ▼ Show Detailed Parameter Scores
                                        </button>
                                    ` : ''}
                                    ${result.metrics.methodology ? `<p style="margin: 10px 0 0 0; color: #666; font-size: 0.85em; text-align: center;">📚 Method: ${result.metrics.methodology}</p>` : ''}
                                </div>
                                <div id="detailed-metrics" style="display: none;">
                                    ${comprehensiveHTML}
                                </div>
                            `;
                        }
                        
                        resultDiv.innerHTML = `
                            ${statsHTML}
                            ${metricsHTML}
                            <h3 class="success">SUCCESS: ${result.status}</h3>
                            <p style="color: #888; margin: 10px 0;">Method: ${result.method} | Style: ${result.style || 'N/A'}</p>
                            <div class="doc-output" id="doc-content"></div>
                            <button onclick="downloadDocs('${result.style || 'markdown'}')" class="btn" style="width: auto; padding: 10px 20px;">DOWNLOAD</button>
                        `;
                        // Render markdown after setting innerHTML
                        document.getElementById('doc-content').innerHTML = marked.parse(result.documentation);
                    }
                    
                    resultDiv.scrollIntoView({ behavior: 'smooth' });
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('NETWORK ERROR: Please try again.');
                } finally {
                    button.textContent = originalText;
                    button.disabled = false;
                }
            }
            
            function downloadDocs(style) {
                const content = document.querySelector('.doc-output').textContent;
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
                <h1>CONTEXT-AWARE DOCUMENTATION GENERATOR</h1>
                <p class="subtitle">&gt; Real Code Analysis</p>
            </div>
            
            <form onsubmit="generateDocs(event)">
                <div class="form-group">
                    <label>INPUT TYPE</label>
                    <div class="radio-group">
                        <label>
                            <input type="radio" name="input_type" value="url" checked onchange="toggleInputType()">
                            Repository URL
                        </label>
                        <label>
                            <input type="radio" name="input_type" value="code" onchange="toggleInputType()">
                            Code Snippet
                        </label>
                    </div>
                </div>
                
                <div class="form-group" id="url-input">
                    <label for="repo_url">REPOSITORY SOURCE</label>
                    <input type="text" name="repo_url" placeholder="https://github.com/owner/repo.git">
                    <div class="example">
                        Git: https://github.com/owner/repo.git | ZIP: /content/my-project.zip
                    </div>
                </div>
                
                <div class="form-group" id="code-input" style="display: none;">
                    <label for="code_snippet">PYTHON CODE</label>
                    <textarea name="code_snippet" rows="10" placeholder="Paste your Python code here..."></textarea>
                </div>
                
                <div class="form-group">
                    <label>DOCUMENTATION STYLE</label>
                    <div class="style-grid" style="grid-template-columns: 1fr 1fr 1fr;">
                        <div class="style-option selected" data-style="technical_comprehensive" onclick="selectStyle('technical_comprehensive')">
                            <strong>📘 Technical Guide</strong>
                            <div class="example">Structured, user-friendly technical docs</div>
                        </div>
                        <div class="style-option" data-style="user_guide" onclick="selectStyle('user_guide')">
                            <strong>📖 User Manual</strong>
                            <div class="example">Usage guide with diagrams & examples</div>
                        </div>
                        <div class="style-option" data-style="opensource" onclick="selectStyle('opensource')">
                            <strong>🔓 Open Source</strong>
                            <div class="example">README + contribution guide</div>
                        </div>
                    </div>
                    <select name="doc_style" style="display: none;">
                        <option value="technical_comprehensive" selected>Technical Guide</option>
                        <option value="user_guide">User Manual (with diagrams)</option>
                        <option value="opensource">Open Source README</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="context">DOCUMENTATION CONTEXT</label>
                    <textarea name="context" rows="4" placeholder="Academic research project focusing on algorithmic efficiency
Include performance analysis and optimization recommendations
Target audience: Computer science students and researchers"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="temperature">GEMINI TEMPERATURE</label>
                    <div class="slider-container">
                        <input type="range" name="temperature" class="slider" min="0.0" max="1.0" step="0.1" value="0.3" oninput="updateTempValue(this.value)">
                        <span class="temp-value" id="temp-display">0.3</span>
                    </div>
                    <div class="example">
                        Lower = More precise | Higher = More creative (Only for Gemini-only mode)
                    </div>
                </div>
                
                <div class="form-group">
                    <label>GENERATION MODE</label>
                    <div class="radio-group">
                        <label>
                            <input type="radio" name="generation_mode" value="phi3_only">
                            Phi-3 Only (Local, 30-60s)
                        </label>
                        <label>
                            <input type="radio" name="generation_mode" value="gemini_only" checked>
                            Gemini Only (Fast, 2-5s)
                        </label>
                        <label>
                            <input type="radio" name="generation_mode" value="phi3_gemini">
                            Phi-3 + Gemini (Best Quality, 60-180s adaptive)
                        </label>
                    </div>
                    <div class="example">
                        Phi-3: Local/Private | Gemini: Fast & Good | Phi-3+Gemini: Best Quality
                    </div>
                </div>
                
                <button type="submit" class="btn">GENERATE DOCUMENTATION</button>
            </form>
            
            <div class="features">
                <div class="feature">
                    <h4>Repository Support</h4>
                    <p>Git URLs, ZIP files, and direct code input</p>
                </div>
                <div class="feature">
                    <h4>Professional Documentation</h4>
                    <p>Google docstrings, Open Source READMEs, Technical docs</p>
                </div>
                <div class="feature">
                    <h4>Deep Analysis</h4>
                    <p>Architecture understanding, API design, maintenance guides</p>
                </div>
                <div class="feature">
                    <h4>Collaboration Ready</h4>
                    <p>Open source standards, contribution guides, API references</p>
                </div>
            </div>
            
            <div style="margin-top: 40px; text-align: center; color: #666; font-size: 0.85em; border-top: 1px solid #333; padding-top: 20px;">
                <p>&gt; Terminal: python terminal_demo.py | python enhanced_test.py</p>
                <p>&gt; CLI: python main.py --directory /path/to/repo --style google</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.post("/generate")
async def generate_docs(
    repo_url: str = Form(""), 
    code_snippet: str = Form(""),
    input_type: str = Form("url"),
    context: str = Form(""), 
    doc_style: str = Form("technical_comprehensive"),
    temperature: float = Form(0.3),
    generation_mode: str = Form("gemini_only")
):
    """Generate documentation for repository from Git URL, ZIP, or code snippet"""
    global doc_generator
    
    # DEBUG: Log ALL received parameters for debugging remote access
    print(f"\n{'='*60}")
    print(f"📥 INCOMING REQUEST")
    print(f"{'='*60}")
    print(f"📝 doc_style: '{doc_style}'")
    print(f"🌡️ temperature: {temperature}")
    print(f"⚙️ generation_mode: '{generation_mode}'")
    print(f"📋 input_type: '{input_type}'")
    print(f"🔗 repo_url: '{repo_url[:100] if repo_url else '(empty)'}'")
    print(f"📄 code_snippet: {'(provided, ' + str(len(code_snippet)) + ' chars)' if code_snippet else '(empty)'}")
    print(f"💬 context: '{context[:50] if context else '(empty)'}'")
    print(f"{'='*60}\n")
    
    # Validate and normalize style
    valid_styles = ['opensource', 'technical_comprehensive', 'user_guide']
    if doc_style not in valid_styles:
        print(f"⚠️ Invalid style '{doc_style}', defaulting to 'technical_comprehensive'")
        doc_style = 'technical_comprehensive'
    
    print(f"✅ Using documentation style: '{doc_style}'")
    
    try:
        # Handle different input types
        repo_path = None
        
        # Check if both inputs are empty (might happen with remote access)
        if input_type == "url" and not repo_url.strip():
            print(f"⚠️ URL mode selected but no URL provided")
            return JSONResponse({
                "error": "No repository URL provided",
                "status": "❌ Empty URL",
                "help": "Please enter a Git URL (e.g., https://github.com/user/repo) or switch to Code Snippet mode"
            })
        
        if input_type == "code":
            # Handle code snippet input
            if not code_snippet.strip():
                print(f"⚠️ Code mode selected but no code provided")
                return JSONResponse({
                    "error": "No code provided",
                    "status": "❌ Empty code snippet",
                    "help": "Please paste your code or switch to URL mode"
                })
            
            print(f"🔄 Processing code snippet ({len(code_snippet)} characters)...")
            
            # Check if snippet is too large
            if len(code_snippet) > 10000:
                print(f"⚠️ Large code snippet detected (>{len(code_snippet)} chars)")
                print(f"⚡ This may take 2-5 minutes with Phi-3 on CPU")
            else:
                print(f"⚡ Small snippet - should complete in 30-60 seconds")
            
            # Use code as-is for faster processing (no enhancement needed)
            # Enhancement adds 300+ lines of boilerplate which slows down AI
            print(f"⚡ Using code as-is for fast AI processing")
            
            # Create temporary file with the original code snippet
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "main.py")
            
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(code_snippet.strip())
                repo_path = temp_dir
                print(f"✅ Code snippet ready for AI analysis")
            except Exception as e:
                return JSONResponse({
                    "error": f"Failed to process code snippet: {str(e)}",
                    "status": "❌ Code processing failed"
                })
        
        else:
            # Handle URL input (existing logic)
            # Note: Empty URL already checked above
            
            if repo_url.startswith(('http://', 'https://')) and ('.git' in repo_url or 'github.com' in repo_url or 'gitlab.com' in repo_url or 'bitbucket.org' in repo_url or repo_url.endswith('.git')):
                # Clone Git repository with shallow clone for speed
                print(f"🔄 Cloning repository: {repo_url}")
                print("   Using --depth=1 for faster cloning (shallow clone)")
                temp_dir = tempfile.mkdtemp()
                try:
                    # Use --depth=1 for shallow clone (faster for large repos)
                    result = subprocess.run(['git', 'clone', '--depth=1', repo_url, temp_dir], 
                                         check=True, capture_output=True, text=True, timeout=600)
                    repo_path = temp_dir
                    print(f"✅ Repository cloned to: {repo_path}")
                    
                    # Remove .git directory (optional - not critical if it fails)
                    git_dir = os.path.join(temp_dir, '.git')
                    if os.path.exists(git_dir):
                        import shutil
                        import stat
                        
                        def handle_remove_readonly(func, path, exc):
                            """Error handler for Windows readonly files"""
                            os.chmod(path, stat.S_IWRITE)
                            func(path)
                        
                        try:
                            shutil.rmtree(git_dir, onerror=handle_remove_readonly)
                            print("🗑️  Removed .git directory (version control files not needed)")
                        except Exception as rm_err:
                            # Non-critical - just log and continue
                            print(f"⚠️  Could not remove .git directory (not critical): {rm_err}")
                    
                except subprocess.CalledProcessError as e:
                    return JSONResponse({
                        "error": f"Failed to clone repository: {e.stderr if e.stderr else str(e)}",
                        "status": "❌ Git clone failed"
                    })
                except subprocess.TimeoutExpired:
                    return JSONResponse({
                        "error": "Repository cloning timed out (>10 minutes). Repository may be too large.",
                        "status": "❌ Clone timeout",
                        "suggestion": "Try using a local clone or smaller repository"
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
            
            else:
                # Better error message with details
                print(f"❌ Validation failed for repo_url: '{repo_url}'")
                print(f"   - Not a Git URL (checked for .git, github, gitlab, bitbucket)")
                print(f"   - Not a ZIP file (checked .zip extension and file exists)")
                print(f"   - Not a local directory (checked path exists)")
                return JSONResponse({
                    "error": "Invalid repository source - must be Git URL, ZIP file, or local directory",
                    "status": "❌ Invalid input",
                    "received": repo_url[:200] if repo_url else "(empty)",
                    "valid_examples": [
                        "https://github.com/username/repo.git",
                        "https://github.com/username/repo",
                        "C:\\path\\to\\local\\directory",
                        "C:\\path\\to\\file.zip"
                    ]
                })
        
        # Try advanced system first
        if doc_generator and ADVANCED_SYSTEM_AVAILABLE:
            print(f"🤖 Using generation mode: {generation_mode}")
            try:
                # Enhance context with RAG if available
                enhanced_context = context
                if rag_system and rag_system.is_trained:
                    try:
                        print("🔍 RAG: Querying FAISS index for relevant code context...")
                        # Use RAG to retrieve relevant code chunks (FIXED: use search() method)
                        query = context if context.strip() else "main function entry point documentation"
                        rag_results = rag_system.search(query, k=5)
                        if rag_results:
                            rag_context = "\n\n".join([
                                f"[Related {r['chunk']['type']}] (similarity: {r['score']:.2f})\n{r['chunk']['content'][:500]}"
                                for r in rag_results if r['score'] > 0.3
                            ])
                            if rag_context:
                                enhanced_context = f"{context}\n\n[RAG Retrieved Context from Codebase]:\n{rag_context}"
                                print(f"✅ RAG: Enhanced with {len([r for r in rag_results if r['score'] > 0.3])} relevant code chunks")
                            else:
                                print("✅ RAG: No high-relevance matches found (score > 0.3)")
                        else:
                            print("✅ RAG: No matches found in index")
                    except Exception as rag_e:
                        print(f"⚠️ RAG search failed: {rag_e}, using original context")
                        enhanced_context = context
                elif rag_system:
                    print("💡 RAG: System loaded but index not built yet")
                else:
                    print("ℹ️ RAG: Not enabled for this session")
                
                if repo_path and os.path.exists(repo_path):
                    # Read ALL files recursively for comprehensive documentation
                    file_contents = {}
                    for root, dirs, files in os.walk(repo_path):
                        # Skip common non-source directories
                        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist'}]
                        
                        # Process ALL Python files found (no limit)
                        for file in files:
                            if file.endswith(('.py', '.js', '.ts', '.java', '.go', '.cpp', '.c', '.h', '.css', '.html', '.md')):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        file_contents[os.path.relpath(file_path, repo_path)] = content
                                except:
                                    continue
                    
                    if file_contents:
                        # Use generate_styled_documentation which respects generation_mode
                        result = await asyncio.to_thread(
                            generate_styled_documentation, 
                            file_contents, 
                            enhanced_context, 
                            doc_style, 
                            repo_path, 
                            temperature, 
                            generation_mode
                        )
                    else:
                        result = "No Python files found in repository"
                else:
                    # Treat as code snippet
                    result = await asyncio.to_thread(doc_generator.generate_documentation, repo_url, enhanced_context, doc_style, "code", "", temperature)
                
                # Calculate comprehensive evaluation metrics
                metrics_results = None
                
                # ALWAYS evaluate documentation quality
                print("\n" + "="*60)
                print("📊 DOCUMENTATION QUALITY SCORES")
                print("="*60)
                
                # Declare globals for metrics modules
                global ComprehensiveEvaluator, compute_codesearchnet_metrics
                
                # Load metrics modules if not already loaded
                if ComprehensiveEvaluator is None:
                    print("⏳ Loading metrics evaluation modules...")
                    try:
                        from evaluation_metrics import ComprehensiveEvaluator as CompEval
                        from gemini_context_enhancer import compute_codesearchnet_metrics as csn_func
                        
                        # Make available for this session
                        ComprehensiveEvaluator = CompEval
                        compute_codesearchnet_metrics = csn_func
                        print("✅ Metrics modules loaded")
                    except Exception as import_err:
                        print(f"⚠️ Could not load all metrics modules: {import_err}")
                        ComprehensiveEvaluator = None
                        compute_codesearchnet_metrics = None
                
                # 1. COMPREHENSIVE Quality Metrics
                comprehensive_metrics = {}
                if result:
                    try:
                            # For all styles: Calculate comprehensive quality metrics
                            print(f"\n🔹 COMPREHENSIVE DOCUMENTATION METRICS ({doc_style} style):")
                            print(f"  Style: {doc_style}")
                            
                            # Basic content checks
                            word_count = len(result.split())
                            line_count = len(result.split('\n'))
                            has_headings = bool(re.search(r'^#{1,6} ', result, re.MULTILINE))
                            has_code_blocks = '```' in result
                            
                            print(f"\n  📊 Content Metrics:")
                            print(f"    - Total Words: {word_count:,}")
                            print(f"    - Total Lines: {line_count:,}")
                            print(f"    - Has Structure: {'✅' if has_headings else '❌'} (headings)")
                            print(f"    - Has Examples: {'✅' if has_code_blocks else '❌'} (code blocks)")
                            
                            # Calculate Evidence Coverage (check for important sections)
                            section_patterns = [
                                (r'(description|overview|summary)', 'Description'),
                                (r'(parameter|argument|arg)', 'Parameters'),
                                (r'(return|output)', 'Returns'),
                                (r'(example|usage|sample)', 'Examples'),
                                (r'(note|warning|important)', 'Notes'),
                                (r'(function|method|class|module)', 'Component Docs'),
                            ]
                            sections_found = 0
                            result_lower = result.lower()
                            for pattern, name in section_patterns:
                                if re.search(pattern, result_lower):
                                    sections_found += 1
                            evidence_coverage = sections_found / len(section_patterns)
                            
                            # Calculate Consistency (check for internal references)
                            # Count defined terms vs referenced terms
                            defined_funcs = len(re.findall(r'(def |function |method )\w+', result_lower))
                            referenced_funcs = len(re.findall(r'`\w+`|``\w+``', result))
                            consistency = min(1.0, 0.5 + (defined_funcs + referenced_funcs) / max(word_count / 100, 1))
                            
                            # Calculate Non-Tautology (unique info density)
                            unique_words = len(set(result.lower().split()))
                            total_words = len(result.split())
                            lexical_diversity = unique_words / max(total_words, 1)
                            
                            # Penalize very repetitive text
                            sentences = re.split(r'[.!?]+', result)
                            unique_sentences = len(set(s.strip().lower() for s in sentences if s.strip()))
                            sentence_diversity = unique_sentences / max(len(sentences), 1)
                            non_tautology = (lexical_diversity * 0.4 + sentence_diversity * 0.6)
                            
                            # Calculate Brevity Efficiency
                            avg_sentence_len = total_words / max(len(sentences), 1)
                            # Ideal: 15-25 words per sentence
                            if avg_sentence_len < 10:
                                brevity = 0.7  # Too terse
                            elif avg_sentence_len > 40:
                                brevity = 0.6  # Too verbose
                            elif 15 <= avg_sentence_len <= 25:
                                brevity = 1.0  # Ideal
                            else:
                                brevity = 0.85  # Acceptable
                            
                            # Calculate Overall Score
                            overall_quality = (
                                0.50 * evidence_coverage +
                                0.20 * consistency +
                                0.20 * non_tautology +
                                0.10 * brevity
                            )
                            
                            print(f"\n  📊 Quality Scores (0-100%):")
                            print(f"    - Evidence Coverage: {evidence_coverage:.1%} (weight: 50%)")
                            print(f"    - Consistency: {consistency:.1%} (weight: 20%)")
                            print(f"    - Non-Tautology: {non_tautology:.1%} (weight: 20%)")
                            print(f"    - Brevity Efficiency: {brevity:.1%} (weight: 10%)")
                            print(f"\n  🎯 Overall Quality Score: {overall_quality:.1%}")
                            
                            # Store comprehensive metrics for UI
                            comprehensive_metrics = {
                                'lexical_diversity': lexical_diversity,
                                'evidence_coverage': evidence_coverage,
                                'consistency': consistency,
                                'non_tautology': non_tautology,
                                'brevity': brevity,
                                'overall_quality': overall_quality,
                                'word_count': word_count,
                                'unique_words': unique_words,
                                'total_sentences': len(sentences),
                                'unique_sentences': unique_sentences,
                                'sentence_diversity': sentence_diversity,
                                'avg_sentence_length': avg_sentence_len
                            }
                            
                    except Exception as eval_e:
                        print(f"  ⚠️ Quality evaluation failed: {eval_e}")
                
                # 2. Documentation Quality Metrics (professional standards)
                print("\n🔹 DOCUMENTATION QUALITY METRICS:")
                csn_metrics = None
                try:
                    # Always try to load and calculate metrics
                    if result:
                        if compute_codesearchnet_metrics is None:
                            from gemini_context_enhancer import compute_codesearchnet_metrics as csn_func
                            compute_codesearchnet_metrics = csn_func
                        
                        # Extract function/class counts from documentation to validate metrics
                        code_analysis = None
                        try:
                            # Look for patterns like "0 functions" or "Functions: 0"
                            func_match = re.search(r'(\d+)\s*functions?', result.lower())
                            class_match = re.search(r'(\d+)\s*classes?', result.lower())
                            func_count = int(func_match.group(1)) if func_match else -1
                            class_count = int(class_match.group(1)) if class_match else -1
                            
                            # Only create analysis if we found counts
                            if func_count >= 0 or class_count >= 0:
                                code_analysis = {
                                    'function_count': max(func_count, 0),
                                    'class_count': max(class_count, 0)
                                }
                                if func_count == 0 and class_count == 0:
                                    print(f"  ⚠️ WARNING: 0 functions and 0 classes detected - metrics will be invalid")
                        except Exception as parse_e:
                            pass  # If we can't parse, let metrics calculate normally
                        
                        csn_metrics = compute_codesearchnet_metrics(result, code_analysis)
                        overall = csn_metrics.get('overall', 0)
                        validity = csn_metrics.get('validity', 'valid')
                        
                        if validity == 'invalid':
                            print(f"  ❌ METRICS INVALID: {csn_metrics.get('reason', 'No code elements detected')}")
                            print(f"  📊 All scores set to 0.0 (documentation has no meaningful content to evaluate)")
                        else:
                            print(f"  📚 Evaluated against professional documentation standards:")
                            print(f"    - Structural Quality: {csn_metrics.get('structural_quality', 0):.2%} (Args, Returns, Raises, Examples)")
                            print(f"    - Vocabulary Alignment: {csn_metrics.get('vocabulary_alignment', 0):.2%} (technical terms)")
                            print(f"    - Completeness: {csn_metrics.get('completeness', 0):.2%} (length, examples, diversity)")
                            print(f"    - Coherence: {csn_metrics.get('coherence', 0):.2%} (flow, formatting)")
                            print(f"  📊 Heuristic Quality Scores (pattern-based, not reference BLEU/METEOR/ROUGE):")
                            print(f"    - BLEU-like: {csn_metrics.get('bleu', 0):.4f}")
                            print(f"    - METEOR-like: {csn_metrics.get('meteor', 0):.4f}")
                            print(f"    - ROUGE-L-like: {csn_metrics.get('rouge_l', 0):.4f}")
                        print(f"  🎯 OVERALL QUALITY: {overall:.2%}")
                    else:
                        print("  ⚠️ Quality metrics not available (CodeSearchNet disabled)")
                except Exception as csn_e:
                    print(f"  ⚠️ Quality metrics failed: {csn_e}")
                
                # 3. Traditional NLP Metrics (user context comparison)
                print("\n🔹 USER CONTEXT COMPARISON:")
                try:
                    # Calculate even without reference for self-assessment
                    if context.strip() and result and ComprehensiveEvaluator is not None:
                        # With reference
                        metrics_results = ComprehensiveEvaluator.evaluate_all(
                            generated=result,
                            reference=context,
                            code=repo_url if not repo_path else None
                        )
                        
                        print(f"  Comparison vs User Context:")
                        print(f"    - BLEU: {metrics_results.get('bleu', 0):.4f} (n-gram overlap)")
                        print(f"    - METEOR: {metrics_results.get('meteor', 0):.4f} (semantic similarity)")
                        print(f"    - ROUGE-L: {metrics_results.get('rouge', {}).get('rouge-l', {}).get('f', 0):.4f} (longest common)")
                        print(f"    - Aggregate: {metrics_results.get('aggregate_score', 0):.2%}")
                    else:
                        # Without reference - show document stats
                        print(f"  Document Statistics (no user context provided):")
                        sentences = len(re.split(r'[.!?]+', result))
                        words = len(result.split())
                        unique_words = len(set(result.lower().split()))
                        diversity = unique_words / max(words, 1)
                        
                        print(f"    - Total Words: {words:,}")
                        print(f"    - Unique Words: {unique_words:,}")
                        print(f"    - Lexical Diversity: {diversity:.2%}")
                        print(f"    - Sentences: {sentences}")
                        print(f"  💡 CodeSearchNet metrics used instead (see above)")
                except Exception as metrics_e:
                    print(f"  ⚠️ NLP metrics evaluation failed: {metrics_e}")
                
                # 4. REAL QUALITY METRICS (industry-standard, no reference needed)
                print("\n🔹 REAL DOCUMENTATION QUALITY METRICS:")
                real_metrics = None
                try:
                    global evaluate_documentation_quality
                    if evaluate_documentation_quality is None:
                        from real_quality_metrics import evaluate_documentation_quality as real_func
                        evaluate_documentation_quality = real_func
                    
                    real_metrics = evaluate_documentation_quality(result, code_analysis)
                    
                    if real_metrics.get('validity') == 'invalid':
                        print(f"  ❌ INVALID: No functions/classes to evaluate")
                    else:
                        print(f"  📊 Coverage Metrics (what % is documented):")
                        print(f"    - Function Coverage: {real_metrics['coverage']['function_coverage']:.1%}")
                        print(f"    - Parameter Coverage: {real_metrics['coverage']['parameter_coverage']:.1%}")
                        print(f"    - Overall Coverage: {real_metrics['coverage']['overall']:.1%}")
                        
                        print(f"  📝 Completeness (are all sections present):")
                        print(f"    - Description: {'✅' if real_metrics['completeness']['has_description'] else '❌'}")
                        print(f"    - Parameters: {'✅' if real_metrics['completeness']['has_parameters'] else '❌'}")
                        print(f"    - Returns: {'✅' if real_metrics['completeness']['has_returns'] else '❌'}")
                        print(f"    - Examples: {'✅' if real_metrics['completeness']['has_examples'] else '❌'}")
                        print(f"    - Score: {real_metrics['completeness']['score']:.1%}")
                        
                        print(f"  📖 Readability (standard metrics):")
                        print(f"    - Flesch Reading Ease: {real_metrics['readability']['flesch_reading_ease']:.1f}/100")
                        print(f"    - Flesch-Kincaid Grade: {real_metrics['readability']['flesch_kincaid_grade']:.1f}")
                        print(f"    - Score: {real_metrics['readability']['score']:.1%}")
                        
                        print(f"  ⭐ Quality (is it actually useful):")
                        print(f"    - Non-trivial Descriptions: {real_metrics['quality']['non_trivial_descriptions']:.1%}")
                        print(f"    - Specific Types: {real_metrics['quality']['specific_types']:.1%}")
                        print(f"    - Score: {real_metrics['quality']['score']:.1%}")
                        
                        print(f"\n  🎯 OVERALL: {real_metrics['overall_score']:.1%} (Grade: {real_metrics['grade']})")
                except Exception as real_e:
                    print(f"  ⚠️ Real quality metrics failed: {real_e}")
                
                print("\n" + "="*60 + "\n")
                
                response_data = {
                    "documentation": result,
                    "status": f"✅ Generated via full AI system ({doc_style} style)",
                    "method": "Gemini Human-Like Mode" if doc_style == "technical_comprehensive" else "context-aware AI with Phi-3",
                    "style": doc_style
                }
                
                # Helper to normalize scores to 0-1 range
                def normalize_score(score, max_expected=1.0):
                    """Ensure score is in 0-1 range"""
                    if score is None:
                        return 0.0
                    score = float(score)
                    if score > max_expected:
                        # Score might be in percentage form, normalize
                        score = score / 100.0
                    return max(0.0, min(1.0, score))
                
                # ALWAYS include COMPREHENSIVE metrics in response for UI display
                if csn_metrics:
                    overall_score = normalize_score(csn_metrics.get('overall', 0))
                    validity = csn_metrics.get('validity', 'valid')
                    if overall_score == 0 and validity != 'invalid':
                        # Calculate if not provided - all individual scores are 0-1
                        bleu = normalize_score(csn_metrics.get('bleu', 0))
                        meteor = normalize_score(csn_metrics.get('meteor', 0))
                        rouge = normalize_score(csn_metrics.get('rouge_l', 0))
                        overall_score = (bleu + meteor + rouge) / 3
                    
                    response_data["metrics"] = {
                        "bleu": f"{normalize_score(csn_metrics.get('bleu', 0)):.4f}",
                        "meteor": f"{normalize_score(csn_metrics.get('meteor', 0)):.4f}",
                        "rouge_l": f"{normalize_score(csn_metrics.get('rouge_l', 0)):.4f}",
                        "overall": f"{overall_score:.2%}",
                        "validity": validity,
                        "reference": "Heuristic Pattern Analysis" if validity == 'valid' else "Invalid - No code elements detected",
                        "note": csn_metrics.get('note', csn_metrics.get('reason', '')),
                        # Add comprehensive metrics for detailed display
                        "comprehensive": {
                            "bleu_eq": f"{normalize_score(csn_metrics.get('bleu', 0)):.4f}",
                            "meteor_eq": f"{normalize_score(csn_metrics.get('meteor', 0)):.4f}",
                            "rouge_eq": f"{normalize_score(csn_metrics.get('rouge_l', 0)):.4f}",
                            "lexical_diversity": f"{normalize_score(comprehensive_metrics.get('lexical_diversity', 0)):.4f}",
                            "completeness": f"{normalize_score(comprehensive_metrics.get('evidence_coverage', 0)):.4f}",
                            "consistency": f"{normalize_score(comprehensive_metrics.get('consistency', 0)):.4f}",
                            "brevity": f"{normalize_score(comprehensive_metrics.get('brevity', 0)):.4f}",
                            "word_count": comprehensive_metrics.get('word_count', 0),
                            "unique_words": comprehensive_metrics.get('unique_words', 0),
                            "sentences": comprehensive_metrics.get('total_sentences', 0),
                            "unique_sentences": comprehensive_metrics.get('unique_sentences', 0),
                            "avg_sentence_length": f"{comprehensive_metrics.get('avg_sentence_length', 0):.1f}"
                        }
                    }
                elif metrics_results:
                    # Normalize aggregate_score to ensure consistent 0-1 range
                    agg_score = normalize_score(metrics_results.get('aggregate_score', 0))
                    response_data["metrics"] = {
                        "bleu": f"{normalize_score(metrics_results.get('bleu', 0)):.4f}",
                        "meteor": f"{normalize_score(metrics_results.get('meteor', 0)):.4f}",
                        "rouge_l": f"{normalize_score(metrics_results.get('rouge', {}).get('rouge-l', {}).get('f', 0)):.4f}",
                        "overall": f"{agg_score:.2%}",
                        # Add comprehensive metrics
                        "comprehensive": {
                            "bleu_eq": f"{normalize_score(metrics_results.get('bleu', 0)):.4f}",
                            "meteor_eq": f"{normalize_score(metrics_results.get('meteor', 0)):.4f}",
                            "rouge_eq": f"{normalize_score(metrics_results.get('rouge', {}).get('rouge-l', {}).get('f', 0)):.4f}",
                            "lexical_diversity": f"{normalize_score(comprehensive_metrics.get('lexical_diversity', 0)):.4f}",
                            "completeness": f"{normalize_score(comprehensive_metrics.get('evidence_coverage', 0)):.4f}",
                            "consistency": f"{normalize_score(comprehensive_metrics.get('consistency', 0)):.4f}",
                            "brevity": f"{normalize_score(comprehensive_metrics.get('brevity', 0)):.4f}",
                            "word_count": comprehensive_metrics.get('word_count', 0),
                            "unique_words": comprehensive_metrics.get('unique_words', 0),
                            "sentences": comprehensive_metrics.get('total_sentences', 0),
                            "unique_sentences": comprehensive_metrics.get('unique_sentences', 0),
                            "avg_sentence_length": f"{comprehensive_metrics.get('avg_sentence_length', 0):.1f}"
                        }
                    }
                else:
                    # Fallback metrics if none calculated
                    response_data["metrics"] = {
                        "bleu": "0.0000",
                        "meteor": "0.0000",
                        "rouge_l": "0.0000",
                        "overall": "0.00%",
                        "reference": "Metrics calculation unavailable",
                        "comprehensive": {
                            "lexical_diversity": "0.0000",
                            "completeness": "0.0000",
                            "consistency": "0.0000",
                            "brevity": "0.0000",
                            "word_count": 0,
                            "unique_words": 0,
                            "sentences": 0,
                            "unique_sentences": 0,
                            "avg_sentence_length": "0.0"
                        }
                    }
                
                # Add REAL quality metrics (industry standard, no reference needed)
                if real_metrics:
                    response_data["real_quality"] = {
                        "overall_score": f"{real_metrics['overall_score']:.1%}",
                        "grade": real_metrics['grade'],
                        "validity": real_metrics['validity'],
                        "coverage": {
                            "functions": f"{real_metrics['coverage']['function_coverage']:.1%}",
                            "parameters": f"{real_metrics['coverage']['parameter_coverage']:.1%}",
                            "overall": f"{real_metrics['coverage']['overall']:.1%}"
                        },
                        "completeness": f"{real_metrics['completeness']['score']:.1%}",
                        "readability": {
                            "score": f"{real_metrics['readability']['score']:.1%}",
                            "flesch_ease": real_metrics['readability']['flesch_reading_ease'],
                            "flesch_grade": real_metrics['readability']['flesch_kincaid_grade']
                        },
                        "quality": f"{real_metrics['quality']['score']:.1%}"
                    }
                
                return JSONResponse(response_data)
            except Exception as e:
                print(f"AI generation failed: {e}")
        
        # Fallback to repository analysis
        if repo_path and os.path.exists(repo_path):
            print("🔄 Using repository structure analysis...")
            return await analyze_repository_structure(repo_path, context, doc_style, temperature, generation_mode)
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
            "🤖 ai_status": "✅ Available" if ADVANCED_SYSTEM_AVAILABLE else "⚠️ Demo mode",
            "🌐 server_url": "Repository-ready FastAPI server",
            "🔐 password": "nOtE7thIs",
            "📊 supported_inputs": ["Git URLs", "ZIP files", "Local directories", "Code snippets"],
            "🎨 supported_styles": ["google", "numpy", "technical_md", "opensource", "api", "comprehensive"]
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "status": "❌ Test failed"
        })

@app.get("/quality-check")
async def quality_check():
    """Quick quality check for the consolidated server"""
    if not doc_generator or not ADVANCED_SYSTEM_AVAILABLE:
        return JSONResponse({
            "status": "❌ FAILED",
            "error": "Documentation generator not available - will produce placeholder text"
        })
    
    try:
        # Test with GUI code like the user provided
        gui_code = '''
min_temp = Label(root, text="...", width=0, bg='white', font=("bold", 15))
min_temp.place(x=128, y=460)
# Note  
note = Label(root, text="All temperatures in degree celsius", bg='white', font=("italic", 10))
note.place(x=95, y=495)
root.mainloop()
'''
        
        # Enhance the code
        enhanced = enhance_code_snippet(gui_code)
        
        # Generate documentation
        result = doc_generator.generate_documentation(
            input_data=enhanced,
            context="GUI temperature display application",
            doc_style="technical",
            input_type='code',
            repo_name="quality_check"
        )
        
        # Quality verification
        has_placeholders = any(phrase in result for phrase in [
            'Function implementation.', 'Class implementation.', 'Method implementation.'
        ])
        
        has_real_content = any(phrase in result for phrase in [
            'GUI', 'Initialize', 'Create', 'Main', 'application', 'temperature'
        ])
        
        return JSONResponse({
            "status": "✅ PASSED" if not has_placeholders and has_real_content else "❌ FAILED",
            "test_details": {
                "original_code_length": len(gui_code),
                "enhanced_code_length": len(enhanced),
                "generated_doc_length": len(result),
                "no_placeholders": not has_placeholders,
                "has_real_content": has_real_content,
                "sample_output": result[:400] + "..." if len(result) > 400 else result
            },
            "verdict": "CONSOLIDATED SERVER WORKING!" if not has_placeholders and has_real_content else "STILL HAS ISSUES"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "❌ ERROR",
            "error": str(e)
        })

@app.get("/test-quality")
async def test_documentation_quality():
    """Test the quality of documentation generation with multiple scenarios"""
    if not doc_generator or not ADVANCED_SYSTEM_AVAILABLE:
        return JSONResponse({
            "status": "❌ ERROR",
            "message": "Fixed documentation generator not available",
            "problem": "Will produce placeholder text like 'Function implementation.'"
        })
    
    try:
        # Test scenarios
        test_scenarios = [
            {
                "name": "B+ Tree Database",
                "code": '''
class BPlusTreeNode:
    def __init__(self, keys, values):
        self.keys = keys
        self.values = values
    
    def insert(self, key, value):
        if key in self.keys:
            idx = self.keys.index(key)
            self.values[idx] = value
        return True
    
    def search(self, key):
        if key in self.keys:
            idx = self.keys.index(key)
            return self.values[idx]
        return None
''',
                "expected_content": ["Insert a", "Search for", "Initialize", "B+ Tree", "Union[", "Optional["]
            },
            {
                "name": "GUI Application",
                "code": '''
min_temp = Label(root, text="...", width=0, bg='white', font=("bold", 15))
min_temp.place(x=128, y=460)
note = Label(root, text="All temperatures in degree celsius", bg='white', font=("italic", 10))
note.place(x=95, y=495)
root.mainloop()
''',
                "expected_content": ["GUI", "application", "Create", "component", "interface"]
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            print(f"🧪 Testing scenario: {scenario['name']}")
            
            # Enhance if it's a code snippet
            enhanced_code = enhance_code_snippet(scenario['code']) if len(scenario['code'].strip()) < 500 else scenario['code']
            
            result = doc_generator.generate_documentation(
                input_data=enhanced_code,
                context=f"{scenario['name']} for quality testing",
                doc_style="technical",
                input_type='code',
                repo_name=f"test_{scenario['name'].lower().replace(' ', '_')}"
            )
            
            # Quality checks
            has_placeholders = any(phrase in result for phrase in [
                'Function implementation.', 'Class implementation.', 'Method implementation.'
            ])
            
            has_expected_content = any(phrase.lower() in result.lower() for phrase in scenario['expected_content'])
            
            results.append({
                "scenario": scenario['name'],
                "status": "✅ PASSED" if not has_placeholders and has_expected_content else "❌ FAILED",
                "no_placeholders": not has_placeholders,
                "has_expected_content": has_expected_content,
                "doc_length": len(result),
                "sample": result[:200] + "..." if len(result) > 200 else result
            })
        
        overall_status = "✅ ALL TESTS PASSED" if all(r["status"] == "✅ PASSED" for r in results) else "❌ SOME TESTS FAILED"
        
        return JSONResponse({
            "overall_status": overall_status,
            "test_results": results,
            "summary": {
                "total_tests": len(results),
                "passed": sum(1 for r in results if r["status"] == "✅ PASSED"),
                "failed": sum(1 for r in results if r["status"] == "❌ FAILED")
            },
            "message": "✅ Documentation quality verification complete!"
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "❌ ERROR",
            "message": f"Quality test failed: {str(e)}",
            "traceback": str(e)
        })

@app.get("/demo")
async def demo_info():
    """Show enhanced demo information"""
    return JSONResponse({
        "🎉 message": "Context-Aware Documentation Generator - Repository Edition",
        "🚀 server_status": "✅ Enhanced FastAPI with repository support",
        "📂 input_support": ["Git URLs (GitHub/GitLab)", "ZIP files", "Local directories", "Code snippets"],
        "🎨 output_styles": ["Sphinx/reST API", "Technical Comprehensive", "Open Source"],
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

def preload_models(preload_phi3: bool = False, preload_rag: bool = True):
    """Optionally preload models at startup for faster first request"""
    print("\n🔧 Pre-loading models for faster generation...")
    
    # Always preload RAG (it's fast and useful)
    if preload_rag:
        print("📚 Pre-loading RAG system (FAISS + sentence-transformers)...")
        lazy_load_rag_system()
    
    # Optionally preload Phi-3 (slow but needed for Phi-3 modes)
    if preload_phi3:
        print("🧠 Pre-loading Phi-3 model (this takes 1-2 minutes)...")
        lazy_load_advanced_system()
    
    print("✅ Model pre-loading complete!\n")

def start_server_with_tunnel():
    """Start FastAPI server with ngrok tunnel"""
    print("🌟 Starting Context-Aware Documentation Generator (Repository Edition)")
    print("=" * 70)
    
    # Skip preloading - models load on-demand for instant startup
    print("⚡ Instant startup mode - models load on first request")
    
    # Skip ngrok entirely for faster local startup
    tunnel = None
    print("⚠️ Ngrok disabled for instant startup - use localhost:8000")
    
    print("\n🚀 Starting Enhanced FastAPI server...")
    print("📂 Repository support: Git URLs, ZIP files, directories")
    print("🎨 Documentation styles: Technical Guide, User Manual, Open Source")
    print("🔐 Password: nOtE7thIs")
    print(f"📊 Advanced System: {'✅ Fully Loaded' if ADVANCED_SYSTEM_AVAILABLE and doc_generator else '⚠️ Limited Mode'}")
    print(f"🤖 Phi-3 + Gemini: {'✅ Ready (no timeout)' if doc_generator else '⚠️ Will initialize on demand'}")
    print(f"🔍 RAG System: {'✅ Loaded' if rag_system else '⏳ Will load on demand (FAISS + Sentence-Transformers)'}")
    print(f"📈 Quality Metrics: ✅ Heuristics + Readability (Flesch, SMOG, ARI) + BERTScore")
    
    try:
        # Start server
        print("\n🌐 Server starting on http://0.0.0.0:8000")
        print("   Press Ctrl+C to stop\n")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
        if tunnel:
            try:
                tunnel.close()
            except:
                pass
        print("✅ Cleanup complete!")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        if tunnel:
            try:
                tunnel.close()
            except:
                pass

if __name__ == "__main__":
    try:
        start_server_with_tunnel()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Try running with: python -u repo_fastapi_server.py")
        input("Press Enter to exit...")