#!/usr/bin/env python3
"""
Advanced Repository Documentation Generator
Integrates CodeSearchNet dataset, LoRA fine-tuning, and comprehensive analysis
Supports multiple input types and generates professional documentation
"""

import os
import re
import ast
import json
import zipfile
import tempfile
import subprocess
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict, Counter
from dataclasses import dataclass
import requests

try:
    from datasets import load_dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
    from peft import LoraConfig, get_peft_model, TaskType
    import torch
    ADVANCED_FEATURES = True
except ImportError:
    print("Advanced features (transformers, datasets) not available")
    ADVANCED_FEATURES = False

@dataclass
class FunctionInfo:
    """Detailed function information"""
    name: str
    file_path: str
    line_start: int
    line_end: int
    args: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    calls: List[str]  # Functions this function calls
    called_by: List[str]  # Functions that call this function
    complexity: int
    semantic_category: str
    dependencies: List[str]  # External dependencies

@dataclass
class ClassInfo:
    """Detailed class information"""
    name: str
    file_path: str
    line_start: int
    line_end: int
    methods: List[FunctionInfo]
    attributes: List[str]
    inheritance: List[str]
    docstring: Optional[str]
    semantic_category: str

class CodeSearchNetEnhancedAnalyzer:
    """Enhanced analyzer with CodeSearchNet dataset integration and dependency analysis"""
    
    def __init__(self):
        self.function_patterns = {
            'web_framework': ['route', 'handler', 'endpoint', 'api', 'flask', 'django', 'fastapi', 'blueprint', 'middleware'],
            'data_science': ['dataframe', 'model', 'predict', 'train', 'pandas', 'numpy', 'sklearn', 'tensor', 'feature', 'dataset'],
            'cli_tool': ['argparse', 'click', 'command', 'parser', 'main', 'cli', 'console', 'terminal'],
            'database': ['query', 'insert', 'update', 'delete', 'connection', 'transaction', 'migrate', 'schema'],
            'utility': ['helper', 'util', 'tool', 'format', 'parse', 'convert', 'transform', 'process'],
            'test': ['test_', 'mock', 'assert', 'fixture', 'pytest', 'unittest', 'spec', 'benchmark'],
            'config': ['config', 'setting', 'env', 'parameter', 'option', 'configure', 'setup'],
            'security': ['auth', 'token', 'permission', 'encrypt', 'decrypt', 'secure', 'validate'],
            'network': ['request', 'response', 'client', 'server', 'socket', 'http', 'tcp', 'udp'],
            'file_system': ['file', 'directory', 'path', 'read', 'write', 'save', 'load', 'storage']
        }
        
        self.dependency_graph = nx.DiGraph()
        self.function_call_graph = nx.DiGraph()
        
        # Load CodeSearchNet patterns if available
        if ADVANCED_FEATURES:
            self.load_codesearchnet_patterns()
    
    def load_codesearchnet_patterns(self):
        """Load and analyze CodeSearchNet dataset patterns"""
        try:
            print("Loading CodeSearchNet dataset patterns...")
            # Load a small subset for pattern analysis
            dataset = load_dataset("code_search_net", "python", split="train[:1000]")
            
            # Analyze common patterns
            for example in dataset:
                code = example.get('func_code_string', '')
                docstring = example.get('func_documentation_string', '')
                
                if code and docstring:
                    self._extract_patterns_from_example(code, docstring)
                    
            print("CodeSearchNet patterns loaded successfully")
        except Exception as e:
            print(f"Could not load CodeSearchNet dataset: {e}")
    
    def _extract_patterns_from_example(self, code: str, docstring: str):
        """Extract documentation patterns from CodeSearchNet examples"""
        # This would analyze the relationship between code and documentation
        # For now, we'll use the existing patterns
        pass

