# Expected Sphinx/reST Documentation Format

## What You Should Get (Correct Sphinx Style)

When you select **"Sphinx/reST API"** in the web UI, the output should look like this:

```markdown
# MyProject - API Documentation

**Documentation Style**: Sphinx/reST - Professional Python API documentation

---

## Overview

API documentation for the MyProject project.

**Project Type:** Web Application  
**Total Files:** 5  
**Functions:** 25  
**Classes:** 8  

---

## API Reference

### Module: `main.py`

#### Class: `GitHandler`

Handle Git repository operations for code analysis.

:Inherits: object

##### Method: `clone_repository`

```python
def clone_repository(repo_url, branch):
    ...
```

Clone a GitHub repository to a temporary directory.

:param repo_url: GitHub repository URL
:type repo_url: str
:param branch: Branch name to clone
:type branch: str

:return: Path to cloned repository
:rtype: str

##### Method: `cleanup`

```python
def cleanup(repo_path):
    ...
```

Clean up temporary directories.

:param repo_path: Path to repository to clean
:type repo_path: str

:return: None
:rtype: None
```

---

## What You Got (Wrong - Technical Comprehensive Style)

Your downloaded files show narrative documentation with sections like:

```markdown
# RepoRequest System - Technical Comprehensive Documentation

**Documentation Style**: Technical Comprehensive - In-depth analysis

## Executive Summary
## Part I: Overview & Concept
## Part II: System Architecture
## Part III: Detailed Technical Implementation
```

This is the **"Technical Comprehensive"** style - which is for detailed technical reports, not API documentation.

---

## How to Fix

1. Open the web UI: http://localhost:8000
2. In the "Documentation Style" section, **click on the "Sphinx/reST API" box** (first box on the left)
3. Make sure it's highlighted/selected
4. Generate documentation again
5. Download the result

The file should be named `documentation_sphinx.md` and contain API reference format.

---

## Quick Comparison

| Style | Use Case | Format |
|-------|----------|--------|
| **Sphinx/reST API** | Python API docs | `:param:`, `:type:`, `:return:` |
| **Open Source** | GitHub README | Contributor guide, setup |
| **Technical Comprehensive** | Technical report | Executive summary, architecture |

You wanted #1 but got #3.
