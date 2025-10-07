# 🚀 Advanced Context-Aware Documentation Generator

## Overview

A sophisticated documentation generation system that leverages **CodeSearchNet dataset insights**, **semantic code analysis**, and **inter-file dependency tracking** to produce professional documentation in multiple styles. The system supports various input types including code snippets, git repositories, and zip files.

## ✨ Key Features

### 🎨 Multiple Documentation Styles

- **Google Style**: Clean, professional documentation following Google's style guide
- **NumPy Style**: Scientific documentation with parameter/return specifications
- **Technical Markdown**: Comprehensive technical documentation with metrics and analysis
- **Open Source**: GitHub-ready documentation with badges and contribution guidelines
- **API Documentation**: Detailed API reference with function signatures and examples
- **Comprehensive**: All-in-one documentation combining multiple approaches

### 📊 Advanced Code Analysis

- **Semantic Pattern Recognition**: Automatically detects project types (web app, data science, CLI tool, etc.)
- **Inter-File Dependency Analysis**: Maps relationships between functions and classes across files
- **Complexity Metrics**: McCabe complexity analysis for code quality assessment
- **Documentation Coverage**: Measures and reports documentation completeness
- **Technology Detection**: Automatically identifies frameworks and libraries used

### 🔄 Multi-Input Support

- **Direct Code**: Paste code directly for instant documentation
- **Git Repositories**: Process entire GitHub/GitLab repositories
- **Zip Files**: Upload compressed project archives
- **Local Directories**: Process local Python projects

### 🔬 CodeSearchNet Integration

- **Semantic Understanding**: Inspired by Microsoft's CodeSearchNet dataset patterns
- **Function Classification**: Categorizes functions by purpose (web, data science, utility, etc.)
- **Pattern Recognition**: Identifies common coding patterns and architectural decisions

## 🛠️ Installation

### Prerequisites

```bash
pip install -r requirements.txt
```

### Core Dependencies

- `fastapi>=0.104.0` - Web interface
- `uvicorn>=0.24.0` - ASGI server
- `datasets>=2.15.0` - CodeSearchNet dataset access
- `transformers>=4.35.0` - Advanced NLP features (optional)
- `torch>=2.0.0` - PyTorch for model fine-tuning (optional)
- `networkx>=3.0` - Dependency graph analysis

## 🚀 Usage

### Command Line Interface

#### Basic Usage
```bash
# Generate comprehensive documentation for a local project
python3 main.py /path/to/project --use-generic --context "Web application for user management" --style comprehensive

# Generate Google-style documentation
python3 main.py /path/to/project --use-generic --context "Data science pipeline" --style google

# Generate NumPy-style documentation
python3 main.py /path/to/project --use-generic --context "Scientific computing library" --style numpy
```

#### Advanced Options
```bash
# All available styles
python3 main.py project/ --use-generic \
    --context "Advanced ML pipeline with REST API" \
    --style technical_md \
    -o advanced_docs.md

# Supported styles: comprehensive, google, numpy, technical_md, opensource, api, technical, user_guide, tutorial
```

### Web Interface

```bash
# Start the FastAPI server
python3 fastapi_server.py

# Access the web interface
# Local: http://localhost:8000
# Colab: Use ngrok integration for external access
```

#### Web Features

- **📁 File Upload**: Upload multiple Python files
- **🌐 Git Repository**: Process repositories directly from URLs
- **🎛️ Style Selection**: Choose from all documentation styles
- **📊 Real-time Analysis**: See processing metrics and file counts

### Python API

```python
from comprehensive_docs_advanced import DocumentationGenerator

# Initialize generator
generator = DocumentationGenerator()

# Generate documentation from code
docs = generator.generate_documentation(
    input_data="your_python_code",
    context="Description of your project",
    doc_style="google",
    input_type="code",
    repo_name="MyProject"
)

# Generate from git repository
docs = generator.generate_documentation(
    input_data="https://github.com/user/repo.git",
    context="Open source Python library",
    doc_style="opensource",
    input_type="git",
    repo_name="LibraryName"
)
```

## 📋 Documentation Styles Comparison

| Style | Best For | Key Features |
|-------|----------|--------------|
| **Google** | Professional projects | Clean formatting, method documentation, usage examples |
| **NumPy** | Scientific libraries | Parameter/return specs, mathematical notation support |
| **Technical MD** | Technical teams | Metrics, complexity analysis, architecture diagrams |
| **Open Source** | GitHub projects | Badges, contribution guidelines, installation instructions |
| **API** | Libraries/frameworks | Detailed function signatures, parameter documentation |
| **Comprehensive** | Complete documentation | Combines all approaches for maximum coverage |

## 🏗️ Advanced Features

### Semantic Analysis

The system automatically detects:

