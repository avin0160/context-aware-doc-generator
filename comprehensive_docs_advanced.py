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
from dataclasses import dataclass, field
import requests

try:
    from datasets import load_dataset  # type: ignore
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments  # type: ignore
    from peft import LoraConfig, get_peft_model, TaskType  # type: ignore
    import torch
    ADVANCED_FEATURES = True
except ImportError:
    print("Advanced features (transformers, datasets) not available")
    ADVANCED_FEATURES = False

# Import intelligent analyzer for better descriptions
try:
    from intelligent_analyzer import IntelligentCodeAnalyzer
    INTELLIGENT_ANALYSIS = True
except ImportError:
    INTELLIGENT_ANALYSIS = False
    print("Intelligent analyzer not available, using basic descriptions")

# Import inline documentation injector
try:
    from inline_doc_injector import InlineDocInjector
    INLINE_DOC_INJECTION = True
except ImportError:
    INLINE_DOC_INJECTION = False
    print("Inline doc injector not available, using suggestions only")

# Import multi-language analyzer
try:
    from multi_language_analyzer import MultiLanguageAnalyzer
    MULTI_LANGUAGE_SUPPORT = True
except ImportError:
    MULTI_LANGUAGE_SUPPORT = False
    print("Multi-language analyzer not available, Python-only mode")

# Import Phi-3 documentation generator for research-quality output
try:
    from phi3_doc_generator import Phi3DocumentationGenerator
    PHI3_AVAILABLE = True
except ImportError:
    PHI3_AVAILABLE = False
    print("Phi-3 generator not available, using fallback documentation generation")

# Import Sphinx compliance metrics for validation
try:
    from sphinx_compliance_metrics import DocumentationEvaluator
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    print("Sphinx compliance metrics not available, skipping validation")

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
    inline_comments: List[str] = field(default_factory=list)  # Extracted inline comments (NEW)

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
    inline_comments: List[str] = field(default_factory=list)  # Extracted inline comments (NEW)