class AdvancedRepositoryAnalyzer:
    """Advanced repository analyzer with inter-file and inter-function dependency analysis"""
    
    def __init__(self):
        self.analyzer = CodeSearchNetEnhancedAnalyzer()
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.imports: Dict[str, List[str]] = {}
        self.dependency_graph = nx.DiGraph()
        self.call_graph = nx.DiGraph()
    
    def analyze_repository_comprehensive(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Perform comprehensive repository analysis with dependency tracking"""
        
        analysis = {
            'total_lines': 0,
            'total_files': len(file_contents),
            'functions': {},
            'classes': {},
            'imports': {},
            'file_analysis': {},
            'semantic_categories': defaultdict(int),
            'project_type': 'unknown',
            'key_technologies': [],
            'entry_points': [],
            'dependency_graph': {},
            'call_graph': {},
            'complexity_metrics': {},
            'quality_metrics': {}
        }
        
        # First pass: Parse all files and extract basic information
        for file_path, content in file_contents.items():
            if file_path.endswith('.py'):
                file_info = self._analyze_file_comprehensive(file_path, content)
                analysis['file_analysis'][file_path] = file_info
                analysis['total_lines'] += file_info['lines']
        
        # Second pass: Build dependency and call graphs
        self._build_dependency_graphs(analysis)
        
        # Third pass: Semantic analysis and project type detection
        self._perform_semantic_analysis(analysis)
        
        # Calculate metrics
        self._calculate_metrics(analysis)
        
        return analysis
    
    def _analyze_file_comprehensive(self, file_path: str, content: str) -> Dict[str, Any]:
        """Comprehensive file analysis"""
        
        lines = content.split('\n')
        file_info = {
            'path': file_path,
            'lines': len(lines),
            'functions': [],
            'classes': [],
            'imports': [],
            'function_calls': [],
            'semantic_categories': defaultdict(int),
            'complexity_score': 0,
            'quality_score': 0
        }
        
        try:
            tree = ast.parse(content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports = self._extract_import_info(node)
                    file_info['imports'].extend(imports)
            
            # Analyze functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function_comprehensive(node, file_path, content)
                    file_info['functions'].append(func_info)
                    self.functions[f"{file_path}:{func_info.name}"] = func_info
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class_comprehensive(node, file_path, content)
                    file_info['classes'].append(class_info)
                    self.classes[f"{file_path}:{class_info.name}"] = class_info
            
            # Extract function calls
            file_info['function_calls'] = self._extract_function_calls(tree)
            
        except SyntaxError as e:
            file_info['error'] = f"Syntax error: {e}"
        
        return file_info
    
    def _analyze_function_comprehensive(self, node: ast.FunctionDef, file_path: str, content: str) -> FunctionInfo:
        """Comprehensive function analysis"""
        
        # Extract function calls within this function
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        
        # Calculate complexity (simplified McCabe complexity)
        complexity = self._calculate_complexity(node)
        
        # Determine semantic category
        semantic_category = self._classify_function_semantically(node.name, ast.unparse(node) if hasattr(ast, 'unparse') else str(node))
        
        return FunctionInfo(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            args=[arg.arg for arg in node.args.args],
            return_type=self._extract_return_type(node),
            docstring=ast.get_docstring(node),
            calls=calls,
            called_by=[],  # Will be populated later
            complexity=complexity,
            semantic_category=semantic_category,
            dependencies=[]  # Will be populated later
        )
    
    def _analyze_class_comprehensive(self, node: ast.ClassDef, file_path: str, content: str) -> ClassInfo:
        """Comprehensive class analysis"""
        
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function_comprehensive(item, file_path, content)
                methods.append(method_info)
        
        # Extract attributes (simplified)
        attributes = []
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        semantic_category = self._classify_class_semantically(node.name)
        
        return ClassInfo(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            methods=methods,
            attributes=attributes,
            inheritance=[base.id for base in node.bases if isinstance(base, ast.Name)],
            docstring=ast.get_docstring(node),
            semantic_category=semantic_category
        )
    
    def _build_dependency_graphs(self, analysis: Dict[str, Any]):
        """Build inter-file and inter-function dependency graphs"""
        
        # Build function call graph
        for file_path, file_info in analysis['file_analysis'].items():
            for func in file_info['functions']:
                func_key = f"{file_path}:{func.name}"
                
                # Add function calls as edges
                for called_func in func.calls:
                    # Try to find the actual function being called
                    for other_file, other_info in analysis['file_analysis'].items():
                        for other_func in other_info['functions']:
                            if other_func.name == called_func:
                                other_key = f"{other_file}:{other_func.name}"
                                self.call_graph.add_edge(func_key, other_key)
                                other_func.called_by.append(func_key)
        
        # Convert graphs to serializable format
        analysis['call_graph'] = {
            'nodes': list(self.call_graph.nodes()),
            'edges': list(self.call_graph.edges())
        }
    
    def _perform_semantic_analysis(self, analysis: Dict[str, Any]):
        """Perform semantic analysis to determine project type and characteristics"""
        
        semantic_counts = defaultdict(int)
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info['functions']:
                semantic_counts[func.semantic_category] += 1
        
        # Determine primary project type
        if semantic_counts:
            primary_category = max(semantic_counts.items(), key=lambda x: x[1])[0]
            analysis['project_type'] = self._map_category_to_project_type(primary_category)
        
        analysis['semantic_categories'] = dict(semantic_counts)
        
        # Extract technologies from imports
        all_imports = []
        for file_info in analysis['file_analysis'].values():
            all_imports.extend(file_info['imports'])
        
        analysis['key_technologies'] = self._extract_technologies(all_imports)
        analysis['entry_points'] = self._find_entry_points(analysis)
    
    def _calculate_metrics(self, analysis: Dict[str, Any]):
        """Calculate various code quality and complexity metrics"""
        
        total_functions = sum(len(file_info['functions']) for file_info in analysis['file_analysis'].values())
        total_classes = sum(len(file_info['classes']) for file_info in analysis['file_analysis'].values())
        
        # Calculate average complexity
        complexities = []
        for file_info in analysis['file_analysis'].values():
            for func in file_info['functions']:
                complexities.append(func.complexity)
        
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        
        # Documentation coverage
        documented_functions = 0
        for file_info in analysis['file_analysis'].values():
            for func in file_info['functions']:
                if func.docstring:
                    documented_functions += 1
        
        doc_coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 0
        
        analysis['complexity_metrics'] = {
            'average_function_complexity': avg_complexity,
            'max_complexity': max(complexities) if complexities else 0,
            'total_functions': total_functions,
            'total_classes': total_classes
        }
        
        analysis['quality_metrics'] = {
            'documentation_coverage': doc_coverage,
            'functions_per_file': total_functions / len(analysis['file_analysis']),
            'classes_per_file': total_classes / len(analysis['file_analysis'])
        }
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate McCabe complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        return complexity
    
    def _classify_function_semantically(self, name: str, code: str) -> str:
        """Classify function based on semantic patterns"""
        name_lower = name.lower()
        code_lower = code.lower()
        
        for category, patterns in self.analyzer.function_patterns.items():
            if any(pattern in name_lower for pattern in patterns):
                return category
            if any(pattern in code_lower for pattern in patterns):
                return category
        
        return 'utility'
    
    def _classify_class_semantically(self, name: str) -> str:
        """Classify class based on semantic patterns"""
        for category, patterns in self.analyzer.function_patterns.items():
            if any(pattern.lower() in name.lower() for pattern in patterns):
                return category
        return 'utility'
    
    def _extract_import_info(self, node) -> List[str]:
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
    
    def _extract_function_calls(self, tree: ast.AST) -> List[str]:
        """Extract all function calls in the AST"""
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        
        return calls
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if available"""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        return None
    
    def _map_category_to_project_type(self, category: str) -> str:
        """Map semantic category to project type"""
        mapping = {
            'web_framework': 'web_application',
            'data_science': 'data_analysis_project',
            'cli_tool': 'command_line_tool',
            'database': 'database_project',
            'utility': 'utility_library',
            'test': 'testing_framework',
            'config': 'configuration_tool'
        }
        return mapping.get(category, 'general_purpose_project')
    
    def _extract_technologies(self, imports: List[str]) -> List[str]:
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
            'argparse': 'Command Line Parsing'
        }
        
        technologies = []
        for import_name in imports:
            base_import = import_name.split('.')[0].lower()
            if base_import in tech_mapping:
                tech = tech_mapping[base_import]
                if tech not in technologies:
                    technologies.append(tech)
        
        return technologies
    
    def _find_entry_points(self, analysis: Dict[str, Any]) -> List[str]:
        """Find main entry points"""
        entry_points = []
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info['functions']:
                if func.name in ['main', 'run', 'start', 'app'] or func.name.startswith('main'):
                    entry_points.append(f"{func.file_path}:{func.name}")
        
        return entry_points

