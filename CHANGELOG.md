# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Support for additional programming languages (Rust, Kotlin, Swift)
- IDE integration (VS Code extension)
- Custom model training interface
- Documentation quality scoring
- Batch processing for multiple repositories

### Changed
- Performance optimizations for large codebases
- Improved error handling and user feedback

### Fixed
- Memory optimization for large files
- Better handling of edge cases in parsing

## [0.1.0] - 2025-01-05

### Added
- **Core Features**
  - Multi-language code parsing using tree-sitter
  - Support for Python, JavaScript, Java, Go, C++, and more
  - RAG system with sentence transformers and FAISS
  - Microsoft Phi-3 model integration with QLoRA support
  - Context-aware documentation generation

- **Interfaces**
  - FastAPI backend for API services
  - Streamlit web interface for user interaction
  - Command-line interface for batch processing
  - RESTful API endpoints for integration

- **Documentation Formats**
  - Google-style docstrings
  - NumPy-style docstrings  
  - Sphinx-style docstrings
  - Comprehensive Markdown documentation

- **Input Methods**
  - GitHub repository processing
  - ZIP file upload support
  - Local directory processing

- **Development Tools**
  - Jupyter notebooks for training and examples
  - Model fine-tuning with QLoRA
  - Comprehensive test suite
  - Development environment setup scripts

- **Configuration**
  - Environment variable configuration
  - Flexible model and API settings
  - Logging and monitoring setup

### Technical Details
- **Parser**: tree-sitter for universal syntax tree parsing
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Search**: FAISS for efficient similarity search
- **LLM**: Microsoft Phi-3-mini-4k-instruct
- **Backend**: FastAPI with async support
- **Frontend**: Streamlit with responsive design
- **Git Integration**: GitPython for repository handling

### Documentation
- Comprehensive README with examples
- Contributing guidelines
- License (MIT)
- Setup and installation scripts
- API documentation
- Usage examples and tutorials

### Infrastructure
- GitHub repository setup
- Version control with Git
- Python package structure
- Dependencies management
- Environment configuration

---

## Version Format

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions  
- **PATCH** version for backwards-compatible bug fixes

## Categories

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes