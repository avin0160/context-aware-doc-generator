# Documentation Styles Guide

## Project: Context-Aware Documentation Generator

---

## Overview

This project supports **4 documentation styles**, each designed for a specific purpose and audience.

---

## Style 1: State Diagram

**Keywords:** `state_diagram`, `state`, `diagram`, `flow`

### Purpose
Visualize system flows, state transitions, and entry points through graphical ASCII diagrams.

### Audience
- Architects
- System designers
- Developers learning system architecture
- Technical leads

### Key Features
- **Entry Points Section** - All system starting points prominently displayed
- **System Architecture Overview** - High-level project metrics
- **System Flow Diagram** - Execution path visualization
- **Module Interaction Map** - How modules communicate
- **Data Flow Analysis** - How data moves through the system
- **Function Call Hierarchy** - Call graph visualization
- **Class Structure Diagrams** - OOP structure (when classes present)
- **Dependency Graphs** - Import and dependency visualization
- **Execution Timeline** - Typical execution flow over time
- **State Transitions** - State machine visualization
- **Common Usage Flows** - Typical user/system workflows
- **Flow Legend** - Guide to reading the diagrams

### Output Format
Markdown with ASCII art diagrams showing boxes, arrows, and flow charts

### Example Use Case
"I need to understand how this system works and see the execution flow visually"

---

## Style 2: Google

**Keywords:** `google`

### Purpose
Generate inline documentation following Google's Python Style Guide for docstrings.

### Audience
- Developers adding documentation to existing code
- Teams standardizing on Google style
- Projects requiring detailed inline docs

### Key Features
- **Google Docstring Format** - Exactly follows Google's Python Style Guide
- **Module Docstrings** - Top-level module documentation
- **Class Docstrings** - With attributes section
- **Method Docstrings** - With Args, Returns, Raises sections
- **Function Docstrings** - Complete parameter and return documentation
- **Example Sections** - Usage examples in docstrings
- **Implementation Guide** - Step-by-step instructions to add docs
- **Verification Commands** - How to test the documentation

### Output Format
Markdown showing suggested docstrings in proper Google format with implementation instructions

### Docstring Structure Example
```python
def function_name(param1, param2):
    """Brief description.
    
    Longer description explaining behavior.
    
    Args:
        param1 (type): Description.
        param2 (type): Description.
    
    Returns:
        type: Description.
    
    Raises:
        ErrorType: When error occurs.
    
    Example:
        >>> function_name(1, 2)
        3
    """
```

### Example Use Case
"I need to add proper inline documentation to all my code following industry standards"

### Note
This style generates documentation suggestions. To actually modify source files, apply the suggestions manually or use automated tooling.

---

## Style 3: Technical Comprehensive

**Keywords:** `technical_comprehensive`, `technical`, `comprehensive` (default)

### Purpose
Provide exhaustive long-form documentation with intelligent context-awareness, starting with big picture then diving into details.

### Audience
- New developers joining the project
- Technical writers
- Documentation maintainers
- Anyone needing complete understanding

### Key Features
- **6-Part Structure** for organized deep dive
- **Executive Summary** - High-level overview
- **Intelligent Sensing** - Context-aware explanations
- **Big Picture First** - Overall concept before details
- **Technology Explanations** - Why each tech is used
- **Architecture Narrative** - Story of how it's built
- **Module-by-Module Analysis** - Detailed breakdown of every module
- **Quality Metrics** - Comprehensive code quality assessment
- **Dependency Analysis** - Complete dependency examination
- **Recommendations** - Actionable improvement suggestions
- **Complete API Inventory** - Every public API documented

### Structure
1. **Part I: Overview & Concept**
   - Executive summary
   - Project vision
   - Scale and scope
   - Technology foundation
   - Problem domain
   - Key capabilities

2. **Part II: System Architecture**
   - High-level architecture
   - Architectural patterns
   - Module organization
   - Entry points and execution flow
   - Component interactions

3. **Part III: Detailed Technical Implementation**
   - Code structure analysis
   - Complexity distribution
   - Module-by-module breakdown
   - Class and function analysis
   - Purpose and usage context

4. **Part IV: Quality & Maintainability**
   - Code quality metrics
   - Dependency analysis
   - Improvement recommendations

5. **Part V: Development Guide**
   - Installation instructions
   - Running the project
   - Testing guidelines
   - Contributing guidelines

6. **Part VI: Technical Reference**
   - Complete API inventory
   - All public classes and functions

### Output Format
Long-form Markdown document (typically 5000-20000 words depending on project size)

### Example Use Case
"I'm new to this project and need to understand everything from architecture to implementation details"

---

## Style 4: Open Source

**Keywords:** `opensource`

### Purpose
Documentation specifically designed for contributors and maintainers of open source projects.

### Audience
- New contributors
- Active contributors
- Project maintainers
- Community managers

