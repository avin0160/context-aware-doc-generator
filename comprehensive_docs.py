#!/usr/bin/env python3
"""
Generic Repository Documentation Generator
Uses CodeSearchNet dataset principles for semantic code understanding
Generates repository-specific documentation without hardcoded templates
"""

import os
import ast
import re
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter
import json

# Import the advanced analyzer
from comprehensive_docs_advanced import (
    DocumentationGenerator,
    MultiInputHandler,
    AdvancedRepositoryAnalyzer,
    CodeSearchNetEnhancedAnalyzer
)

class CodeSearchNetAnalyzer:
    """Analyzer that uses CodeSearchNet patterns for semantic understanding"""
    
    def __init__(self):
        self.function_patterns = {
            'web_framework': ['route', 'handler', 'endpoint', 'api', 'flask', 'django', 'fastapi'],
            'data_science': ['dataframe', 'model', 'predict', 'train', 'pandas', 'numpy', 'sklearn'],
            'cli_tool': ['argparse', 'click', 'command', 'parser', 'main', 'cli'],
            'database': ['query', 'insert', 'update', 'delete', 'connection', 'transaction'],
            'utility': ['helper', 'util', 'tool', 'format', 'parse', 'convert'],
            'test': ['test_', 'mock', 'assert', 'fixture', 'pytest', 'unittest'],
            'config': ['config', 'setting', 'env', 'parameter', 'option']
        }
        
        self.class_patterns = {
            'web_framework': ['App', 'Server', 'Handler', 'Controller', 'View', 'Router'],
            'data_science': ['Model', 'Predictor', 'Classifier', 'Regressor', 'Pipeline'],
            'cli_tool': ['CLI', 'Command', 'Parser', 'Interface'],
            'database': ['Manager', 'Connection', 'Repository', 'DAO', 'ORM'],
            'utility': ['Helper', 'Util', 'Tool', 'Factory', 'Builder'],
            'test': ['Test', 'Mock', 'Fixture', 'Suite'],
            'config': ['Config', 'Settings', 'Options', 'Parameters']
        }

def analyze_repository_semantically(file_contents: Dict[str, str]) -> Dict[str, Any]:
    """Analyze repository using semantic understanding principles from CodeSearchNet"""
    
    analyzer = CodeSearchNetAnalyzer()
    analysis = {
        'total_lines': 0,
        'functions': [],
        'classes': [],
        'imports': [],
        'file_analysis': {},
        'semantic_categories': defaultdict(int),
        'project_type': 'unknown',
        'key_technologies': [],
        'entry_points': [],
        'dependencies': []
    }
    
    for file_path, content in file_contents.items():
        file_info = analyze_file_semantically(file_path, content, analyzer)
        analysis['file_analysis'][file_path] = file_info
        
        # Aggregate semantic information
        analysis['total_lines'] += file_info['lines']
        analysis['functions'].extend(file_info['functions'])
        analysis['classes'].extend(file_info['classes'])
        analysis['imports'].extend(file_info['imports'])
        
        # Update semantic categories
        for category, count in file_info['semantic_categories'].items():
            analysis['semantic_categories'][category] += count
    
    # Determine project type based on semantic analysis
    analysis['project_type'] = determine_project_type(analysis['semantic_categories'])
    analysis['key_technologies'] = extract_key_technologies(analysis['imports'])
    analysis['entry_points'] = find_entry_points(analysis['functions'])
    
    return analysis

def analyze_file_semantically(file_path: str, content: str, analyzer: CodeSearchNetAnalyzer) -> Dict[str, Any]:
    """Analyze a single file using semantic patterns"""
    
    lines = content.split('\n')
    file_info = {
        'lines': len(lines),
        'functions': [],
        'classes': [],
        'imports': [],
        'semantic_categories': defaultdict(int),
        'docstrings': [],
        'complexity_score': 0
    }
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = analyze_function_semantically(node, analyzer)
                file_info['functions'].append(func_info)
                
                # Update semantic categories
                for category in func_info['semantic_categories']:
                    file_info['semantic_categories'][category] += 1
                    
            elif isinstance(node, ast.ClassDef):
                class_info = analyze_class_semantically(node, analyzer)
                file_info['classes'].append(class_info)
                
                # Update semantic categories
                for category in class_info['semantic_categories']:
                    file_info['semantic_categories'][category] += 1
                    
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_info = extract_import_info(node)
                file_info['imports'].extend(import_info)
                
    except SyntaxError:
        # Handle files that can't be parsed as Python
        pass
    
    return file_info