- **Web Applications**: Flask, Django, FastAPI patterns
- **Data Science**: Pandas, NumPy, scikit-learn usage
- **CLI Tools**: argparse, click command structures
- **Database Projects**: SQLAlchemy, database operations
- **Testing Frameworks**: pytest, unittest patterns

### Dependency Analysis

- **Function Call Graphs**: Maps which functions call which
- **Import Dependencies**: Tracks external library usage
- **Inter-file Relationships**: Shows how files connect
- **Complexity Metrics**: Identifies high-complexity functions

### Quality Metrics

- **Documentation Coverage**: Percentage of documented functions
- **Cyclomatic Complexity**: Code complexity measurements
- **Function Distribution**: Functions per file analysis
- **Technology Stack**: Automatic framework detection

## 🔧 Architecture

### Core Components

```
comprehensive_docs_advanced.py     # Main advanced generator
├── DocumentationGenerator         # Main generation interface
├── AdvancedRepositoryAnalyzer    # Code analysis engine
├── CodeSearchNetEnhancedAnalyzer # Semantic pattern recognition
└── MultiInputHandler             # Input processing (git, zip, code)

comprehensive_docs.py              # Enhanced legacy system
├── Enhanced with advanced features
└── Backward compatibility maintained

fastapi_server.py                  # Web interface
├── File upload support
├── Git repository processing
└── Multiple documentation styles

main.py                           # CLI interface
├── All documentation styles
├── Advanced processing options
└── Multi-input support
```

### Data Flow

```
Input (Code/Git/Zip) → MultiInputHandler → AdvancedRepositoryAnalyzer
                                         ↓
                                    Semantic Analysis
                                         ↓
                                   Dependency Graph
                                         ↓
                                  Quality Metrics
                                         ↓
                               DocumentationGenerator
                                         ↓
                              Style-Specific Formatting
                                         ↓
                                 Final Documentation
```

## 📊 Example Outputs

### Google Style Sample
```markdown
# ProjectName

Description of the project

## Overview

This is a web application built with Flask Web Framework.

### `main.py`

#### class `UserManager`

Manages user operations and authentication.

**Methods:**

#### `create_user(email: str, password: str)`

Creates a new user account with validation.

**Returns:** User object or None if validation fails
```

### NumPy Style Sample
```markdown
ProjectName
===========

Description of the project

Parameters
----------
project_type : str
    Web Application
technologies : list
    ['Flask', 'SQLAlchemy']

Returns
-------
documentation : str
    Comprehensive NumPy-style documentation
```

### Technical Markdown Sample
```markdown
# ProjectName - Technical Documentation

## 📊 Codebase Metrics

| Metric | Value |
|--------|-------|
| Total Functions | 25 |
| Documentation Coverage | 85.0% |
| Average Complexity | 3.2 |

## 🏗️ Architecture Overview

**High Complexity Functions:**
- `process_data`: Complexity 12
- `validate_input`: Complexity 8
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python3 test_comprehensive_features.py
```

This tests:
- ✅ All documentation styles
- ✅ Multi-input processing  
- ✅ Dependency analysis
- ✅ Quality metrics
- ✅ Error handling

## 🌐 Web Interface Features

- **Dual Input Methods**: File upload or Git repository URL
- **Real-time Processing**: Live progress updates
- **Style Preview**: See documentation as it's generated
- **Export Options**: Download generated documentation
- **Error Handling**: Comprehensive error reporting

## 🔍 CodeSearchNet Integration

The system incorporates insights from Microsoft's CodeSearchNet dataset:

- **Pattern Recognition**: Identifies common code patterns
- **Semantic Classification**: Categorizes functions by purpose
- **Documentation Templates**: Uses patterns from high-quality codebases
- **Quality Indicators**: Applies learned quality metrics

## 🚧 Future Enhancements

- [ ] **Fine-tuned Models**: Custom language models for code understanding
- [ ] **Multi-language Support**: JavaScript, TypeScript, Java support
- [ ] **Interactive Documentation**: Searchable, interactive docs
- [ ] **Performance Optimization**: Faster processing for large repositories
- [ ] **Custom Templates**: User-defined documentation templates

## 📈 Performance

- **Small Projects** (< 10 files): < 5 seconds
- **Medium Projects** (10-100 files): 10-30 seconds  
- **Large Projects** (100+ files): 1-5 minutes
- **Git Repository Processing**: 30 seconds - 2 minutes (depending on size)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `python3 test_comprehensive_features.py`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [CodeSearchNet](https://github.com/github/CodeSearchNet) - Microsoft's code search dataset
- [transformers](https://github.com/huggingface/transformers) - HuggingFace transformers library
- [FastAPI](https://github.com/tiangolo/fastapi) - Modern web framework for APIs

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/user/repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/user/repo/discussions)
- **Documentation**: This README and inline code documentation

---

*Generated with ❤️ by the Advanced Context-Aware Documentation Generator*