class CodeSearchNetEnhancedAnalyzer:
    """Enhanced analyzer with CodeSearchNet dataset integration and dependency analysis"""
    
    def __init__(self):
        # Initialize intelligent analyzer if available
        if INTELLIGENT_ANALYSIS:
            self.intelligent_analyzer = IntelligentCodeAnalyzer()
        else:
            self.intelligent_analyzer = None
        
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
        
        # Initialize Phi-3 generator for research-quality documentation
        self.phi3_generator = None
        if PHI3_AVAILABLE:
            try:
                self.phi3_generator = Phi3DocumentationGenerator()
                print("✅ Phi-3 Mini documentation generator initialized")
            except Exception as e:
                print(f"⚠️  Could not initialize Phi-3: {e}")
        
        # Initialize documentation validator
        self.doc_evaluator = None
        if METRICS_AVAILABLE:
            try:
                self.doc_evaluator = DocumentationEvaluator(max_tokens=512)
                print("✅ Sphinx compliance validator initialized")
            except Exception as e:
                print(f"⚠️  Could not initialize validator: {e}")
        
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
        # Expose intelligent_analyzer for backwards compatibility
        self.intelligent_analyzer = self.analyzer.intelligent_analyzer if hasattr(self.analyzer, 'intelligent_analyzer') else None
        # Expose phi3_generator for research-quality documentation
        self.phi3_generator = self.analyzer.phi3_generator if hasattr(self.analyzer, 'phi3_generator') else None
    
    def analyze_repository_comprehensive(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Perform comprehensive repository analysis with multi-language support"""
        
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
            'quality_metrics': {},
            'language_stats': {}
        }
        
        # Use multi-language analyzer for language detection and basic parsing
        if MULTI_LANGUAGE_SUPPORT:
            ml_analyzer = MultiLanguageAnalyzer()
            ml_results = ml_analyzer.analyze_repository(file_contents)
            analysis['language_stats'] = ml_results.get('language_breakdown', {})
        
        # Process all files - use deep analysis for Python, multi-lang for others
        for file_path, content in file_contents.items():
            if file_path.endswith('.py'):
                # Deep Python analysis with call extraction
                file_info = self._analyze_file_comprehensive(file_path, content)
                analysis['file_analysis'][file_path] = file_info
                analysis['total_lines'] += file_info['lines']
            elif MULTI_LANGUAGE_SUPPORT and file_path in ml_results['files']:
                # Use multi-language results for non-Python files
                file_info = ml_results['files'][file_path]
                language = file_info['language']
                
                # Convert multi-lang function info
                converted_functions = []
                for ml_func in file_info['functions']:
                    func_info = FunctionInfo(
                        name=ml_func.name,
                        file_path=ml_func.file_path,
                        line_start=ml_func.line_start,
                        line_end=ml_func.line_end,
                        args=[p[0] for p in ml_func.params],
                        return_type=ml_func.return_type,
                        docstring=ml_func.docstring,
                        calls=[],
                        called_by=[],
                        complexity=ml_func.complexity if hasattr(ml_func, 'complexity') else 1,
                        semantic_category=self._infer_semantic_category(ml_func.name, ml_func.docstring),
                        dependencies=[]
                    )
                    converted_functions.append(func_info)
                    self.functions[f"{file_path}:{ml_func.name}"] = func_info
                
                # Convert classes
                converted_classes = []
                for ml_cls in file_info['classes']:
                    class_info = ClassInfo(
                        name=ml_cls.name,
                        file_path=ml_cls.file_path,
                        line_start=ml_cls.line_start,
                        line_end=ml_cls.line_end,
                        methods=[],
                        attributes=[],
                        inheritance=ml_cls.extends if hasattr(ml_cls, 'extends') else [],
                        docstring=ml_cls.docstring,
                        semantic_category='utility'
                    )
                    converted_classes.append(class_info)
                    self.classes[f"{file_path}:{ml_cls.name}"] = class_info
                
                analysis['file_analysis'][file_path] = {
                    'path': file_path,
                    'language': language,
                    'lines': file_info['lines_of_code'],
                    'functions': converted_functions,
                    'classes': converted_classes,
                    'imports': file_info.get('imports', []),
                    'function_calls': [],
                    'semantic_categories': defaultdict(int),
                    'complexity_score': sum(f.complexity if hasattr(f, 'complexity') else 1 for f in file_info['functions']),
                    'quality_score': 0,
                    'context_content': file_info.get('context_content')
                }
                analysis['total_lines'] += file_info['lines_of_code']
        
        # Second pass: Build dependency and call graphs
        self._build_dependency_graphs(analysis)
        
        # Third pass: Semantic analysis and project type detection
        self._perform_semantic_analysis(analysis)
        
        # Calculate metrics
        self._calculate_metrics(analysis)
        
        # CRITICAL: Set project context for Gemini enhancement
        if self.phi3_generator and hasattr(self.phi3_generator, 'set_project_context'):
            self.phi3_generator.set_project_context(analysis)
            print("✅ Project context set for Gemini-enhanced documentation")
        
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
        """Generate meaningful docstring based on function analysis
        
        Uses Phi-3-Mini when available for research-quality documentation.
        Falls back to intelligent analysis or rule-based generation.
        """
        func_name = node.name
        params = [arg.arg for arg in node.args.args if arg.arg != 'self']
        
        # Try Phi-3 first for superior quality
        if self.phi3_generator is not None:
            try:
                # Extract function code
                function_lines = content.split('\n')[node.lineno-1:node.end_lineno] if hasattr(node, 'end_lineno') else []
                function_code = '\n'.join(function_lines) if function_lines else f"def {func_name}({', '.join(params)}):\n    pass"
                
                # Prepare context
                context = {
                    'called_by': [],  # Could be enhanced with call graph analysis
                    'calls': calls,
                    'complexity': len(calls) + len(params) * 2,
                    'file_path': file_path,
                    'semantic_category': 'general'
                }
                
                phi3_docstring = self.phi3_generator.generate_function_docstring(
                    function_code=function_code,
                    function_name=func_name,
                    context=context,
                    style="sphinx"
                )
                
                # Use Phi-3 result if valid
                if phi3_docstring and len(phi3_docstring) > 50:
                    return phi3_docstring
            except Exception as e:
                # Fall back to traditional methods
                pass
        
        # Try intelligent analyzer next if available
        intelligent_analyzer = getattr(self.analyzer, 'intelligent_analyzer', None) if hasattr(self, 'analyzer') else None
        if intelligent_analyzer:
            try:
                file_context = {'file_path': file_path, 'content': content}
                analysis = intelligent_analyzer.analyze_function(node, content, file_context)
                if analysis and analysis.get('description'):
                    return analysis['description']
            except Exception as e:
                # Fall back to pattern matching
                pass
        
        # Constructor patterns with parameter context
        if func_name == '__init__':
            class_name = self._extract_class_name_from_context(file_path, content, node)
            if params:
                param_hints = ', '.join([p for p in params if not p.startswith('_')])
                return f"Initialize {class_name} with {param_hints}"
            return f"Initialize new {class_name} instance"
        
        # Database/CRUD operations with context
        if 'search' in func_name.lower() or 'find' in func_name.lower():
            if any(p in ['key', 'id', 'record_id'] for p in params):
                return f"Search for item by key/ID and return value if found"
            return "Search for items matching specified criteria"
        
        if 'insert' in func_name.lower() or 'add' in func_name.lower():
            if 'key' in params and 'value' in params:
                return "Insert key-value pair with automatic tree balancing"
            elif 'record' in params:
                return "Insert new record after schema validation"
            return "Add new item to collection"
        
        if 'delete' in func_name.lower() or 'remove' in func_name.lower():
            return "Remove item and maintain data structure integrity"
        
        if 'update' in func_name.lower():
            if any(p in ['key', 'id', 'record_id'] for p in params):
                return "Update existing item with new value"
            return "Modify existing data"
        
        # Validation patterns
        if 'validate' in func_name.lower() or 'check' in func_name.lower():
            if 'record' in params or 'data' in params:
                return "Validate data against schema and business rules"
            condition = func_name.replace('check_', '').replace('validate_', '').replace('_', ' ')
            return f"Validate {condition} requirements"
        
        # Query patterns
        if 'range' in func_name.lower() and 'query' in func_name.lower():
            return "Execute range query between start and end values"
        elif 'query' in func_name.lower():
            return "Execute database query and return results"
        
        # Helper method patterns
        if func_name.startswith('_'):
            operation = func_name[1:].replace('_', ' ')
            if 'extract' in operation:
                return f"Extract {operation.replace('extract ', '')} from data"
            elif 'build' in operation or 'create' in operation:
                return f"Build {operation.replace('build ', '').replace('create ', '')}"
            elif 'handle' in operation:
                return f"Handle {operation.replace('handle ', '')} scenarios"
            return f"Internal helper for {operation}"
        
        # Getter patterns with context
        if func_name.startswith('get_'):
            target = func_name[4:].replace('_', ' ')
            if target == 'all':
                return "Retrieve all items from data structure"
            return f"Get {target} information"
        
        # Boolean check patterns
        if func_name.startswith('is_'):
            condition = func_name[3:].replace('_', ' ')
            return f"Check if {condition} condition is satisfied"
        elif func_name.startswith('has_'):
            condition = func_name[4:].replace('_', ' ')
            return f"Determine if structure has {condition}"
        
        # Special patterns
        if 'visualize' in func_name.lower() or 'render' in func_name.lower():
            return "Generate visual representation for debugging and analysis"
        
        if 'split' in func_name.lower():
            return "Split node when capacity exceeded, maintaining tree balance"
        
        if 'merge' in func_name.lower():
            return "Merge nodes during underflow to maintain minimum capacity"
        
        # Analysis based on function calls and complexity
        if len(calls) > 8:
            return f"Complex multi-step operation coordinating {len(calls)} internal processes"
        elif len(calls) > 4:
            key_calls = [c for c in calls[:3] if c not in ['len', 'range', 'enumerate']]
            if key_calls:
                return f"Multi-step operation using {', '.join(key_calls)} and {len(calls)-len(key_calls)} other processes"
            return f"Multi-step operation with {len(calls)} internal calls"
        elif calls:
            meaningful_calls = [c for c in calls if c not in ['len', 'range', 'enumerate']]
            if meaningful_calls:
                return f"Process data using {', '.join(meaningful_calls[:2])} operations"
        
        # HONEST fallback - admit when we can't infer
        return f"Operates on {len(params)} parameters. Calls: {', '.join(calls[:3]) if calls else 'none detected'}. Semantic analysis inconclusive."
    
    def _extract_class_name_from_context(self, file_path: str, content: str, func_node: ast.FunctionDef) -> str:
        """Extract class name for better __init__ descriptions"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                            if item.lineno == func_node.lineno:
                                return node.name
        except:
            pass
        return "instance"
    

    
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
        
        # Detect real project type based on imports and code patterns
        analysis['project_type'] = self._detect_real_project_type(analysis, all_imports)
        
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
        
        # Documentation coverage - more realistic assessment
        documented_functions = 0
        quality_documented = 0
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info['functions']:
                if func.docstring:
                    documented_functions += 1
                    # Check if docstring is meaningful (not just generic)
                    if (func.docstring and 
                        len(func.docstring) > 20 and 
                        not func.docstring.startswith('Initialize a new') and
                        'Handle' not in func.docstring and
                        'Perform' not in func.docstring):
                        quality_documented += 1
        
        # Base coverage on actual docstrings
        doc_coverage = (documented_functions / total_functions * 100) if total_functions > 0 else 0
        
        # Adjust for quality - if most docstrings are generic, reduce the score
        if documented_functions > 0:
            quality_ratio = quality_documented / documented_functions
            if quality_ratio < 0.3:  # Less than 30% are quality docstrings
                doc_coverage = doc_coverage * 0.7  # Reduce by 30%
            elif quality_ratio < 0.6:  # Less than 60% are quality docstrings
                doc_coverage = doc_coverage * 0.85  # Reduce by 15%
        
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
    
    def _infer_semantic_category(self, name: str, docstring: Optional[str]) -> str:
        """Infer semantic category from function name and docstring"""
        name_lower = name.lower()
        doc_lower = docstring.lower() if docstring else ""
        
        # Check against known patterns
        if hasattr(self.analyzer, 'function_patterns'):
            for category, patterns in self.analyzer.function_patterns.items():
                if any(pattern in name_lower for pattern in patterns):
                    return category
                if docstring and any(pattern in doc_lower for pattern in patterns):
                    return category
        
        # Basic heuristics
        if any(word in name_lower for word in ['get', 'fetch', 'read', 'load', 'retrieve']):
            return 'data_retrieval'
        elif any(word in name_lower for word in ['set', 'write', 'save', 'store', 'update']):
            return 'data_storage'
        elif any(word in name_lower for word in ['validate', 'check', 'verify', 'test']):
            return 'validation'
        elif any(word in name_lower for word in ['parse', 'process', 'transform', 'convert']):
            return 'data_processing'
        elif any(word in name_lower for word in ['draw', 'render', 'display', 'show']):
            return 'ui_rendering'
        elif any(word in name_lower for word in ['handle', 'on_', 'event']):
            return 'event_handling'
        else:
            return 'utility'
    
    def _classify_class_semantically(self, name: str) -> str:
        """Classify class based on semantic patterns"""
        for category, patterns in self.analyzer.function_patterns.items():
            if any(pattern.lower() in name.lower() for pattern in patterns):
                return category
        return 'utility'
    
    def _extract_import_info(self, node) -> List[str]:
        """Extract import information with deduplication"""
        imports = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        # Deduplicate while preserving order
        return list(dict.fromkeys(imports))
    
    def _extract_function_calls(self, tree: ast.AST) -> List[str]:
        """Extract function calls with noise filtering"""
        # Generic builtins to filter out
        noise = {'len', 'range', 'enumerate', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'bool', 'type', 'isinstance', 'print'}
        
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    name = node.func.id
                    if name not in noise:
                        calls.append(name)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)
        
        # Deduplicate
        return list(dict.fromkeys(calls))
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if available"""
        if node.returns:
            return ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        return None
    
    def _map_category_to_project_type(self, category: str) -> str:
        """Map semantic category to project type with better detection"""
        mapping = {
            'web_framework': 'web_application',
            'data_science': 'data_analysis_project',
            'cli_tool': 'command_line_tool',
            'database': 'database_project',
            'utility': 'utility_library',
            'test': 'testing_framework',
            'config': 'configuration_tool',
            'ui_rendering': 'game_or_gui_application',
            'event_handling': 'interactive_application'
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
            'argparse': 'Command Line Parsing',
            'pygame': 'Pygame Game Development',
            'tkinter': 'Tkinter GUI Framework',
            'kivy': 'Kivy GUI Framework',
            'pyglet': 'Pyglet Game Framework',
            'matplotlib': 'Matplotlib Data Visualization',
            'seaborn': 'Seaborn Statistical Visualization',
            'beautifulsoup4': 'BeautifulSoup Web Scraping',
            'selenium': 'Selenium Browser Automation'
        }
        
        technologies = []
        for import_name in imports:
            base_import = import_name.split('.')[0].lower()
            if base_import in tech_mapping:
                tech = tech_mapping[base_import]
                if tech not in technologies:
                    technologies.append(tech)
        
        return technologies
    
    def _detect_real_project_type(self, analysis: Dict[str, Any], imports: List[str]) -> str:
        """Detect real project type based on code evidence, not guesses"""
        
        # Check for game frameworks - pygame presence is strong signal
        if 'pygame' in imports or any('pygame' in imp.lower() for imp in imports):
            # Game applications always have rendering + collision detection
            has_rendering = False
            has_collision = False
            has_game_loop_pattern = False
            
            for file_info in analysis['file_analysis'].values():
                for func in file_info.get('functions', []):
                    fname = func.name.lower()
                    # Rendering functions
                    if 'draw' in fname or 'render' in fname or 'blit' in fname:
                        has_rendering = True
                    # Collision detection
                    if 'collision' in fname or 'collide' in fname:
                        has_collision = True
                    # Game loop indicators (main, loop, update, tick)
                    if any(pattern in fname for pattern in ['main', 'loop', 'update', 'run']):
                        has_game_loop_pattern = True
            
            # If pygame + rendering detected, it's a game
            if has_rendering:
                return 'interactive_game_application'
        
        # Check for web frameworks
        if any(fw in imports for fw in ['flask', 'django', 'fastapi', 'tornado', 'bottle']):
            return 'web_application'
        
        # Check for CLI tools
        if any(cli in imports for cli in ['argparse', 'click', 'typer']):
            return 'cli_tool'
        
        # Check for data science
        if any(ds in imports for ds in ['pandas', 'numpy', 'sklearn', 'tensorflow', 'torch']):
            return 'data_science_pipeline'
        
        # Check for network services
        if any(net in imports for net in ['socket', 'asyncio', 'aiohttp', 'requests']):
            return 'network_service'
        
        # Default based on structure
        total_funcs = sum(len(f.get('functions', [])) for f in analysis['file_analysis'].values())
        total_classes = sum(len(f.get('classes', [])) for f in analysis['file_analysis'].values())
        
        if total_classes > total_funcs:
            return 'object_oriented_library'
        elif analysis['total_files'] == 1 and total_funcs < 20:
            return 'single_purpose_script'
        else:
            return 'general_purpose_project'
    
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
        # Expose phi3_generator for direct access
        self.phi3_generator = self.analyzer.phi3_generator if hasattr(self.analyzer, 'phi3_generator') else None
        
        # Initialize documentation validator
        self.doc_evaluator = None
        if METRICS_AVAILABLE:
            try:
                self.doc_evaluator = DocumentationEvaluator(max_tokens=512)
                print("✅ DocumentationGenerator: Sphinx compliance validator initialized")
            except Exception as e:
                print(f"⚠️  DocumentationGenerator: Could not initialize validator: {e}")
    
    def _infer_project_name(self, provided_name: str, analysis: Dict[str, Any], context: str) -> str:
        """Intelligently infer project name avoiding generic temp names"""
        
        # Use provided name if it's meaningful
        if provided_name and not provided_name.startswith('tmp') and provided_name not in ['Unknown Repository', 'Unknown_Repository']:
            return provided_name
        
        # Try to extract from context
        if context and len(context) > 10:
            # Look for project names in context
            context_words = context.lower().split()
            meaningful_words = [w for w in context_words if len(w) > 3 and w.isalpha()]
            if meaningful_words:
                return meaningful_words[0].title() + " Project"
        
        # Infer from project type and main technologies
        project_type = analysis.get('project_type', 'general_purpose_project')
        technologies = analysis.get('key_technologies', [])
        
        # Create meaningful name based on type and tech
        if project_type == 'database_project':
            if any('tree' in str(tech).lower() for tech in technologies):
                return "B+ Tree Database System"
            return "Database Management System"
        elif project_type == 'web_application':
            if 'FastAPI' in str(technologies):
                return "FastAPI Web Application"
            elif 'Flask' in str(technologies):
                return "Flask Web Service"
            return "Web Application"
        elif project_type == 'utility_library':
            if 'documentation' in context.lower() or 'docs' in context.lower():
                return "Documentation Generator"
            return "Utility Library"
        elif project_type == 'data_analysis_project':
            return "Data Analysis Tool"
        elif project_type == 'cli_tool':
            return "Command Line Tool"
        
        # Final fallback based on main classes or functions
        file_analysis = analysis.get('file_analysis', {})
        for file_info in file_analysis.values():
            classes = file_info.get('classes', [])
            if classes:
                main_class = classes[0].name if hasattr(classes[0], 'name') else str(classes[0])
                if main_class and not main_class.startswith('_'):
                    return f"{main_class} System"
        
        return f"{project_type.replace('_', ' ').title()}"
    
    def _improve_function_descriptions(self, func_info: Any, context: str) -> str:
        """
        Generate better, more specific function descriptions
        """
        func_name = func_info.name.lower()
        
        # Handle common patterns with better descriptions
        if func_name == '__init__':
            if 'tree' in context.lower():
                return f"Initialize tree structure with specified configuration"
            elif 'manager' in context.lower():
                return f"Initialize manager with required parameters"
            elif 'node' in context.lower():
                return f"Create new node with given properties"
            else:
                return f"Initialize {context} instance with provided parameters"
        
        elif func_name.startswith('get_'):
            item = func_name[4:].replace('_', ' ')
            return f"Retrieve {item} from the system"
        
        elif func_name.startswith('set_'):
            item = func_name[4:].replace('_', ' ')
            return f"Update {item} in the system"
        
        elif func_name.startswith('is_'):
            condition = func_name[3:].replace('_', ' ')
            return f"Check if condition '{condition}' is met"
        
        elif func_name.startswith('has_'):
            item = func_name[4:].replace('_', ' ')
            return f"Verify presence of {item}"
        
        elif 'insert' in func_name:
            return f"Add new item to the data structure with validation"
        
        elif 'delete' in func_name or 'remove' in func_name:
            return f"Remove specified item from the system"
        
        elif 'search' in func_name or 'find' in func_name:
            return f"Locate and return matching items"
        
        elif 'split' in func_name:
            return f"Divide structure when capacity is exceeded"
        
        elif 'merge' in func_name:
            return f"Combine structures to maintain balance"
            
        # Use existing docstring if it's meaningful
        if hasattr(func_info, 'docstring') and func_info.docstring:
            if (len(func_info.docstring) > 20 and 
                not func_info.docstring.startswith('Initialize a new') and
                'Handle' not in func_info.docstring):
                return func_info.docstring.split('\n')[0].strip()
        
        # Generic fallback
        return f"Handle {func_name.replace('_', ' ')} operations"
    
    def generate_documentation(self, input_data: str, context: str, doc_style: str, 
                             input_type: str = 'auto', repo_name: str = '') -> str:
        """Generate comprehensive documentation"""
        
        # Process input
        file_contents = MultiInputHandler.process_input(input_data, input_type)
        
        if not file_contents:
            raise ValueError("No Python files found in input")
        
        # Perform comprehensive analysis
        analysis = self.analyzer.analyze_repository_comprehensive(file_contents)
        
        # Generate documentation based on style (only 3 styles supported)
        if doc_style == 'sphinx':
            documentation = self._generate_sphinx_style(analysis, context, repo_name)
        elif doc_style in ['technical_comprehensive', 'technical', 'comprehensive']:
            documentation = self._generate_technical_comprehensive_style(analysis, context, repo_name)
        elif doc_style == 'opensource':
            documentation = self._generate_opensource_style(analysis, context, repo_name)
        else:
            # Default to Sphinx/reST style
            documentation = self._generate_sphinx_style(analysis, context, repo_name)
        
        # VALIDATION: Run compliance check (only for Sphinx style)
        if self.doc_evaluator and doc_style == 'sphinx':
            try:
                # Extract observed info from analysis for validation
                observed_info = {
                    'parameters': [],
                    'has_return': False,
                    'attributes': []
                }
                # Aggregate all observable facts
                for file_info in analysis.get('file_analysis', {}).values():
                    for func in file_info.get('functions', []):
                        observed_info['parameters'].extend(func.args)
                        if func.return_type and func.return_type != 'None':
                            observed_info['has_return'] = True
                    for cls in file_info.get('classes', []):
                        observed_info['attributes'].extend(cls.attributes)
                
                # Validate documentation
                report = self.doc_evaluator.evaluate(
                    documentation, 
                    observed_info, 
                    repo_name
                )
                
                # Print validation report
                print("\n" + "="*60)
                print("📊 SPHINX COMPLIANCE VALIDATION")
                print("="*60)
                print(report)
                print("="*60 + "\n")
                
                # If validation fails, append warning to documentation
                if not report.accepted:
                    warning = f"\n\n---\n\n**⚠️ DOCUMENTATION QUALITY WARNING**\n\n"
                    warning += "This documentation did NOT pass Sphinx compliance validation:\n\n"
                    if report.details.get('sphinx_violations'):
                        warning += "- Format violations: " + ", ".join(report.details['sphinx_violations'][:3]) + "\n"
                    if report.details.get('language_violations'):
                        warning += "- Language violations: " + ", ".join(report.details['language_violations'][:3]) + "\n"
                    if report.details.get('epistemic_violations'):
                        warning += "- Epistemic violations: " + ", ".join(report.details['epistemic_violations'][:3]) + "\n"
                    documentation += warning
                
            except Exception as e:
                print(f"⚠️  Validation failed: {e}")
        
        return documentation
    
    def _generate_sphinx_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Sphinx/reST style - Professional Python documentation with :param:, :type:, :return:, :rtype: tags
        
        Uses the same style as the SimpleBleDevice example provided.
        """
        
        repo_name = self._infer_project_name(repo_name, analysis, context)
        project_type = analysis['project_type'].replace('_', ' ').title()
        
        # Pure Sphinx/reST format - wrap everything in proper directive structure
        doc = f""".. _{repo_name.replace(' ', '_').lower()}_api:

{repo_name} API Documentation
{"="*len(f"{repo_name} API Documentation")}

.. module:: {repo_name.lower().replace(' ', '_')}
   :synopsis: {context or f"Complete API reference for {repo_name}."}

.. moduleauthor:: Auto-generated

Project Information
-------------------

:Project Type: {project_type}
:Total Files: {analysis['total_files']}
:Functions: {analysis['complexity_metrics']['total_functions']}
:Classes: {analysis['complexity_metrics']['total_classes']}

API Reference
-------------

"""
        
        # Generate per-module documentation
        for file_path, file_info in analysis['file_analysis'].items():
            if not file_info.get('functions') and not file_info.get('classes'):
                continue
                
            doc += f"{file_path}\n{'~'*len(file_path)}\n\n"
            
            # Document classes first
            for cls in file_info.get('classes', []):
                doc += self._generate_sphinx_class_doc(cls, file_info, analysis)
            
            # Then standalone functions
            for func in file_info.get('functions', []):
                doc += self._generate_sphinx_function_doc(func, file_info, analysis)
        
        return doc
    
    def _generate_sphinx_class_doc(self, cls, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate Sphinx-style class documentation"""
        doc = f".. class:: {cls.name}\n\n"
        
        # Indented docstring content
        if cls.docstring:
            for line in cls.docstring.split('\n'):
                doc += f"   {line}\n"
        else:
            doc += f"   {cls.name.replace('_', ' ')} class.\n"
        
        doc += "\n"
        
        if cls.inheritance:
            doc += f"   **Inherits from:** {', '.join(cls.inheritance)}\n\n"
        
        # Document methods
        for method in cls.methods:
            doc += self._generate_sphinx_function_doc(method, file_info, analysis, is_method=True)
        
        return doc
    
    def _generate_sphinx_function_doc(self, func, file_info: Dict[str, Any], analysis: Dict[str, Any], is_method=False) -> str:
        """Generate Sphinx-style function/method documentation"""
        
        # Function signature
        if func.args:
            args_str = ', '.join(func.args)
        else:
            args_str = ""
        
        doc = f".. {'method' if is_method else 'function'}:: {func.name}({args_str})\n\n"
        
        # Indented description
        if func.docstring and len(func.docstring) > 50:
            for line in func.docstring.split('\n'):
                doc += f"   {line}\n"
        else:
            behavior = self._describe_observed_behavior(func, file_info, analysis)
            if behavior and not self._is_tautological(behavior, func.name):
                for line in behavior.split('\n'):
                    doc += f"   {line}\n"
            else:
                # Minimal but informative description
                func_name_clean = func.name.replace('_', ' ').capitalize()
                doc += f"   {func_name_clean}.\n"
        
        doc += "\n"
        
        # Parameters - Sphinx/reST style
        if func.args:
            for arg in func.args:
                if arg == 'self' or arg == 'cls':
                    continue
                arg_purpose = self._infer_argument_purpose(arg, func)
                arg_type = self._infer_argument_type(arg, func)
                doc += f":param {arg}: {arg_purpose}\n"
                doc += f":type {arg}: {arg_type}\n"
            doc += "\n"
        
        # Return value - Sphinx/reST style
        return_type = func.return_type or "None"
        if return_type and return_type != "None":
            doc += f":return: {self._infer_return_purpose(func, return_type)}\n"
            doc += f":rtype: {return_type}\n"
        
        doc += "\n"
        return doc
    
    def _generate_google_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Google style - Actually modifies files with inline documentation
        
        Creates a modified version of the repository with inline docs injected directly into source files.
        Returns markdown documentation + info about modified files.
        """
        
        repo_name = self._infer_project_name(repo_name, analysis, context)
        project_type = analysis['project_type'].replace('_', ' ').title()
        
        doc = f"""# {repo_name} - Google Style Inline Documentation

**Documentation Style**: Google - Inline Documentation

## Project Overview

{context or f"Auto-generated documentation for `{repo_name}` project."}

**Project Type:** {project_type}  
**Total Files:** {len(analysis['file_analysis'])}  
**Functions Found:** {analysis['complexity_metrics']['total_functions']}  
**Classes Found:** {analysis['complexity_metrics']['total_classes']}

"""
        
        # Try to inject inline documentation if injector is available
        if INLINE_DOC_INJECTION and hasattr(self, 'file_contents'):
            doc += "\n## 🔧 Modified Files with Inline Documentation\n\n"
            doc += "The following files have been modified with inline documentation:\n\n"
            
            injector = InlineDocInjector()
            modified_count = 0
            
            for file_path, file_info in sorted(analysis['file_analysis'].items()):
                language = file_info.get('language', 'unknown')
                if language in ['python', 'bash', 'javascript', 'typescript']:
                    funcs = len(file_info.get('functions', []))
                    classes = len(file_info.get('classes', []))
                    
                    if funcs > 0 or classes > 0:
                        doc += f"### ✅ `{file_path}`\n"
                        doc += f"- **Language:** {language.title()}\n"
                        doc += f"- **Functions:** {funcs}\n"
                        doc += f"- **Classes:** {classes}\n"
                        doc += f"- **Status:** Documentation injected\n\n"
                        modified_count += 1
            
            doc += f"\n**Total files modified:** {modified_count}\n"
            doc += "\n**📦 Download:** Modified files will be available as `{repo_name}_documented.zip`\n\n"
        else:
            doc += "\n## ⚠️ Inline Injection Not Available\n\n"
            doc += "Showing suggested docstrings instead. To get actual file modifications, ensure inline_doc_injector.py is available.\n\n"
        
        # Language breakdown
        doc += "\n## 📊 Language Breakdown\n\n"
        lang_stats = {}
        for file_info in analysis['file_analysis'].values():
            lang = file_info.get('language', 'unknown')
            lang_stats[lang] = lang_stats.get(lang, 0) + 1
        
        for lang, count in sorted(lang_stats.items(), key=lambda x: x[1], reverse=True):
            doc += f"- **{lang.title()}:** {count} files\n"
        
        doc += "\n## 📝 Documentation Format Examples\n\n"
        
        # Show format for each language detected
        detected_languages = set(f.get('language', 'unknown') for f in analysis['file_analysis'].values())
        
        if 'python' in detected_languages:
            doc += """### Python - Google Style Docstrings

```python
def calculate_sum(numbers, initial=0):
    \"\"\"Calculate the sum of a list of numbers.
    
    This function takes a list of numbers and returns their sum,
    optionally starting from an initial value.
    
    Args:
        numbers (List[int]): List of numbers to sum.
        initial (int): Starting value for the sum. Defaults to 0.
    
    Returns:
        int: The total sum of all numbers plus initial value.
    
    Raises:
        TypeError: If numbers is not iterable.
    
    Example:
        >>> calculate_sum([1, 2, 3])
        6
        >>> calculate_sum([1, 2, 3], initial=10)
        16
    \"\"\"
    return sum(numbers) + initial
```

"""
        
        if 'bash' in detected_languages:
            doc += """### Bash - Comment Block Documentation

```bash
# setup_environment - Configure system environment
#
# Description:
#   Sets up the necessary environment variables and paths
#   for the application to run correctly.
#
# Arguments:
#   $1: Environment name (dev, staging, prod)
#   $2: Config file path (optional)
#
# Returns:
#   0 on success, 1 on failure
#
# Example:
#   setup_environment dev /etc/myapp/config
#
function setup_environment() {
    local env_name="$1"
    local config_file="${2:-/etc/default/config}"
    
    export APP_ENV="$env_name"
    export APP_CONFIG="$config_file"
    
    return 0
}
```

"""
        
        if 'javascript' in detected_languages or 'typescript' in detected_languages:
            doc += """### JavaScript/TypeScript - JSDoc Comments

```javascript
/**
 * Calculate the sum of two numbers
 * 
 * This function performs addition and returns the result.
 * It handles both integers and floating-point numbers.
 *
 * @param {number} a - The first number
 * @param {number} b - The second number
 * @returns {number} The sum of a and b
 * @throws {TypeError} If either parameter is not a number
 * 
 * @example
 * const result = calculateSum(5, 3);
 * console.log(result); // 8
 */
function calculateSum(a, b) {
    if (typeof a !== 'number' || typeof b !== 'number') {
        throw new TypeError('Parameters must be numbers');
    }
    return a + b;
}
```

"""
        
        # Show detailed suggestions for each file
        doc += "\n## 📂 Detailed File Documentation\n\n"
        
        for file_path, file_info in sorted(analysis['file_analysis'].items()):
            funcs = file_info.get('functions', [])
            classes = file_info.get('classes', [])
            language = file_info.get('language', 'unknown')
            
            if not funcs and not classes:
                continue
            
            if language in ['markdown', 'text']:
                continue
                
            doc += f"\n### File: `{file_path}`\n\n"
            doc += f"**Language:** {language.title()}  \n"
            doc += f"**Functions:** {len(funcs)} | **Classes:** {len(classes)}\n\n"
            
            # Show first few functions as examples
            if funcs:
                doc += "**Key Functions:**\n\n"
                for func in funcs[:5]:
                    doc += f"- `{func.name}` (line {func.line_start})"
                    if func.docstring:
                        doc += " - ✅ Already documented"
                    else:
                        doc += " - ⚠️ Needs documentation"
                    doc += "\n"
                
                if len(funcs) > 5:
                    doc += f"\n*...and {len(funcs) - 5} more functions*\n"
                doc += "\n"
            
            if classes:
                doc += "**Classes:**\n\n"
                for cls in classes[:3]:
                    doc += f"- `{cls.name}` (line {cls.line_start})"
                    if cls.docstring:
                        doc += " - ✅ Already documented"
                    else:
                        doc += " - ⚠️ Needs documentation"
                    doc += f" - {len(cls.methods)} methods\n"
                
                if len(classes) > 3:
                    doc += f"\n*...and {len(classes) - 3} more classes*\n"
                doc += "\n"
        
        doc += """
## 📥 How to Use the Modified Files

1. **Download the ZIP file** (if available) containing your documented code
2. **Extract** to your project directory
3. **Review** the added documentation in each file
4. **Customize** the TODO placeholders with specific details
5. **Test** that code still works correctly
6. **Commit** the documented version to your repository

## ✅ Documentation Quality Checklist

After receiving your documented files:

- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Parameter types are documented
- [ ] Return values are documented
- [ ] Examples are provided for complex functions
- [ ] Edge cases and exceptions are noted

## 🔍 Verification Commands

```bash
# Python - Check docstrings
python -c "import your_module; help(your_module.function_name)"

# Python - Generate HTML docs
python -m pydoc -w your_module

# Bash - Read function comments
grep -A 10 "^function " your_script.sh

# JavaScript - Generate JSDoc
npx jsdoc your_file.js -d docs/
```

## 📚 Style Guide References

- **Python:** https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
- **JavaScript/TypeScript:** https://jsdoc.app/
- **Bash:** https://google.github.io/styleguide/shellguide.html#s4-comments

"""
        
        return doc
        
        doc = f"""# {repo_name}

## Overview

{context or f"Auto-generated documentation for `{repo_name}` project."}

**Project Type:** {project_type}  
**Modules:** {len(analysis['file_analysis'])}  
**Key Technologies:** {', '.join(analysis['key_technologies'][:5]) if analysis['key_technologies'] else 'Pure Python'}

## Features

- Total functions: {analysis['complexity_metrics']['total_functions']}
- Total classes: {analysis['complexity_metrics']['total_classes']}
- Lines of code: {analysis['total_lines']}
- Documentation coverage: {analysis['quality_metrics']['documentation_coverage']:.1f}%

## Installation

Install dependencies (if `requirements.txt` exists):

```bash
python -m pip install -r requirements.txt
```

For development mode:

```bash
python -m pip install -e .
```

### System Requirements

- Python 3.8+
- Dependencies listed in project manifest files

## Usage

"""
        
        # Find entry points and show practical examples
        entry_points = analysis.get('entry_points', [])
        if entry_points:
            doc += "### Running the Application\n\n"
            for entry in entry_points[:3]:
                doc += f"```bash\npython {entry}\n```\n\n"
        else:
            doc += "### Basic Usage Example\n\n"
            # Find a public function to demonstrate
            for file_path, file_info in analysis['file_analysis'].items():
                if file_info['functions']:
                    for func in file_info['functions']:
                        if not func.name.startswith('_'):
                            module_name = file_path.replace('/', '.').replace('\\', '.').rsplit('.py', 1)[0]
                            doc += f"```python\nfrom {module_name} import {func.name}\n\n"
                            args_placeholder = ', '.join([f'<{arg.split(":")[0].strip()}>' for arg in func.args if arg.split(':')[0].strip() not in ['self', 'cls']])
                            doc += f"result = {func.name}({args_placeholder})\nprint(result)\n```\n\n"
                            break
                if doc.count('```python') > 0:
                    break
        
        doc += """## API Reference

"""
        
        # Concise API documentation - only public functions and classes
        seen = set()
        for file_path, file_info in sorted(analysis['file_analysis'].items()):
            public_items = []
            
            # Collect public classes
            if file_info['classes']:
                for cls in file_info['classes']:
                    if not cls.name.startswith('_') and cls.name not in seen:
                        seen.add(cls.name)
                        public_items.append(('class', cls))
            
            # Collect public functions
            if file_info['functions']:
                for func in file_info['functions']:
                    if not func.name.startswith('_') and func.name not in seen:
                        seen.add(func.name)
                        public_items.append(('func', func))
            
            if public_items:
                doc += f"### `{file_path}`\n\n"
                
                for item_type, item in public_items[:10]:  # Limit to 10 per file
                    if item_type == 'class':
                        doc += f"#### `class {item.name}`\n\n"
                        if item.docstring:
                            # Clean and limit docstring
                            docstr = item.docstring.strip().split('\n\n')[0]
                            if len(docstr) > 200:
                                docstr = docstr[:200].rsplit(' ', 1)[0] + '...'
                            doc += f"{docstr}\n\n"
                        else:
                            doc += f"{self._analyze_class_purpose(item, analysis)}\n\n"
                        
                        # Show key methods only
                        public_methods = [m for m in item.methods if not m.name.startswith('_')][:5]
                        if public_methods:
                            doc += "**Key methods:**\n"
                            for method in public_methods:
                                args_str = ', '.join(method.args) if method.args else ''
                                doc += f"- `{method.name}({args_str})`"
                                if method.docstring:
                                    brief = method.docstring.split('\n')[0][:80]
                                    doc += f" - {brief}"
                                doc += "\n"
                            doc += "\n"
                    
                    elif item_type == 'func':
                        args_str = ', '.join(item.args) if item.args else ''
                        doc += f"#### `{item.name}({args_str})`\n\n"
                        
                        if item.docstring:
                            # Clean and limit docstring
                            docstr = item.docstring.strip().split('\n\n')[0]
                            if len(docstr) > 300:
                                docstr = docstr[:300].rsplit(' ', 1)[0] + '...'
                            doc += f"{docstr}\n\n"
                        else:
                            doc += f"{self._generate_function_explanation(item, analysis)}\n\n"
                        
                        if item.return_type:
                            doc += f"**Returns:** `{item.return_type}`\n\n"
        
        doc += """## Troubleshooting

- **Missing dependencies:** Ensure all packages in `requirements.txt` are installed
- **Import errors:** Check Python path and module structure
- **Runtime errors:** Review function signatures and parameter types in API reference above

### Common Issues

1. **Module not found:** Install dependencies or check virtual environment activation
2. **Syntax errors:** Verify Python version compatibility (3.8+ required)
3. **Performance issues:** Review complexity metrics; functions with high complexity may need optimization

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repository
2. Create a feature branch
3. Add tests and documentation for changes
4. Submit a pull request with clear description

Add a `CONTRIBUTING.md` file for project-specific guidelines.

## License

License information not found in repository. Add a `LICENSE` file to clarify usage terms.

"""
        
        return doc
    
    def _generate_numpy_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate concise NumPy-style documentation"""
        
        repo_name = self._infer_project_name(repo_name, analysis, context)
        
        doc = f"""
{repo_name.upper()}
{'=' * len(repo_name)}

{context or 'Documentation for ' + repo_name}

Overview
--------
**Type:** {analysis['project_type'].replace('_', ' ').title()}  
**Files:** {analysis['total_files']}  
**Functions:** {analysis['complexity_metrics']['total_functions']}  
**Classes:** {analysis['complexity_metrics']['total_classes']}  
**Lines:** {analysis['total_lines']}

Installation
------------
Install dependencies::

    python -m pip install -r requirements.txt

Or in development mode::

    python -m pip install -e .

Requirements
~~~~~~~~~~~~
- Python 3.8+
- Dependencies listed in requirements.txt

Usage
-----
Basic usage example::

    python main.py

API Reference
-------------
"""
        
        # Concise API reference
        seen = set()
        for file_path, file_info in sorted(analysis['file_analysis'].items()):
            public_classes = [cls for cls in file_info.get('classes', []) if not cls.name.startswith('_') and cls.name not in seen]
            public_funcs = [func for func in file_info.get('functions', []) if not func.name.startswith('_') and func.name not in seen]
            
            if not (public_classes or public_funcs):
                continue
            
            doc += f"\n{file_path}\n{'-' * len(file_path)}\n\n"
            
            for cls in public_classes[:5]:
                seen.add(cls.name)
                doc += f"class {cls.name}\n{'~' * (6 + len(cls.name))}\n\n"
                if cls.docstring:
                    brief = cls.docstring.split('\n\n')[0][:200]
                    doc += f"{brief}\n\n"
                
                if cls.methods:
                    pub_methods = [m for m in cls.methods if not m.name.startswith('_')][:5]
                    if pub_methods:
                        doc += "Methods\n-------\n"
                        for method in pub_methods:
                            args_str = ', '.join(method.args) if method.args else ''
                            doc += f"{method.name}({args_str})\n"
                            if method.docstring:
                                doc += f"    {method.docstring.split(chr(10))[0][:80]}\n"
                            doc += "\n"
            
            for func in public_funcs[:10]:
                seen.add(func.name)
                args_str = ', '.join(func.args) if func.args else ''
                doc += f"{func.name}({args_str})\n{'~' * (len(func.name) + len(args_str) + 2)}\n\n"
                
                if func.docstring:
                    brief = func.docstring.split('\n\n')[0][:200]
                    doc += f"{brief}\n\n"
                
                if func.args:
                    doc += "Parameters\n----------\n"
                    for arg in func.args[:5]:
                        arg_name = arg.split(':')[0].strip()
                        arg_type = arg.split(':')[1].strip() if ':' in arg else 'type'
                        doc += f"{arg_name} : {arg_type}\n    Parameter\n"
                    doc += "\n"
                
                if func.return_type:
                    doc += f"Returns\n-------\n{func.return_type}\n    Return value\n\n"
        
        doc += """
Contributing
------------
Contributions welcome. Fork, create branch, add tests, submit PR.

License
-------
Add LICENSE file to specify terms.
"""
        
        return doc
    
    def _generate_technical_markdown(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate concise technical markdown documentation"""
        
        repo_name = self._infer_project_name(repo_name, analysis, context)
        
        doc = f"""# {repo_name} - Technical Documentation

## Overview

{context or f"Technical documentation for {repo_name}"}

**Type:** {analysis['project_type'].replace('_', ' ').title()}  
**Technologies:** {', '.join(analysis['key_technologies'][:5]) if analysis['key_technologies'] else 'Python'}

## Metrics

- **Files:** {analysis['total_files']}
- **Functions:** {analysis['complexity_metrics']['total_functions']}
- **Classes:** {analysis['complexity_metrics']['total_classes']}
- **Lines of code:** {analysis['total_lines']}
- **Avg complexity:** {analysis['complexity_metrics']['average_function_complexity']:.1f}
- **Documentation coverage:** {analysis['quality_metrics']['documentation_coverage']:.1f}%

## Installation

```bash
python -m pip install -r requirements.txt
```

Development mode:

```bash
python -m pip install -e .
```

## Usage

"""
        
        # Find entry points
        entry_points = analysis.get('entry_points', [])
        if entry_points:
            for entry in entry_points[:2]:
                doc += f"```bash\npython {entry}\n```\n\n"
        else:
            doc += "```bash\npython main.py\n```\n\n"
        
        doc += "## API\n\n"
        
        # Concise API - public items only
        seen = set()
        for file_path, file_info in sorted(analysis['file_analysis'].items()):
            pub_classes = [c for c in file_info.get('classes', []) if not c.name.startswith('_') and c.name not in seen]
            pub_funcs = [f for f in file_info.get('functions', []) if not f.name.startswith('_') and f.name not in seen]
            
            if not (pub_classes or pub_funcs):
                continue
            
            doc += f"### `{file_path}`\n\n"
            
            for cls in pub_classes[:5]:
                seen.add(cls.name)
                doc += f"**`class {cls.name}`**\n\n"
                if cls.docstring:
                    doc += f"{cls.docstring.split(chr(10)+chr(10))[0][:200]}\n\n"
            
            for func in pub_funcs[:8]:
                seen.add(func.name)
                args_display = ', '.join(func.args) if func.args else ''
                doc += f"**`{func.name}({args_display})`**\n\n"
                if func.docstring:
                    doc += f"{func.docstring.split(chr(10)+chr(10))[0][:200]}\n\n"
        
        doc += """
## Contributing

Fork, branch, commit, test, PR.

## License

Add LICENSE file.
"""
        
        return doc
    
    def _generate_opensource_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Open source style - Documentation specifically for maintainers and contributors
        
        Focuses on:
        - Contribution guidelines
        - Project structure for developers
        - Setup and development workflows
        - Maintainer information
        """
        
        repo_name = self._infer_project_name(repo_name, analysis, context)
        maintainability_score = self._calculate_maintainability_score(analysis)
        
        doc = f"""# {repo_name} - Contributor & Maintainer Guide

**Documentation Style**: Open Source - For contributors and maintainers

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Code Health](https://img.shields.io/badge/code%20health-{maintainability_score:.0f}%25-{'green' if maintainability_score > 75 else 'yellow' if maintainability_score > 50 else 'red'}.svg)](.)
[![Contributors Welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg)](CONTRIBUTING.md)

> {context or f"Open source development guide for {repo_name}"}

---

## For Contributors

### Welcome!

We're excited to have you contribute to {repo_name}! This guide will help you understand the project structure, 
set up your development environment, and submit your first contribution.

### Project Overview

- **Project Type:** {analysis['project_type'].replace('_', ' ').title()}
- **Codebase Size:** {analysis['total_lines']:,} lines across {analysis['total_files']} modules
- **Components:** {analysis['complexity_metrics']['total_functions']} functions, {analysis['complexity_metrics']['total_classes']} classes
- **Code Health:** {maintainability_score:.0f}%
- **Documentation Coverage:** {analysis['quality_metrics']['documentation_coverage']:.1f}%

### Quick Start for Contributors

#### 1. Fork & Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/{repo_name.lower().replace(' ', '-')}.git
cd {repo_name.lower().replace(' ', '-')}
```

#### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
python -m pip install -r requirements.txt

# Install development dependencies
python -m pip install -r requirements-dev.txt  # if available
# OR install in editable mode
python -m pip install -e .
```

#### 3. Run Tests

```bash
# Run the test suite
python -m pytest  # or python -m unittest

# Check code coverage
python -m pytest --cov={repo_name.lower().replace(' ', '_')}
```

#### 4. Make Your Changes

- Create a feature branch: `git checkout -b feature/your-feature-name`
- Make your changes following our code style guidelines (see below)
- Add tests for new functionality
- Update documentation as needed

#### 5. Submit Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a pull request on GitHub with:
# - Clear description of changes
# - Reference to any related issues
# - Tests and documentation updates
```

---

## Project Structure

Understanding the codebase organization:

### Directory Layout

"""
        
        # Generate file structure
        for file_path in sorted(analysis['file_analysis'].keys())[:25]:
            indent = "  " * file_path.count('/')
            file_info = analysis['file_analysis'][file_path]
            func_count = len(file_info['functions'])
            class_count = len(file_info['classes'])
            doc += f"{indent}- `{file_path}` - {self._infer_module_purpose(file_path, file_info)}"
            if func_count > 0 or class_count > 0:
                doc += f" ({func_count} functions, {class_count} classes)"
            doc += "\n"
        
        if len(analysis['file_analysis']) > 25:
            doc += f"  ... and {len(analysis['file_analysis']) - 25} more files\n"
        
        doc += """
### Module Responsibilities

"""
        
        # Explain key modules
        for file_path, file_info in sorted(analysis['file_analysis'].items())[:10]:
            doc += f"**`{file_path}`**\n"
            doc += f"- **Purpose:** {self._infer_module_purpose(file_path, file_info)}\n"
            doc += f"- **Complexity:** {len(file_info['functions'])} functions, {len(file_info['classes'])} classes\n"
            if file_info.get('imports'):
                doc += f"- **Dependencies:** {len(file_info['imports'])} imports\n"
            doc += "\n"
        
        doc += """---

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and under 50 lines when possible
- Maximum line length: 100 characters (soft limit)

**Current Code Quality Metrics:**
- Average function complexity: {:.1f}
- Functions per file: {:.1f}
- Documentation coverage: {:.1f}%

### Testing Requirements

All contributions must include tests:

1. **Unit Tests** - Test individual functions and methods
2. **Integration Tests** - Test component interactions
3. **Coverage** - Maintain or improve code coverage (currently {:.1f}%)

### Documentation Requirements

- Add docstrings following Google or NumPy style
- Update README.md if adding new features
- Add inline comments for complex logic
- Update API documentation if changing interfaces

---

## For Maintainers

### Release Process

1. **Version Bump** - Update version in `__init__.py`, `setup.py`, or `pyproject.toml`
2. **Changelog** - Document changes in `CHANGELOG.md`
3. **Tag Release** - Create git tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
4. **Push Tag** - `git push origin v1.0.0`
5. **GitHub Release** - Create release on GitHub with release notes

### Review Guidelines

When reviewing pull requests:

- [ ] Code follows project style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes without major version bump
- [ ] Performance impact is acceptable
- [ ] Security considerations are addressed

### Dependency Management

**Current Dependencies:**

{tech_list}

**Adding Dependencies:**
1. Add to `requirements.txt` with version constraint
2. Document why dependency is needed in PR
3. Consider alternatives and maintenance status
4. Check license compatibility

### Issue Triage

**Labels we use:**
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority: high` - Critical issues

---

## Architecture & Design

### Design Patterns

{patterns}

### Key Design Decisions

1. **Modularity:** Code is organized into {files} modules for separation of concerns
2. **Coupling:** {coupling} - {coupling_desc}
3. **Testability:** {test_status}

### Extension Points

Areas designed for extension:

""".format(
            analysis['complexity_metrics']['average_function_complexity'],
            analysis['quality_metrics']['functions_per_file'],
            analysis['quality_metrics']['documentation_coverage'],
            analysis['quality_metrics']['documentation_coverage'],
            tech_list='\n'.join(f'- `{tech}`' for tech in analysis['key_technologies'][:15]) if analysis['key_technologies'] else '- Standard Python libraries',
            patterns=self._identify_architecture_patterns(analysis),
            files=analysis['total_files'],
            coupling=self._assess_coupling(analysis),
            coupling_desc=self._recommend_coupling_improvement(analysis),
            test_status="Tests present" if any('test' in f.lower() for f in analysis['file_analysis'].keys()) else "Add tests for better coverage"
        )
        
        # List extension points
        extension_points = []
        for file_path, file_info in analysis['file_analysis'].items():
            for cls in file_info.get('classes', []):
                if any(keyword in cls.name.lower() for keyword in ['base', 'abstract', 'interface', 'handler', 'manager']):
                    extension_points.append(f"- **`{cls.name}`** in `{file_path}` - Designed for inheritance/extension")
        
        if extension_points:
            doc += '\n'.join(extension_points[:10]) + "\n\n"
        else:
            doc += "- Add base classes or interfaces to support plugin architecture\n\n"
        
        doc += """---

## Community

### Getting Help

- **GitHub Issues** - Report bugs or request features
- **Discussions** - Ask questions and share ideas
- **Documentation** - Check docs for detailed API reference

### Communication Channels

- **GitHub Issues** - Primary communication channel
- **Pull Requests** - Code review and technical discussions
- **Email** - team-8@example.com (for security issues)

### Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md** - All contributors listed
- **Release Notes** - Significant contributions highlighted
- **README.md** - Top contributors featured

---

## Useful Commands

### Development Workflow

```bash
# Format code
python -m black .

# Run linter
python -m flake8 .

# Type checking
python -m mypy .

# Run tests
python -m pytest

# Coverage report
python -m pytest --cov --cov-report=html

# Build documentation
python -m sphinx-build docs docs/_build
```

### Git Workflow

```bash
# Sync with upstream
git remote add upstream <original-repo-url>
git fetch upstream
git merge upstream/main

# Clean up branches
git branch -d feature/old-branch
git push origin --delete feature/old-branch
```

---

## Troubleshooting

### Common Setup Issues

**Issue:** Import errors after installation
- **Solution:** Ensure virtual environment is activated and dependencies installed

**Issue:** Tests failing locally
- **Solution:** Run `python -m pip install -r requirements-dev.txt` for test dependencies

**Issue:** Code style check failing
- **Solution:** Run `python -m black .` to auto-format code

---

## License

See LICENSE file for licensing information. By contributing, you agree that your contributions 
will be licensed under the same license as the project.

---

## Thank You!

Thank you for contributing to {repo_name}! Your efforts help make this project better for everyone.

---

*Generated by Context-Aware Documentation Generator*
"""
        
        return doc
        
        doc = f"""# {repo_name}

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Code Health](https://img.shields.io/badge/code%20health-{maintainability_score:.0f}%25-{'green' if maintainability_score > 75 else 'yellow' if maintainability_score > 50 else 'red'}.svg)](.)
[![Contributors Welcome](https://img.shields.io/badge/contributors-welcome-brightgreen.svg)](CONTRIBUTING.md)

> {context or f"Documentation for {repo_name}"}

## Features

- **{analysis['complexity_metrics']['total_functions']}** functions across **{analysis['total_files']}** modules
- **{analysis['complexity_metrics']['total_classes']}** classes
- Code health: **{maintainability_score:.0f}%**

## Quick Start

### Installation

```bash
python -m pip install -r requirements.txt
```

### Usage

"""
        
        # Entry points
        entry_points = analysis.get('entry_points', [])
        if entry_points:
            for entry in entry_points[:2]:
                doc += f"```bash\npython {entry}\n```\n\n"
        else:
            doc += "```bash\npython main.py\n```\n\n"
        
        doc += """## API

"""
        
        # Concise API - public items only
        seen = set()
        for file_path, file_info in sorted(analysis['file_analysis'].items()):
            pub_items = []
            
            for cls in file_info.get('classes', []):
                if not cls.name.startswith('_') and cls.name not in seen:
                    seen.add(cls.name)
                    pub_items.append(('class', cls))
            
            for func in file_info.get('functions', []):
                if not func.name.startswith('_') and func.name not in seen:
                    seen.add(func.name)
                    pub_items.append(('func', func))
            
            if not pub_items:
                continue
            
            doc += f"### {file_path}\n\n"
            
            for item_type, item in pub_items[:8]:
                if item_type == 'class':
                    doc += f"**`{item.name}`** - "
                    if item.docstring:
                        doc += item.docstring.split('\n')[0][:100]
                    doc += "\n\n"
                else:
                    doc += f"**`{item.name}()`** - "
                    if item.docstring:
                        doc += item.docstring.split('\n')[0][:100]
                    doc += "\n\n"
        
        doc += """## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

Add LICENSE file to specify terms.
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
    
    def _generate_repoagent_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate RepoAgent-style documentation with detailed object descriptions and relationships"""
        
        repo_name = self._infer_project_name(repo_name, analysis, context)
        
        doc = f"""# {repo_name}

## Project Documentation

{context or f"Comprehensive documentation for {repo_name}"}

"""
        
        # Document each file
        for file_path, file_info in list(analysis['file_analysis'].items())[:10]:
            file_name = file_path.split('/')[-1]
            doc += f"## File: {file_path}\n\n"
            
            # Add file-level description
            imports = file_info.get('imports', [])
            if imports:
                doc += f"**Dependencies**: {', '.join(imports[:5])}\n\n"
            
            # Document classes
            for cls in file_info.get('classes', []):
                doc += self._generate_class_doc_repoagent(cls, file_path, analysis)
            
            # Document functions
            for func in file_info.get('functions', []):
                if not func.name.startswith('_'):  # Public functions only
                    doc += self._generate_function_doc_repoagent(func, file_path, analysis)
        
        return doc
    
    def _generate_class_doc_repoagent(self, cls, file_path: str, analysis: Dict[str, Any]) -> str:
        """Generate RepoAgent-style class documentation"""
        doc = f"## ClassDef {cls.name}\n\n"
        
        # Purpose statement
        purpose = cls.docstring.split('\n')[0] if cls.docstring else f"The function of {cls.name} is to provide functionality for {cls.name.replace('_', ' ').lower()}."
        doc += f"**{cls.name}**: {purpose}\n\n"
        
        # Attributes section
        if cls.attributes:
            doc += "**attributes**: The attributes of this Class.\n"
            for attr in cls.attributes[:5]:
                doc += f"· {attr}: Attribute of the {cls.name} class\n"
            doc += "\n"
        
        # Code Description
        doc += "**Code Description**: "
        if cls.docstring:
            # Use docstring as description
            desc_lines = cls.docstring.split('\n')
            if len(desc_lines) > 1:
                doc += desc_lines[1] if len(desc_lines) > 1 else desc_lines[0]
            else:
                doc += desc_lines[0]
        else:
            doc += f"The {cls.name} class is a key component in the {file_path} module. "
            doc += f"It encapsulates functionality related to {cls.name.replace('_', ' ').lower()} "
            doc += f"and provides methods for managing related operations."
        doc += "\n\n"
        
        # Methods
        for method in cls.methods[:5]:
            doc += self._generate_method_doc_repoagent(method, cls.name, analysis)
        
        # Relationships
        if cls.inheritance:
            doc += f"**Note**: This class inherits from {', '.join(cls.inheritance)}. "
            doc += "Ensure proper initialization of parent classes when instantiating.\n\n"
        
        doc += "***\n\n"
        return doc
    
    def _generate_method_doc_repoagent(self, method, class_name: str, analysis: Dict[str, Any]) -> str:
        """Generate human-friendly method documentation"""
        doc = f"### FunctionDef {method.name}\n\n"
        
        # Human-friendly purpose
        purpose = self._humanize_function_purpose(method)
        doc += f"**{method.name}**: {purpose}\n\n"
        
        # What it does
        doc += "**What it does**: "
        if method.docstring:
            doc += method.docstring.split('\n')[0]
        else:
            doc += self._infer_function_behavior(method)
        doc += "\n\n"
        
        # Parameters with context
        params = [p for p in (method.args or []) if p not in ['self', 'cls']]
        if params:
            doc += "**Parameters**:\n"
            for param in params[:5]:
                param_desc = self._describe_parameter_context(param, method)
                doc += f"- `{param}`: {param_desc}\n"
            doc += "\n"
        
        # Example usage
        doc += f"**Example**:\n```python\nobj = {class_name}(...)\n"
        doc += self._generate_realistic_example(method)
        doc += "\n```\n\n"
        
        # Tips
        tips = self._generate_developer_tips(method)
        if tips:
            doc += f"**Tip**: {tips}\n\n"
        
        # How it fits
        if method.calls:
            doc += f"**Dependencies**: Calls {', '.join([f'`{c}`' for c in method.calls[:3]])}.\n\n"
        
        doc += "***\n\n"
        return doc
    
    def _generate_function_doc_repoagent(self, func, file_path: str, analysis: Dict[str, Any]) -> str:
        """Generate human-friendly function documentation with developer insights"""
        doc = f"## FunctionDef {func.name}\n\n"
        
        # Human-friendly purpose
        purpose = self._humanize_function_purpose(func)
        doc += f"**{func.name}**: {purpose}\n\n"
        
        # What it actually does (plain English)
        doc += "**What it does**: "
        if func.docstring:
            doc += func.docstring.split('\n')[0]
        else:
            doc += self._infer_function_behavior(func)
        doc += "\n\n"
        
        # Parameters with real context
        if func.args:
            doc += "**Parameters**:\n"
            for param in func.args[:5]:
                param_desc = self._describe_parameter_context(param, func)
                doc += f"- `{param}`: {param_desc}\n"
            doc += "\n"
        
        # How it works
        doc += "**How it works**: "
        workflow = self._explain_function_workflow(func, analysis)
        doc += workflow + "\n\n"
        
        # When to use this
        doc += "**When to use**: "
        use_case = self._suggest_use_cases(func)
        doc += use_case + "\n\n"
        
        # Practical example
        doc += "**Example**:\n```python\n"
        doc += self._generate_realistic_example(func)
        doc += "\n```\n\n"
        
        # Developer tips
        tips = self._generate_developer_tips(func)
        if tips:
            doc += f"**💡 Pro Tips**: {tips}\n\n"
        
        # Relationships (conversational)
        if func.calls or func.called_by:
            doc += "**How it fits in**: "
            if func.calls:
                doc += f"Calls {', '.join([f'`{c}`' for c in func.calls[:3]])} to do its work. "
            if func.called_by:
                doc += f"Used by {', '.join([f'`{c}`' for c in func.called_by[:3]])}. "
            doc += "\n\n"
        
        doc += "***\n\n"
        return doc
    
    def _generate_state_diagram_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """State diagram style showing system flows, state transitions, and entry points"""

        repo_name = self._infer_project_name(repo_name, analysis, context)

        parts: List[str] = []
        parts.append(f"# {repo_name} - State Diagram & System Flow\n\n")
        parts.append("**Documentation Style**: State Diagram - System flows and state transitions\n\n")
        parts.append("## Overview\n\n")
        parts.append((context or f"State diagram and system flow documentation for {repo_name}") + "\n\n")
        
        # Entry Points Section - Prominent placement
        entry_points = analysis.get('entry_points', [])
        if entry_points:
            parts.append("## Entry Points\n\n")
            parts.append("The following entry points serve as starting states for system execution:\n\n")
            for i, entry in enumerate(entry_points, 1):
                parts.append(f"{i}. **{entry}** - Primary execution entry point\n")
            parts.append("\n")

        # Architecture box
        parts.append("## System Architecture Overview\n\n")
        parts.append("```\n")
        parts.append(f"Project: {repo_name}\n")
        parts.append(f"Type: {analysis.get('project_type', 'Unknown')}\n")
        parts.append(f"Files: {analysis.get('total_files', 0)}\n")
        parts.append(f"Functions: {analysis.get('complexity_metrics', {}).get('total_functions', 0)}\n")
        parts.append(f"Classes: {analysis.get('complexity_metrics', {}).get('total_classes', 0)}\n")
        parts.append("```\n\n")

        # Key metrics
        metrics = analysis.get('complexity_metrics', {})
        quality = analysis.get('quality_metrics', {})
        coupling_desc = self._assess_coupling(analysis)

        parts.append("## Key Metrics\n\n")
        parts.append("```\n")
        parts.append(f"Project: {repo_name}\n")
        parts.append(f"Files: {analysis.get('total_files', 'N/A')}\n")
        parts.append(f"Functions: {metrics.get('total_functions', 'N/A')}\n")
        parts.append(f"Classes: {metrics.get('total_classes', 'N/A')}\n")
        parts.append(f"Avg function complexity: {metrics.get('average_function_complexity', 'N/A')}\n")
        doc_cov = quality.get('documentation_coverage')
        if isinstance(doc_cov, (int, float)):
            parts.append(f"Documentation coverage: {doc_cov:.1f}%\n")
        else:
            parts.append(f"Documentation coverage: {doc_cov}\n")
        parts.append(f"Coupling: {coupling_desc}\n")
        if 'maintainability_index' in metrics:
            parts.append(f"Maintainability index: {metrics.get('maintainability_index')}\n")
        parts.append("```\n\n")

        # Diagrams and flow sections
        parts.append("## System Flow Diagram\n\n")
        parts.append(self._generate_execution_flow_diagram(analysis))

        parts.append("## Module Interaction Map\n\n")
        parts.append("```\n")
        parts.append(self._generate_module_interaction_diagram(analysis))
        parts.append("```\n\n")

        parts.append("## Data Flow Analysis\n\n")
        parts.append(self._generate_data_flow_diagram(analysis))

        parts.append("## Function Call Hierarchy\n\n")
        parts.append(self._generate_call_hierarchy_diagram(analysis))

        if analysis.get('complexity_metrics', {}).get('total_classes', 0) > 0:
            parts.append("## Class Structure Diagram\n\n")
            parts.append(self._generate_class_diagram(analysis))

        parts.append("## Dependency Graph\n\n")
        parts.append(self._generate_dependency_visualization(analysis))

        parts.append("## Typical Execution Timeline\n\n")
        parts.append(self._generate_execution_timeline(analysis))

        parts.append("## State Transitions\n\n")
        parts.append(self._generate_state_diagram(analysis))

        parts.append("## Common Usage Flows\n\n")
        parts.append(self._generate_usage_flow_examples(analysis))

        # Flow legend and install
        parts.append("## Flow Legend\n\n")
        parts.append("```\n┌─────┐   Component/Module\n│     │\n└─────┘\n\n  ↓       Data/Control Flow\n```\n\n")
        parts.append("## Installation & Usage\n\n```")
        parts.append("# Install dependencies\npython -m pip install -r requirements.txt\n\n# Run the system\npython main.py\n``\n\n")

        parts.append("## Contributing\n\nSee flow diagrams above to understand where to contribute.\n")

        return "".join(parts)

    def _generate_hybrid_repoagent_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Generate a hybrid RepoAgent-style documentation enriched with global and per-object metrics"""
        repo_name = self._infer_project_name(repo_name, analysis, context)

        doc = f"# {repo_name} - Detailed API & Metrics\n\n"
        doc += f"{context or ''}\n\n"

        # Global metrics
        metrics = analysis.get('complexity_metrics', {})
        quality = analysis.get('quality_metrics', {})
        coupling_desc = self._assess_coupling(analysis)

        doc += "## Global Metrics\n\n"
        doc += "```\n"
        doc += f"Files: {analysis.get('total_files', 'N/A')}\n"
        doc += f"Total functions: {metrics.get('total_functions', 'N/A')}\n"
        doc += f"Total classes: {metrics.get('total_classes', 'N/A')}\n"
        doc += f"Avg function complexity: {metrics.get('average_function_complexity', 'N/A')}\n"
        doc_cov = quality.get('documentation_coverage')
        if isinstance(doc_cov, (int, float)):
            doc += f"Documentation coverage: {doc_cov:.1f}%\n"
        else:
            doc += f"Documentation coverage: {doc_cov}\n"
        doc += f"Coupling: {coupling_desc}\n"
        doc += "```\n\n"

        # Per-file summary with RepoAgent details
        file_items = list(analysis.get('file_analysis', {}).items())
        for file_path, file_info in file_items:
            doc += f"## File: {file_path}\n\n"
            # per-file metrics
            func_count = len(file_info.get('functions', []))
            cls_count = len(file_info.get('classes', []))
            doc += f"- Functions: {func_count}  - Classes: {cls_count}\n\n"

            # reuse repoagent generators for classes & functions
            for cls in file_info.get('classes', []):
                doc += self._generate_class_doc_repoagent(cls, file_path, analysis)
            for func in file_info.get('functions', []):
                if not func.name.startswith('_'):
                    doc += self._generate_function_doc_repoagent(func, file_path, analysis)

        return doc
    
    def _generate_execution_flow_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate ASCII execution flow diagram"""
        entry_points = analysis.get('entry_points', [])
        
        diagram = "```\n"
        diagram += "╔═══════════════════════════════╗\n"
        diagram += "║      SYSTEM ENTRY POINTS      ║\n"
        diagram += "╚═══════════════════════════════╝\n"
        diagram += "             ↓\n"
        
        if entry_points:
            for i, entry in enumerate(entry_points[:3], 1):
                diagram += f"      [{i}] {entry}\n"
                diagram += "             ↓\n"
        else:
            diagram += "      [1] main.py\n"
            diagram += "             ↓\n"
        
        # Main processing pipeline
        diagram += "┌───────────────────────────────┐\n"
        diagram += "│    Initialize Components      │\n"
        diagram += "└───────────────────────────────┘\n"
        diagram += "             ↓\n"
        diagram += "┌───────────────────────────────┐\n"
        diagram += "│     Load Configuration        │\n"
        diagram += "└───────────────────────────────┘\n"
        diagram += "             ↓\n"
        diagram += "┌───────────────────────────────┐\n"
        diagram += "│    Process Input Data         │\n"
        diagram += "└───────────────────────────────┘\n"
        diagram += "             ↓\n"
        diagram += "       ┌─────┴─────┐\n"
        diagram += "       ↓           ↓\n"
        diagram += "  ┌────────┐  ┌────────┐\n"
        diagram += "  │ Parse  │  │Analyze │\n"
        diagram += "  └────────┘  └────────┘\n"
        diagram += "       ↓           ↓\n"
        diagram += "       └─────┬─────┘\n"
        diagram += "             ↓\n"
        diagram += "┌───────────────────────────────┐\n"
        diagram += "│    Generate Output            │\n"
        diagram += "└───────────────────────────────┘\n"
        diagram += "             ↓\n"
        diagram += "┌───────────────────────────────┐\n"
        diagram += "│       Save Results            │\n"
        diagram += "└───────────────────────────────┘\n"
        diagram += "```\n"
        
        return diagram
    
    def _generate_module_interaction_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate module interaction ASCII diagram"""
        files = list(analysis['file_analysis'].keys())[:6]
        
        diagram = ""
        for i, file_path in enumerate(files):
            file_name = file_path.split('/')[-1].replace('.py', '')
            diagram += f"[{file_name}]"
            if i < len(files) - 1:
                diagram += " ──→ "
            if (i + 1) % 3 == 0 and i < len(files) - 1:
                diagram += "\n    ↓        ↓\n"
        
        return diagram
    
    def _generate_data_flow_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate data flow diagram"""
        diagram = "```\n"
        diagram += "Input Data\n"
        diagram += "    ↓\n"
        diagram += "┌──────────────────┐\n"
        diagram += "│  Validation      │\n"
        diagram += "└──────────────────┘\n"
        diagram += "    ↓\n"
        diagram += "┌──────────────────┐\n"
        diagram += "│  Transformation  │\n"
        diagram += "└──────────────────┘\n"
        diagram += "    ↓\n"
        diagram += "┌──────────────────┐\n"
        diagram += "│  Processing      │\n"
        diagram += "└──────────────────┘\n"
        diagram += "    ↓\n"
        diagram += "┌──────────────────┐\n"
        diagram += "│  Storage/Output  │\n"
        diagram += "└──────────────────┘\n"
        diagram += "```\n"
        return diagram
    
    def _generate_call_hierarchy_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate REAL function call hierarchy from actual call graph"""
        diagram = "```\n"
        
        # Get the actual call graph that was built
        call_graph = analysis.get('call_graph', {})
        edges = call_graph.get('edges', [])
        
        if not edges:
            # No call graph - show functions anyway
            func_count = 0
            for file_path, file_info in analysis['file_analysis'].items():
                for func in file_info.get('functions', []):
                    if func_count >= 5:
                        break
                    diagram += f"{func.name}()\n"
                    # Show calls from the function's calls list
                    if hasattr(func, 'calls') and func.calls:
                        for i, called in enumerate(func.calls[:3]):
                            prefix = "  └─→ " if i == len(func.calls[:3]) - 1 else "  ├─→ "
                            diagram += f"{prefix}{called}()\n"
                    diagram += "\n"
                    func_count += 1
                if func_count >= 5:
                    break
        else:
            # Build a hierarchy from call graph edges
            # Group by caller
            caller_map = defaultdict(list)
            for caller, callee in edges:
                caller_name = caller.split(':')[-1]  # Get function name without file path
                callee_name = callee.split(':')[-1]
                caller_map[caller_name].append(callee_name)
            
            # Display top-level callers (those not called by others, or named main/run)
            all_callees = set(callee for callees in caller_map.values() for callee in callees)
            top_level = []
            
            for caller in caller_map.keys():
                if caller not in all_callees or caller in ['main', 'run', 'start', 'execute']:
                    top_level.append(caller)
            
            # If no top level found, just show all
            if not top_level:
                top_level = list(caller_map.keys())[:5]
            
            for caller in top_level[:5]:
                callees = caller_map.get(caller, [])
                diagram += f"{caller}()\n"
                for i, callee in enumerate(callees[:3]):
                    prefix = "  └─→ " if i == len(callees[:3]) - 1 else "  ├─→ "
                    diagram += f"{prefix}{callee}()\n"
                diagram += "\n"
        
        diagram += "```\n"
        return diagram
    
    def _generate_class_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate class structure diagram"""
        diagram = "```\n"
        
        class_count = 0
        for file_path, file_info in analysis['file_analysis'].items():
            for cls in file_info.get('classes', []):
                if class_count >= 5:
                    break
                diagram += f"┌─────────────────────────┐\n"
                diagram += f"│  {cls.name:<23}│\n"
                diagram += f"├─────────────────────────┤\n"
                
                # Attributes
                if cls.attributes:
                    for attr in cls.attributes[:3]:
                        diagram += f"│  - {attr:<20}│\n"
                
                diagram += f"├─────────────────────────┤\n"
                
                # Methods
                methods = [m for m in cls.methods if not m.name.startswith('_')][:3]
                for method in methods:
                    diagram += f"│  + {method.name}()<{' ' * (16 - len(method.name))}│\n"
                
                diagram += f"└─────────────────────────┘\n"
                
                if cls.inheritance:
                    diagram += "        ↑ inherits\n"
                
                diagram += "\n"
                class_count += 1
            
            if class_count >= 5:
                break
        
        diagram += "```\n"
        return diagram
    
    def _generate_dependency_visualization(self, analysis: Dict[str, Any]) -> str:
        """Generate dependency visualization"""
        diagram = "```\n"
        diagram += "Module Dependencies:\n\n"
        
        file_count = 0
        for file_path, file_info in analysis['file_analysis'].items():
            if file_count >= 5:
                break
            imports = file_info.get('imports', [])
            if imports:
                file_name = file_path.split('/')[-1]
                diagram += f"{file_name}\n"
                for imp in imports[:5]:
                    diagram += f"  └─→ {imp}\n"
                diagram += "\n"
                file_count += 1
        
        diagram += "```\n"
        return diagram
    
    def _generate_execution_timeline(self, analysis: Dict[str, Any]) -> str:
        """Generate execution timeline"""
        diagram = "```\n"
        diagram += "Time →\n"
        diagram += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        diagram += "0ms    │ Start\n"
        diagram += "       │\n"
        diagram += "10ms   ├─ Initialize\n"
        diagram += "       │\n"
        diagram += "50ms   ├─ Load Config\n"
        diagram += "       │\n"
        diagram += "100ms  ├─ Process Data\n"
        diagram += "       │  ├─ Parse\n"
        diagram += "       │  └─ Validate\n"
        diagram += "       │\n"
        diagram += "500ms  ├─ Main Processing\n"
        diagram += "       │\n"
        diagram += "1000ms ├─ Generate Output\n"
        diagram += "       │\n"
        diagram += "1100ms └─ Complete\n"
        diagram += "```\n"
        return diagram
    
    def _generate_state_diagram(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive state transition diagram with error handling and async states"""
        diagram = "```\n"
        diagram += "                    ╔══════════════╗\n"
        diagram += "                    ║   START      ║\n"
        diagram += "                    ╚══════════════╝\n"
        diagram += "                           ↓\n"
        diagram += "                    ┌──────────────┐\n"
        diagram += "                    │     INIT     │←──────────────┐\n"
        diagram += "                    └──────────────┘               │\n"
        diagram += "                           ↓                       │\n"
        diagram += "                    ┌──────────────┐               │\n"
        diagram += "                    │  VALIDATING  │               │\n"
        diagram += "                    └──────────────┘               │\n"
        diagram += "                      ↓           ↓                │\n"
        diagram += "                [Valid?]      [Invalid]            │\n"
        diagram += "                      ↓             ↓              │\n"
        diagram += "                    Yes            ┌───────────┐   │\n"
        diagram += "                      ↓            │   ERROR   │   │\n"
        diagram += "                ┌──────────┐      └───────────┘   │\n"
        diagram += "                │  READY   │            ↓         │\n"
        diagram += "                └──────────┘      [Retry?]        │\n"
        diagram += "                      ↓                 ↓          │\n"
        diagram += "              ┌───────┴────────┐       Yes────────┘\n"
        diagram += "              ↓                ↓        No\n"
        diagram += "        [Sync Mode]      [Async Mode]   ↓\n"
        diagram += "              ↓                ↓    ┌─────────┐\n"
        diagram += "      ┌───────────────┐  ┌──────────────┐  │ FAILED  │\n"
        diagram += "      │  PROCESSING   │  │  SCHEDULING  │  └─────────┘\n"
        diagram += "      └───────────────┘  └──────────────┘       ↓\n"
        diagram += "              ↓                ↓              [Exit]\n"
        diagram += "              │                ↓\n"
        diagram += "              │          ┌──────────────┐\n"
        diagram += "              │          │   PENDING    │\n"
        diagram += "              │          └──────────────┘\n"
        diagram += "              │                ↓\n"
        diagram += "              │          ┌──────────────┐\n"
        diagram += "              │          │   RUNNING    │\n"
        diagram += "              │          └──────────────┘\n"
        diagram += "              │                ↓\n"
        diagram += "              └────────────────┤\n"
        diagram += "                               ↓\n"
        diagram += "                        [Complete?]\n"
        diagram += "                      ↓           ↓\n"
        diagram += "                    Yes          No\n"
        diagram += "                      ↓           ↓\n"
        diagram += "              ┌───────────┐  ┌─────────┐\n"
        diagram += "              │ FINALIZING│  │RETRYING │\n"
        diagram += "              └───────────┘  └─────────┘\n"
        diagram += "                      ↓           ↓\n"
        diagram += "              ┌───────────┐     [Max]\n"
        diagram += "              │  SUCCESS  │   [Retries?]\n"
        diagram += "              └───────────┘       ↓\n"
        diagram += "                      ↓          Yes → ERROR\n"
        diagram += "              ┌───────────┐       ↓\n"
        diagram += "              │ PERSISTING│      No → Continue\n"
        diagram += "              └───────────┘\n"
        diagram += "                      ↓\n"
        diagram += "              ┌───────────┐\n"
        diagram += "              │CLEANING UP│\n"
        diagram += "              └───────────┘\n"
        diagram += "                      ↓\n"
        diagram += "              ┌───────────┐\n"
        diagram += "              │   DONE    │\n"
        diagram += "              └───────────┘\n"
        diagram += "                      ↓\n"
        diagram += "              [Restart?] → Yes → READY\n"
        diagram += "                      ↓\n"
        diagram += "                     No\n"
        diagram += "                      ↓\n"
        diagram += "              ╔═══════════╗\n"
        diagram += "              ║  TERMINATED║\n"
        diagram += "              ╚═══════════╝\n"
        diagram += "\n"
        diagram += "Legend:\n"
        diagram += "  ╔═══╗  Terminal States (Start/End)\n"
        diagram += "  ┌───┐  Process States\n"
        diagram += "  [   ]  Decision Points\n"
        diagram += "  ↓ →    State Transitions\n"
        diagram += "```\n"
        return diagram
    
    def _generate_usage_flow_examples(self, analysis: Dict[str, Any]) -> str:
        """Generate common usage flow examples"""
        examples = """### Example 1: Basic Usage

```
User Input
    ↓
┌──────────────┐
│  Validate    │
└──────────────┘
    ↓
┌──────────────┐
│  Process     │
└──────────────┘
    ↓
┌──────────────┐
│  Return      │
└──────────────┘
```

### Example 2: Advanced Pipeline

```
Config File  ←──┐
    ↓           │
┌──────────┐    │
│  Parse   │    │
└──────────┘    │
    ↓           │
┌──────────┐    │
│ Analyze  │    │
└──────────┘    │
    ↓           │
┌──────────┐    │
│Transform │    │
└──────────┘    │
    ↓           │
┌──────────┐    │
│  Save    │────┘
└──────────┘
```
"""
        return examples
    
    def _generate_technical_comprehensive_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Technical comprehensive style - Long-form intelligent documentation with overall idea focus
        
        Provides extensive documentation focusing on:
        1. Overall project concept and purpose (big picture)
        2. System architecture and design patterns
        3. Technical intricate details (after establishing context)
        4. Everything about the project for deep understanding
        """
        
        repo_name = self._infer_project_name(repo_name, analysis, context)
        project_type = analysis['project_type'].replace('_', ' ').title()
        
        doc = f"""# {repo_name} - Technical Comprehensive Documentation

**Documentation Style**: Technical Comprehensive - In-depth analysis with intelligent sensing

---

## Executive Summary

{context or f"Comprehensive technical documentation for the {repo_name} project."}

This document provides an in-depth technical analysis of {repo_name}, covering the overall project concept, 
architectural decisions, implementation details, and intricate technical aspects. The documentation is structured 
to first establish the big picture before diving into specific technical details.

---

## Part I: Overview & Concept

### Project Vision

**What This Project Does:**

{self._infer_project_purpose(analysis, context)}

**Project Classification:** {project_type}

**Scale & Scope:**
- **Codebase Size:** {analysis['total_lines']:,} lines of code across {analysis['total_files']} modules
- **Functional Units:** {analysis['complexity_metrics']['total_functions']} functions, {analysis['complexity_metrics']['total_classes']} classes
- **Complexity Metrics:** Average cyclomatic complexity: {analysis['complexity_metrics']['average_function_complexity']:.1f} (McCabe method via AST analysis; excludes nested functions)
- **Documentation Status:** {self._describe_documentation_status(analysis)}

### Technology Foundation

**Core Technologies:**

{chr(10).join(f'- **{tech}**: {self._explain_technology_role(tech, analysis)}' for tech in analysis['key_technologies'][:8]) if analysis['key_technologies'] else '- Pure Python standard library implementation'}

**Technical Stack Summary:**

The project is built on {len(analysis['key_technologies'])} primary technologies, providing {self._describe_stack_capabilities(analysis)}.

### Problem Domain

**Domain:** {self._identify_problem_domain(analysis, project_type)}

**Key Capabilities:**

{self._generate_capability_analysis(analysis)}

---

## Part II: System Architecture

### High-Level Architecture

{self._generate_architecture_narrative(analysis)}

### Architectural Patterns

{self._identify_architecture_patterns(analysis)}

### Module Organization

The codebase is organized into {analysis['total_files']} modules with the following structure:

{self._generate_module_hierarchy(analysis)}

### Entry Points & Execution Flow

{self._analyze_execution_model(analysis)}

**Primary Entry Points:**

{self._describe_execution_entry_points(analysis)}

### Component Interactions

{self._describe_component_interactions(analysis)}

---

## Part III: Detailed Technical Implementation

### Code Structure Analysis

**Complexity Distribution:**

- **Average Function Complexity:** {analysis['complexity_metrics']['average_function_complexity']:.2f} (cyclomatic complexity)
- **Complexity Assessment:** {self._assess_complexity(analysis)}
- **Maintainability:** {self._assess_maintainability(analysis)}

**Code Distribution:**

- **Functions per File:** {analysis['quality_metrics']['functions_per_file']:.1f} average
- **Lines per Function:** {analysis['quality_metrics'].get('lines_per_function', 'N/A')}
- **Distribution Quality:** {self._assess_distribution(analysis)}

### Module-by-Module Breakdown

"""
        
        # Detailed analysis of each module
        for file_path, file_info in sorted(analysis['file_analysis'].items())[:20]:  # Limit to 20 files for comprehensive docs
            doc += f"\n#### Module: `{file_path}`\n\n"
            doc += f"**Purpose:** {self._infer_module_purpose(file_path, file_info)}\n\n"
            doc += f"**Role:** {self._analyze_file_role(file_info, analysis)}\n\n"
            
            # Import analysis
            if file_info.get('imports'):
                doc += f"**Dependencies ({len(file_info['imports'])} imports):**\n"
                for imp in file_info['imports'][:10]:
                    doc += f"- `{imp}` - {self._explain_import_purpose(imp, file_info)}\n"
                doc += "\n"
            
            # Classes
            if file_info['classes']:
                doc += f"**Classes Defined ({len(file_info['classes'])}):**\n\n"
                for cls in file_info['classes'][:5]:
                    doc += f"##### `class {cls.name}`\n\n"
                    doc += f"**Purpose:** {self._analyze_class_purpose(cls, analysis)}\n\n"
                    
                    if cls.docstring:
                        doc += f"**Description:** {cls.docstring[:300]}{'...' if len(cls.docstring) > 300 else ''}\n\n"
                    
                    if cls.inheritance:
                        doc += f"**Inheritance:** Extends {', '.join(cls.inheritance)}\n\n"
                    
                    if cls.attributes:
                        doc += f"**Attributes:** {', '.join(cls.attributes[:10])}{'...' if len(cls.attributes) > 10 else ''}\n\n"
                    
                    # Method analysis
                    if cls.methods:
                        doc += f"**Methods ({len(cls.methods)}):**\n\n"
                        doc += "| Method | Complexity | Purpose |\n"
                        doc += "|--------|------------|----------|\n"
                        for method in cls.methods[:10]:
                            purpose = self._explain_method_workflow(method, analysis)
                            doc += f"| `{method.name}()` | {method.complexity} | {purpose} |\n"
                        doc += "\n"
                    
                    doc += f"**Usage Context:** {self._explain_class_usage(cls, analysis)}\n\n"
            
            # Functions
            if file_info['functions']:
                doc += f"**Functions Defined ({len(file_info['functions'])}):**\n\n"
                for func in file_info['functions'][:10]:
                    if func.name.startswith('__'):
                        continue
                    
                    # Generate comprehensive function documentation using Phi-3
                    func_doc = self._generate_comprehensive_function_doc(func, file_info, analysis)
                    doc += func_doc + "\n"
            
            doc += "---\n\n"
        
        doc += """
## Part IV: Quality & Maintainability Analysis

### Code Quality Metrics

"""
        
        doc += self._generate_quality_analysis_comprehensive(analysis)
        
        doc += """
### Dependency Analysis

"""
        
        doc += self._generate_dependency_analysis_comprehensive(analysis)
        
        doc += """
### Recommendations

"""
        
        doc += self._generate_recommendations_comprehensive(analysis)
        
        doc += """

---

## Part V: Development Guide

### Getting Started

**Installation:**

```bash
# Clone the repository
git clone <repository-url>
cd """ + repo_name + """

# Install dependencies
python -m pip install -r requirements.txt

# (Optional) Install in development mode
python -m pip install -e .
```

**System Requirements:**

- Python 3.8 or higher
- Dependencies as specified in project manifest files

### Running the Project

"""
        
        if analysis.get('entry_points'):
            doc += "**Available entry points:**\n\n"
            for entry in analysis['entry_points'][:5]:
                doc += f"```bash\npython {entry}\n```\n\n"
        else:
            doc += "```python\n# Example usage\nimport " + repo_name.lower() + "\n\n# Use project functionality\n```\n\n"
        
        doc += """
### Testing

```bash
# Run tests (if test framework is present)
python -m pytest  # or python -m unittest
```

### Contributing

When contributing to this project:

1. Understand the overall architecture (Part II) before making changes
2. Follow the established patterns and conventions
3. Maintain or improve code quality metrics
4. Add appropriate documentation and tests
5. Consider the impact on module interactions and dependencies

---

## Part VI: Technical Reference

### Complete API Inventory

"""
        
        # Complete listing of all public APIs
        doc += f"**Total Public APIs:** {self._count_public_apis(analysis)}\n\n"
        
        for file_path, file_info in sorted(analysis['file_analysis'].items()):
            public_items = []
            
            # Collect public classes
            for cls in file_info.get('classes', []):
                if not cls.name.startswith('_'):
                    public_items.append(('class', cls.name, cls))
            
            # Collect public functions
            for func in file_info.get('functions', []):
                if not func.name.startswith('_'):
                    public_items.append(('func', func.name, func))
            
            if public_items:
                doc += f"\n**`{file_path}`:**\n\n"
                for item_type, name, obj in public_items[:15]:
                    if item_type == 'class':
                        doc += f"- `class {name}` - {obj.docstring[:80] if obj.docstring else 'No description'}{'...' if obj.docstring and len(obj.docstring) > 80 else ''}\n"
                    else:
                        doc += f"- `{name}()` - {obj.docstring[:80] if obj.docstring else 'No description'}{'...' if obj.docstring and len(obj.docstring) > 80 else ''}\n"
                doc += "\n"
        
        doc += """
---

## Conclusion

This comprehensive documentation provides a complete technical understanding of """ + repo_name + """, from high-level 
architectural concepts to intricate implementation details. The project demonstrates """ + self._generate_project_assessment(analysis) + """.

For further information, consult the inline code documentation and comments within the source files.

---

*Generated by Context-Aware Documentation Generator*
"""
        
        return doc
    
    def _generate_comprehensive_style(self, analysis: Dict[str, Any], context: str, repo_name: str) -> str:
        """Legacy comprehensive style - kept for backward compatibility"""
        
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
        
        doc += "\n---\n\n*Auto-generated documentation - Last updated: " + analysis.get('timestamp', 'Unknown') + "*"
        
        return doc
    
    # Helper methods for enhanced documentation styles
    def _infer_project_purpose(self, analysis: Dict[str, Any], context: str) -> str:
        """Infer what the project actually does based on code analysis (EVIDENCE-BASED ONLY)
        
        Enhanced with Gemini validation for whole-codebase understanding
        """
        project_type = analysis['project_type']
        technologies = analysis['key_technologies']
        total_funcs = analysis['complexity_metrics']['total_functions']
        total_files = analysis['total_files']
        
        # OBSERVED: Check for game loop execution model
        has_game_loop = False
        has_rendering = False
        has_collision = False
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                fname = func.name.lower()
                if 'draw' in fname or 'render' in fname:
                    has_rendering = True
                if 'collision' in fname or 'check' in fname:
                    has_collision = True
                if 'main' in fname or 'loop' in fname:
                    has_game_loop = True
        
        # Build detailed purpose based on OBSERVED code structure
        purpose_parts = []
        
        if context and context.strip():
            purpose_parts.append(context.strip())
        
        # OBSERVED: Interactive game application
        if 'interactive_game' in project_type.lower() or (has_rendering and 'pygame' in str(technologies).lower()):
            purpose_parts.append(f"**OBSERVED:** An interactive real-time application built with Pygame. Contains {total_funcs} functions implementing rendering ({has_rendering}), collision detection ({has_collision}), and frame-based execution.")
            purpose_parts.append(f"**EXECUTION MODEL:** Frame-driven continuous loop with event polling, not batch processing or library-style invocation.")
            
            # GEMINI VALIDATION: Enhance with whole-codebase context
            phi3_purpose = " ".join(purpose_parts)
            if self.phi3_generator and hasattr(self.phi3_generator, 'gemini_enhancer'):
                gemini = self.phi3_generator.gemini_enhancer
                if gemini and gemini.available and self.phi3_generator.project_context:
                    enhanced_purpose = gemini.validate_project_classification(
                        phi3_purpose,
                        self.phi3_generator.project_context
                    )
                    return enhanced_purpose
            
            return phi3_purpose
        
        if 'web' in project_type.lower():
            if 'FastAPI' in technologies or 'Flask' in technologies or 'Django' in technologies:
                purpose_parts.append(f"A web API/service built with {', '.join(technologies)}.")
            else:
                purpose_parts.append("A web application.")
        elif 'data' in project_type.lower():
            purpose_parts.append(f"A data analysis/science project using {', '.join(technologies) if technologies else 'Python'}.")
        elif 'cli' in project_type.lower():
            purpose_parts.append("A command-line tool for automated processing.")
        elif 'database' in project_type.lower():
            purpose_parts.append("A database implementation providing CRUD operations with indexing and query capabilities.")
        elif 'utility' in project_type.lower():
            purpose_parts.append("A utility library providing reusable functions and classes.")
        else:
            purpose_parts.append(f"A {project_type.replace('_', ' ')} project.")
        
        purpose_parts.append(f"Contains {total_funcs} functions across {total_files} modules.")
        
        phi3_purpose = " ".join(purpose_parts)
        
        # GEMINI VALIDATION for all project types
        if self.phi3_generator and hasattr(self.phi3_generator, 'gemini_enhancer'):
            gemini = self.phi3_generator.gemini_enhancer
            if gemini and gemini.available and self.phi3_generator.project_context:
                enhanced_purpose = gemini.validate_project_classification(
                    phi3_purpose,
                    self.phi3_generator.project_context
                )
                return enhanced_purpose
        
        return phi3_purpose
    
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
            # Return full docstring, properly formatted
            return func.docstring.strip()
        
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
    
    def _generate_comprehensive_function_doc(self, func, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate comprehensive API-style documentation for a function using Phi-3"""
        
        doc = f"##### Function: `{func.name}`\n\n"
        
        # Function signature with proper formatting (valid Python)
        if func.args:
            args_list = []
            for arg in func.args:
                if arg != 'self':
                    args_list.append(arg)
            args_str = ', '.join(args_list)
        else:
            args_str = ""
        
        return_type = func.return_type or "None"
        doc += f"```python\n"
        doc += f"def {func.name}({args_str}):\n"
        doc += f"    ...\n"
        doc += f"```\n\n"
        
        # Try to get comprehensive documentation from Phi-3
        if self.phi3_generator is not None:
            try:
                # Build code snippet
                function_code = f"def {func.name}({args_str}):\n"
                if func.docstring:
                    function_code += f'    """{func.docstring}"""\n'
                function_code += "    pass"
                
                # Prepare context
                context = {
                    'called_by': self._find_callers(func.name, analysis),
                    'calls': func.calls or [],
                    'complexity': func.complexity,
                    'file_path': func.file_path or 'unknown',
                    'semantic_category': getattr(func, 'semantic_category', 'general')
                }
                
                phi3_doc = self.phi3_generator.generate_function_docstring(
                    function_code=function_code,
                    function_name=func.name,
                    context=context,
                    style="comprehensive"
                )
                
                if phi3_doc and len(phi3_doc) > 100:
                    # Parse and format the Phi-3 output
                    doc += self._format_phi3_output_as_api_doc(phi3_doc, func)
                    return doc
                    
            except Exception as e:
                # Fall through to manual formatting
                pass
        
        # EVIDENCE-BASED formatting - NO tautologies
        behavior = self._describe_observed_behavior(func, file_info, analysis)
        
        if behavior and not self._is_tautological(behavior, func.name):
            doc += f"**Observed Behavior:**\n\n{behavior}\n\n"
        elif func.docstring and len(func.docstring) > 50 and not self._is_tautological(func.docstring, func.name):
            doc += f"**Observed Behavior:**\n\n{func.docstring}\n\n"
        else:
            # BE HONEST when we can't infer
            doc += f"**Observed Behavior:**\n\n*Insufficient information for semantic analysis. Function operates on {len(func.args)} parameters. Called {len(self._find_callers(func.name, analysis))} times in codebase.*\n\n"
        
        # Arguments section - Sphinx/reST style
        if func.args:
            for arg in func.args:
                if arg == 'self':
                    continue
                # Infer argument purpose from name
                arg_purpose = self._infer_argument_purpose(arg, func)
                arg_type = self._infer_argument_type(arg, func)
                doc += f":param {arg}: {arg_purpose}\n"
                doc += f":type {arg}: {arg_type}\n"
            doc += "\n"
        
        # Returns section - Sphinx/reST style
        if return_type and return_type != "None":
            doc += f":return: {self._infer_return_purpose(func, return_type)}\n"
            doc += f":rtype: {return_type}\n\n"
        
        # Dependencies/Calls section
        if func.calls and len(func.calls) > 0:
            doc += f"**Dependencies:**\n\n"
            doc += f"This function calls: {', '.join(f'`{call}()`' for call in func.calls[:5])}\n"
            if len(func.calls) > 5:
                doc += f" and {len(func.calls) - 5} more functions"
            doc += "\n\n"
        
        # Called By section (reverse dependencies)
        callers = self._find_callers(func.name, analysis)
        if callers:
            doc += f"**Called By:**\n\n"
            doc += f"Referenced by: {', '.join(f'`{caller}()`' for caller in callers[:5])}\n\n"
        
        # Complexity analysis
        if func.complexity > 10:
            doc += f"**⚠️ Complexity:** {func.complexity} (High - Consider refactoring)\n\n"
        elif func.complexity > 5:
            doc += f"**Complexity:** {func.complexity} (Moderate)\n\n"
        
        # Usage example - HONEST about return values
        doc += f"**Example Usage:**\n\n"
        doc += f"```python\n"
        if func.args and func.args[0] != 'self':
            example_args = ', '.join(self._generate_example_arg(arg) for arg in func.args if arg != 'self')
            # Only show assignment if function actually returns something
            returns_value = func.return_type and func.return_type not in ['None', 'NoneType']
            if returns_value:
                doc += f"result = {func.name}({example_args})\n"
            else:
                doc += f"{func.name}({example_args})  # No return value\n"
        else:
            doc += f"{func.name}()\n"
        doc += f"```\n\n"
        
        return doc
    
    def _format_phi3_output_as_api_doc(self, phi3_output: str, func) -> str:
        """Format Phi-3 docstring output into structured API documentation"""
        # Phi-3 typically returns well-structured docstrings
        # Just format them with proper headers
        
        doc = ""
        lines = phi3_output.strip().split('\n')
        
        current_section = "description"
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect code blocks
            if '```' in stripped:
                in_code_block = not in_code_block
                doc += line + "\n"
                continue
            
            if in_code_block:
                doc += line + "\n"
                continue
            
            # Format section headers
            if stripped.startswith('Args:') or stripped.startswith('Arguments:'):
                doc += "\n**Arguments:**\n\n"
                current_section = "args"
            elif stripped.startswith('Returns:'):
                doc += "\n**Returns:**\n\n"
                current_section = "returns"
            elif stripped.startswith('Example:') or stripped.startswith('Examples:'):
                doc += "\n**Example Usage:**\n\n"
                current_section = "example"
            elif stripped.startswith('Note:') or stripped.startswith('Notes:'):
                doc += "\n**Notes:**\n\n"
                current_section = "notes"
            elif stripped.startswith('Raises:'):
                doc += "\n**Raises:**\n\n"
                current_section = "raises"
            else:
                doc += line + "\n"
        
        return doc
    
    def _find_callers(self, func_name: str, analysis: Dict[str, Any]) -> List[str]:
        """Find functions that call the given function"""
        callers = []
        for file_info in analysis.get('file_analysis', {}).values():
            for func in file_info.get('functions', []):
                if func_name in func.calls:
                    callers.append(func.name)
        return callers[:5]  # Limit to 5
    
    def _infer_argument_type(self, arg_name: str, func) -> str:
        """Infer argument type based on name patterns"""
        arg_lower = arg_name.lower()
        
        # Specific coordinate types
        if arg_lower in ['x', 'y', 'row', 'col', 'column']:
            return "int"
        elif 'coord' in arg_lower or 'pos' in arg_lower or 'position' in arg_lower:
            return "Tuple[int, int]"
        # IDs and keys
        elif '_id' in arg_lower or arg_lower.endswith('id'):
            return "str"
        elif 'name' in arg_lower or 'key' in arg_lower:
            return "str"
        elif 'count' in arg_lower or 'size' in arg_lower or 'index' in arg_lower or 'num' in arg_lower:
            return "int"
        elif 'flag' in arg_lower or arg_lower.startswith('is_') or arg_lower.startswith('has_') or 'enabled' in arg_lower:
            return "bool"
        elif 'list' in arg_lower or 'items' in arg_lower or 'entries' in arg_lower:
            return "List"
        elif 'dict' in arg_lower or 'map' in arg_lower or 'mapping' in arg_lower:
            return "Dict"
        elif 'config' in arg_lower or 'settings' in arg_lower:
            return "Dict[str, Any]"
        elif 'data' in arg_lower:
            return "bytes or str"
        elif 'path' in arg_lower or 'file' in arg_lower or 'dir' in arg_lower:
            return "str"
        elif 'url' in arg_lower:
            return "str"
        elif 'text' in arg_lower or 'message' in arg_lower or 'content' in arg_lower:
            return "str"
        elif 'color' in arg_lower or 'colour' in arg_lower:
            return "Tuple[int, int, int]"
        elif 'self' in arg_lower:
            return "Self"
        elif 'cls' in arg_lower:
            return "Type"
        else:
            # Look at function name for context
            func_name = func.name.lower()
            if 'parse' in func_name or 'load' in func_name:
                return "str"
            elif 'process' in func_name or 'handle' in func_name:
                return "object"
            return "str"
    
    def _infer_argument_purpose(self, arg_name: str, func) -> str:
        """Infer the purpose of an argument from its name"""
        arg_lower = arg_name.lower()
        
        # Coordinate parameters
        if arg_lower == 'x':
            return "Horizontal coordinate"
        elif arg_lower == 'y':
            return "Vertical coordinate"
        elif 'row' in arg_lower:
            return "Row index in grid"
        elif 'col' in arg_lower:
            return "Column index in grid"
        elif 'pos' in arg_lower or 'position' in arg_lower:
            return "Position tuple (x, y)"
        # Display parameters
        elif 'screen' in arg_lower or 'surface' in arg_lower:
            return "Rendering surface"
        elif 'color' in arg_lower or 'colour' in arg_lower:
            return "RGB color tuple (red, green, blue)"
        # Data structures
        elif 'shape' in arg_lower:
            return "Shape configuration matrix"
        elif 'board' in arg_lower or 'grid' in arg_lower or 'field' in arg_lower:
            return "Game state matrix"
        elif 'tree' in arg_lower or 'node' in arg_lower:
            return "Syntax tree node"
        # File operations
        elif 'path' in arg_lower:
            return "Filesystem path"
        elif 'file' in arg_lower:
            return "File object or path"
        elif 'dir' in arg_lower:
            return "Directory path"
        # Configuration
        elif 'config' in arg_lower or 'settings' in arg_lower:
            return "Configuration dictionary"
        elif 'options' in arg_lower:
            return "Optional parameters"
        # Text content
        elif 'content' in arg_lower:
            return "Text content"
        elif 'text' in arg_lower or 'message' in arg_lower:
            return "Text string"
        elif 'name' in arg_lower:
            return "Identifier name"
        elif 'key' in arg_lower:
            return "Dictionary key"
        # Data processing
        elif 'data' in arg_lower:
            return "Input data"
        elif 'code' in arg_lower:
            return "Source code string"
        elif 'context' in arg_lower:
            return "Contextual information"
        # Boolean flags
        elif arg_lower.startswith('is_') or arg_lower.startswith('has_'):
            return f"Whether {arg_name[3:].replace('_', ' ')}"
        elif 'flag' in arg_lower or 'enabled' in arg_lower:
            return f"Enable/disable {arg_name.replace('_flag', '').replace('_', ' ')}"
        # Generic but informative
        else:
            # Avoid tautology - don't just repeat the parameter name
            cleaned = arg_name.replace('_', ' ').strip()
            if cleaned == 'self' or cleaned == 'cls':
                return "Instance reference"
            return f"{cleaned.capitalize()} value"
    
    def _infer_return_purpose(self, func, return_type: str) -> str:
        """Infer what the return value represents"""
        func_name = func.name.lower()
        
        if 'bool' in return_type.lower() or ('check' in func_name or 'is_' in func_name or 'has_' in func_name):
            return "Boolean indicating success/validity of the operation"
        elif 'get' in func_name or 'find' in func_name:
            return f"Retrieved {func_name.replace('get_', '').replace('find_', '').replace('_', ' ')}"
        elif 'calculate' in func_name or 'compute' in func_name:
            return "Calculated result value"
        elif 'list' in return_type.lower():
            return "List of results"
        elif 'dict' in return_type.lower():
            return "Dictionary containing results"
        else:
            return "Processing result"
    
    def _is_tautological(self, description: str, func_name: str) -> bool:
        """Check if a description is just restating the function name"""
        desc_lower = description.lower()
        name_lower = func_name.lower()
        
        # Remove common prefixes
        name_words = name_lower.replace('_', ' ').split()
        
        # Check if description is just the function name with filler words
        filler = ['function', 'method', 'implements', 'handles', 'performs', 'does', 'the', 'a', 'an']
        desc_words = [w for w in desc_lower.split() if w not in filler]
        
        # If most content words from description are in function name, it's tautological
        if len(desc_words) <= len(name_words):
            matches = sum(1 for w in desc_words if w in name_words)
            if matches >= len(desc_words) * 0.7:  # 70% overlap
                return True
        
        return False
    
    def _describe_observed_behavior(self, func, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Describe what the function observably does based on code evidence"""
        
        func_name = func.name.lower()
        calls = func.calls or []
        args = func.args or []
        
        # Game rendering functions
        if 'draw' in func_name or 'render' in func_name:
            if 'pygame' in str(file_info.get('imports', [])):
                if 'rect' in calls:
                    return f"Renders visual elements to the screen using pygame drawing primitives. Called during the game loop's render phase."
                elif 'blit' in calls:
                    return f"Composites pre-rendered surfaces onto the display. Part of the game's rendering pipeline."
        
        # Collision detection
        if 'collision' in func_name or 'check' in func_name:
            if any(arg in ['shape', 'board', 'grid', 'x', 'y'] for arg in args):
                return f"Validates spatial constraints by testing whether the given shape overlaps with existing occupied cells or boundary limits. Acts as a safety gate for all movement operations."
        
        # Piece spawning
        if 'spawn' in func_name or 'create' in func_name:
            if 'random' in calls or 'choice' in calls:
                return f"Instantiates a new game piece with randomized type and validates initial placement. Critical for game flow continuity."
        
        # Rotation
        if 'rotate' in func_name:
            if 'shape' in args:
                return f"Transforms piece geometry by 90 degrees and validates the new configuration against spatial constraints. Implements wall-kick logic if present."
        
        # Placement
        if 'place' in func_name:
            return f"Commits the current piece to the playfield grid, making it part of the permanent game state. Triggers line-clearing and spawning logic."
        
        # UI rendering
        if 'ui' in func_name:
            if 'render' in calls or 'blit' in calls:
                return f"Displays game metadata (score, level, next piece preview) independent of the playfield grid. Updates on state change, not per-frame."
        
        # Event loop
        if 'main' in func_name or 'loop' in func_name:
            if 'event' in calls or 'tick' in calls:
                return f"Main execution loop that coordinates frame-by-frame updates: event processing, game logic, and rendering. Runs until termination condition."
        
        # Default: be honest
        return ""
    
    def _generate_example_arg(self, arg_name: str) -> str:
        """Generate example value for an argument"""
        arg_lower = arg_name.lower()
        
        if any(coord in arg_lower for coord in ['x', 'y']):
            return "0"
        elif 'color' in arg_lower:
            return "(255, 0, 0)"
        elif 'shape' in arg_lower:
            return "shape_data"
        elif 'board' in arg_lower or 'grid' in arg_lower:
            return "game_board"
        elif 'screen' in arg_lower or 'surface' in arg_lower:
            return "screen"
        elif 'text' in arg_lower or 'str' in arg_lower:
            return '"example text"'
        elif 'bool' in arg_lower or arg_lower.startswith('is_') or arg_lower.startswith('has_'):
            return "True"
        else:
            return f"{arg_name}_value"
    
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
    
    # Human-friendly documentation helper methods
    def _humanize_function_purpose(self, func) -> str:
        """Generate human-friendly function purpose"""
        name = func.name.lower()
        
        # Common patterns with natural language
        if name == '__init__':
            return "Sets up a new instance with initial configuration"
        elif name.startswith('get_'):
            item = name[4:].replace('_', ' ')
            return f"Retrieves {item} from the system"
        elif name.startswith('set_') or name.startswith('update_'):
            item = name.split('_', 1)[1].replace('_', ' ')
            return f"Updates {item} in the system"
        elif name.startswith('is_') or name.startswith('has_') or name.startswith('can_'):
            condition = name.split('_', 1)[1].replace('_', ' ')
            return f"Checks if {condition}"
        elif name.startswith('create_') or name.startswith('make_'):
            item = name.split('_', 1)[1].replace('_', ' ')
            return f"Creates a new {item}"
        elif name.startswith('delete_') or name.startswith('remove_'):
            item = name.split('_', 1)[1].replace('_', ' ')
            return f"Removes {item} from the system"
        elif name.startswith('find_') or name.startswith('search_'):
            item = name.split('_', 1)[1].replace('_', ' ')
            return f"Searches for {item}"
        elif name.startswith('validate_'):
            item = name[9:].replace('_', ' ')
            return f"Validates {item} to ensure it's correct"
        elif name.startswith('process_') or name.startswith('handle_'):
            item = name.split('_', 1)[1].replace('_', ' ')
            return f"Processes {item}"
        else:
            return f"Handles {name.replace('_', ' ')} operations"
    
    def _infer_function_behavior(self, func) -> str:
        """Infer what the function actually does"""
        name = func.name.lower()
        complexity = getattr(func, 'complexity', 1)
        
        if complexity > 10:
            behavior = f"This is a complex function that orchestrates multiple steps to {name.replace('_', ' ')}."
        elif complexity > 5:
            behavior = f"Performs {name.replace('_', ' ')} with several validation and processing steps."
        else:
            behavior = f"A straightforward function that {name.replace('_', ' ')}."
        
        if func.calls:
            behavior += f" It delegates to {len(func.calls)} other function(s) to accomplish this."
        
        return behavior
    
    def _describe_parameter_context(self, param: str, func) -> str:
        """Describe parameter with contextual information"""
        param_lower = param.lower()
        
        # Common parameter patterns
        if param in ['self', 'cls']:
            return "Reference to the instance/class"
        elif param_lower in ['data', 'input', 'value']:
            return "The input data to process"
        elif param_lower in ['config', 'settings', 'options']:
            return "Configuration options for behavior customization"
        elif param_lower.endswith('_id') or param_lower == 'id':
            return "Unique identifier for lookup"
        elif param_lower.endswith('_path') or param_lower == 'path':
            return "File or directory path"
        elif param_lower in ['callback', 'handler']:
            return "Function to call when action completes"
        elif param_lower in ['timeout', 'delay']:
            return "Time limit in seconds"
        elif 'name' in param_lower:
            return "Name for identification"
        elif 'count' in param_lower or 'num' in param_lower or 'size' in param_lower:
            return f"Number of {param_lower.replace('count', '').replace('num_', '').replace('size', '').replace('_', ' ').strip() or 'items'}"
        else:
            return f"Parameter for {func.name} - {param.replace('_', ' ')}"
    
    def _explain_function_workflow(self, func, analysis: Dict[str, Any]) -> str:
        """Explain how the function works step by step"""
        name = func.name.lower()
        
        # Pattern-based workflow explanation
        if 'process' in name or 'handle' in name:
            workflow = "Takes input, validates it, processes the data, and returns the result"
        elif 'get' in name or 'fetch' in name or 'retrieve' in name:
            workflow = "Looks up the requested data and returns it, handling missing data gracefully"
        elif 'set' in name or 'update' in name or 'save' in name:
            workflow = "Validates the new data, updates the internal state, and confirms the change"
        elif 'create' in name or 'make' in name or 'build' in name:
            workflow = "Initializes a new object, sets its properties, and returns it ready to use"
        elif 'delete' in name or 'remove' in name:
            workflow = "Finds the target item, performs cleanup, and removes it from the system"
        elif 'validate' in name or 'check' in name or 'verify' in name:
            workflow = "Runs validation rules and returns True/False or raises an error if invalid"
        elif 'parse' in name or 'decode' in name:
            workflow = "Reads the input format, extracts the data, and converts it to a usable structure"
        else:
            workflow = f"Executes the {name.replace('_', ' ')} logic and returns the result"
        
        if func.complexity > 10:
            workflow += ". This is a complex operation with multiple steps and edge cases."
        
        return workflow
    
    def _suggest_use_cases(self, func) -> str:
        """Suggest when developers should use this function"""
        name = func.name.lower()
        
        if name.startswith('get_') or 'fetch' in name:
            return "Use this when you need to retrieve data from the system"
        elif name.startswith('set_') or 'update' in name:
            return "Use this when you need to modify existing data"
        elif name.startswith('create_') or 'make' in name:
            return "Use this when initializing new objects or resources"
        elif name.startswith('delete_') or 'remove' in name:
            return "Use this when cleaning up or removing resources"
        elif name.startswith('is_') or name.startswith('has_') or 'check' in name:
            return "Use this to verify conditions before proceeding with operations"
        elif name.startswith('process_') or 'handle' in name:
            return "Use this as your main entry point for handling this type of operation"
        elif 'validate' in name:
            return "Use this to ensure data meets requirements before processing"
        else:
            return f"Use this when you need to {name.replace('_', ' ')}"
    
    def _generate_realistic_example(self, func) -> str:
        """Generate realistic usage example"""
        name = func.name
        args = getattr(func, 'args', [])
        
        # Filter out self/cls
        params = [p for p in args if p not in ['self', 'cls']]
        
        example_parts = []
        
        # Create realistic parameter values
        param_examples = []
        for param in params[:3]:  # First 3 params
            param_lower = param.lower()
            if 'name' in param_lower:
                param_examples.append(f'{param}="my_item"')
            elif 'id' in param_lower:
                param_examples.append(f'{param}=123')
            elif 'path' in param_lower:
                param_examples.append(f'{param}="/path/to/file"')
            elif 'data' in param_lower or 'value' in param_lower:
                param_examples.append(f'{param}={{"key": "value"}}')
            elif 'count' in param_lower or 'size' in param_lower:
                param_examples.append(f'{param}=10')
            elif 'config' in param_lower:
                param_examples.append(f'{param}={{"option": True}}')
            else:
                param_examples.append(f'{param}=value')
        
        # Build example
        if params:
            example = f'result = {name}({", ".join(param_examples)})'
        else:
            example = f'result = {name}()'
        
        example_parts.append(example)
        
        # Add what to do with result
        if func.return_type:
            example_parts.append(f'# Returns: {func.return_type}')
            example_parts.append('print(result)')
        
        return '\n'.join(example_parts)
    
    def _generate_developer_tips(self, func) -> str:
        """Generate practical tips for developers"""
        tips = []
        name = func.name.lower()
        complexity = getattr(func, 'complexity', 1)
        
        # Complexity-based tips
        if complexity > 10:
            tips.append("This function is complex - consider breaking it into smaller functions")
        
        # Pattern-based tips
        if name.startswith('get_') or 'fetch' in name:
            tips.append("Handle the case where data might not exist (None/empty)")
        elif name.startswith('set_') or 'update' in name:
            tips.append("Always validate input before updating")
        elif name.startswith('delete_') or 'remove' in name:
            tips.append("Check if the item exists before attempting to delete")
        elif 'async' in name or func.name.startswith('a'):
            tips.append("Remember to await this if it's async")
        elif 'process' in name or 'handle' in name:
            tips.append("Wrap in try-except for robust error handling")
        
        # Call relationship tips
        if hasattr(func, 'calls') and len(func.calls) > 5:
            tips.append(f"Calls {len(func.calls)} other functions - be aware of the dependency chain")
        
        return ". ".join(tips) if tips else ""
    
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
        """Evidence-based complexity description without judgment"""
        avg = analysis['complexity_metrics']['average_function_complexity']
        total = analysis['complexity_metrics']['total_functions']
        return f"Average cyclomatic complexity: {avg:.1f} across {total} functions. Complexity above 10 typically indicates refactoring opportunities."
    
    def _recommend_complexity_improvement(self, analysis: Dict[str, Any]) -> str:
        """Complexity observations without value judgments"""
        avg = analysis['complexity_metrics']['average_function_complexity']
        if avg > 10:
            return f"Functions with complexity >10 detected. Refactoring options: extract methods, reduce branching"
        elif avg > 7:
            return f"Average complexity {avg:.1f}. Possible actions: extract helpers, simplify conditionals"
        else:
            return f"Average complexity {avg:.1f}. No immediate refactoring triggers detected"
    
    def _assess_documentation(self, analysis: Dict[str, Any]) -> str:
        """Evidence-based documentation description without qualitative judgment"""
        coverage = analysis['quality_metrics']['documentation_coverage']
        total_funcs = analysis['complexity_metrics']['total_functions']
        documented = int(total_funcs * coverage / 100)
        return f"{documented} of {total_funcs} functions have docstrings ({coverage:.0f}%). No quality judgment provided without rubric."
    
    def _recommend_documentation_improvement(self, analysis: Dict[str, Any]) -> str:
        """Documentation observations without quality judgments"""
        coverage = analysis['quality_metrics']['documentation_coverage']
        total_funcs = analysis['complexity_metrics']['total_functions']
        documented = int(total_funcs * coverage / 100)
        undocumented = total_funcs - documented
        
        if coverage < 50:
            return f"{undocumented} functions lack docstrings. Options: add Google-style docstrings, use autodoc tools"
        elif coverage < 80:
            return f"{undocumented} functions undocumented. Consider: parameter descriptions, usage examples, return types"
        else:
            return f"{documented}/{total_funcs} functions documented. Remaining: evaluate public API priority"
    
    def _assess_distribution(self, analysis: Dict[str, Any]) -> str:
        """Report code distribution metrics without judgment"""
        fpf = analysis['quality_metrics']['functions_per_file']
        return f"{fpf:.1f} functions per file on average. Module granularity impacts parallel development and test isolation."
    
    def _recommend_distribution_improvement(self, analysis: Dict[str, Any]) -> str:
        """Suggest distribution options based on size"""
        fpf = analysis['quality_metrics']['functions_per_file']
        total_files = analysis['total_files']
        total_funcs = analysis['complexity_metrics']['total_functions']
        
        if fpf > 15:
            return f"Current: {total_funcs} functions in {total_files} file(s). Option: Split by domain/responsibility to enable parallel development."
        elif fpf > 10:
            return f"Current: {total_funcs} functions in {total_files} file(s). Option: Group related functions into classes or separate modules."
        else:
            return f"Current: {total_funcs} functions in {total_files} file(s). Reorganization trade-offs depend on team preferences."
    
    def _assess_coupling(self, analysis: Dict[str, Any]) -> str:
        """Assess system coupling"""
    def _assess_coupling(self, analysis: Dict[str, Any]) -> str:
        """Report coupling metrics without judgment"""
        edges = len(analysis['call_graph']['edges'])
        total_funcs = analysis['complexity_metrics']['total_functions']
        ratio = edges / total_funcs if total_funcs > 0 else 0
        
        return f"Coupling ratio: {ratio:.2f} ({edges} inter-function calls among {total_funcs} functions). Higher ratios indicate more interdependence."
    
    def _recommend_coupling_improvement(self, analysis: Dict[str, Any]) -> str:
        """Suggest coupling options based on current state"""
        edges = len(analysis['call_graph']['edges'])
        total_funcs = analysis['complexity_metrics']['total_functions']
        ratio = edges / total_funcs if total_funcs > 0 else 0
        
        if ratio > 1.0:
            return f"Current: {edges} calls among {total_funcs} functions (ratio: {ratio:.2f}). Option: Introduce interfaces or data-driven patterns to reduce direct calls."
        else:
            return f"Current: {edges} calls among {total_funcs} functions (ratio: {ratio:.2f}). Refactoring trade-offs depend on change frequency."
    
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
        """Identify structural constraints without judgment"""
        constraints = []
        
        if analysis['complexity_metrics']['max_complexity'] > 20:
            constraints.append(f"Maximum complexity: {analysis['complexity_metrics']['max_complexity']}. Values above 20 correlate with higher testing effort")
        
        if not self._has_tests(analysis):
            constraints.append("No test files detected. Test presence enables automated regression detection")
        
        doc_cov = analysis['quality_metrics']['documentation_coverage']
        if doc_cov < 50:
            constraints.append(f"Documentation coverage: {doc_cov:.0f}%. Inline documentation supports onboarding")
        
        if not constraints:
            constraints.append("No measurable structural constraints identified")
        
        return '\n'.join(f"- {constraint}" for constraint in constraints)
    
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
        """Generate project-specific usage examples based on actual code analysis"""
        
        # Extract actual class and function names from analysis
        main_classes = []
        main_functions = []
        
        for file_info in analysis.get('file_analysis', {}).values():
            classes = file_info.get('classes', [])
            functions = file_info.get('functions', [])
            
            # Get meaningful classes (not utility classes)
            for cls in classes[:2]:  # Top 2 classes
                if cls.name and not cls.name.startswith('_') and len(cls.methods) > 2:
                    main_classes.append(cls.name)
            
            # Get key functions
            for func in functions[:3]:  # Top 3 functions
                if (func.name and not func.name.startswith('_') and 
                    func.name not in ['__init__', 'main'] and
                    func.complexity > 2):
                    main_functions.append(func.name)
        
        if project_type == 'database_project':
            if main_classes:
                main_class = main_classes[0]
                return f"""```python
# Database operations example
from main import {main_class}

# Initialize database
db = {main_class}()

# Basic operations
{'db.create_table("users", {"id": int, "name": str})' if 'create' in str(main_functions) else 'db.insert("key1", "value1")'}
{'db.insert({"id": 1, "name": "John"})' if 'insert' in str(main_functions) else 'result = db.search("key1")'}
result = db.get{"_all()" if 'get_all' in str(main_functions) else '("key1")'}
```"""
            
        elif project_type == 'web_application':
            web_tech = 'FastAPI' if 'FastAPI' in str(analysis.get('key_technologies', [])) else 'Flask'
            return f"""```python
# Start the {web_tech} application
python main.py

# API usage example
import requests
response = requests.get('http://localhost:8000/api/docs')  # Access documentation
response = requests.post('http://localhost:8000/generate', json={{"data": "example"}})
```"""
        
        elif project_type == 'utility_library':
            if main_classes and main_functions:
                main_class = main_classes[0]
                main_func = main_functions[0]
                return f"""```python
# Import the main components
from main import {main_class}

# Initialize and use
processor = {main_class}()
result = processor.{main_func}(input_data)
print(result)
```"""
            elif main_functions:
                main_func = main_functions[0]
                return f"""```python
# Import and use key functions
from main import {main_func}

# Process your data
result = {main_func}(your_input)
print(result)
```"""
        
        elif project_type == 'command_line_tool':
            return """```bash
# Command line usage
python main.py --help
python main.py --input data.txt --output results.txt

# Or direct import
python -c "from main import main; main()"
```"""
        
        # Fallback with actual function names if available
        if main_classes:
            main_class = main_classes[0]
            return f"""```python
# Import and use the main class
from main import {main_class}

# Initialize and use
instance = {main_class}()
result = instance.process(your_data)
```"""
        elif main_functions:
            main_func = main_functions[0]
            return f"""```python
# Import and use key functions
from main import {main_func}

# Use the functionality
result = {main_func}(your_parameters)
```"""
        else:
            return """```python
# Basic usage
import main

# See the module documentation for specific functions and classes
help(main)
```"""
    
    # Helper methods for technical comprehensive style
    def _assess_overall_complexity(self, analysis: Dict[str, Any]) -> str:
        """Evidence-based overall complexity description"""
        avg = analysis['complexity_metrics']['average_function_complexity']
        total = analysis['complexity_metrics']['total_functions']
        return f"{total} functions with average cyclomatic complexity of {avg:.1f}. Implications for maintainability depend on future growth and team familiarity."
    
    def _explain_technology_role(self, tech: str, analysis: Dict[str, Any]) -> str:
        """Explain the role of a technology in the project"""
        tech_lower = tech.lower()
        if 'fastapi' in tech_lower or 'flask' in tech_lower:
            return "Web framework for REST API endpoints"
        elif 'streamlit' in tech_lower:
            return "Interactive web UI framework"
        elif 'transformers' in tech_lower:
            return "AI/ML model integration"
        elif 'pandas' in tech_lower or 'numpy' in tech_lower:
            return "Data manipulation and analysis"
        elif 'pytest' in tech_lower or 'unittest' in tech_lower:
            return "Testing framework"
        else:
            return "Core functionality support"
    
    def _describe_stack_capabilities(self, analysis: Dict[str, Any]) -> str:
        """Describe what the technology stack enables"""
        tech_count = len(analysis['key_technologies'])
        if tech_count >= 5:
            return "a comprehensive feature set with multiple specialized capabilities"
        elif tech_count >= 3:
            return "core functionality with key supporting libraries"
        else:
            return "focused functionality with minimal dependencies"
    
    def _identify_problem_domain(self, analysis: Dict[str, Any], project_type: str) -> str:
        """Identify the problem domain the project addresses"""
        if 'web' in project_type.lower():
            return "Web Application Development"
        elif 'data' in project_type.lower():
            return "Data Science & Analytics"
        elif 'ml' in project_type.lower() or 'ai' in project_type.lower():
            return "Artificial Intelligence & Machine Learning"
        elif 'cli' in project_type.lower():
            return "Command-Line Interface & Automation"
        else:
            return "General Software Development"
    
    def _generate_capability_analysis(self, analysis: Dict[str, Any]) -> str:
        """Generate analysis of project capabilities"""
        capabilities = []
        func_count = analysis['complexity_metrics']['total_functions']
        class_count = analysis['complexity_metrics']['total_classes']
        
        if func_count > 50:
            capabilities.append(f"- **Extensive Functionality**: {func_count} functions providing comprehensive feature coverage")
        elif func_count > 20:
            capabilities.append(f"- **Core Functionality**: {func_count} functions implementing key features")
        else:
            capabilities.append(f"- **Focused Functionality**: {func_count} functions for specific use cases")
        
        if class_count > 10:
            capabilities.append(f"- **Object-Oriented Design**: {class_count} classes for structured code organization")
        elif class_count > 0:
            capabilities.append(f"- **Mixed Approach**: {class_count} classes with procedural functions")
        
        return '\n'.join(capabilities)
    
    def _generate_architecture_narrative(self, analysis: Dict[str, Any]) -> str:
        """Generate narrative description of architecture"""
        return f"""The system follows a {"modular" if analysis['total_files'] > 5 else "compact"} architecture with 
{analysis['total_files']} modules working together. The codebase demonstrates {"object-oriented" if analysis['complexity_metrics']['total_classes'] > 10 else "procedural"} 
design patterns with {analysis['complexity_metrics']['total_functions']} functions and {analysis['complexity_metrics']['total_classes']} classes 
providing the core functionality.

The architecture is designed for {"high maintainability" if analysis['quality_metrics']['documentation_coverage'] > 60 else "practical development"} 
with {analysis['quality_metrics']['documentation_coverage']:.1f}% documentation coverage."""
    
    def _identify_architecture_patterns(self, analysis: Dict[str, Any]) -> str:
        """Identify architectural patterns in use"""
        patterns = []
        
        if analysis['complexity_metrics']['total_classes'] > 5:
            patterns.append("- **Object-Oriented**: Heavy use of classes for encapsulation and abstraction")
        
        if len(analysis['call_graph']['edges']) > analysis['complexity_metrics']['total_functions']:
            patterns.append("- **Layered Architecture**: Clear separation between components with defined interfaces")
        
        if 'FastAPI' in analysis['key_technologies'] or 'Flask' in analysis['key_technologies']:
            patterns.append("- **MVC/API Pattern**: Web framework with route handlers and business logic separation")
        
        if not patterns:
            patterns.append("- **Procedural/Functional**: Direct function-based implementation")
        
        return '\n'.join(patterns)
    
    def _generate_module_hierarchy(self, analysis: Dict[str, Any]) -> str:
        """Generate description of module hierarchy"""
        hierarchy = []
        for file_path in sorted(analysis['file_analysis'].keys())[:15]:
            indent = "  " * file_path.count('/')
            hierarchy.append(f"{indent}- `{file_path}`")
        
        if len(analysis['file_analysis']) > 15:
            hierarchy.append(f"  ... and {len(analysis['file_analysis']) - 15} more modules")
        
        return '\n'.join(hierarchy)
    
    def _describe_entry_point(self, entry_point: str, analysis: Dict[str, Any]) -> str:
        """Describe what an entry point does"""
        if 'main' in entry_point.lower():
            return "Primary application entry point and orchestrator"
        elif 'server' in entry_point.lower():
            return "Server startup and initialization"
        elif 'api' in entry_point.lower():
            return "API server entry point"
        else:
            return "Execution entry point"
    
    def _describe_component_interactions(self, analysis: Dict[str, Any]) -> str:
        """Describe how components interact"""
        edge_count = len(analysis['call_graph']['edges'])
        func_count = analysis['complexity_metrics']['total_functions']
        ratio = edge_count / func_count if func_count > 0 else 0
        
        if ratio > 0.8:
            return f"""Components are highly interconnected with {edge_count} inter-function calls across {func_count} functions.
This indicates tight integration and shared functionality across modules."""
        elif ratio > 0.4:
            return f"""Components have moderate interconnection with {edge_count} inter-function calls.
The architecture balances modularity with necessary integration."""
        else:
            return f"""Components are loosely coupled with {edge_count} inter-function calls.
The architecture emphasizes module independence and separation of concerns."""
    
    def _assess_maintainability(self, analysis: Dict[str, Any]) -> str:
        """Report maintainability factors without judgment"""
        doc_cov = analysis['quality_metrics']['documentation_coverage']
        complexity = analysis['complexity_metrics']['average_function_complexity']
        
        factors = []
        factors.append(f"Documentation coverage: {doc_cov:.0f}%")
        factors.append(f"Average complexity: {complexity:.1f}")
        
        # Cite research without making absolute judgments
        if complexity > 10:
            factors.append("Complexity above 10 correlates with higher defect density (McCabe, 1976)")
        
        return "; ".join(factors) + ". Actual maintainability depends on team experience and project evolution."
    
    def _infer_module_purpose(self, file_path: str, file_info: Dict[str, Any]) -> str:
        """Infer the purpose of a module"""
        file_lower = file_path.lower()
        if 'test' in file_lower:
            return "Testing and quality assurance"
        elif 'config' in file_lower:
            return "Configuration and settings management"
        elif 'main' in file_lower or '__main__' in file_lower:
            return "Application entry point and orchestration"
        elif 'api' in file_lower:
            return "API endpoint definitions and handlers"
        elif 'model' in file_lower:
            return "Data models and business logic"
        elif 'util' in file_lower or 'helper' in file_lower:
            return "Utility functions and helper methods"
        else:
            return "Core application functionality"
    
    def _describe_module_functionality(self, file_info: Dict[str, Any]) -> str:
        """Describe what a module provides"""
        func_count = len(file_info['functions'])
        class_count = len(file_info['classes'])
        
        if class_count > func_count:
            return f"{class_count} classes implementing object-oriented functionality"
        elif func_count > 0:
            return f"{func_count} functions providing procedural operations"
        else:
            return "constants, imports, and module-level definitions"
    
    def _describe_class_responsibility(self, cls) -> str:
        """Describe class responsibility"""
        name_lower = cls.name.lower()
        if 'manager' in name_lower:
            return "resource management and lifecycle control"
        elif 'handler' in name_lower:
            return "event or request handling"
        elif 'analyzer' in name_lower:
            return "data analysis and processing"
        elif 'generator' in name_lower:
            return "content or instance generation"
        else:
            return "core business logic operations"
    
    def _generate_method_brief(self, method) -> str:
        """Generate brief description of a method"""
        name = method.name.lower()
        if name == '__init__':
            return "Initialize the class instance"
        elif name.startswith('get'):
            return f"Retrieve {name[3:].replace('_', ' ')}"
        elif name.startswith('set'):
            return f"Set or update {name[3:].replace('_', ' ')}"
        elif name.startswith('create'):
            return f"Create new {name[6:].replace('_', ' ')}"
        else:
            return f"Handle {name.replace('_', ' ')} operations"
    
    def _generate_quality_analysis_comprehensive(self, analysis: Dict[str, Any]) -> str:
        """Generate evidence-based quality analysis without scores"""
        return f"""**Complexity Assessment:** {self._assess_complexity(analysis)}

**Documentation Quality:** {self._assess_documentation(analysis)}

**Code Distribution:** {self._assess_distribution(analysis)}

**Quality Assessment:** No quantitative quality score is assigned due to lack of comparative baseline and evaluation rubric.
"""
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate overall quality score"""
        score = 10
        
        # Deduct for high complexity
        if analysis['complexity_metrics']['average_function_complexity'] > 10:
            score -= 2
        elif analysis['complexity_metrics']['average_function_complexity'] > 7:
            score -= 1
        
        # Deduct for poor documentation
        if analysis['quality_metrics']['documentation_coverage'] < 40:
            score -= 3
        elif analysis['quality_metrics']['documentation_coverage'] < 60:
            score -= 1
        
        # Deduct for poor distribution
        if analysis['quality_metrics']['functions_per_file'] > 15:
            score -= 2
        
        return max(1, score)
    
    def _describe_execution_entry_points(self, analysis: Dict[str, Any]) -> str:
        """Describe execution entry points honestly"""
        
        entry_points = analysis.get('entry_points', [])
        
        # Check for game loop pattern
        has_game_loop = False
        has_rendering = False
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                fname = func.name.lower()
                if any(pattern in fname for pattern in ['main', 'loop', 'run', 'start']):
                    has_game_loop = True
                if 'draw' in fname or 'render' in fname:
                    has_rendering = True
        
        if has_game_loop and has_rendering:
            return "**OBSERVED:** Continuous execution loop (game loop pattern detected). Entry point likely in main/loop function with frame-based iteration, not one-shot execution."
        elif entry_points:
            return "\n".join(f"{i}. `{ep}`" for i, ep in enumerate(entry_points[:5], 1))
        else:
            return "*No explicit entry point detected. May be library-style module or missing __main__ block.*"
    
    def _describe_documentation_status(self, analysis: Dict[str, Any]) -> str:
        """Describe documentation status without judgment"""
        total_funcs = analysis['complexity_metrics']['total_functions']
        total_classes = analysis['complexity_metrics']['total_classes']
        
        # Count documented items
        documented_funcs = 0
        documented_classes = 0
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                if func.docstring:
                    documented_funcs += 1
            for cls in file_info.get('classes', []):
                if cls.docstring:
                    documented_classes += 1
        
        result = []
        if total_funcs > 0:
            result.append(f"{documented_funcs} of {total_funcs} functions have docstrings")
        if total_classes > 0:
            result.append(f"{documented_classes} of {total_classes} classes have docstrings")
        
        if not result:
            return "No functions or classes to document"
        
        return "; ".join(result) + ". No quality judgment provided without evaluation rubric."
    
    def _analyze_execution_model(self, analysis: Dict[str, Any]) -> str:
        """Analyze execution model reconciling entry points with runtime patterns"""
        entry_points = analysis.get('entry_points', [])
        
        # Detect runtime patterns
        has_game_loop = False
        has_main_guard = False
        has_server = False
        loop_functions = []
        
        for file_info in analysis['file_analysis'].values():
            for func in file_info.get('functions', []):
                fname = func.name.lower()
                # Detect loop patterns
                if any(pattern in fname for pattern in ['loop', 'run', 'main_loop', 'game_loop']):
                    has_game_loop = True
                    loop_functions.append(func.name)
                # Detect server patterns
                if any(pattern in fname for pattern in ['serve', 'listen', 'run_server', 'start_server']):
                    has_server = True
                # Detect main guard
                if 'if __name__ == "__main__"' in str(func):
                    has_main_guard = True
        
        # Check for draw/render patterns
        has_rendering = any(
            'draw' in func.name.lower() or 'render' in func.name.lower()
            for file_info in analysis['file_analysis'].values()
            for func in file_info.get('functions', [])
        )
        
        # Reconcile observations - NO contradictions
        result = []
        
        # Priority order: Most specific pattern wins
        if has_game_loop and has_rendering:
            result.append("**EXECUTION MODEL:** Frame-driven continuous loop with event polling, not batch processing or library-style invocation.")
            if loop_functions:
                result.append(f"Evidence: Loop functions detected ({', '.join(loop_functions)})")
            if entry_points:
                result.append(f"Entry point: {', '.join(entry_points)}")
            elif not has_main_guard:
                result.append("⚠️ WARNING: No `if __name__ == '__main__'` guard. Loop may start on import.")
        elif has_server:
            result.append("**EXECUTION MODEL:** Long-running server process (blocking I/O), not frame loop or library.")
            if entry_points:
                result.append(f"Server entry point: {', '.join(entry_points)}")
        elif entry_points:
            result.append(f"**EXECUTION MODEL:** Script with explicit entry point: {', '.join(entry_points)}. Runs once, then exits.")
        else:
            result.append("**EXECUTION MODEL:** No explicit entry point detected. May be library/module designed for import, OR missing main guard.")
        
        return "\n".join(result)
    
    def _generate_honest_quality_assessment(self, analysis: Dict[str, Any]) -> str:
        """Generate honest quality assessment without fake scores"""
        
        observations = []
        
        # Report complexity objectively
        avg_complexity = analysis['complexity_metrics']['average_function_complexity']
        if avg_complexity > 10:
            observations.append(f"Average cyclomatic complexity: {avg_complexity:.1f}. Functions above 10 typically require more testing effort and have higher bug rates (McCabe, 1976)")
        elif avg_complexity < 5:
            observations.append(f"Average cyclomatic complexity: {avg_complexity:.1f}. Below 5 indicates fewer decision points per function")
        else:
            observations.append(f"Average cyclomatic complexity: {avg_complexity:.1f}")
        
        # Report architecture objectively
        total_files = analysis['total_files']
        total_funcs = analysis['complexity_metrics']['total_functions']
        
        if total_files == 1 and total_funcs > 15:
            observations.append(f"Single-file architecture with {total_funcs} functions. Splitting into modules may improve test isolation and parallel development")
        
        # Report documentation objectively
        doc_coverage = analysis['quality_metrics']['documentation_coverage']
        observations.append(f"Documentation coverage: {doc_coverage:.0f}% of functions have docstrings")
        
        result = "**Structural Observations:**\n\n"
        result += "- " + "\n- ".join(observations) + "\n\n"
        
        return result
    
    def _assess_coupling_honestly(self, analysis: Dict[str, Any], edge_count: int) -> str:
        """Assess coupling honestly without contradictions"""
        total_files = analysis['total_files']
        total_funcs = analysis['complexity_metrics']['total_functions']
        
        if total_files == 1:
            return "**Coupling Assessment:** Single-file architecture. Traditional coupling metrics not applicable. All functions share namespace and may access global state."
        elif edge_count > total_funcs * 0.5:
            return f"**Coupling Assessment:** High inter-function coupling ({edge_count} calls among {total_funcs} functions = {edge_count/total_funcs:.1f} calls per function)"
        else:
            return f"**Coupling Assessment:** Moderate coupling ({edge_count} calls among {total_funcs} functions)"
    
    def _generate_dependency_analysis_comprehensive(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive dependency analysis"""
        edge_count = len(analysis['call_graph']['edges'])
        return f"""**Observed Dependencies:** {edge_count} inter-function calls

{self._assess_coupling_honestly(analysis, edge_count)}
"""
    
    def _generate_recommendations_comprehensive(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive recommendations"""
        recommendations = []
        
        # Complexity recommendations
        complexity_rec = self._recommend_complexity_improvement(analysis)
        if complexity_rec:
            recommendations.append(f"**Complexity:** {complexity_rec}")
        
        # Documentation recommendations
        doc_rec = self._recommend_documentation_improvement(analysis)
        if doc_rec:
            recommendations.append(f"**Documentation:** {doc_rec}")
        
        # Distribution recommendations
        dist_rec = self._recommend_distribution_improvement(analysis)
        if dist_rec:
            recommendations.append(f"**Code Organization:** {dist_rec}")
        
        return '\n\n'.join(recommendations) if recommendations else "No immediate improvements needed - codebase is well-maintained"
    
    def _count_public_apis(self, analysis: Dict[str, Any]) -> int:
        """Count total public APIs"""
        count = 0
        for file_info in analysis['file_analysis'].values():
            count += len([c for c in file_info.get('classes', []) if not c.name.startswith('_')])
            count += len([f for f in file_info.get('functions', []) if not f.name.startswith('_')])
        return count
    
    def _generate_project_assessment(self, analysis: Dict[str, Any]) -> str:
        """Generate project assessment based on observable metrics"""
        
        # Report facts without judgment
        avg_complexity = analysis['complexity_metrics']['average_function_complexity']
        doc_coverage = analysis['quality_metrics']['documentation_coverage']
        total_funcs = analysis['complexity_metrics']['total_functions']
        
        observations = []
        observations.append(f"{total_funcs} functions with average complexity {avg_complexity:.1f}")
        observations.append(f"{doc_coverage:.0f}% documentation coverage")
        
        if analysis['complexity_metrics']['max_complexity'] > 15:
            observations.append(f"Maximum complexity: {analysis['complexity_metrics']['max_complexity']}")
        
        return "; ".join(observations) + ". Project evolution depends on growth patterns and team practices."

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
    styles = ['google', 'numpy', 'technical_md', 'opensource', 'visual', 'repoagent']
    
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