def analyze_function_semantically(node: ast.FunctionDef, analyzer: CodeSearchNetAnalyzer) -> Dict[str, Any]:
    """Analyze function using CodeSearchNet-style semantic understanding"""
    
    func_info = {
        'name': node.name,
        'line': node.lineno,
        'args': [arg.arg for arg in node.args.args],
        'docstring': ast.get_docstring(node),
        'semantic_categories': [],
        'is_private': node.name.startswith('_'),
        'is_main': node.name == 'main',
        'is_test': node.name.startswith('test_')
    }
    
    # Semantic analysis based on function name and content
    func_name_lower = node.name.lower()
    
    for category, patterns in analyzer.function_patterns.items():
        if any(pattern in func_name_lower for pattern in patterns):
            func_info['semantic_categories'].append(category)
    
    # Analyze function body for additional semantic clues
    func_body = ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    func_body_lower = func_body.lower()
    
    for category, patterns in analyzer.function_patterns.items():
        if any(pattern in func_body_lower for pattern in patterns):
            if category not in func_info['semantic_categories']:
                func_info['semantic_categories'].append(category)
    
    return func_info

def analyze_class_semantically(node: ast.ClassDef, analyzer: CodeSearchNetAnalyzer) -> Dict[str, Any]:
    """Analyze class using semantic patterns"""
    
    class_info = {
        'name': node.name,
        'line': node.lineno,
        'methods': [],
        'docstring': ast.get_docstring(node),
        'semantic_categories': [],
        'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)]
    }
    
    # Semantic analysis based on class name
    for category, patterns in analyzer.class_patterns.items():
        if any(pattern.lower() in node.name.lower() for pattern in patterns):
            class_info['semantic_categories'].append(category)
    
    # Analyze methods for additional context
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            method_info = analyze_function_semantically(item, analyzer)
            class_info['methods'].append(method_info)
            
            # Inherit semantic categories from methods
            for category in method_info['semantic_categories']:
                if category not in class_info['semantic_categories']:
                    class_info['semantic_categories'].append(category)
    
    return class_info

def extract_import_info(node) -> List[str]:
    """Extract import information"""
    imports = []
    
    if isinstance(node, ast.Import):
        for alias in node.names:
            imports.append(alias.name)
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ''
        for alias in node.names:
            imports.append(f"{module}.{alias.name}" if module else alias.name)
    
    return imports

def determine_project_type(semantic_categories: Dict[str, int]) -> str:
    """Determine project type based on semantic analysis"""
    
    if not semantic_categories:
        return 'utility'
    
    # Find dominant category
    dominant_category = max(semantic_categories.items(), key=lambda x: x[1])
    
    # Map to high-level project types
    category_mapping = {
        'web_framework': 'web_application',
        'data_science': 'data_analysis',
        'cli_tool': 'command_line_tool',
        'database': 'data_management',
        'utility': 'utility_library',
        'test': 'testing_framework',
        'config': 'configuration_tool'
    }
    
    return category_mapping.get(dominant_category[0], 'general_purpose')

def extract_key_technologies(imports: List[str]) -> List[str]:
    """Extract key technologies from imports"""
    
    tech_mapping = {
        'flask': 'Flask Web Framework',
        'django': 'Django Web Framework',
        'fastapi': 'FastAPI Web Framework',
        'pandas': 'Pandas Data Analysis',
        'numpy': 'NumPy Scientific Computing',
        'sklearn': 'Scikit-learn Machine Learning',
        'tensorflow': 'TensorFlow Deep Learning',
        'torch': 'PyTorch Deep Learning',
        'requests': 'HTTP Requests Library',
        'sqlalchemy': 'SQLAlchemy ORM',
        'click': 'Click CLI Framework',
        'argparse': 'Command Line Parsing',
        'boto3': 'AWS SDK',
        'redis': 'Redis Data Store'
    }
    
    technologies = []
    for import_name in imports:
        base_import = import_name.split('.')[0].lower()
        if base_import in tech_mapping:
            tech = tech_mapping[base_import]
            if tech not in technologies:
                technologies.append(tech)
    
    return technologies

def find_entry_points(functions: List[Dict]) -> List[str]:
    """Find main entry points in the codebase"""
    
    entry_points = []
    for func in functions:
        if func['is_main'] or func['name'] in ['main', 'run', 'start', 'app']:
            entry_points.append(func['name'])
    
    return entry_points

