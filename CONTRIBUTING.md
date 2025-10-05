# Contributing to Context-Aware Code Documentation Generator

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve docs, examples, or tutorials
- **Testing**: Add test cases or improve test coverage

### Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/avin0160/context-aware-doc-generator.git
   cd context-aware-doc-generator
   ```

2. **Set Up Development Environment**
   ```bash
   ./setup.sh
   source venv/bin/activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install pytest black flake8 mypy
   ```

4. **Run Tests**
   ```bash
   pytest tests/
   ```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where possible
- Write descriptive docstrings for all functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Code Formatting

Before submitting, format your code:

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Testing

- Write tests for new functionality
- Ensure existing tests pass
- Aim for good test coverage
- Use pytest for testing framework

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### Documentation

- Update README.md if you add new features
- Add docstrings to new functions/classes
- Update type hints
- Add examples for new functionality

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, dependency versions
- **Steps to Reproduce**: Clear steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error messages and stack traces
- **Code Examples**: Minimal code that demonstrates the issue

Use this template:

```markdown
## Bug Report

**Environment:**
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.0]
- Package Version: [e.g., 0.1.0]

**Description:**
Brief description of the bug.

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen.

**Actual Behavior:**
What actually happens.

**Error Message:**
```
Full error message here
```

**Additional Context:**
Any additional information.
```

## 💡 Feature Requests

For feature requests, please include:

- **Use Case**: Why is this feature needed?
- **Description**: Detailed description of the feature
- **Examples**: How would the feature be used?
- **Alternatives**: Any alternative solutions considered?

## 🔧 Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following our guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   pytest tests/
   black src/ tests/
   flake8 src/ tests/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Guidelines

- **Title**: Use a clear, descriptive title
- **Description**: Explain what changes you made and why
- **Testing**: Describe how you tested your changes
- **Documentation**: Update docs if needed
- **Breaking Changes**: Clearly mark any breaking changes

### Commit Message Format

Use conventional commit format:

```
type(scope): description

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(parser): add support for Rust language parsing
fix(rag): resolve memory leak in index building
docs(readme): add installation instructions for Windows
```

## 🧪 Development Areas

### High Priority
- [ ] Support for additional programming languages
- [ ] Performance optimizations for large codebases
- [ ] Better error handling and user feedback
- [ ] Comprehensive test suite

### Medium Priority
- [ ] IDE integrations (VS Code extension)
- [ ] Custom model training interface
- [ ] Documentation quality metrics
- [ ] Batch processing improvements

### Research Areas
- [ ] Advanced context understanding
- [ ] Multi-modal documentation generation
- [ ] Code similarity detection
- [ ] Domain-specific fine-tuning

## 📚 Development Resources

### Architecture Overview
- `src/parser.py`: Multi-language code parsing
- `src/rag.py`: Retrieval-Augmented Generation system
- `src/llm.py`: Language model integration
- `src/api.py`: FastAPI backend
- `src/frontend.py`: Streamlit web interface

### Key Dependencies
- **tree-sitter**: Universal syntax parsing
- **transformers**: Hugging Face transformers
- **sentence-transformers**: Text embeddings
- **faiss**: Vector similarity search
- **fastapi**: Web API framework
- **streamlit**: Web UI framework

### Testing Strategy
- Unit tests for individual components
- Integration tests for full workflows
- Performance tests for large codebases
- End-to-end tests for API endpoints

## 🚀 Release Process

1. **Version Bump**: Update version in `src/__init__.py`
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Ensure all tests pass
4. **Documentation**: Update documentation
5. **Tag Release**: Create git tag
6. **Deploy**: Deploy to package repositories

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/avin0160/context-aware-doc-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/avin0160/context-aware-doc-generator/discussions)
- **Email**: avin0160@example.com

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to the Context-Aware Code Documentation Generator! 🎉