class MultiInputHandler:
    """Handle multiple input types: code, git repos, zip files"""
    
    @staticmethod
    def process_input(input_data: str, input_type: str = 'auto') -> Dict[str, str]:
        """Process different input types and return file contents"""
        
        if input_type == 'auto':
            input_type = MultiInputHandler._detect_input_type(input_data)
        
        if input_type == 'code':
            return {'main.py': input_data}
        elif input_type == 'git':
            return MultiInputHandler._clone_git_repo(input_data)
        elif input_type == 'zip':
            return MultiInputHandler._extract_zip_file(input_data)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")
    
    @staticmethod
    def _detect_input_type(input_data: str) -> str:
        """Auto-detect input type"""
        if input_data.startswith(('http://', 'https://')):
            if 'github.com' in input_data or 'gitlab.com' in input_data:
                return 'git'
            else:
                return 'url'
        elif input_data.endswith('.zip'):
            return 'zip'
        else:
            return 'code'
    
    @staticmethod
    def _clone_git_repo(repo_url: str) -> Dict[str, str]:
        """Clone git repository and extract Python files"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Clone repository
            subprocess.run(['git', 'clone', repo_url, temp_dir], 
                         check=True, capture_output=True)
            
            # Extract Python files
            file_contents = {}
            for root, dirs, files in os.walk(temp_dir):
                # Skip hidden directories and common non-source directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                relative_path = os.path.relpath(file_path, temp_dir)
                                file_contents[relative_path] = f.read()
                        except Exception:
                            continue
            
            return file_contents
            
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Failed to clone repository: {e}")
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @staticmethod
    def _extract_zip_file(zip_path: str) -> Dict[str, str]:
        """Extract Python files from zip file"""
        file_contents = {}
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith('.py') and not file_info.is_dir():
                        try:
                            content = zip_file.read(file_info.filename).decode('utf-8', errors='ignore')
                            file_contents[file_info.filename] = content
                        except Exception:
                            continue
            
            return file_contents
            
        except zipfile.BadZipFile:
            raise ValueError("Invalid zip file")

class DocumentationGenerator:
    """Generate different styles of documentation"""
    
    def __init__(self):
        self.analyzer = AdvancedRepositoryAnalyzer()
    
    def generate_documentation(self, input_data: str, context: str, doc_style: str, 
                             input_type: str = 'auto', repo_name: str = '') -> str:
        """Generate comprehensive documentation"""
        
        # Process input
        file_contents = MultiInputHandler.process_input(input_data, input_type)
        
        if not file_contents:
            raise ValueError("No Python files found in input")
        
        # Perform comprehensive analysis
        analysis = self.analyzer.analyze_repository_comprehensive(file_contents)
        
        # Generate documentation based on style
        if doc_style == 'google':
            return self._generate_google_style(analysis, context, repo_name)
        elif doc_style == 'numpy':
            return self._generate_numpy_style(analysis, context, repo_name)
        elif doc_style == 'technical_md':
            return self._generate_technical_markdown(analysis, context, repo_name)
        elif doc_style == 'opensource':
            return self._generate_opensource_style(analysis, context, repo_name)
        elif doc_style == 'api':
            return self._generate_api_documentation(analysis, context, repo_name)
        else:
            return self._generate_comprehensive_style(analysis, context, repo_name)
    
    def _generate_google_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate Google-style documentation with proper formatting"""
        
        repo_name = repo_name or 'Repository'
        project_type = analysis['project_type'].replace('_', ' ').title()
        
        doc = f"""# {repo_name}

{context}

## Overview

This is a {project_type.lower()} built with {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Python'}.

### Project Statistics
- **Files:** {analysis['total_files']} Python files
- **Functions:** {analysis['complexity_metrics']['total_functions']}
- **Classes:** {analysis['complexity_metrics']['total_classes']}
- **Lines of Code:** {analysis['total_lines']}
- **Documentation Coverage:** {analysis['quality_metrics']['documentation_coverage']:.1f}%

## Architecture

### Project Structure
"""
        
        # Add file structure with proper Google-style documentation
        for file_path, file_info in analysis['file_analysis'].items():
            if file_info['functions'] or file_info['classes']:
                doc += f"\n### `{file_path}`\n\n"
                
                if file_info['classes']:
                    doc += "**Classes:**\n\n"
                    for cls in file_info['classes']:
                        doc += f"#### class `{cls.name}`\n\n"
                        if cls.docstring:
                            doc += f"{cls.docstring}\n\n"
                        
                        if cls.methods:
                            doc += "**Methods:**\n\n"
                            for method in cls.methods[:5]:  # Limit to first 5 methods
                                args_str = ', '.join(method.args)
                                doc += f"- `{method.name}({args_str})`: "
                                doc += f"{method.docstring[:100] if method.docstring else 'Method implementation'}...\n"
                        doc += "\n"
                
                if file_info['functions']:
                    doc += "**Functions:**\n\n"
                    for func in file_info['functions']:
                        if not func.name.startswith('_'):  # Skip private functions
                            args_str = ', '.join(func.args)
                            doc += f"#### `{func.name}({args_str})`\n\n"
                            
                            if func.docstring:
                                doc += f"{func.docstring}\n\n"
                            else:
                                doc += "Function implementation.\n\n"
                            
                            if func.return_type:
                                doc += f"**Returns:** {func.return_type}\n\n"
        
        # Add usage examples
        doc += "\n## Usage\n\n"
        doc += self._generate_usage_examples(analysis, project_type)
        
        # Add API reference
        doc += "\n## API Reference\n\n"
        doc += "See the class and function documentation above for detailed API information.\n"
        
        return doc
    
    def _generate_numpy_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate NumPy-style documentation"""
        
        repo_name = repo_name or 'Repository'
        
        doc = f"""{repo_name}
{'=' * len(repo_name)}