def generate_comprehensive_documentation(file_contents: Dict[str, str], context: str, doc_style: str, repo_path: str = '') -> str:
    """Generate comprehensive documentation with advanced features"""
    
    # Try to use the advanced generator first
    try:
        generator = DocumentationGenerator()
        repo_name = os.path.basename(repo_path) if repo_path else "Repository"
        
        # Map old styles to new comprehensive styles
        style_mapping = {
            'technical': 'technical_md',
            'api': 'api', 
            'user_guide': 'opensource',
            'tutorial': 'google',
            'comprehensive': 'comprehensive',
            'google': 'google',
            'numpy': 'numpy',
            'technical_md': 'technical_md',
            'opensource': 'opensource'
        }
        
        mapped_style = style_mapping.get(doc_style, 'comprehensive')
        
        # Use advanced analyzer for better results
        analysis = generator.analyzer.analyze_repository_comprehensive(file_contents)
        
        # Generate using the appropriate advanced method
        if mapped_style == 'google':
            return generator._generate_google_style(analysis, context, repo_name)
        elif mapped_style == 'numpy':
            return generator._generate_numpy_style(analysis, context, repo_name)
        elif mapped_style == 'technical_md':
            return generator._generate_technical_markdown(analysis, context, repo_name)
        elif mapped_style == 'opensource':
            return generator._generate_opensource_style(analysis, context, repo_name)
        elif mapped_style == 'api':
            return generator._generate_api_documentation(analysis, context, repo_name)
        else:
            return generator._generate_comprehensive_style(analysis, context, repo_name)
            
    except Exception as e:
        print(f"Advanced generation failed, using fallback: {e}")
        # Fallback to original method
        analysis = analyze_repository_semantically(file_contents)
        repo_name = os.path.basename(repo_path) if repo_path else 'Repository'
        
        if doc_style == "technical":
            return generate_technical_documentation(analysis, context, repo_name)
        elif doc_style == "api":
            return generate_api_documentation(analysis, context, repo_name)
        elif doc_style == "user_guide":
            return generate_user_guide(analysis, context, repo_name)
        elif doc_style == "tutorial":
            return generate_tutorial_documentation(analysis, context, repo_name)
        else:
            return generate_comprehensive_overview(analysis, context, repo_name)

def generate_technical_documentation(analysis: Dict, context: str, repo_name: str) -> str:
    """Generate technical documentation based on actual code analysis"""
    
    project_type = analysis['project_type']
    key_techs = analysis['key_technologies']
    total_functions = len(analysis['functions'])
    total_classes = len(analysis['classes'])
    
    # Generate project-specific documentation
    doc = f"""# {repo_name} - Technical Documentation

## Project Overview

**Type:** {project_type.replace('_', ' ').title()}
**Context:** {context}

### Key Technologies
{chr(10).join(f'- {tech}' for tech in key_techs) if key_techs else '- Standard Python libraries'}

### Codebase Statistics
- **Functions:** {total_functions}
- **Classes:** {total_classes}
- **Files:** {len(analysis['file_analysis'])}
- **Total Lines:** {analysis['total_lines']}

## Architecture Overview

### Project Structure
"""
    
    # Add file-by-file analysis
    for file_path, file_info in analysis['file_analysis'].items():
        if file_info['functions'] or file_info['classes']:
            doc += f"\n#### {file_path}\n"
            
            if file_info['classes']:
                doc += "**Classes:**\n"
                for cls in file_info['classes']:
                    doc += f"- `{cls['name']}`: {cls['docstring'][:100] if cls['docstring'] else 'Class implementation'}...\n"
            
            if file_info['functions']:
                doc += "**Functions:**\n"
                for func in file_info['functions']:
                    if not func['is_private']:  # Skip private functions
                        doc += f"- `{func['name']}({', '.join(func['args'])})`: "
                        doc += f"{func['docstring'][:100] if func['docstring'] else 'Function implementation'}...\n"
    
    # Add usage information based on project type
    doc += f"\n## Usage\n\n{generate_usage_section(analysis, project_type)}"
    
    # Add API reference for key functions
    doc += f"\n## API Reference\n\n{generate_api_reference(analysis)}"
    
    return doc

def generate_usage_section(analysis: Dict, project_type: str) -> str:
    """Generate usage section based on project type"""
    
    entry_points = analysis['entry_points']
    key_techs = analysis['key_technologies']
    
    if project_type == 'web_application':
        return """This is a web application. To run:

```python
# Start the web server
python main.py
# or
python app.py
```

Access the application at `http://localhost:8000` (or configured port)."""
    
    elif project_type == 'data_analysis':
        return """This is a data analysis project. Typical usage:

```python
import pandas as pd
from your_module import analyze_data

# Load and analyze data
data = pd.read_csv('data.csv')
results = analyze_data(data)
```"""
    
    elif project_type == 'command_line_tool':
        return """This is a command-line tool. Usage:

```bash
python main.py --help
python main.py [options] [arguments]
```"""
    
    elif project_type == 'utility_library':
        return """This is a utility library. Import and use:

```python
from your_module import utility_function

result = utility_function(arguments)
```"""
    
    else:
        return f"""This is a {project_type.replace('_', ' ')} project.

Entry points: {', '.join(entry_points) if entry_points else 'See main.py'}
Technologies: {', '.join(key_techs) if key_techs else 'Standard Python'}"""

