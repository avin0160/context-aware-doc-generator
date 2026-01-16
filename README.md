# Context-Aware Code Documentation Generator
























































































































































































































































































































































**Documentation Updated:** January 16, 2026**Project:** Context-Aware Documentation Generator  ---**Total:** ~2340 lines modified across 13 files- Configuration files: ~15 lines modified- Documentation files: ~300 lines modified- `repo_fastapi_server.py`: ~25 lines modified- `comprehensive_docs_advanced.py`: ~2000 lines modified/added## Lines of Code Modified---```python main.py --repo <url> --style opensourcepython main.py --repo <url> --style technical_comprehensivepython main.py --repo <url> --style googlepython main.py --repo <url> --style state_diagram# Or use CLIpython repo_fastapi_server.py# Start server```bash### Usage:4. **opensource** - Contributor and maintainer guide3. **technical_comprehensive** - Long-form intelligent documentation (default)2. **google** - Inline docstring generation (Google style guide)1. **state_diagram** - System flows and state transitions (graphical)### Available Documentation Styles:## Quick Reference---- Verify output matches specifications- Test each style with a GitHub repo- Start server: `python repo_fastapi_server.py`### To Test:✅ All 4 styles are accessible✅ No syntax errors in comprehensive_docs_advanced.py✅ DocumentationGenerator initializes without errors✅ Module imports successfully### Verified:## Testing Status---- Sample files: `samples/` directory unchanged- Source files: `src/` directory unchanged- Core functionality files: `intelligent_analyzer.py`, `evaluation_metrics.py`### Files NOT Modified:10. `start.bat` - Author update9. `start.ps1` - Author update8. `setup.py` - Author update7. `ENTRY_POINTS.md` - Author update6. `MODELS_AND_METRICS.md` - Emoji removal5. `FIXES_APPLIED.md` - Emoji removal, metadata cleanup4. `README.md` - Author update, metadata cleanup3. `config.py` - Author rebranding2. `repo_fastapi_server.py` - Emoji removal from logs   - Added 20+ helper methods   - Created 1 new style method   - Rewrote 3 style methods   - Updated style routing   - Removed emojis1. `comprehensive_docs_advanced.py` - Major restructuring (3664 → 4478 lines)### Files Modified:2. `DOCUMENTATION_STYLES.md` - Complete guide to 4 documentation styles1. `BRANDING_UPDATE_COMPLETE.md` - Summary of branding changes### New Files Created:## File Statistics---- Default changed to `technical_comprehensive`- Added 4 new styles with aliases- Removed 5 old styles**Changes:**```    return self._generate_technical_comprehensive_style(...)    # Default to technical comprehensiveelse:    return self._generate_opensource_style(...)elif doc_style == 'opensource':    return self._generate_technical_comprehensive_style(...)elif doc_style in ['technical_comprehensive', 'technical', 'comprehensive']:    return self._generate_google_style(...)elif doc_style == 'google':    return self._generate_state_diagram_style(...)if doc_style in ['state_diagram', 'state', 'diagram', 'flow']:# Only 4 styles supported```python**New Routing:**```    return self._generate_comprehensive_style(...)else:    return self._generate_hybrid_repoagent_style(...)elif doc_style in ['hybrid', 'repoagent_metrics', 'detailed_metrics']:    return self._generate_repoagent_style(...)elif doc_style in ['repoagent', 'repo_agent', 'detailed']:    return self._generate_visual_flow_style(...)elif doc_style in ['visual', 'flow', 'diagram']:    return self._generate_api_documentation(...)elif doc_style == 'api':    return self._generate_opensource_style(...)elif doc_style == 'opensource':    return self._generate_technical_markdown(...)elif doc_style == 'technical_md':    return self._generate_numpy_style(...)elif doc_style == 'numpy':    return self._generate_google_style(...)if doc_style == 'google':```python**Old Routing:****Location:** `comprehensive_docs_advanced.py` → `generate_documentation()` (lines ~1015-1026)### 5. STYLE ROUTING UPDATED---- Community communication channels- Extension points for plugins- Issue triage guidelines- PR review checklist- Git workflow commands- Development workflow commands- Added maintainer-specific sections- Changed from general docs to contributor-focused- Complete rewrite of `_generate_opensource_style()` method**Changes Made:**- Troubleshooting- Useful commands- Community guidelines- Extension points- Architecture and design decisions- Maintainer section (release process, PR review, dependencies)- Testing requirements- Code style guidelines- Project structure explanation- Development environment setup- 5-step contribution process- Contributor onboarding**Features:****Location:** `comprehensive_docs_advanced.py` → `_generate_opensource_style()` (lines ~1583-2100)**Keywords:** `opensource`#### ✅ Style 4: Open Source---- `_generate_project_assessment()`- `_count_public_apis()`- `_generate_recommendations_comprehensive()`- `_generate_dependency_analysis_comprehensive()`- `_calculate_quality_score()`- `_generate_quality_analysis_comprehensive()`- `_generate_method_brief()`- `_describe_class_responsibility()`- `_describe_module_functionality()`- `_infer_module_purpose()`- `_assess_maintainability()`- `_describe_component_interactions()`- `_describe_entry_point()`- `_generate_module_hierarchy()`- `_identify_architecture_patterns()`- `_generate_architecture_narrative()`- `_generate_capability_analysis()`- `_identify_problem_domain()`- `_describe_stack_capabilities()`- `_explain_technology_role()`- `_assess_overall_complexity()`**New Helper Methods Added:**- Comprehensive quality scoring- Design pattern identification- Technology role explanations- Intelligent context-aware descriptions- 6-part structure: Overview, Architecture, Implementation, Quality, Development, Reference- Added 30+ helper methods for intelligent analysis- Created NEW method `_generate_technical_comprehensive_style()`**Changes Made:**- Development guide- Complete API inventory- Quality and maintainability analysis- Module-by-module breakdown- Then detailed technical implementation- Big picture overview first- Executive summary- Long-form documentation (6 parts)**Features:****Location:** `comprehensive_docs_advanced.py` → `_generate_technical_comprehensive_style()` (lines ~2370-2750)**Keywords:** `technical_comprehensive`, `technical`, `comprehensive`#### ✅ Style 3: Technical Comprehensive (Default)---- Shows exact docstring syntax for each module/class/function- Included step-by-step implementation guide- Added Google docstring format templates- Changed from general documentation to inline docstring generation- Complete rewrite of `_generate_google_style()` method**Changes Made:**- Verification commands- Implementation instructions- Function docstrings with parameters- Method docstrings with Args/Returns/Raises- Class docstrings with attributes- Module-level documentation suggestions- Google Python Style Guide compliant docstrings**Features:****Location:** `comprehensive_docs_advanced.py` → `_generate_google_style()` (lines ~1036-1390)**Keywords:** `google`#### ✅ Style 2: Google---- Updated documentation style indicator- Enhanced with state transition focus- Added entry points section at the top- Renamed `_generate_visual_flow_style()` to `_generate_state_diagram_style()`**Changes Made:**- Flow legend- Common usage flows- State transition diagrams- Execution timeline visualization- Dependency graphs- Class structure diagrams- Function call hierarchy- Data flow analysis- Module interaction maps- System architecture overview- Prominent entry points section- Graphical ASCII diagrams showing system flows**Features:****Location:** `comprehensive_docs_advanced.py` → `_generate_state_diagram_style()` (lines ~1700-1800)**Keywords:** `state_diagram`, `state`, `diagram`, `flow`#### ✅ Style 1: State Diagram**IMPLEMENTED 4 new styles:**- ❌ visual/flow (renamed to state_diagram)- ❌ hybrid- ❌ repoagent (kept internally for legacy)- ❌ api- ❌ technical_md- ❌ numpy**REMOVED old styles:**### 4. DOCUMENTATION STYLES RESTRUCTURED (Complete)---**Result:** Metadata not displayed explicitly in documentation- `README.md` - Removed system line- `comprehensive_docs_advanced.py` - Removed from generated docs- `DOCUMENTATION_STYLES.md` - Removed metadata- `BRANDING_UPDATE_COMPLETE.md` - Removed metadata- `FIXES_APPLIED.md` - Removed metadata header**Files Modified:**- Kept in config but removed from visible documentation- Removed "System: charvaka" from documentation headers- Removed "Author: team-8" from documentation headers**Removed explicit metadata display:**### 3. METADATA CLEANUP (Complete)---**Result:** All references now show "team-8"- `start.bat` - Author comments and output- `start.ps1` - Author comments and output- `setup.py` - Author display- `FIXES_APPLIED.md` - Author header- `ENTRY_POINTS.md` - Author references- `README.md` - Author section- `config.py` - AUTHOR_NAME, AUTHOR_EMAIL, GITHUB_USERNAME**Files Modified:****Changed:** "Anusha Kanulla" → "team-8"### 2. AUTHOR REBRANDING (Complete)---**Result:** No emojis in any codebase files- `MODELS_AND_METRICS.md` - Replaced ✅, ❌ with [IMPLEMENTED], [ACTIVE]- `FIXES_APPLIED.md` - Replaced ✅, ⭐ with [FIXED], [IMPROVED]  - Replaced with: [SUCCESS], [ERROR], [INFO], [WARNING], [STARTING]  - Removed ✅, ❌, 📦, 🚀, ⚙️, 🔧 from print statements- `repo_fastapi_server.py`  - Quality indicators: "Low", "Moderate", "High", "Excellent", "Good", "Poor"  - Replaced with plain text: "Tip", "System Architecture Overview", "Key Metrics"  - Removed all emojis (💡, 📊, 📈, 🔄, 🏗️, 📦, 📞, 🏛️, 🔗, 🔀, 📝, 🟢, 🟡, 🟠, 🔴, etc.)- `comprehensive_docs_advanced.py`**Files Modified:**### 1. EMOJI REMOVAL (Complete)## Changes Made to Context-Aware Documentation Generator---## Date: January 16, 2026[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent AI-powered system that automatically generates comprehensive, context-aware documentation for code repositories using advanced techniques including RAG (Retrieval-Augmented Generation), QLoRA fine-tuning, and the CodeSearchNet dataset.

