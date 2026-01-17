"""
Multi-Language Code Analyzer
Supports: Python, JavaScript, TypeScript, Java, Go, C++, Rust, Ruby, PHP, Bash/Shell
Context: Markdown (.md) and Text (.txt) files for additional documentation
"""

import re
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class MultiLangFunctionInfo:
    """Universal function information across languages"""
    name: str
    language: str
    file_path: str
    line_start: int
    line_end: int
    params: List[Tuple[str, Optional[str]]]  # (name, type)
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int
    is_async: bool
    visibility: str  # public, private, protected
    is_static: bool
    decorators: List[str]
    annotations: List[str]

@dataclass
class MultiLangClassInfo:
    """Universal class information across languages"""
    name: str
    language: str
    file_path: str
    line_start: int
    line_end: int
    methods: List[MultiLangFunctionInfo]
    fields: List[Tuple[str, Optional[str]]]  # (name, type)
    extends: List[str]
    implements: List[str]
    docstring: Optional[str]
    visibility: str
    is_abstract: bool
    annotations: List[str]

class LanguageDetector:
    """Detect programming language from file extension and content"""
    
    EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.jsx': 'javascript',
        '.java': 'java',
        '.go': 'go',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.hpp': 'cpp',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
        '.ksh': 'bash',
        '.md': 'markdown',
        '.txt': 'text'
    }
    
    @classmethod
    def detect(cls, filename: str, content: str = "") -> str:
        """Detect language from filename and optionally content"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext in cls.EXTENSIONS:
            return cls.EXTENSIONS[ext]
        
        # Content-based detection
        if content:
            if 'def ' in content and 'import ' in content:
                return 'python'
            elif 'function ' in content or 'const ' in content:
                return 'javascript'
            elif 'interface ' in content or ': type' in content:
                return 'typescript'
            elif 'public class' in content or 'private class' in content:
                return 'java'
            elif 'func ' in content and 'package ' in content:
                return 'go'
            elif 'fn ' in content or 'impl ' in content:
                return 'rust'
            elif 'class << ' in content or 'def ' in content and 'end' in content:
                return 'ruby'
            elif '<?php' in content:
                return 'php'
            elif '#!/bin/bash' in content or '#!/bin/sh' in content or 'function ' in content:
                return 'bash'
        
        return 'unknown'

class PythonParser:
    """Parse Python code"""
    
    @staticmethod
    def parse_functions(content: str, file_path: str) -> List[MultiLangFunctionInfo]:
        """Extract functions from Python code"""
        import ast
        functions = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract parameters
                    params = []
                    for arg in node.args.args:
                        arg_name = arg.arg
                        arg_type = ast.unparse(arg.annotation) if arg.annotation else None
                        params.append((arg_name, arg_type))
                    
                    # Extract return type
                    return_type = ast.unparse(node.returns) if node.returns else None
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node)
                    
                    # Extract decorators
                    decorators = [ast.unparse(d) for d in node.decorator_list]
                    
                    # Calculate complexity (simplified)
                    complexity = PythonParser._calculate_complexity(node)
                    
                    func_info = MultiLangFunctionInfo(
                        name=node.name,
                        language='python',
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        params=params,
                        return_type=return_type,
                        docstring=docstring,
                        complexity=complexity,
                        is_async=isinstance(node, ast.AsyncFunctionDef),
                        visibility='private' if node.name.startswith('_') else 'public',
                        is_static='staticmethod' in decorators,
                        decorators=decorators,
                        annotations=[]
                    )
                    functions.append(func_info)
        except Exception as e:
            print(f"⚠️ WARNING: Skipping {file_path} due to parse error at line {e}")
            print(f"   This file will be excluded from documentation.")
            # Return empty list to skip this file
            return []
        
        return functions
    
    @staticmethod
    def _calculate_complexity(node) -> int:
        """Calculate cyclomatic complexity"""
        import ast
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    @staticmethod
    def parse_classes(content: str, file_path: str) -> List[MultiLangClassInfo]:
        """Extract classes from Python code"""
        import ast
        classes = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract methods
                    methods = []
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            method_funcs = PythonParser.parse_functions(ast.unparse(item), file_path)
                            methods.extend(method_funcs)
                    
                    # Extract fields
                    fields = []
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id
                            field_type = ast.unparse(item.annotation) if item.annotation else None
                            fields.append((field_name, field_type))
                    
                    # Extract base classes
                    extends = [ast.unparse(base) for base in node.bases]
                    
                    class_info = MultiLangClassInfo(
                        name=node.name,
                        language='python',
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        methods=methods,
                        fields=fields,
                        extends=extends,
                        implements=[],
                        docstring=ast.get_docstring(node),
                        visibility='private' if node.name.startswith('_') else 'public',
                        is_abstract=any(d.id == 'abstractmethod' if isinstance(d, ast.Name) else False for d in node.decorator_list),
                        annotations=[ast.unparse(d) for d in node.decorator_list]
                    )
                    classes.append(class_info)
        except Exception as e:
            print(f"⚠️ WARNING: Skipping classes in {file_path} due to parse error")
            # Return empty list to skip this file's classes
            return []
        
        return classes

class JavaScriptParser:
    """Parse JavaScript/TypeScript code"""
    
    @staticmethod
    def parse_functions(content: str, file_path: str) -> List[MultiLangFunctionInfo]:
        """Extract functions from JavaScript/TypeScript code"""
        functions = []
        
        # Regex patterns for function declarations
        patterns = [
            r'function\s+(\w+)\s*\((.*?)\)\s*\{',  # function name(params)
            r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>', # const name = (params) =>
            r'(\w+)\s*:\s*function\s*\((.*?)\)\s*\{',  # name: function(params)
            r'async\s+function\s+(\w+)\s*\((.*?)\)\s*\{',  # async function
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                params_str = match.group(2)
                
                # Parse parameters
                params = []
                if params_str:
                    for param in params_str.split(','):
                        param = param.strip()
                        if ':' in param:  # TypeScript type annotation
                            param_name, param_type = param.split(':', 1)
                            params.append((param_name.strip(), param_type.strip()))
                        else:
                            params.append((param, None))
                
                # Find line number
                line_start = content[:match.start()].count('\n') + 1
                
                func_info = MultiLangFunctionInfo(
                    name=name,
                    language='javascript',
                    file_path=file_path,
                    line_start=line_start,
                    line_end=line_start + 10,  # Approximate
                    params=params,
                    return_type=None,
                    docstring=JavaScriptParser._extract_jsdoc(content, match.start()),
                    complexity=5,  # Default
                    is_async='async' in match.group(0),
                    visibility='public',
                    is_static=False,
                    decorators=[],
                    annotations=[]
                )
                functions.append(func_info)
        
        return functions
    
    @staticmethod
    def _extract_jsdoc(content: str, pos: int) -> Optional[str]:
        """Extract JSDoc comment before function"""
        lines = content[:pos].split('\n')
        doc_lines = []
        
        for line in reversed(lines[-10:]):  # Look back 10 lines
            line = line.strip()
            if line.startswith('*/'):
                continue
            elif line.startswith('*'):
                doc_lines.insert(0, line[1:].strip())
            elif line.startswith('/**'):
                doc_lines.insert(0, line[3:].strip())
                break
            elif not line or line.startswith('//'):
                continue
            else:
                break
        
        return '\n'.join(doc_lines) if doc_lines else None
    
    @staticmethod
    def parse_classes(content: str, file_path: str) -> List[MultiLangClassInfo]:
        """Extract classes from JavaScript/TypeScript code"""
        classes = []
        
        # Match class declarations
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{'
        
        for match in re.finditer(class_pattern, content):
            name = match.group(1)
            extends = [match.group(2)] if match.group(2) else []
            line_start = content[:match.start()].count('\n') + 1
            
            class_info = MultiLangClassInfo(
                name=name,
                language='javascript',
                file_path=file_path,
                line_start=line_start,
                line_end=line_start + 50,  # Approximate
                methods=[],
                fields=[],
                extends=extends,
                implements=[],
                docstring=JavaScriptParser._extract_jsdoc(content, match.start()),
                visibility='public',
                is_abstract=False,
                annotations=[]
            )
            classes.append(class_info)
        
        return classes

class BashParser:
    """Parse Bash/Shell scripts"""
    
    @staticmethod
    def parse_functions(content: str, file_path: str) -> List[MultiLangFunctionInfo]:
        """Extract functions from Bash scripts"""
        functions = []
        
        # Regex patterns for bash function declarations
        patterns = [
            r'^\s*function\s+(\w+)\s*\(\)\s*\{',  # function name() {
            r'^\s*(\w+)\s*\(\)\s*\{',  # name() {
            r'^\s*function\s+(\w+)\s*\{',  # function name {
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                name = match.group(1)
                line_start = content[:match.start()].count('\n') + 1
                
                # Extract docstring (comments above function)
                docstring = BashParser._extract_bash_comment(content, match.start())
                
                # Estimate complexity by counting conditions
                func_end = BashParser._find_function_end(content, match.end())
                func_body = content[match.end():func_end]
                complexity = func_body.count('if ') + func_body.count('for ') + func_body.count('while ') + func_body.count('case ')
                
                func_info = MultiLangFunctionInfo(
                    name=name,
                    language='bash',
                    file_path=file_path,
                    line_start=line_start,
                    line_end=line_start + func_body.count('\n'),
                    params=[],  # Bash doesn't have formal parameters
                    return_type=None,
                    docstring=docstring,
                    complexity=max(1, complexity),
                    is_async=False,
                    visibility='public',
                    is_static=False,
                    decorators=[],
                    annotations=[]
                )
                functions.append(func_info)
        
        return functions
    
    @staticmethod
    def _extract_bash_comment(content: str, pos: int) -> Optional[str]:
        """Extract comment block before function"""
        lines = content[:pos].split('\n')
        doc_lines = []
        
        for line in reversed(lines[-10:]):
            line = line.strip()
            if line.startswith('#'):
                doc_lines.insert(0, line.lstrip('#').strip())
            elif line:
                break
        
        return '\n'.join(doc_lines) if doc_lines else None
    
    @staticmethod
    def _find_function_end(content: str, start: int) -> int:
        """Find the end of a bash function by matching braces"""
        brace_count = 1
        pos = start
        
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return pos
    
    @staticmethod
    def parse_classes(content: str, file_path: str) -> List[MultiLangClassInfo]:
        """Bash doesn't have classes, return empty list"""
        return []