def generate_api_reference(analysis: Dict) -> str:
    """Generate API reference based on actual functions and classes"""
    
    api_doc = ""
    
    # Document public functions
    public_functions = [f for f in analysis['functions'] if not f['is_private'] and not f['is_test']]
    if public_functions:
        api_doc += "### Functions\n\n"
        for func in public_functions[:10]:  # Limit to top 10 functions
            api_doc += f"#### `{func['name']}({', '.join(func['args'])})`\n\n"
            if func['docstring']:
                api_doc += f"{func['docstring']}\n\n"
            else:
                api_doc += "Function implementation.\n\n"
    
    # Document classes
    if analysis['classes']:
        api_doc += "### Classes\n\n"
        for cls in analysis['classes'][:5]:  # Limit to top 5 classes
            api_doc += f"#### `{cls['name']}`\n\n"
            if cls['docstring']:
                api_doc += f"{cls['docstring']}\n\n"
            else:
                api_doc += "Class implementation.\n\n"
            
            if cls['methods']:
                api_doc += "**Methods:**\n"
                for method in cls['methods'][:5]:  # Limit methods
                    if not method['is_private']:
                        api_doc += f"- `{method['name']}({', '.join(method['args'])})`\n"
                api_doc += "\n"
    
    return api_doc

def generate_api_documentation(analysis: Dict, context: str, repo_name: str) -> str:
    """Generate API-focused documentation"""
    
    return f"""# {repo_name} API Reference

{context}

## Quick Reference

{generate_api_reference(analysis)}

## Installation

```bash
pip install {repo_name.lower()}
```

## Examples

See the usage section for implementation examples.
"""

def generate_user_guide(analysis: Dict, context: str, repo_name: str) -> str:
    """Generate user-friendly documentation"""
    
    return f"""# {repo_name} User Guide

## What is {repo_name}?

{context}

This is a {analysis['project_type'].replace('_', ' ')} that uses {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Python'}.

## Getting Started

{generate_usage_section(analysis, analysis['project_type'])}

## Features

- {len(analysis['functions'])} functions available
- {len(analysis['classes'])} classes implemented
- Built with {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Python'}

## Need Help?

Check the technical documentation for detailed API reference.
"""

def generate_tutorial_documentation(analysis: Dict, context: str, repo_name: str) -> str:
    """Generate tutorial-style documentation"""
    
    return f"""# {repo_name} Tutorial

## Step 1: Understanding the Project

{context}

This project is a {analysis['project_type'].replace('_', ' ')} with the following components:

- **{len(analysis['functions'])} functions** for core functionality
- **{len(analysis['classes'])} classes** for object-oriented design
- **Technologies:** {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Standard Python'}

## Step 2: Installation and Setup

{generate_usage_section(analysis, analysis['project_type'])}

## Step 3: Basic Usage

Follow the examples in the usage section above.

## Step 4: Advanced Features

Explore the API reference for advanced functionality.
"""

def generate_comprehensive_overview(analysis: Dict, context: str, repo_name: str) -> str:
    """Generate comprehensive overview documentation"""
    
    return f"""# {repo_name} - Complete Documentation

## Overview

{context}

**Project Type:** {analysis['project_type'].replace('_', ' ').title()}

## Technical Specifications

- **Total Files:** {len(analysis['file_analysis'])}
- **Functions:** {len(analysis['functions'])}
- **Classes:** {len(analysis['classes'])}
- **Lines of Code:** {analysis['total_lines']}

## Technologies Used

{chr(10).join(f'- {tech}' for tech in analysis['key_technologies']) if analysis['key_technologies'] else '- Standard Python libraries'}

## Getting Started

{generate_usage_section(analysis, analysis['project_type'])}

## API Reference

{generate_api_reference(analysis)}

---

*Generated by Generic Documentation System using semantic code analysis*
"""

if __name__ == "__main__":
    # Test the system
    test_files = {
        "app.py": '''
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    """Get all users from the database"""
    return jsonify([{"id": 1, "name": "John"}])

if __name__ == '__main__':
    app.run(debug=True)
        ''',
        "models.py": '''
class User:
    """User model for the application"""
    
    def __init__(self, name, email):
        self.name = name
        self.email = email
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {"name": self.name, "email": self.email}
        '''
    }
    
    docs = generate_comprehensive_documentation(
        test_files, 
        "A simple web application for user management", 
        "technical"
    )
    print(docs)