### Key Features
- **Contributor Welcome** - Friendly onboarding
- **5-Step Contribution Process** - Fork, setup, change, test, PR
- **Development Environment Setup** - Complete setup instructions
- **Project Structure Explained** - File-by-file breakdown
- **Code Style Guidelines** - Exact standards required
- **Testing Requirements** - What tests are needed
- **Maintainer Section** - Release process, PR review, dependency management
- **Architecture & Design** - Design patterns and decisions explained
- **Extension Points** - Where to add new features
- **Community Guidelines** - Communication channels
- **Useful Commands** - Development and Git workflows
- **Troubleshooting** - Common issues and solutions

### Sections
1. **For Contributors**
   - Welcome message
   - Quick start (5 steps)
   - Project overview

2. **Project Structure**
   - Directory layout with explanations
   - Module responsibilities

3. **Development Guidelines**
   - Code style requirements
   - Testing requirements
   - Documentation requirements

4. **For Maintainers**
   - Release process
   - PR review checklist
   - Dependency management
   - Issue triage

5. **Architecture & Design**
   - Design patterns in use
   - Design decisions
   - Extension points

6. **Community**
   - Getting help
   - Communication channels
   - Recognition

7. **Useful Commands**
   - Development workflow
   - Git workflow

8. **Troubleshooting**
   - Common issues and solutions

### Output Format
Markdown with badges, code blocks, checklists, and contributor-friendly formatting

### Example Use Case
"I want to make my project contributor-friendly with clear guidelines for maintainers and contributors"

---

## Style Comparison

| Feature | State Diagram | Google | Technical Comprehensive | Open Source |
|---------|---------------|--------|-------------------------|-------------|
| **Length** | Medium | Medium | Very Long | Long |
| **Visual** | High | Low | Medium | Low |
| **Detail** | Medium | High | Very High | Medium |
| **Code Focus** | Flow | Inline Docs | Complete Analysis | Project Setup |
| **Best For** | Architecture | Documentation | Learning | Contributing |
| **Audience** | Architects | All Devs | New Devs | Contributors |

---

## How to Use

### From Web Interface (repo_fastapi_server.py)

1. Start the server:
   ```bash
   .\start.ps1
   # or
   python repo_fastapi_server.py
   ```

2. Open browser: http://localhost:8000

3. Enter GitHub URL or upload ZIP

4. Select style from dropdown:
   - State Diagram
   - Google
   - Technical Comprehensive
   - Open Source

5. Click "Generate Documentation"

### From Command Line (main.py)

```bash
python main.py --repo <github-url> --style state_diagram
python main.py --repo <github-url> --style google
python main.py --repo <github-url> --style technical_comprehensive
python main.py --repo <github-url> --style opensource
```

### From Python Code

```python
from comprehensive_docs_advanced import DocumentationGenerator

generator = DocumentationGenerator()

# State diagram style
doc = generator.generate_documentation(
    code_or_files,
    context="My project description",
    doc_style="state_diagram",
    input_type="repo",
    repo_name="my-project"
)

# Google style
doc = generator.generate_documentation(
    code_or_files,
    context="My project description",
    doc_style="google",
    input_type="repo",
    repo_name="my-project"
)

# Technical comprehensive (default)
doc = generator.generate_documentation(
    code_or_files,
    context="My project description",
    doc_style="technical_comprehensive",
    input_type="repo",
    repo_name="my-project"
)

# Open source style
doc = generator.generate_documentation(
    code_or_files,
    context="My project description",
    doc_style="opensource",
    input_type="repo",
    repo_name="my-project"
)
```

---

## Style Selection Guide

**Choose State Diagram when:**
- You need to visualize system architecture
- You want to see execution flows
- You're explaining the system to architects or leads
- You need diagrams for documentation

**Choose Google when:**
- You need to add inline docstrings
- You want to follow Google's style guide
- You're standardizing documentation format
- You need parameter and return documentation

**Choose Technical Comprehensive when:**
- You're onboarding new developers
- You need complete project understanding
- You want everything in one document
- You need both overview and details

**Choose Open Source when:**
- You're building an open source project
- You want to attract contributors
- You need maintainer documentation
- You want community-friendly docs

---

## Technical Notes

### Implementation Files
- Main implementation: `comprehensive_docs_advanced.py`
- Web interface: `repo_fastapi_server.py`
- CLI interface: `main.py`
- Configuration: `config.py`

### Style Method Mapping
- `state_diagram` → `_generate_state_diagram_style()`
- `google` → `_generate_google_style()`
- `technical_comprehensive` → `_generate_technical_comprehensive_style()`
- `opensource` → `_generate_opensource_style()`

### Aliases
- State diagram: `state`, `diagram`, `flow`
- Technical comprehensive: `technical`, `comprehensive`

### Default Style
If no style specified or invalid style provided, defaults to `technical_comprehensive`

---

**Generated:** January 16, 2026
