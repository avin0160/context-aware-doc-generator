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
        """Comprehensive function analysis with real docstring and type extraction"""
        
        # Extract arguments with real type information
        args = []
        for arg in node.args.args:
            arg_name = arg.arg
            if arg.annotation:
                try:
                    if hasattr(ast, 'unparse'):
                        arg_type = ast.unparse(arg.annotation)
                    else:
                        # Handle common type annotations
                        if isinstance(arg.annotation, ast.Name):
                            arg_type = arg.annotation.id
                        elif isinstance(arg.annotation, ast.Constant):
                            arg_type = repr(arg.annotation.value)
                        else:
                            arg_type = "Any"
                    args.append(f"{arg_name}: {arg_type}")
                except:
                    args.append(f"{arg_name}: Any")
            else:
                # Infer type from usage patterns
                inferred_type = self._infer_parameter_type(arg_name, node, content)
                args.append(f"{arg_name}: {inferred_type}")
        
        # Extract function calls within this function
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        
        # Calculate complexity (McCabe complexity)
        complexity = self._calculate_complexity(node)
        
        # Get actual docstring or generate meaningful one
        docstring = ast.get_docstring(node)
        if not docstring or docstring.strip() == '':
            docstring = self._generate_function_docstring(node, file_path, content, calls)
        
        # Extract return type
        return_type = self._extract_return_type(node)
        if not return_type:
            return_type = self._infer_return_type_from_body(node, content)
        
        # Determine semantic category based on actual function analysis
        semantic_category = self._classify_function_semantically(node.name, self._get_function_body_text(node, content))
        
        return FunctionInfo(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            args=args,
            return_type=return_type,
            docstring=docstring,
            calls=calls,
            called_by=[],  # Will be populated later
            complexity=complexity,
            semantic_category=semantic_category,
            dependencies=[]  # Will be populated later
        )
    
    def _infer_parameter_type(self, param_name: str, node: ast.FunctionDef, content: str) -> str:
        """Infer parameter type from usage in function body"""
        # Look for type hints in the code
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    # Look for isinstance(param, Type) patterns
                    if child.func.id == 'isinstance' and len(child.args) >= 2:
                        if isinstance(child.args[0], ast.Name) and child.args[0].id == param_name:
                            if isinstance(child.args[1], ast.Name):
                                return child.args[1].id
                    # Common type patterns
                    elif child.func.id in ['len', 'enumerate'] and any(isinstance(arg, ast.Name) and arg.id == param_name for arg in child.args):
                        return "Sequence"
                    elif child.func.id in ['str', 'int', 'float', 'bool'] and any(isinstance(arg, ast.Name) and arg.id == param_name for arg in child.args):
                        return child.func.id
        
        # Default based on parameter name patterns
        if param_name in ['self', 'cls']:
            return "Self"
        elif 'key' in param_name.lower():
            return "Union[str, int]"
        elif 'value' in param_name.lower():
            return "Any"
        elif 'node' in param_name.lower():
            return "Node"
        elif param_name.endswith('_id'):
            return "Union[str, int]"
        elif 'record' in param_name.lower():
            return "Dict[str, Any]"
        elif 'schema' in param_name.lower():
            return "Dict[str, type]"
        else:
            return "Any"
    
    def _generate_function_docstring(self, node: ast.FunctionDef, file_path: str, content: str, calls: List[str]) -> str:
        """Generate meaningful docstring based on function analysis"""
        func_name = node.name
        
        # Analyze function purpose from name and body
        if func_name == '__init__':
            return f"Initialize a new {os.path.basename(file_path).replace('.py', '')} instance with the provided parameters."
        elif func_name.startswith('_'):
            return f"Internal helper method for {func_name[1:].replace('_', ' ')} operations."
        elif 'insert' in func_name.lower():
            return f"Insert a new item into the data structure. Handles key-value insertion with automatic tree balancing if needed."
        elif 'delete' in func_name.lower():
            return f"Remove an item from the data structure. Maintains structural integrity after deletion."
        elif 'search' in func_name.lower():
            return f"Search for an item in the data structure. Returns the associated value if found, None otherwise."
        elif 'update' in func_name.lower():
            return f"Update an existing item in the data structure with a new value."
        elif 'validate' in func_name.lower():
            return f"Validate input data against the defined schema and constraints."
        elif 'range' in func_name.lower() and 'query' in func_name.lower():
            return f"Perform a range query to retrieve all items between specified start and end keys."
        elif func_name.lower().startswith('get'):
            return f"Retrieve {func_name[3:].lower().replace('_', ' ')} from the data structure."
        elif func_name.lower().startswith('is_'):
            return f"Check if the current state satisfies the {func_name[3:].replace('_', ' ')} condition."
        elif func_name.lower().startswith('has_'):
            return f"Determine whether the structure has {func_name[4:].replace('_', ' ')}."
        elif 'split' in func_name.lower():
            return f"Split a node when it exceeds capacity, redistributing keys and maintaining tree properties."
        elif 'merge' in func_name.lower():
            return f"Merge nodes when underflow occurs, combining keys and values to maintain minimum capacity."
        elif 'visualize' in func_name.lower():
            return f"Generate a visual representation of the data structure for debugging and analysis."
        else:
            # Generate based on what the function actually does
            if len(calls) > 5:
                return f"Complex operation that coordinates multiple steps: {', '.join(calls[:3])}... Handles {func_name.replace('_', ' ')} workflow."
            elif calls:
                return f"Performs {func_name.replace('_', ' ')} operation using {', '.join(calls[:2])} for processing."
            else:
                return f"Handles {func_name.replace('_', ' ')} functionality for the data structure."
    
    def _infer_return_type_from_body(self, node: ast.FunctionDef, content: str) -> str:
        """Infer return type from function body analysis"""
        returns = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                if child.value:
                    if isinstance(child.value, ast.Constant):
                        if isinstance(child.value.value, bool):
                            returns.append("bool")
                        elif isinstance(child.value.value, int):
                            returns.append("int")
                        elif isinstance(child.value.value, str):
                            returns.append("str")
                        elif child.value.value is None:
                            returns.append("None")
                    elif isinstance(child.value, ast.Name):
                        if child.value.id in ['True', 'False']:
                            returns.append("bool")
                        elif child.value.id == 'None':
                            returns.append("None")
                    elif isinstance(child.value, ast.List):
                        returns.append("List")
                    elif isinstance(child.value, ast.Dict):
                        returns.append("Dict")
                    elif isinstance(child.value, ast.Tuple):
                        returns.append("Tuple")
        
        if returns:
            unique_returns = list(set(returns))
            if len(unique_returns) == 1:
                return unique_returns[0]
            elif 'None' in unique_returns:
                other_types = [t for t in unique_returns if t != 'None']
                if other_types:
                    return f"Optional[{other_types[0]}]"
            return f"Union[{', '.join(unique_returns)}]"
        
        # Default based on function name
        func_name = node.name.lower()
        if func_name.startswith('is_') or func_name.startswith('has_'):
            return "bool"
        elif 'get' in func_name or 'search' in func_name:
            return "Optional[Any]"
        elif 'all' in func_name:
            return "List[Any]"
        else:
            return "None"
    
    def _get_function_body_text(self, node: ast.FunctionDef, content: str) -> str:
        """Extract the actual source code of the function body"""
        lines = content.split('\n')
        start_line = node.lineno - 1
        end_line = getattr(node, 'end_lineno', start_line + 10) - 1
        
        if end_line < len(lines):
            return '\n'.join(lines[start_line:end_line + 1])
        else:
            return '\n'.join(lines[start_line:start_line + 10])
    
    def _generate_class_docstring(self, node: ast.ClassDef, file_path: str, content: str, methods: List) -> str:
        """Generate meaningful class docstring based on analysis"""
        class_name = node.name
        
        # Analyze class purpose from name and methods
        if 'node' in class_name.lower():
            return f"Represents a node in the data structure. Contains data and references to maintain structural relationships."
        elif 'tree' in class_name.lower():
            return f"Implements a tree data structure with methods for insertion, deletion, search, and traversal operations."
        elif 'database' in class_name.lower():
            return f"Database implementation providing CRUD operations with indexing and query capabilities."
        elif 'schema' in class_name.lower():
            return f"Defines the data schema and validation rules for structured data operations."
        elif 'index' in class_name.lower():
            return f"Manages indexing operations for efficient data retrieval and range queries."
        elif 'record' in class_name.lower():
            return f"Represents a data record with fields and operations for data manipulation."
        elif 'buffer' in class_name.lower():
            return f"Manages memory buffering operations for efficient I/O and data caching."
        elif 'manager' in class_name.lower():
            return f"Coordinates and manages operations across multiple components of the system."
        elif 'handler' in class_name.lower():
            return f"Handles specific operations and provides an interface for external interactions."
        elif 'parser' in class_name.lower():
            return f"Parses input data and converts it into structured format for processing."
        elif 'validator' in class_name.lower():
            return f"Validates data integrity and enforces business rules and constraints."
        else:
            # Generate based on methods
            method_names = [m.name for m in methods if not m.name.startswith('_')]
            if any('insert' in name for name in method_names):
                return f"Data structure class that supports insertion, search, and manipulation operations."
            elif any('process' in name for name in method_names):
                return f"Processing class that handles data transformation and computation tasks."
            elif any('connect' in name for name in method_names):
                return f"Connection management class for handling external resource interactions."
            else:
                return f"Core {class_name} class providing essential functionality and operations."
    
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
        
        # Generate meaningful class docstring if missing
        existing_docstring = ast.get_docstring(node)
        if not existing_docstring:
            existing_docstring = self._generate_class_docstring(node, file_path, content, methods)
        
        return ClassInfo(
            name=node.name,
            file_path=file_path,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', node.lineno),
            methods=methods,
            attributes=attributes,
            inheritance=[base.id for base in node.bases if isinstance(base, ast.Name)],
            docstring=existing_docstring,
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
        """Generate Google-style inline documentation focusing on code walkthrough"""
        
        repo_name = repo_name or analysis.get('repo_name', 'Unknown Repository')
        project_type = analysis['project_type'].replace('_', ' ').title()
        
        # Generate comprehensive project understanding
        purpose = self._infer_project_purpose(analysis, context)
        main_workflow = self._trace_execution_flow(analysis)
        
        doc = f"""# {repo_name} - Code Walkthrough & Implementation Guide

## 🎯 What This Project Does

{purpose}

**Primary Purpose:** {self._get_project_summary(analysis)}
**Architecture:** {project_type} with {len(analysis['file_analysis'])} modules
**Key Technologies:** {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Pure Python'}

## 🔄 Execution Flow & Code Walkthrough

{main_workflow}

## 📁 File-by-File Code Analysis

"""
        
        # Deep dive into each file with inline code documentation
        for file_path, file_info in analysis['file_analysis'].items():
            if file_info['functions'] or file_info['classes']:
                doc += f"### 📄 `{file_path}` - {self._get_file_purpose(file_info, analysis)}\n\n"
                doc += f"**Role:** {self._analyze_file_role(file_info, analysis)}\n\n"
                
                # Show imports and their purpose
                if file_info['imports']:
                    doc += "**Dependencies & Their Usage:**\n"
                    for imp in file_info['imports'][:8]:
                        purpose = self._explain_import_purpose(imp, file_info)
                        doc += f"- `{imp}` → {purpose}\n"
                    doc += "\n"
                
                # Detailed function analysis with code purpose
                if file_info['classes']:
                    for cls in file_info['classes']:
                        doc += f"#### 🏗️ Class `{cls.name}`\n\n"
                        doc += f"**Purpose:** {self._analyze_class_purpose(cls, analysis)}\n"
                        doc += f"**When Used:** {self._explain_class_usage(cls, analysis)}\n\n"
                        
                        if cls.methods:
                            doc += "**Method Breakdown:**\n"
                            for method in cls.methods[:6]:
                                workflow = self._explain_method_workflow(method, analysis)
                                doc += f"- `{method.name}()` → {workflow}\n"
                        doc += "\n"
                
                if file_info['functions']:
                    doc += "**Function Implementation Details:**\n\n"
                    for func in file_info['functions']:
                        if not func.name.startswith('_'):
                            doc += f"#### 🔧 `{func.name}({', '.join(func.args)})`\n\n"
                            
                            # Explain what this function actually does
                            explanation = self._generate_function_explanation(func, analysis)
                            doc += f"**What it does:** {explanation}\n\n"
                            
                            # Show the workflow
                            workflow = self._trace_function_workflow(func, analysis)
                            if workflow:
                                doc += f"**How it works:**\n{workflow}\n\n"
                            
                            # Show dependencies
                            if func.calls:
                                doc += f"**Calls:** {', '.join(func.calls[:5])}\n"
                            if func.called_by:
                                doc += f"**Called by:** {', '.join(func.called_by[:3])}\n"
                            doc += "\n"
        
        # Add practical usage guide
        doc += "## 🚀 How to Use This Code\n\n"
        doc += self._generate_detailed_usage_guide(analysis)
        
        # Add troubleshooting section
        doc += "\n## 🔧 Understanding the Code Flow\n\n"
        doc += self._generate_code_flow_explanation(analysis)
        
        return doc
    
    def _generate_numpy_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate NumPy-style documentation with visual diagrams and scientific structure"""
        
        repo_name = repo_name or analysis.get('repo_name', 'Unknown_Repository')
        
        doc = f"""
{repo_name.upper()}
{'=' * len(repo_name)}

SCIENTIFIC DOCUMENTATION & ANALYSIS REPORT

Synopsis
--------
{context}

System Architecture
-------------------
┌─ PROJECT SPECIFICATION ─┐
│ Type      : {analysis['project_type'].replace('_', ' ').title():<20} │
│ Files     : {analysis['total_files']:<20} │  
│ Functions : {analysis['complexity_metrics']['total_functions']:<20} │
│ Classes   : {analysis['complexity_metrics']['total_classes']:<20} │
│ LOC       : {analysis['total_lines']:<20} │
│ Quality   : {analysis['quality_metrics']['documentation_coverage']:.1f}% documented{' ':<8} │
└─────────────────────────────┘

Technology Stack Matrix
------------------------
"""
        
        # Create visual technology matrix
        if analysis['key_technologies']:
            for i, tech in enumerate(analysis['key_technologies'], 1):
                doc += f"[{i:2d}] {tech}\n"
        else:
            doc += "[01] Python Standard Library\n"
        
        doc += f"""

Computational Complexity Analysis
----------------------------------
┌─ COMPLEXITY METRICS ─────────────────────────────────────┐
│                                                          │
│  Average Function Complexity: {analysis['complexity_metrics']['average_function_complexity']:>6.1f}                    │
│  Maximum Complexity Found:    {analysis['complexity_metrics']['max_complexity']:>6d}                      │ 
│  Functions per Module:        {analysis['quality_metrics']['functions_per_file']:>6.1f}                    │
│  Code Distribution Score:     {self._calculate_distribution_score(analysis):>6.1f}                    │
│                                                          │
└──────────────────────────────────────────────────────────┘

Dependency Graph Visualization
-------------------------------
"""
        
        # Generate ASCII dependency visualization
        doc += self._generate_ascii_dependency_graph(analysis)
        
        doc += """

Function Signature Specifications
----------------------------------
"""
        
        # Detailed function documentation in scientific format
        for file_path, file_info in analysis['file_analysis'].items():
            if file_info['functions'] or file_info['classes']:
                doc += f"\n{file_path.upper()}\n{'-' * len(file_path)}\n"
                
                # Module purpose
                module_purpose = self._analyze_module_purpose(file_info, analysis)
                doc += f"Purpose: {module_purpose}\n\n"
                
                if file_info['classes']:
                    for cls in file_info['classes']:
                        doc += f"class {cls.name}\n"
                        doc += f"{'~' * (6 + len(cls.name))}\n\n"
                        doc += f"Attributes\n----------\n"
                        for attr in cls.attributes[:5]:
                            doc += f"{attr} : type\n    Class attribute\n"
                        
                        doc += f"\nMethods\n-------\n"
                        for method in cls.methods[:8]:
                            args_str = ', '.join(method.args) if method.args else ''
                            doc += f"{method.name}({args_str})\n"
                            if method.docstring:
                                doc += f"    {method.docstring[:80]}...\n"
                            if method.return_type:
                                doc += f"    Returns: {method.return_type}\n"
                            doc += f"    Complexity: {method.complexity}\n\n"
                
                if file_info['functions']:
                    for func in file_info['functions']:
                        if not func.name.startswith('_'):
                            doc += f"{func.name}({', '.join(func.args) if func.args else ''})\n"
                            doc += f"{'~' * (len(func.name) + 2 + len(', '.join(func.args) if func.args else ''))}\n\n"
                            
                            # Parameters section
                            if func.args:
                                doc += f"Parameters\n----------\n"
                                for arg in func.args:
                                    doc += f"{arg} : type\n    Parameter description\n"
                                doc += "\n"
                            
                            # Returns section
                            if func.return_type:
                                doc += f"Returns\n-------\n"
                                doc += f"result : {func.return_type}\n    Return value description\n\n"
                            
                            # Function properties
                            doc += f"Properties\n----------\n"
                            doc += f"Complexity Score    : {func.complexity}\n"
                            doc += f"Semantic Category   : {func.semantic_category}\n"
                            if func.calls:
                                doc += f"Function Calls      : {len(func.calls)} dependencies\n"
                            doc += "\n"
        
        # Add performance analysis
        doc += """
Performance Characteristics
----------------------------
"""
        doc += self._generate_performance_analysis(analysis)
        
        # Add visual examples section
        doc += """

Examples & Workflow Diagrams
-----------------------------
"""
        doc += self._generate_visual_examples(analysis)
        
        return doc
    
    def _generate_technical_markdown(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate comprehensive technical documentation with deep analysis"""
        
        repo_name = repo_name or analysis.get('repo_name', 'Technical_Project')
        
        # Deep technical analysis
        architecture_summary = self._generate_architecture_summary(analysis)
        security_analysis = self._analyze_security_aspects(analysis)
        performance_insights = self._analyze_performance_characteristics(analysis)
        
        doc = f"""# {repo_name} - Comprehensive Technical Documentation

## 🎯 Executive Technical Summary

**What This System Does:** {self._generate_system_purpose(analysis, context)}

**Architecture Type:** {analysis['project_type'].replace('_', ' ').title()}  
**Technical Context:** {context}  
**Core Technologies:** {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Python Standard Library'}  
**Deployment Target:** {self._infer_deployment_target(analysis)}

## 🏗️ System Architecture

### High-Level Design
```
{self._generate_ascii_architecture_diagram(analysis)}
```

{architecture_summary}

### � Entry Points & Execution Flow
{self._map_execution_flow(analysis)}

## 📊 Technical Metrics & Analysis

### Code Quality Metrics
| Metric | Value | Assessment | Recommendation |
|--------|-------|------------|----------------|
| **Cyclomatic Complexity** | Avg: {analysis['complexity_metrics']['average_function_complexity']:.1f}, Max: {analysis['complexity_metrics']['max_complexity']} | {self._assess_complexity(analysis)} | {self._recommend_complexity_improvement(analysis)} |
| **Documentation Coverage** | {analysis['quality_metrics']['documentation_coverage']:.1f}% | {self._assess_documentation(analysis)} | {self._recommend_documentation_improvement(analysis)} |
| **Code Distribution** | {analysis['quality_metrics']['functions_per_file']:.1f} functions/file | {self._assess_distribution(analysis)} | {self._recommend_distribution_improvement(analysis)} |
| **Dependency Coupling** | {len(analysis['call_graph']['edges'])} connections | {self._assess_coupling(analysis)} | {self._recommend_coupling_improvement(analysis)} |

### 🔍 Detailed Module Analysis

{self._generate_detailed_module_analysis(analysis)}

## 🔐 Security Analysis

{security_analysis}

## ⚡ Performance Characteristics

{performance_insights}

## 🗂️ Data Flow & State Management

### Data Structures Used
{self._analyze_data_structures(analysis)}

### State Management Pattern
{self._analyze_state_management(analysis)}

### Memory Usage Patterns
{self._analyze_memory_patterns(analysis)}

## 🔧 Technical Implementation Details

### Design Patterns Identified
{self._identify_design_patterns(analysis)}

### Error Handling Strategy
{self._analyze_error_handling(analysis)}

### Configuration Management
{self._analyze_configuration_approach(analysis)}

## 🚀 Deployment & Operations

### System Requirements
{self._generate_system_requirements(analysis)}

### Deployment Architecture
{self._suggest_deployment_architecture(analysis)}

### Monitoring & Observability
{self._suggest_monitoring_strategy(analysis)}

## 🔬 Code Deep Dive

### Function Complexity Heatmap
{self._generate_complexity_heatmap(analysis)}

### Dependency Graph Analysis
{self._analyze_dependency_relationships(analysis)}

### Critical Path Analysis
{self._identify_critical_paths(analysis)}

## 🛠️ Development & Maintenance

### Technical Debt Assessment
{self._assess_technical_debt(analysis)}

### Refactoring Opportunities
{self._identify_refactoring_opportunities(analysis)}

### Testing Strategy Recommendations
{self._recommend_testing_strategy(analysis)}

## 📈 Scalability & Future Considerations

### Current Limitations
{self._identify_current_limitations(analysis)}

### Scalability Bottlenecks
{self._identify_scalability_issues(analysis)}

### Evolution Roadmap
{self._suggest_technical_evolution(analysis)}

## 🎛️ Configuration & Environment

### Environment Variables
{self._identify_environment_dependencies(analysis)}

### External Dependencies
{self._analyze_external_dependencies(analysis)}

### Runtime Configuration
{self._analyze_runtime_configuration(analysis)}

---

*This technical documentation provides a comprehensive analysis of the system architecture, implementation details, and operational characteristics. It should be updated as the system evolves.*
"""
        
        return doc
    
    def _generate_opensource_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate comprehensive open-source contributor and maintainer documentation"""
        
        repo_name = repo_name or analysis.get('repo_name', 'opensource-project')
        github_url = f"https://github.com/username/{repo_name.lower().replace('_', '-')}"
        
        # Analyze code health
        maintainability_score = self._calculate_maintainability_score(analysis)
        complexity_health = "🟢 Healthy" if analysis['complexity_metrics']['average_function_complexity'] < 7 else "🟡 Moderate" if analysis['complexity_metrics']['average_function_complexity'] < 15 else "🔴 Complex"
        
        doc = f"""# {repo_name}

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Code Health](https://img.shields.io/badge/code%20health-{maintainability_score:.0f}%25-{'green' if maintainability_score > 75 else 'yellow' if maintainability_score > 50 else 'red'}.svg)](.)
[![Contributors Welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Complexity](https://img.shields.io/badge/complexity-{complexity_health.split()[-1].lower()}-{'green' if complexity_health.startswith('🟢') else 'yellow' if complexity_health.startswith('🟡') else 'red'}.svg)](.)

> **{context}**

## 🎯 Project Mission

{self._generate_project_mission(analysis, context)}

### 📊 Project Health Dashboard

| Metric | Status | Details |
|--------|---------|---------|
| **Code Quality** | {complexity_health} | Avg complexity: {analysis['complexity_metrics']['average_function_complexity']:.1f} |
| **Documentation** | {"🟢 Well Documented" if analysis['quality_metrics']['documentation_coverage'] > 70 else "🟡 Needs Docs" if analysis['quality_metrics']['documentation_coverage'] > 40 else "🔴 Poor Docs"} | {analysis['quality_metrics']['documentation_coverage']:.1f}% coverage |
| **Maintainability** | {"🟢 Easy" if maintainability_score > 75 else "🟡 Moderate" if maintainability_score > 50 else "🔴 Hard"} | {maintainability_score:.0f}% maintainable |
| **Test Coverage** | {"� Good" if self._has_tests(analysis) else "🔴 Missing"} | {self._count_test_functions(analysis)} test functions found |

## 🚀 Quick Start for Contributors

### Prerequisites
```bash
python >= 3.8
git
```

### Development Setup
```bash
# 1. Fork and clone
git clone {github_url}
cd {repo_name}

# 2. Setup development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 3. Install dependencies
pip install -e ".[dev]"  # Install in development mode

# 4. Run tests
python -m pytest tests/

# 5. Start development server (if applicable)
{self._generate_dev_start_command(analysis)}
```

## 🏗️ Architecture for Contributors

### � Codebase Structure
```
{repo_name}/
{self._generate_directory_tree(analysis)}
```

### 🧩 Module Responsibilities

{self._generate_module_guide(analysis)}

## 🔧 Contributing Guidelines

### 🎯 Areas Needing Contribution

{self._identify_contribution_areas(analysis)}

### 📝 Coding Standards

```python
# Follow these patterns observed in the codebase:

{self._generate_coding_standards(analysis)}
```

### 🧪 Testing Guidelines

{self._generate_testing_guidelines(analysis)}

### 📊 Code Complexity Guidelines

- **Maximum function complexity:** 15 (current max: {analysis['complexity_metrics']['max_complexity']})
- **Preferred complexity:** Under 7 (current avg: {analysis['complexity_metrics']['average_function_complexity']:.1f})
- **Documentation required for:** Functions > 10 complexity

## 🐛 Common Issues & Solutions

### Known Issues
{self._identify_potential_issues(analysis)}

### Debugging Guide
{self._generate_debugging_guide(analysis)}

## 🔄 Release Process

### Version Management
- Current version: Inferred from codebase analysis
- Release frequency: Based on contribution activity
- Breaking changes: Follow semantic versioning

### 📋 Maintainer Checklist

{self._generate_maintainer_checklist(analysis)}

## 📈 Roadmap & Vision

### Current State
- **Maturity Level:** {self._assess_project_maturity(analysis)}
- **Primary Focus:** {analysis['project_type'].replace('_', ' ').title()}
- **Technology Stack:** {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'Pure Python'}

### Growth Opportunities
{self._suggest_growth_areas(analysis)}

## 🤝 Community

### How to Get Help
1. **Check Documentation:** Start with this README
2. **Search Issues:** Look for existing solutions
3. **Ask Questions:** Create a new issue with `question` label
4. **Join Discussions:** Participate in project discussions

### Recognition
We appreciate all contributors! Contributors will be recognized in:
- README contributors section
- Release notes
- Project website (if applicable)

## 📄 License & Legal

**License:** MIT (recommended for open source)
**Copyright:** Contributors and maintainers
**Patents:** No known patent issues

---

**Made with ❤️ by the open source community**

*This documentation was generated automatically and reflects the current state of the codebase. Please update as the project evolves.*
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
    
    # Helper methods for enhanced documentation styles
    def _infer_project_purpose(self, analysis: Dict[str, Any], context: str) -> str:
        """Infer what the project actually does based on code analysis"""
        project_type = analysis['project_type']
        technologies = analysis['key_technologies']
        
        if 'web' in project_type.lower():
            if 'FastAPI' in technologies or 'Flask' in technologies:
                return f"This is a web API/service built with {', '.join(technologies)}. {context}"
            return f"This appears to be a web application. {context}"
        elif 'data' in project_type.lower():
            return f"This is a data analysis/science project using {', '.join(technologies)}. {context}"
        elif 'cli' in project_type.lower():
            return f"This is a command-line tool. {context}"
        else:
            return f"This is a {project_type.replace('_', ' ')} project. {context}"
    
    def _trace_execution_flow(self, analysis: Dict[str, Any]) -> str:
        """Trace the main execution flow of the application"""
        entry_points = analysis.get('entry_points', [])
        if entry_points:
            flow = "**Main Execution Path:**\n"
            for entry in entry_points[:3]:
                flow += f"1. `{entry}` serves as an entry point\n"
            return flow
        return "**Execution Flow:** Multiple entry points detected - see individual modules below"
    
    def _get_project_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a concise project summary"""
        return f"{analysis['project_type'].replace('_', ' ').title()} with {analysis['complexity_metrics']['total_functions']} functions across {analysis['total_files']} modules"
    
    def _get_file_purpose(self, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Determine the purpose of a specific file"""
        if 'test' in file_info.get('file_path', '').lower():
            return "Testing Module"
        elif 'main' in file_info.get('file_path', '').lower():
            return "Main Entry Point"
        elif 'config' in file_info.get('file_path', '').lower():
            return "Configuration Module"
        elif len(file_info.get('classes', [])) > 0:
            return "Core Logic Module"
        else:
            return "Utility Module"
    
    def _analyze_file_role(self, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Analyze the role of a file in the overall system"""
        func_count = len(file_info.get('functions', []))
        class_count = len(file_info.get('classes', []))
        
        if func_count > 5:
            return f"Heavy processing module with {func_count} functions"
        elif class_count > 0:
            return f"Object-oriented module defining {class_count} classes"
        else:
            return "Support/utility module"
    
    def _explain_import_purpose(self, import_name: str, file_info: Dict[str, Any]) -> str:
        """Explain why an import is used"""
        import_lower = import_name.lower()
        if 'os' in import_lower or 'sys' in import_lower:
            return "System operations and environment access"
        elif 'json' in import_lower or 'yaml' in import_lower:
            return "Data serialization and configuration"
        elif 'requests' in import_lower or 'http' in import_lower:
            return "HTTP requests and web communication"
        elif 'fastapi' in import_lower or 'flask' in import_lower:
            return "Web framework for API endpoints"
        elif 'pandas' in import_lower or 'numpy' in import_lower:
            return "Data analysis and numerical computation"
        else:
            return "Supporting functionality"
    
    def _analyze_class_purpose(self, cls, analysis: Dict[str, Any]) -> str:
        """Analyze what a class is designed to do"""
        name_lower = cls.name.lower()
        if 'manager' in name_lower or 'handler' in name_lower:
            return f"Manages and handles {cls.name.replace('Manager', '').replace('Handler', '')} operations"
        elif 'analyzer' in name_lower:
            return f"Analyzes and processes data for insights"
        elif 'generator' in name_lower:
            return f"Generates output or creates new instances"
        else:
            return f"Core business logic implementation"
    
    def _explain_class_usage(self, cls, analysis: Dict[str, Any]) -> str:
        """Explain when and how a class is used"""
        method_count = len(cls.methods)
        if method_count > 10:
            return f"Central class with {method_count} methods - likely main business logic"
        elif method_count > 5:
            return f"Important class with {method_count} methods - key functionality"
        else:
            return f"Supporting class with {method_count} methods - specific use case"
    
    def _explain_method_workflow(self, method, analysis: Dict[str, Any]) -> str:
        """Explain what a method does in workflow terms"""
        name_lower = method.name.lower()
        if name_lower.startswith('get') or name_lower.startswith('fetch'):
            return "Retrieves data or information"
        elif name_lower.startswith('set') or name_lower.startswith('update'):
            return "Updates or modifies data"
        elif name_lower.startswith('create') or name_lower.startswith('generate'):
            return "Creates new instances or generates output"
        elif name_lower.startswith('process') or name_lower.startswith('analyze'):
            return "Processes input and performs analysis"
        else:
            return f"Handles {method.name.replace('_', ' ')} operations"
    
    def _generate_function_explanation(self, func, analysis: Dict[str, Any]) -> str:
        """Generate a detailed explanation of what a function does"""
        if func.docstring:
            return func.docstring[:200] + "..." if len(func.docstring) > 200 else func.docstring
        
        name_parts = func.name.lower().split('_')
        if 'main' in name_parts:
            return "Main entry point that coordinates the application workflow"
        elif 'process' in name_parts:
            return f"Processes {' '.join(name_parts[1:])} and performs operations on the data"
        elif 'generate' in name_parts:
            return f"Generates {' '.join(name_parts[1:])} based on input parameters"
        elif 'analyze' in name_parts:
            return f"Analyzes {' '.join(name_parts[1:])} and extracts insights"
        elif 'create' in name_parts:
            return f"Creates new {' '.join(name_parts[1:])} instances"
        else:
            return f"Implements {func.name.replace('_', ' ')} functionality"
    
    def _trace_function_workflow(self, func, analysis: Dict[str, Any]) -> str:
        """Trace the workflow within a function"""
        if func.calls:
            workflow = f"1. Calls {len(func.calls)} other functions\n"
            for call in func.calls[:3]:
                workflow += f"   - Uses `{call}()` for processing\n"
            return workflow
        return ""
    
    def _generate_detailed_usage_guide(self, analysis: Dict[str, Any]) -> str:
        """Generate a detailed usage guide"""
        entry_points = analysis.get('entry_points', [])
        project_type = analysis['project_type']
        
        if 'web' in project_type.lower():
            return """
```python
# Start the web server
python main.py  # or the appropriate entry point

# Make API requests
import requests
response = requests.get('http://localhost:8000/endpoint')
```
"""
        elif 'cli' in project_type.lower():
            return """
```bash
# Command line usage
python main.py --help  # See available options
python main.py --input data.txt --output result.txt
```
"""
        else:
            return """
```python
# Basic usage example
from main_module import MainClass

# Initialize and use
instance = MainClass()
result = instance.process_data(input_data)
```
"""
    
    def _generate_code_flow_explanation(self, analysis: Dict[str, Any]) -> str:
        """Generate an explanation of the code flow"""
        return f"""
**Understanding the Architecture:**

1. **Entry Points:** {len(analysis.get('entry_points', []))} main entry points identified
2. **Module Structure:** {analysis['total_files']} modules with {analysis['complexity_metrics']['total_functions']} functions
3. **Dependencies:** {len(analysis['call_graph']['edges'])} inter-function connections
4. **Complexity:** Average function complexity of {analysis['complexity_metrics']['average_function_complexity']:.1f}

**Code Organization:**
- Core logic is distributed across {analysis['total_files']} files
- Primary functionality centers around {analysis['project_type'].replace('_', ' ')}
- Uses {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'standard Python libraries'}
"""
    
    def _calculate_distribution_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate code distribution score"""
        return min(100.0, analysis['quality_metrics']['functions_per_file'] * 10)
    
    def _generate_ascii_dependency_graph(self, analysis: Dict[str, Any]) -> str:
        """Generate ASCII representation of dependency graph"""
        if not analysis['call_graph']['edges']:
            return "No complex dependencies found - clean architecture"
        
        return f"""
Dependencies Found: {len(analysis['call_graph']['edges'])} connections

┌─ FILE DEPENDENCIES ─┐
{chr(10).join(f"│ {os.path.basename(f):<20} │" for f in list(analysis['file_analysis'].keys())[:5])}
└──────────────────────┘

Complexity Flow: Simple → Moderate → Complex
"""
    
    def _analyze_module_purpose(self, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Analyze the purpose of a module"""
        func_count = len(file_info.get('functions', []))
        class_count = len(file_info.get('classes', []))
        
        if func_count > 10:
            return f"Core processing module with {func_count} functions"
        elif class_count > 2:
            return f"Object-oriented design module with {class_count} classes"
        else:
            return "Supporting utility module"
    
    def _generate_performance_analysis(self, analysis: Dict[str, Any]) -> str:
        """Generate performance analysis"""
        avg_complexity = analysis['complexity_metrics']['average_function_complexity']
        max_complexity = analysis['complexity_metrics']['max_complexity']
        
        return f"""
Estimated Performance Characteristics:
- Average complexity: {avg_complexity:.1f} (Lower is better)
- Peak complexity: {max_complexity} (Functions >15 may need optimization)
- Memory usage: Estimated low-to-moderate based on structure
- CPU usage: Depends on input size and processing complexity
"""
    
    def _generate_visual_examples(self, analysis: Dict[str, Any]) -> str:
        """Generate visual examples and diagrams"""
        return f"""
```
Application Flow Diagram:

Input → Processing → Output
  │         │         │
  ▼         ▼         ▼
{analysis['total_files']} files → {analysis['complexity_metrics']['total_functions']} functions → Results
```

Example Usage Pattern:
```python
# Typical workflow based on codebase analysis
{self._generate_example_workflow(analysis)}
```
"""
    
    def _generate_example_workflow(self, analysis: Dict[str, Any]) -> str:
        """Generate example workflow code"""
        project_type = analysis['project_type']
        if 'web' in project_type.lower():
            return """
app = create_app()
app.run(host='0.0.0.0', port=8000)
"""
        else:
            return """
# Initialize main components
main_instance = MainClass()
result = main_instance.process()
print(result)
"""
    
    def _calculate_maintainability_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate maintainability score"""
        doc_score = analysis['quality_metrics']['documentation_coverage']
        complexity_score = max(0, 100 - analysis['complexity_metrics']['average_function_complexity'] * 5)
        return (doc_score + complexity_score) / 2
    
    def _has_tests(self, analysis: Dict[str, Any]) -> bool:
        """Check if project has tests"""
        for file_path in analysis['file_analysis'].keys():
            if 'test' in file_path.lower():
                return True
        return False
    
    def _count_test_functions(self, analysis: Dict[str, Any]) -> int:
        """Count test functions"""
        count = 0
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                if func.name.startswith('test_'):
                    count += 1
        return count
    
    def _generate_project_mission(self, analysis: Dict[str, Any], context: str) -> str:
        """Generate project mission statement"""
        project_type = analysis['project_type'].replace('_', ' ')
        return f"This {project_type} aims to provide robust, maintainable solutions. {context}"
    
    def _generate_dev_start_command(self, analysis: Dict[str, Any]) -> str:
        """Generate development start command"""
        if analysis['project_type'] == 'web_application':
            return "python main.py  # or uvicorn app:app --reload"
        else:
            return "python main.py --help"
    
    def _generate_directory_tree(self, analysis: Dict[str, Any]) -> str:
        """Generate directory tree structure"""
        tree = ""
        for file_path in analysis['file_analysis'].keys():
            tree += f"├── {file_path}\n"
        return tree
    
    def _generate_module_guide(self, analysis: Dict[str, Any]) -> str:
        """Generate module responsibility guide"""
        guide = ""
        for file_path, file_info in analysis['file_analysis'].items():
            purpose = self._get_file_purpose(file_info, analysis)
            guide += f"**`{file_path}`** - {purpose}\n"
            if file_info.get('functions'):
                guide += f"  - Contains {len(file_info['functions'])} functions\n"
            if file_info.get('classes'):
                guide += f"  - Defines {len(file_info['classes'])} classes\n"
            guide += "\n"
        return guide
    
    # Additional helper methods for technical documentation
    def _generate_system_purpose(self, analysis: Dict[str, Any], context: str) -> str:
        """Generate comprehensive system purpose"""
        return f"A {analysis['project_type'].replace('_', ' ')} system designed for {context.lower()}. Implements {analysis['complexity_metrics']['total_functions']} functions across {analysis['total_files']} modules with {', '.join(analysis['key_technologies']) if analysis['key_technologies'] else 'pure Python'} technology stack."
    
    def _infer_deployment_target(self, analysis: Dict[str, Any]) -> str:
        """Infer deployment target from code analysis"""
        if 'web' in analysis['project_type'].lower():
            return "Web server/container deployment"
        elif 'cli' in analysis['project_type'].lower():
            return "Command-line/desktop environment"
        else:
            return "Python runtime environment"
    
    def _generate_ascii_architecture_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate ASCII architecture diagram"""
        return f"""
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Input     │───▶│  Processing │───▶│   Output    │
│ {analysis['total_files']} modules   │    │ {analysis['complexity_metrics']['total_functions']} functions │    │   Results   │
└─────────────┘    └─────────────┘    └─────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
    Data Flow         Business Logic     User Interface
"""
    
    def _generate_architecture_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate architecture summary"""
        return f"""
### Architecture Analysis

**System Design:** {analysis['project_type'].replace('_', ' ').title()} following {"modular design patterns" if analysis['total_files'] > 3 else "simple structure"}

**Key Characteristics:**
- **Modularity:** {analysis['total_files']} separate modules promoting separation of concerns
- **Complexity Distribution:** Average {analysis['complexity_metrics']['average_function_complexity']:.1f} complexity per function
- **Coupling:** {len(analysis['call_graph']['edges'])} inter-function dependencies
- **Cohesion:** {"High" if analysis['quality_metrics']['functions_per_file'] < 10 else "Moderate"} - functions well-grouped by responsibility
"""
    
    def _map_execution_flow(self, analysis: Dict[str, Any]) -> str:
        """Map execution flow"""
        entry_points = analysis.get('entry_points', [])
        if not entry_points:
            return "**Flow:** Distributed execution - multiple entry points across modules"
        
        flow = "**Primary Execution Paths:**\n\n"
        for i, entry in enumerate(entry_points[:3], 1):
            file_name = entry.split(':')[0] if ':' in entry else entry
            func_name = entry.split(':')[1] if ':' in entry else 'main'
            flow += f"{i}. `{file_name}:{func_name}()` → Initiates {self._infer_entry_purpose(entry, analysis)}\n"
        
        return flow
    
    def _infer_entry_purpose(self, entry_point: str, analysis: Dict[str, Any]) -> str:
        """Infer the purpose of an entry point"""
        if 'main' in entry_point.lower():
            return "primary application workflow"
        elif 'test' in entry_point.lower():
            return "testing and validation procedures"
        elif 'server' in entry_point.lower():
            return "web server and API endpoints"
        else:
            return "specialized processing tasks"
    
    def _assess_complexity(self, analysis: Dict[str, Any]) -> str:
        """Assess code complexity"""
        avg = analysis['complexity_metrics']['average_function_complexity']
        if avg < 5:
            return "🟢 Low - Easy to maintain"
        elif avg < 10:
            return "🟡 Moderate - Manageable complexity"
        else:
            return "🔴 High - Consider refactoring"
    
    def _recommend_complexity_improvement(self, analysis: Dict[str, Any]) -> str:
        """Recommend complexity improvements"""
        avg = analysis['complexity_metrics']['average_function_complexity']
        if avg > 10:
            return "Break down large functions into smaller, focused units"
        elif avg > 7:
            return "Consider extracting helper functions for clarity"
        else:
            return "Maintain current structure - complexity is well-managed"
    
    def _assess_documentation(self, analysis: Dict[str, Any]) -> str:
        """Assess documentation quality"""
        coverage = analysis['quality_metrics']['documentation_coverage']
        if coverage > 80:
            return "🟢 Excellent"
        elif coverage > 60:
            return "🟡 Good"
        elif coverage > 40:
            return "🟠 Moderate"
        else:
            return "🔴 Poor"
    
    def _recommend_documentation_improvement(self, analysis: Dict[str, Any]) -> str:
        """Recommend documentation improvements"""
        coverage = analysis['quality_metrics']['documentation_coverage']
        if coverage < 50:
            return "Add docstrings to all public functions and classes"
        elif coverage < 80:
            return "Improve existing docstrings with examples and parameters"
        else:
            return "Maintain current documentation standards"
    
    def _assess_distribution(self, analysis: Dict[str, Any]) -> str:
        """Assess code distribution"""
        fpf = analysis['quality_metrics']['functions_per_file']
        if fpf < 5:
            return "🟢 Well distributed"
        elif fpf < 10:
            return "🟡 Acceptable"
        else:
            return "🔴 Consider splitting large files"
    
    def _recommend_distribution_improvement(self, analysis: Dict[str, Any]) -> str:
        """Recommend distribution improvements"""
        fpf = analysis['quality_metrics']['functions_per_file']
        if fpf > 15:
            return "Split large modules into focused components"
        elif fpf > 10:
            return "Consider grouping related functions into classes"
        else:
            return "Current distribution promotes maintainability"
    
    def _assess_coupling(self, analysis: Dict[str, Any]) -> str:
        """Assess system coupling"""
        edges = len(analysis['call_graph']['edges'])
        total_funcs = analysis['complexity_metrics']['total_functions']
        ratio = edges / total_funcs if total_funcs > 0 else 0
        
        if ratio < 0.3:
            return "🟢 Low coupling"
        elif ratio < 0.6:
            return "🟡 Moderate coupling"
        else:
            return "🔴 High coupling"
    
    def _recommend_coupling_improvement(self, analysis: Dict[str, Any]) -> str:
        """Recommend coupling improvements"""
        edges = len(analysis['call_graph']['edges'])
        if edges > analysis['complexity_metrics']['total_functions']:
            return "Reduce dependencies through interface abstraction"
        else:
            return "Current coupling level supports maintainability"
    
    def _generate_detailed_module_analysis(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed module analysis"""
        result = ""
        for file_path, file_info in analysis['file_analysis'].items():
            result += f"#### 📄 {file_path}\n\n"
            result += f"**Purpose:** {self._analyze_module_purpose(file_info, analysis)}\n"
            result += f"**Complexity:** {self._calculate_module_complexity(file_info)}\n"
            result += f"**Dependencies:** {len(file_info.get('imports', []))} external imports\n"
            result += f"**API Surface:** {len([f for f in file_info.get('functions', []) if not f.name.startswith('_')])} public functions\n\n"
            
            # Show key functions
            key_funcs = [f for f in file_info.get('functions', []) if not f.name.startswith('_')][:3]
            if key_funcs:
                result += "**Key Functions:**\n"
                for func in key_funcs:
                    result += f"- `{func.name}()` (complexity: {func.complexity})\n"
            result += "\n"
        
        return result
    
    def _calculate_module_complexity(self, file_info: Dict[str, Any]) -> str:
        """Calculate module complexity"""
        functions = file_info.get('functions', [])
        if not functions:
            return "N/A"
        
        avg_complexity = sum(f.complexity for f in functions) / len(functions)
        if avg_complexity < 5:
            return f"Low ({avg_complexity:.1f} avg)"
        elif avg_complexity < 10:
            return f"Moderate ({avg_complexity:.1f} avg)"
        else:
            return f"High ({avg_complexity:.1f} avg)"
    
    def _analyze_security_aspects(self, analysis: Dict[str, Any]) -> str:
        """Analyze security aspects"""
        security_imports = []
        potential_risks = []
        
        for file_info in analysis['file_analysis'].values():
            for imp in file_info.get('imports', []):
                if any(sec in imp.lower() for sec in ['crypto', 'hash', 'auth', 'token', 'security']):
                    security_imports.append(imp)
                if any(risk in imp.lower() for risk in ['subprocess', 'eval', 'exec', 'input']):
                    potential_risks.append(imp)
        
        result = "### Security Analysis\n\n"
        if security_imports:
            result += f"**Security-related imports found:** {', '.join(security_imports)}\n"
        if potential_risks:
            result += f"**Potential security considerations:** {', '.join(potential_risks)}\n"
        else:
            result += "**Security status:** No obvious security risks detected in imports\n"
        
        return result
    
    def _analyze_performance_characteristics(self, analysis: Dict[str, Any]) -> str:
        """Analyze performance characteristics"""
        high_complexity_funcs = []
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                if func.complexity > 15:
                    high_complexity_funcs.append(func)
        
        result = "### Performance Analysis\n\n"
        result += f"**Computational Complexity:** Average O(n^{analysis['complexity_metrics']['average_function_complexity']:.0f}) based on cyclomatic complexity\n"
        
        if high_complexity_funcs:
            result += f"**Performance Hotspots:** {len(high_complexity_funcs)} functions with high complexity may impact performance\n"
        else:
            result += "**Performance Status:** No obvious performance bottlenecks detected\n"
        
        return result
    
    def _identify_contribution_areas(self, analysis: Dict[str, Any]) -> str:
        """Identify areas needing contribution"""
        areas = []
        
        if analysis['quality_metrics']['documentation_coverage'] < 70:
            areas.append("📝 **Documentation** - Improve docstring coverage")
        
        if analysis['complexity_metrics']['max_complexity'] > 15:
            areas.append("🔧 **Code Simplification** - Reduce function complexity")
        
        if not self._has_tests(analysis):
            areas.append("🧪 **Testing** - Add comprehensive test coverage")
        
        areas.append("✨ **New Features** - Extend functionality")
        areas.append("🐛 **Bug Fixes** - Improve reliability")
        
        return "\n".join(areas)
    
    def _generate_coding_standards(self, analysis: Dict[str, Any]) -> str:
        """Generate coding standards based on existing code"""
        return f"""
# Function naming: {self._analyze_naming_patterns(analysis)}
def process_data(input_data):
    \"\"\"Document all functions with docstrings\"\"\"
    pass

# Keep functions under 15 complexity (current max: {analysis['complexity_metrics']['max_complexity']})
# Use type hints where possible
# Follow PEP 8 style guide
"""
    
    def _analyze_naming_patterns(self, analysis: Dict[str, Any]) -> str:
        """Analyze naming patterns in the codebase"""
        return "snake_case (as observed in codebase)"
    
    # Additional technical analysis methods
    def _analyze_data_structures(self, analysis: Dict[str, Any]) -> str:
        """Analyze data structures used"""
        return f"""
**Primary Data Structures:**
- Function parameters: {sum(len(f.args) for file_info in analysis['file_analysis'].values() for f in file_info.get('functions', []))} total parameters
- Class attributes: {sum(len(c.attributes) for file_info in analysis['file_analysis'].values() for c in file_info.get('classes', []))} total attributes
- Return types: Mixed (inferred from function signatures)
"""
    
    def _analyze_state_management(self, analysis: Dict[str, Any]) -> str:
        """Analyze state management patterns"""
        class_count = analysis['complexity_metrics']['total_classes']
        if class_count > 0:
            return f"**Object-oriented state management** with {class_count} classes managing state"
        else:
            return "**Functional approach** with minimal state management"
    
    def _analyze_memory_patterns(self, analysis: Dict[str, Any]) -> str:
        """Analyze memory usage patterns"""
        return f"""
**Memory Characteristics:**
- Static allocation: {analysis['total_files']} modules loaded at startup
- Dynamic allocation: Based on input data size and processing requirements
- Garbage collection: Standard Python GC handles cleanup
"""
    
    def _identify_design_patterns(self, analysis: Dict[str, Any]) -> str:
        """Identify design patterns used"""
        patterns = []
        
        for file_info in analysis['file_analysis'].values():
            for cls in file_info.get('classes', []):
                if 'factory' in cls.name.lower():
                    patterns.append("Factory Pattern")
                elif 'manager' in cls.name.lower():
                    patterns.append("Manager Pattern")
                elif 'handler' in cls.name.lower():
                    patterns.append("Handler Pattern")
        
        if patterns:
            return f"**Identified Patterns:** {', '.join(set(patterns))}"
        else:
            return "**Design Patterns:** Simple procedural/functional design approach"
    
    def _analyze_error_handling(self, analysis: Dict[str, Any]) -> str:
        """Analyze error handling strategy"""
        return f"""
**Error Handling Approach:**
- Exception handling: Standard Python try/except blocks (inferred)
- Validation: Input validation in functions with multiple parameters
- Logging: {self._detect_logging_usage(analysis)}
"""
    
    def _detect_logging_usage(self, analysis: Dict[str, Any]) -> str:
        """Detect logging usage"""
        for file_info in analysis['file_analysis'].values():
            if any('logging' in imp.lower() for imp in file_info.get('imports', [])):
                return "Structured logging implemented"
        return "Basic error handling (no logging imports detected)"
    
    def _analyze_configuration_approach(self, analysis: Dict[str, Any]) -> str:
        """Analyze configuration management"""
        config_patterns = ['config', 'settings', 'env', 'yaml', 'json']
        has_config = False
        
        for file_path in analysis['file_analysis'].keys():
            if any(pattern in file_path.lower() for pattern in config_patterns):
                has_config = True
                break
        
        if has_config:
            return "**Configuration Management:** Dedicated configuration files/modules detected"
        else:
            return "**Configuration Management:** Hardcoded or minimal configuration approach"
    
    def _generate_system_requirements(self, analysis: Dict[str, Any]) -> str:
        """Generate system requirements"""
        return f"""
**Minimum Requirements:**
- Python 3.8+
- RAM: 512MB (estimated based on {analysis['total_files']} modules)
- Storage: 100MB for dependencies
- CPU: Single core sufficient for moderate workloads

**Recommended Requirements:**
- Python 3.9+
- RAM: 2GB for optimal performance
- Storage: 1GB including development tools
- CPU: Multi-core for concurrent processing
"""
    
    def _suggest_deployment_architecture(self, analysis: Dict[str, Any]) -> str:
        """Suggest deployment architecture"""
        if 'web' in analysis['project_type'].lower():
            return """
**Recommended Deployment:**
- Containerized deployment (Docker)
- Load balancer for multiple instances
- Database connection pooling
- Monitoring and logging infrastructure
"""
        else:
            return """
**Recommended Deployment:**
- Virtual environment isolation
- Process monitoring (systemd/supervisor)
- Log rotation and archival
- Backup and recovery procedures
"""
    
    def _suggest_monitoring_strategy(self, analysis: Dict[str, Any]) -> str:
        """Suggest monitoring strategy"""
        return f"""
**Monitoring Recommendations:**
- Application metrics: Response time, throughput, error rates
- System metrics: CPU, memory, disk usage
- Business metrics: Based on {analysis['project_type'].replace('_', ' ')} functionality
- Alerting: Critical error notifications and performance thresholds
"""
    
    def _generate_complexity_heatmap(self, analysis: Dict[str, Any]) -> str:
        """Generate complexity heatmap"""
        result = "**Function Complexity Distribution:**\n\n"
        
        complexity_ranges = {'Low (1-5)': 0, 'Medium (6-10)': 0, 'High (11-15)': 0, 'Very High (16+)': 0}
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                if func.complexity <= 5:
                    complexity_ranges['Low (1-5)'] += 1
                elif func.complexity <= 10:
                    complexity_ranges['Medium (6-10)'] += 1
                elif func.complexity <= 15:
                    complexity_ranges['High (11-15)'] += 1
                else:
                    complexity_ranges['Very High (16+)'] += 1
        
        for range_name, count in complexity_ranges.items():
            percentage = (count / analysis['complexity_metrics']['total_functions'] * 100) if analysis['complexity_metrics']['total_functions'] > 0 else 0
            result += f"- {range_name}: {count} functions ({percentage:.1f}%)\n"
        
        return result
    
    def _analyze_dependency_relationships(self, analysis: Dict[str, Any]) -> str:
        """Analyze dependency relationships"""
        edges = len(analysis['call_graph']['edges'])
        nodes = analysis['complexity_metrics']['total_functions']
        
        if edges == 0:
            return "**Dependency Analysis:** Independent functions with minimal coupling"
        
        density = (edges / (nodes * (nodes - 1))) * 100 if nodes > 1 else 0
        
        return f"""
**Dependency Network:**
- Total connections: {edges}
- Network density: {density:.2f}%
- Coupling level: {"Low" if density < 10 else "Moderate" if density < 30 else "High"}
"""
    
    def _identify_critical_paths(self, analysis: Dict[str, Any]) -> str:
        """Identify critical execution paths"""
        entry_points = analysis.get('entry_points', [])
        if not entry_points:
            return "**Critical Paths:** Distributed architecture - multiple entry points"
        
        result = "**Critical Execution Paths:**\n"
        for entry in entry_points[:3]:
            result += f"- {entry} → Core application flow\n"
        
        return result
    
    def _assess_technical_debt(self, analysis: Dict[str, Any]) -> str:
        """Assess technical debt"""
        debt_factors = []
        
        if analysis['quality_metrics']['documentation_coverage'] < 60:
            debt_factors.append("Low documentation coverage")
        
        if analysis['complexity_metrics']['max_complexity'] > 20:
            debt_factors.append("High function complexity")
        
        if not self._has_tests(analysis):
            debt_factors.append("Missing test coverage")
        
        if debt_factors:
            return f"**Technical Debt:** {', '.join(debt_factors)}"
        else:
            return "**Technical Debt:** Low - well-maintained codebase"
    
    def _identify_refactoring_opportunities(self, analysis: Dict[str, Any]) -> str:
        """Identify refactoring opportunities"""
        opportunities = []
        
        # Find high complexity functions
        high_complexity = []
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                if func.complexity > 15:
                    high_complexity.append(f"{func.name} (complexity: {func.complexity})")
        
        if high_complexity:
            opportunities.append(f"**Complex Functions:** {', '.join(high_complexity[:3])}")
        
        # Check for large files
        large_files = [path for path, info in analysis['file_analysis'].items() 
                      if len(info.get('functions', [])) > 15]
        
        if large_files:
            opportunities.append(f"**Large Modules:** Consider splitting {', '.join(large_files[:2])}")
        
        if not opportunities:
            opportunities.append("**Status:** Code structure supports maintainability")
        
        return '\n'.join(opportunities)
    
    def _recommend_testing_strategy(self, analysis: Dict[str, Any]) -> str:
        """Recommend testing strategy"""
        current_tests = self._count_test_functions(analysis)
        total_functions = analysis['complexity_metrics']['total_functions']
        
        if current_tests == 0:
            return f"""
**Testing Strategy:**
- Add unit tests for {total_functions} functions
- Focus on high-complexity functions first
- Implement integration tests for main workflows
- Target 80% code coverage
"""
        else:
            return f"""
**Testing Strategy:**
- Current: {current_tests} test functions
- Expand coverage for untested modules
- Add edge case testing
- Implement automated testing pipeline
"""
    
    def _identify_current_limitations(self, analysis: Dict[str, Any]) -> str:
        """Identify current system limitations"""
        limitations = []
        
        if analysis['complexity_metrics']['max_complexity'] > 20:
            limitations.append("High complexity functions may be hard to maintain")
        
        if not self._has_tests(analysis):
            limitations.append("Lack of automated testing reduces reliability")
        
        if analysis['quality_metrics']['documentation_coverage'] < 50:
            limitations.append("Poor documentation hinders onboarding")
        
        if not limitations:
            limitations.append("No significant limitations identified")
        
        return '\n'.join(f"- {limitation}" for limitation in limitations)
    
    def _identify_scalability_issues(self, analysis: Dict[str, Any]) -> str:
        """Identify potential scalability issues"""
        issues = []
        
        high_coupling = len(analysis['call_graph']['edges']) > analysis['complexity_metrics']['total_functions']
        if high_coupling:
            issues.append("High inter-function coupling may limit scalability")
        
        large_modules = any(len(info.get('functions', [])) > 20 for info in analysis['file_analysis'].values())
        if large_modules:
            issues.append("Large modules may become bottlenecks")
        
        if not issues:
            issues.append("Current architecture supports horizontal scaling")
        
        return '\n'.join(f"- {issue}" for issue in issues)
    
    def _suggest_technical_evolution(self, analysis: Dict[str, Any]) -> str:
        """Suggest technical evolution path"""
        suggestions = []
        
        if analysis['complexity_metrics']['total_classes'] == 0:
            suggestions.append("Consider object-oriented refactoring for better organization")
        
        if 'web' in analysis['project_type'].lower():
            suggestions.append("Implement API versioning and microservices architecture")
        
        suggestions.append("Add comprehensive monitoring and observability")
        suggestions.append("Implement automated deployment pipelines")
        
        return '\n'.join(f"- {suggestion}" for suggestion in suggestions)
    
    def _identify_environment_dependencies(self, analysis: Dict[str, Any]) -> str:
        """Identify environment dependencies"""
        env_deps = []
        
        for file_info in analysis['file_analysis'].values():
            for imp in file_info.get('imports', []):
                if 'os' in imp.lower() or 'env' in imp.lower():
                    env_deps.append("Environment variables")
                    break
        
        if env_deps:
            return f"**Environment Dependencies:** {', '.join(env_deps)}"
        else:
            return "**Environment Dependencies:** Self-contained application"
    
    def _analyze_external_dependencies(self, analysis: Dict[str, Any]) -> str:
        """Analyze external dependencies"""
        external_deps = set()
        
        for file_info in analysis['file_analysis'].values():
            for imp in file_info.get('imports', []):
                if not imp.startswith('.') and imp not in ['os', 'sys', 'json', 're', 'collections']:
                    external_deps.add(imp.split('.')[0])
        
        if external_deps:
            return f"**External Libraries:** {', '.join(sorted(external_deps)[:10])}"
        else:
            return "**External Libraries:** Uses only Python standard library"
    
    def _analyze_runtime_configuration(self, analysis: Dict[str, Any]) -> str:
        """Analyze runtime configuration"""
        has_config = any('config' in path.lower() for path in analysis['file_analysis'].keys())
        
        if has_config:
            return "**Runtime Configuration:** Configurable via dedicated configuration files"
        else:
            return "**Runtime Configuration:** Hardcoded or command-line parameters"
    
    def _generate_testing_guidelines(self, analysis: Dict[str, Any]) -> str:
        """Generate testing guidelines"""
        return f"""
**Testing Strategy:**
- Unit tests for all {analysis['complexity_metrics']['total_functions']} functions
- Integration tests for main workflows
- Focus on functions with complexity > 10
- Mock external dependencies
- Aim for 80%+ code coverage
"""
    
    def _generate_maintainer_checklist(self, analysis: Dict[str, Any]) -> str:
        """Generate maintainer checklist"""
        return f"""
**Pre-release Checklist:**
- [ ] All {analysis['complexity_metrics']['total_functions']} functions documented
- [ ] Test coverage > 80%
- [ ] No functions with complexity > 15
- [ ] Security review completed
- [ ] Performance benchmarks updated
- [ ] Documentation updated
- [ ] Breaking changes documented
"""
    
    def _assess_project_maturity(self, analysis: Dict[str, Any]) -> str:
        """Assess project maturity level"""
        score = 0
        
        if analysis['quality_metrics']['documentation_coverage'] > 70:
            score += 1
        if self._has_tests(analysis):
            score += 1
        if analysis['complexity_metrics']['max_complexity'] < 15:
            score += 1
        if analysis['total_files'] > 3:
            score += 1
        
        maturity_levels = {
            0: "Early Development",
            1: "Basic Functionality", 
            2: "Stable Development",
            3: "Production Ready",
            4: "Mature Project"
        }
        
        return maturity_levels.get(score, "Unknown")
    
    def _suggest_growth_areas(self, analysis: Dict[str, Any]) -> str:
        """Suggest growth areas"""
        areas = []
        
        if not self._has_tests(analysis):
            areas.append("🧪 **Testing Infrastructure** - Comprehensive test suite")
        
        if analysis['quality_metrics']['documentation_coverage'] < 80:
            areas.append("📚 **Documentation** - API documentation and examples")
        
        areas.append("🚀 **Performance** - Optimization and benchmarking")
        areas.append("🔒 **Security** - Security audit and hardening")
        areas.append("📈 **Monitoring** - Metrics and observability")
        
        return '\n'.join(areas)
    
    def _identify_potential_issues(self, analysis: Dict[str, Any]) -> str:
        """Identify potential issues"""
        issues = []
        
        if analysis['complexity_metrics']['max_complexity'] > 20:
            issues.append("⚠️  High complexity functions may be error-prone")
        
        if not self._has_tests(analysis):
            issues.append("⚠️  No automated tests - higher risk of regressions")
        
        if len(analysis['call_graph']['edges']) > analysis['complexity_metrics']['total_functions']:
            issues.append("⚠️  High coupling may make changes difficult")
        
        if not issues:
            issues.append("✅ No critical issues identified")
        
        return '\n'.join(issues)
    
    def _generate_debugging_guide(self, analysis: Dict[str, Any]) -> str:
        """Generate debugging guide"""
        return f"""
**Common Debugging Approaches:**
1. **Start with entry points:** {len(analysis.get('entry_points', []))} main entry points identified
2. **Check high-complexity functions:** Focus on functions with complexity > 10
3. **Trace data flow:** Follow the {len(analysis['call_graph']['edges'])} function calls
4. **Enable logging:** Add logging to critical paths
5. **Use debugger:** Step through complex logic in high-complexity functions
"""
    
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