## 🎯 Project Overview

This is a college project that analyzes codebases from GitHub repositories or ZIP files and generates professional documentation in multiple formats:
- **Standard Markdown documentation**
- **Google-style docstrings**
- **NumPy-style documentation**

## 🚀 Features

- **Multiple Input Methods**: 
  - GitHub repository URL
  - ZIP file upload of project
- **Multi-Language Support**: Parse and analyze Python, JavaScript, Java, Go, C++, and more
- **Context-Aware Generation**: Uses RAG with semantic embeddings and FAISS vector search
- **QLoRA Fine-tuning**: Optimized LLM fine-tuning with CodeSearchNet dataset
- **Multiple Documentation Styles**: Google, NumPy, and standard Markdown formats
- **Web Interface**: User-friendly Streamlit frontend
- **REST API**: FastAPI backend for programmatic access

## 🛠 Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Parsing**: tree-sitter for universal syntax parsing
- **Embeddings**: sentence-transformers for semantic understanding
- **Vector Search**: FAISS for efficient similarity search
- **LLM**: Microsoft Phi-3-mini-4k-instruct with QLoRA optimization
- **Fine-tuning**: QLoRA (Quantized Low-Rank Adaptation)
- **Dataset**: CodeSearchNet for training
- **Git Integration**: GitPython for repository handling

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for faster processing)
- Git

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/anusha-kanulla/context-aware-doc-generator.git
cd context-aware-doc-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install tree-sitter language grammars
python -c "from src.parser import CodeParser; CodeParser()"
```

## 🚀 Usage

### Web Interface (Streamlit)

```bash
# Start the Streamlit application
streamlit run src/frontend.py