class MultiLanguageAnalyzer:
    """Unified analyzer for multiple programming languages"""
    
    def __init__(self):
        self.parsers = {
            'python': PythonParser,
            'javascript': JavaScriptParser,
            'typescript': JavaScriptParser,
            'bash': BashParser,
        }
    
    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a single file"""
        language = LanguageDetector.detect(file_path, content)
        
        result = {
            'language': language,
            'file_path': file_path,
            'functions': [],
            'classes': [],
            'imports': [],
            'lines_of_code': len([l for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]),
            'context_content': None  # For MD/TXT files
        }
        
        # Handle context files (markdown/text)
        if language in ['markdown', 'text']:
            result['context_content'] = content
            result['lines_of_code'] = 0  # Don't count as code
        elif language in self.parsers:
            parser = self.parsers[language]
            result['functions'] = parser.parse_functions(content, file_path)
            result['classes'] = parser.parse_classes(content, file_path)
        
        return result
    
    def analyze_repository(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Analyze entire repository with mixed languages"""
        results = {
            'files': {},
            'languages': defaultdict(int),
            'total_functions': 0,
            'total_classes': 0,
            'total_lines': 0,
            'language_breakdown': {},
            'context_files': []  # Store MD/TXT files for RAG
        }
        
        for file_path, content in file_contents.items():
            file_result = self.analyze_file(file_path, content)
            results['files'][file_path] = file_result
            
            # Update statistics
            lang = file_result['language']
            results['languages'][lang] += 1
            results['total_functions'] += len(file_result['functions'])
            results['total_classes'] += len(file_result['classes'])
            results['total_lines'] += file_result['lines_of_code']
            
            # Store context files for RAG
            if lang in ['markdown', 'text'] and file_result.get('context_content'):
                results['context_files'].append({
                    'path': file_path,
                    'type': lang,
                    'content': file_result['context_content']
                })
        
        # Calculate language breakdown
        total_files = sum(results['languages'].values())
        for lang, count in results['languages'].items():
            results['language_breakdown'][lang] = {
                'files': count,
                'percentage': (count / total_files * 100) if total_files > 0 else 0
            }
        
        return results
