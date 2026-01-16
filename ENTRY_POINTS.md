# Project Entry Points

## Main Entry Points

### 1. **Primary Entry Point (Recommended)**
- **File**: `repo_fastapi_server.py`
- **Type**: FastAPI Web Server
- **Description**: Full-featured web interface with repository analysis, ZIP upload, and multiple documentation styles
- **How to run**: 
  ```powershell
  .\start.ps1
  ```
  Or:
  ```powershell
  python repo_fastapi_server.py
  ```
- **Features**:
  - Web UI with GitHub repo URL input
  - ZIP file upload support
  - Multiple documentation styles (Google, NumPy, Markdown, etc.)
  - Public ngrok tunnel for external access
  - Real-time documentation generation

### 2. **Streamlit Frontend**
- **File**: `src/frontend.py`
- **Type**: Streamlit Web Application
- **Description**: Simple, user-friendly Streamlit interface
- **How to run**:
  ```powershell
  streamlit run src/frontend.py
  ```
- **Features**:
  - Clean Streamlit UI
  - GitHub repository analysis
  - Multiple output formats

### 3. **FastAPI REST API**
- **File**: `src/api.py`
- **Type**: REST API Server
- **Description**: API-only backend for programmatic access
- **How to run**:
  ```powershell
  python -m uvicorn src.api:app --reload
  ```
- **Features**:
  - RESTful endpoints
  - `/docs` for Swagger documentation
  - JSON responses

### 4. **Command Line Interface**
- **File**: `main.py`
- **Type**: CLI Tool
- **Description**: Terminal-based documentation generator
- **How to run**:
  ```powershell
  python main.py <path_or_repo_url> [options]
  ```
- **Examples**:
  ```powershell
  # Local directory
  python main.py ./my_project --style google
  
  # GitHub repository
  python main.py https://github.com/user/repo --repo --style numpy
  
  # With output directory
  python main.py ./code --output ./docs --style markdown
  ```
- **Options**:
  - `--repo`: Treat input as GitHub repository URL
  - `--style`: Documentation style (google/numpy/markdown)
  - `--output`: Output directory for generated docs
  - `--branch`: Git branch to analyze

## Quick Start Scripts

### PowerShell Launcher
- **File**: `start.ps1`
- **Description**: Automated startup script for Windows PowerShell
- **What it does**:
  - Activates virtual environment
  - Starts FastAPI server (repo_fastapi_server.py)
  - Shows startup information

### Batch File Launcher
- **File**: `start.bat`
- **Description**: Automated startup script for Windows Command Prompt
- **What it does**:
  - Activates virtual environment
  - Starts FastAPI server
  - Pauses after completion

## Setup and Configuration

### Initial Setup
- **File**: `setup.py`
- **Description**: Project setup and dependency installation
- **How to run**:
  ```powershell
  python setup.py
  ```
- **What it does**:
  - Checks Python version
  - Creates virtual environment
  - Installs all dependencies
  - Creates necessary directories

### Configuration
- **File**: `config.py`
- **Description**: Project configuration settings
- **Contains**:
  - Author information (team-8)
  - System name (charvaka)
  - Model configurations
  - API settings
  - Supported languages

## Development and Testing

### Multi-Language Analyzer
- **File**: `multi_language_analyzer.py`
- **Description**: Standalone analyzer for multiple programming languages
- **How to run**:
  ```powershell
  python multi_language_analyzer.py <path>
  ```

### Style Comparison
- **File**: `style_comparison.py`
- **Description**: Compare different documentation styles
- **How to run**:
  ```powershell
  python style_comparison.py
  ```

### Test Files
- `test_comprehensive_features.py` - Test comprehensive documentation features
- `test_framework.py` - Test the documentation framework
- `test_user_manager.py` - Test with sample Java code

## Core Modules (Not Direct Entry Points)

These are imported by other files:

- `comprehensive_docs_advanced.py` - Main documentation generator engine
- `intelligent_analyzer.py` - Intelligent code analysis module
- `evaluation_metrics.py` - Documentation quality metrics
- `src/parser.py` - Code parsing with tree-sitter
- `src/rag.py` - RAG system with embeddings
- `src/llm.py` - LLM integration and QLoRA
- `src/git_handler.py` - GitHub repository handling

## Recommended Workflow

### For College Project Demonstration:

1. **Start the server**:
   ```powershell
   .\start.ps1
   ```

2. **Access the web interface**: http://localhost:8000

3. **Input options**:
   - Paste GitHub repository URL, OR
   - Upload ZIP file of your project

4. **Select documentation style**:
   - Google (for Google-style docstrings)
   - NumPy (for NumPy-style documentation)
   - Markdown (for standard Markdown docs)
   - OpenSource (GitHub README style)

5. **Download** the generated documentation

### For Quick Testing:

```powershell
# Test with local code
python main.py ./samples --style google

# Test with GitHub repo
python main.py https://github.com/username/repo --repo --style numpy
```

## Access URLs (When Running)

- **Main Web UI**: http://localhost:8000
- **FastAPI Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501 (if running src/frontend.py)
- **ngrok Public URL**: Displayed in terminal when server starts

## Author & System Info

- **Author**: team-8
- **System**: charvaka
- **Project**: Context-Aware Code Documentation Generator
- **Purpose**: College project - AI-powered documentation generation

## Notes

- First run will download AI models (~7GB)
- Virtual environment must be activated
- PowerShell execution policy must allow scripts
- Requires Python 3.8+