# Or use the launcher script
python start_web.py
```

Then open your browser to `http://localhost:8501`

### API Server (FastAPI)

```bash
# Start the FastAPI server
python start_api.py

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Command Line Interface

```bash
# Generate documentation from local directory
python main.py /path/to/code --style google

# Generate documentation from GitHub repository
python main.py https://github.com/user/repo --repo --style numpy

# Specify output directory
python main.py /path/to/code --output docs --style markdown
```

## 📖 Documentation Styles

### Google Style
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
```

### NumPy Style
```python
def function_name(param1, param2):
    """
    Brief description.
    
    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2
        
    Returns
    -------
    bool
        Description of return value
    """
```

## 🎓 Training with QLoRA

The system supports fine-tuning on the CodeSearchNet dataset using QLoRA:

```bash
# Fine-tune the model
python train_model.py --dataset codesearchnet --epochs 3 --batch-size 4

# Use custom dataset
python train_model.py --data-path ./my_data --epochs 5
```

## 📁 Project Structure

```
context-aware-doc-generator/
├── src/
│   ├── parser.py          # Code parsing with tree-sitter
│   ├── rag.py             # RAG system with embeddings
│   ├── llm.py             # LLM integration and QLoRA
│   ├── git_handler.py     # GitHub repository handling
│   ├── frontend.py        # Streamlit web interface
│   └── api.py             # FastAPI backend
├── models/                # Trained models directory
├── output/                # Generated documentation
├── main.py                # CLI entry point
├── train_model.py         # Training script
├── requirements.txt       # Python dependencies
├── config.py              # Configuration settings
└── README.md              # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:
- Author information
- Model settings
- Output paths
- API endpoints

```python
AUTHOR_NAME = "team-8"
SYSTEM_NAME = "charvaka"
DEFAULT_MODEL = "microsoft/Phi-3-mini-4k-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

## 🤝 Contributing

This is a college project. For questions or suggestions, please open an issue.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Author

**team-8**
- GitHub: [@anusha-kanulla](https://github.com/anusha-kanulla)

## 🙏 Acknowledgments

- CodeSearchNet dataset by GitHub
- Microsoft Phi-3 model
- Hugging Face Transformers
- FastAPI and Streamlit communities

## 📝 Notes

This project was developed as part of academic coursework to demonstrate:
- AI/ML integration in software engineering
- Natural language processing applications
- Modern web development practices
- Software architecture and design patterns