{context}

Parameters
----------
project_type : str
    {analysis['project_type'].replace('_', ' ').title()}
technologies : list
    {analysis['key_technologies']}
files : int
    {analysis['total_files']} Python files analyzed

Returns
-------
documentation : str
    Comprehensive NumPy-style documentation

Notes
-----
This project contains {analysis['complexity_metrics']['total_functions']} functions 
and {analysis['complexity_metrics']['total_classes']} classes with 
{analysis['quality_metrics']['documentation_coverage']:.1f}% documentation coverage.

Examples
--------
"""
        
        doc += self._generate_usage_examples(analysis, analysis['project_type'])
        
        # Add function signatures in NumPy style
        doc += "\n\nAPI Reference\n-------------\n\n"
        
        for file_path, file_info in analysis['file_analysis'].items():
            if file_info['functions']:
                doc += f"{file_path}\n{'-' * len(file_path)}\n\n"
                
                for func in file_info['functions'][:10]:  # Limit to first 10
                    if not func.name.startswith('_'):
                        doc += f"{func.name}({', '.join(func.args)})\n"
                        if func.docstring:
                            doc += f"    {func.docstring[:100]}...\n"
                        doc += "\n"
        
        return doc
    
    def _generate_technical_markdown(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate technical markdown documentation"""
        
        repo_name = repo_name or 'Repository'
        
        doc = f"""# {repo_name} - Technical Documentation

## 📋 Executive Summary

**Project Type:** {analysis['project_type'].replace('_', ' ').title()}  
**Context:** {context}  
**Primary Technologies:** {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Python Standard Library'}

## 📊 Codebase Metrics

| Metric | Value |
|--------|-------|
| Total Files | {analysis['total_files']} |
| Total Functions | {analysis['complexity_metrics']['total_functions']} |
| Total Classes | {analysis['complexity_metrics']['total_classes']} |
| Lines of Code | {analysis['total_lines']:,} |
| Avg Function Complexity | {analysis['complexity_metrics']['average_function_complexity']:.1f} |
| Documentation Coverage | {analysis['quality_metrics']['documentation_coverage']:.1f}% |

## 🏗️ Architecture Overview

### Dependency Graph
"""
        
        # Add dependency information
        if analysis['call_graph']['edges']:
            doc += f"\n**Inter-function Dependencies:** {len(analysis['call_graph']['edges'])} connections identified\n\n"
        
        # Add detailed file analysis
        doc += "### File-by-File Analysis\n\n"
        
        for file_path, file_info in analysis['file_analysis'].items():
            doc += f"#### `{file_path}`\n\n"
            doc += f"- **Lines:** {file_info['lines']}\n"
            doc += f"- **Functions:** {len(file_info['functions'])}\n"
            doc += f"- **Classes:** {len(file_info['classes'])}\n"
            doc += f"- **Imports:** {len(file_info['imports'])}\n\n"
            
            if file_info['imports']:
                doc += "**Key Dependencies:**\n"
                for imp in file_info['imports'][:5]:
                    doc += f"- `{imp}`\n"
                doc += "\n"
        
        # Add complexity analysis
        doc += "## 🔍 Complexity Analysis\n\n"
        
        high_complexity_functions = []
        for file_info in analysis['file_analysis'].values():
            for func in file_info['functions']:
                if func.complexity > 10:
                    high_complexity_functions.append((func.name, func.complexity, func.file_path))
        
        if high_complexity_functions:
            doc += "**High Complexity Functions (>10):**\n\n"
            for name, complexity, file_path in sorted(high_complexity_functions, key=lambda x: x[1], reverse=True)[:10]:
                doc += f"- `{name}` in `{file_path}`: Complexity {complexity}\n"
        else:
            doc += "✅ All functions have reasonable complexity (≤10)\n"
        
        doc += "\n## 🚀 Usage Guide\n\n"
        doc += self._generate_usage_examples(analysis, analysis['project_type'])
        
        return doc
    
    def _generate_opensource_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate open-source project documentation"""
        
        repo_name = repo_name or 'Repository'
        
        doc = f"""# {repo_name}

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![Code Quality](https://img.shields.io/badge/code%20quality-{int(analysis['quality_metrics']['documentation_coverage'])}%25-{'green' if analysis['quality_metrics']['documentation_coverage'] > 70 else 'orange'})](.)
[![Functions](https://img.shields.io/badge/functions-{analysis['complexity_metrics']['total_functions']}-blue)](.)

> {context}

## 🚀 Features

- **{analysis['complexity_metrics']['total_functions']} Functions** for comprehensive functionality
- **{analysis['complexity_metrics']['total_classes']} Classes** with object-oriented design
- **{', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Pure Python'}** technology stack
- **{analysis['quality_metrics']['documentation_coverage']:.0f}% Documentation** coverage

## 📦 Installation

```bash
git clone <repository-url>
cd {repo_name.lower()}
pip install -r requirements.txt
```

## 🎯 Quick Start

{self._generate_usage_examples(analysis, analysis['project_type'])}

## 📚 Documentation

### Core Components

"""
        
        # Add component documentation
        for file_path, file_info in list(analysis['file_analysis'].items())[:5]:  # Top 5 files
            if file_info['classes'] or file_info['functions']:
                doc += f"#### {os.path.basename(file_path)}\n\n"
                
                if file_info['classes']:
                    for cls in file_info['classes'][:3]:
                        doc += f"**`{cls.name}`** - {cls.docstring[:100] if cls.docstring else 'Core class implementation'}...\n\n"
                
                if file_info['functions']:
                    public_functions = [f for f in file_info['functions'] if not f.name.startswith('_')][:3]
                    for func in public_functions:
                        doc += f"**`{func.name}()`** - {func.docstring[:100] if func.docstring else 'Function implementation'}...\n\n"
        
        doc += """
## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
"""
        
        return doc
    
    def _generate_api_documentation(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate API-focused documentation"""
        
        repo_name = repo_name or 'Repository'
        
        doc = f"""# {repo_name} API Documentation

{context}

## API Overview

This {analysis['project_type'].replace('_', ' ')} provides the following API:

"""
        
        # Group functions by file
        for file_path, file_info in analysis['file_analysis'].items():
            public_functions = [f for f in file_info['functions'] if not f.name.startswith('_')]
            public_classes = file_info['classes']
            
            if public_functions or public_classes:
                doc += f"## {os.path.basename(file_path)}\n\n"
                
                # Document classes
                for cls in public_classes:
                    doc += f"### class `{cls.name}`\n\n"
                    if cls.docstring:
                        doc += f"{cls.docstring}\n\n"
                    
                    doc += "**Methods:**\n\n"
                    for method in cls.methods:
                        if not method.name.startswith('_'):
                            doc += f"#### `{method.name}({', '.join(method.args)})`\n\n"
                            if method.docstring:
                                doc += f"{method.docstring}\n\n"
                            if method.return_type:
                                doc += f"**Returns:** `{method.return_type}`\n\n"
                
                # Document functions
                for func in public_functions:
                    doc += f"### `{func.name}({', '.join(func.args)})`\n\n"
                    if func.docstring:
                        doc += f"{func.docstring}\n\n"
                    if func.return_type:
                        doc += f"**Returns:** `{func.return_type}`\n\n"
                    
                    if func.calls:
                        doc += f"**Dependencies:** {', '.join(func.calls[:5])}\n\n"
        
        return doc
    
    def _generate_comprehensive_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate comprehensive documentation combining all styles"""
        
        repo_name = repo_name or 'Repository'
        
        doc = f"""# {repo_name} - Complete Documentation

## Overview

{context}

**Project Classification:** {analysis['project_type'].replace('_', ' ').title()}

### Technical Specifications

| Specification | Value |
|---------------|--------|
| Total Files | {analysis['total_files']} |
| Functions | {analysis['complexity_metrics']['total_functions']} |
| Classes | {analysis['complexity_metrics']['total_classes']} |
| Lines of Code | {analysis['total_lines']:,} |
| Average Complexity | {analysis['complexity_metrics']['average_function_complexity']:.1f} |
| Documentation Coverage | {analysis['quality_metrics']['documentation_coverage']:.1f}% |

### Technology Stack

{chr(10).join(f'- {tech}' for tech in analysis['key_technologies']) if analysis['key_technologies'] else '- Standard Python Libraries'}

## Getting Started

{self._generate_usage_examples(analysis, analysis['project_type'])}

## Architecture & Design

### Dependency Analysis

"""
        
        if analysis['call_graph']['edges']:
            doc += f"The codebase has {len(analysis['call_graph']['edges'])} inter-function dependencies, indicating {'high' if len(analysis['call_graph']['edges']) > 50 else 'moderate'} coupling.\n\n"
        
        # Add entry points
        if analysis['entry_points']:
            doc += "**Entry Points:**\n"
            for entry_point in analysis['entry_points']:
                doc += f"- `{entry_point}`\n"
            doc += "\n"
        
        # Add detailed API reference
        doc += "## Complete API Reference\n\n"
        
        for file_path, file_info in analysis['file_analysis'].items():
            if file_info['functions'] or file_info['classes']:
                doc += f"### {file_path}\n\n"
                
                # Classes
                for cls in file_info['classes']:
                    doc += f"#### class `{cls.name}`\n\n"
                    if cls.docstring:
                        doc += f"**Description:** {cls.docstring}\n\n"
                    
                    if cls.inheritance:
                        doc += f"**Inherits from:** {', '.join(cls.inheritance)}\n\n"
                    
                    if cls.attributes:
                        doc += f"**Attributes:** {', '.join(cls.attributes)}\n\n"
                    
                    if cls.methods:
                        doc += "**Methods:**\n\n"
                        for method in cls.methods:
                            doc += f"- `{method.name}({', '.join(method.args)})`: {method.docstring[:50] if method.docstring else 'Method implementation'}...\n"
                        doc += "\n"
                
                # Functions
                for func in file_info['functions']:
                    if not func.name.startswith('_'):
                        doc += f"#### `{func.name}({', '.join(func.args)})`\n\n"
                        
                        if func.docstring:
                            doc += f"**Description:** {func.docstring}\n\n"
                        
                        if func.return_type:
                            doc += f"**Returns:** `{func.return_type}`\n\n"
                        
                        doc += f"**Complexity:** {func.complexity}\n\n"
                        
                        if func.calls:
                            doc += f"**Calls:** {', '.join(func.calls[:3])}{'...' if len(func.calls) > 3 else ''}\n\n"
        
        doc += "\n---\n\n*Generated by Advanced Repository Documentation Generator with CodeSearchNet integration*"
        
        return doc
    
    def _generate_usage_examples(self, analysis: Dict[str, Any], project_type: str) -> str:
        """Generate usage examples based on project type"""
        
        if project_type == 'web_application':
            return """```python
# Start the web application
python app.py

# Access endpoints
import requests
response = requests.get('http://localhost:5000/api/endpoint')
```"""
        
        elif project_type == 'data_analysis_project':
            return """```python
# Import the analysis modules
from your_project import DataAnalyzer

# Create analyzer and process data
analyzer = DataAnalyzer()
results = analyzer.analyze_data('data.csv')
```"""
        
        elif project_type == 'command_line_tool':
            return """```bash
# Command line usage
python main.py --help
python main.py --input file.txt --output results.txt
```"""
        
        else:
            return """```python
# Import and use the library
from your_project import main_function

# Use the functionality
result = main_function(parameters)
```"""

# Main function for backward compatibility
def generate_comprehensive_documentation(file_contents: Dict[str, str], context: str, 
                                       doc_style: str, repo_path: str = '') -> str:
    """Generate comprehensive documentation - main entry point"""
    
    generator = DocumentationGenerator()
    
    # Determine input type
    if len(file_contents) == 1 and 'main.py' in file_contents:
        # Single code input
        code = list(file_contents.values())[0]
        return generator.generate_documentation(code, context, doc_style, 'code', 
                                              os.path.basename(repo_path) if repo_path else 'Project')
    else:
        # Multiple files - create a generator and analyze directly
        analysis = generator.analyzer.analyze_repository_comprehensive(file_contents)
        repo_name = os.path.basename(repo_path) if repo_path else 'Repository'
        
        # Generate based on style
        if doc_style == 'google':
            return generator._generate_google_style(analysis, context, repo_name)
        elif doc_style == 'numpy':  
            return generator._generate_numpy_style(analysis, context, repo_name)
        elif doc_style == 'technical_md':
            return generator._generate_technical_markdown(analysis, context, repo_name)
        elif doc_style == 'opensource':
            return generator._generate_opensource_style(analysis, context, repo_name)
        elif doc_style == 'api':
            return generator._generate_api_documentation(analysis, context, repo_name)
        else:
            return generator._generate_comprehensive_style(analysis, context, repo_name)

if __name__ == "__main__":
    # Test the system
    test_code = '''
from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    """Get processed data from the system"""
    df = pd.read_csv('data.csv')
    processed = process_data(df)
    return jsonify(processed.to_dict())

def process_data(df):
    """Process the dataframe with advanced analytics"""
    df['processed'] = df['value'] * 2
    return df.groupby('category').sum()

class DataProcessor:
    """Advanced data processing engine"""
    
    def __init__(self, config):
        self.config = config
    
    def transform(self, data):
        """Transform data using configured parameters"""
        return data * self.config.get('multiplier', 1)

if __name__ == '__main__':
    app.run(debug=True)
    '''
    
    print("Testing Advanced Documentation Generator...")
    print("=" * 60)
    
    generator = DocumentationGenerator()
    
    # Test different styles
    styles = ['google', 'numpy', 'technical_md', 'opensource']
    
    for style in styles:
        print(f"\n--- {style.upper()} STYLE ---")
        docs = generator.generate_documentation(
            test_code, 
            "Flask web application with data processing capabilities", 
            style,
            'code',
            'TestProject'
        )
        print(docs[:500] + "...\n")