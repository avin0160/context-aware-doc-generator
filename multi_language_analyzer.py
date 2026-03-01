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
        except SyntaxError as e:
            # Syntax error in the actual Python file (not our code)
            print(f"⚠️  WARNING: {file_path} has syntax errors (line {e.lineno if hasattr(e, 'lineno') else 'unknown'})")
            print(f"   Reason: The Python file itself contains invalid syntax.")
            print(f"   This happens when:")
            print(f"     - File is auto-generated or corrupted")
            print(f"     - File contains Python 2 syntax in Python 3")
            print(f"     - File has encoding issues")
            print(f"   Solution: Fix syntax errors in the source file, or exclude it from documentation.")
            # Return empty to skip this broken file
            return []
        except Exception as e:
            # Other errors - log but continue
            print(f"⚠️  WARNING: Could not parse {file_path}: {type(e).__name__}: {e}")
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
        except SyntaxError as e:
            # Syntax error in the actual Python file
            print(f"⚠️  WARNING: {file_path} has syntax errors (cannot parse classes)")
            return []
        except Exception as e:
            print(f"⚠️  WARNING: Could not parse classes in {file_path}: {type(e).__name__}")
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

class JavaParser:
    """Parse Java code"""
    
    @staticmethod
    def parse_functions(content: str, file_path: str) -> List[MultiLangFunctionInfo]:
        """Extract methods from Java code"""
        functions = []
        
        # Regex for Java method declarations
        # Matches: public/private/protected + static/abstract + return_type + name(params)
        method_pattern = r'''
            ^\s*                                           # Start, optional whitespace
            (?:@\w+(?:\([^)]*\))?\s*)*                     # Annotations like @Override, @Test
            (public|private|protected)?\s*                 # Visibility
            (static|abstract|final|synchronized|native)*\s*  # Modifiers
            (\w+(?:<[^>]+>)?(?:\[\])?)\s+                  # Return type (including generics, arrays)
            (\w+)\s*                                       # Method name
            \(([^)]*)\)                                    # Parameters
            (?:\s*throws\s+[\w,\s]+)?                      # Optional throws clause
            \s*\{                                          # Opening brace
        '''
        
        for match in re.finditer(method_pattern, content, re.MULTILINE | re.VERBOSE):
            visibility = match.group(1) or 'package'
            modifiers = match.group(2) or ''
            return_type = match.group(3)
            name = match.group(4)
            params_str = match.group(5)
            
            # Skip constructors (return type same as class name pattern)
            if return_type == name:
                continue
            
            # Parse parameters
            params = []
            if params_str.strip():
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        parts = param.split()
                        if len(parts) >= 2:
                            param_type = ' '.join(parts[:-1])
                            param_name = parts[-1]
                            params.append((param_name, param_type))
            
            line_start = content[:match.start()].count('\n') + 1
            
            # Extract Javadoc
            docstring = JavaParser._extract_javadoc(content, match.start())
            
            # Calculate complexity
            func_end = JavaParser._find_method_end(content, match.end())
            func_body = content[match.end():func_end]
            complexity = 1 + func_body.count('if ') + func_body.count('for ') + func_body.count('while ') + func_body.count('switch ') + func_body.count('catch ')
            
            func_info = MultiLangFunctionInfo(
                name=name,
                language='java',
                file_path=file_path,
                line_start=line_start,
                line_end=line_start + func_body.count('\n'),
                params=params,
                return_type=return_type,
                docstring=docstring,
                complexity=complexity,
                is_async=False,
                visibility=visibility,
                is_static='static' in modifiers,
                decorators=[],
                annotations=[]
            )
            functions.append(func_info)
        
        return functions
    
    @staticmethod
    def _extract_javadoc(content: str, pos: int) -> Optional[str]:
        """Extract Javadoc comment before method"""
        lines = content[:pos].split('\n')
        doc_lines = []
        in_javadoc = False
        
        for line in reversed(lines[-20:]):
            line = line.strip()
            if line.endswith('*/'):
                in_javadoc = True
                continue
            elif in_javadoc:
                if line.startswith('/**'):
                    doc_lines.insert(0, line[3:].strip())
                    break
                elif line.startswith('*'):
                    doc_lines.insert(0, line[1:].strip())
            elif line and not line.startswith('@') and not line.startswith('//'):
                break
        
        return '\n'.join(doc_lines) if doc_lines else None
    
    @staticmethod
    def _find_method_end(content: str, start: int) -> int:
        """Find the end of a Java method by matching braces"""
        brace_count = 1
        pos = start
        in_string = False
        string_char = None
        
        while pos < len(content) and brace_count > 0:
            char = content[pos]
            if char in '"\'':
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and content[pos-1] != '\\':
                    in_string = False
            elif not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            pos += 1
        
        return pos
    
    @staticmethod
    def parse_classes(content: str, file_path: str) -> List[MultiLangClassInfo]:
        """Extract classes from Java code"""
        classes = []
        
        # Match class declarations
        class_pattern = r'''
            ^\s*
            (?:@\w+(?:\([^)]*\))?\s*)*                     # Annotations
            (public|private|protected)?\s*                 # Visibility
            (abstract|final|static)*\s*                    # Modifiers
            (class|interface|enum)\s+                      # Type
            (\w+)                                          # Name
            (?:\s*<[^>]+>)?                                # Generic parameters
            (?:\s+extends\s+([\w.]+(?:<[^>]+>)?))?         # Extends
            (?:\s+implements\s+([\w.,\s<>]+))?             # Implements
            \s*\{
        '''
        
        for match in re.finditer(class_pattern, content, re.MULTILINE | re.VERBOSE):
            visibility = match.group(1) or 'package'
            modifiers = match.group(2) or ''
            class_type = match.group(3)
            name = match.group(4)
            extends = [match.group(5)] if match.group(5) else []
            implements = [i.strip() for i in match.group(6).split(',')] if match.group(6) else []
            
            line_start = content[:match.start()].count('\n') + 1
            
            class_info = MultiLangClassInfo(
                name=name,
                language='java',
                file_path=file_path,
                line_start=line_start,
                line_end=line_start + 100,  # Approximate
                methods=[],
                fields=[],
                extends=extends,
                implements=implements,
                docstring=JavaParser._extract_javadoc(content, match.start()),
                visibility=visibility,
                is_abstract='abstract' in modifiers or class_type == 'interface',
                annotations=[]
            )
            classes.append(class_info)
        
        return classes


class CppParser:
    """Parse C/C++ code"""
    
    @staticmethod
    def parse_functions(content: str, file_path: str) -> List[MultiLangFunctionInfo]:
        """Extract functions from C/C++ code"""
        functions = []
        
        # Regex for C/C++ function declarations
        # Handles: return_type name(params) { or return_type Class::name(params) {
        func_pattern = r'''
            ^\s*                                           # Start
            (?:static|inline|virtual|explicit|extern|const)*\s*  # Optional modifiers
            ([\w:*&<>,\s]+?)                               # Return type (complex)
            \s+
            ((?:\w+::)?[\w~]+)                             # Function name (may include class::)
            \s*
            \(([^)]*)\)                                    # Parameters
            \s*
            (?:const)?                                     # Optional const qualifier
            (?:\s*override)?                               # Optional override
            (?:\s*noexcept(?:\([^)]*\))?)?                 # Optional noexcept
            \s*\{                                          # Opening brace
        '''
        
        for match in re.finditer(func_pattern, content, re.MULTILINE | re.VERBOSE):
            return_type = match.group(1).strip()
            full_name = match.group(2)
            params_str = match.group(3)
            
            # Extract just the function name (strip class:: prefix)
            if '::' in full_name:
                name = full_name.split('::')[-1]
            else:
                name = full_name
            
            # Skip if looks like control structure
            if name.lower() in ['if', 'for', 'while', 'switch', 'catch']:
                continue
            
            # Parse parameters
            params = []
            if params_str.strip():
                # Split by comma but respect angle brackets for templates
                param_parts = CppParser._split_params(params_str)
                for param in param_parts:
                    param = param.strip()
                    if param and param != 'void':
                        # Get the last word as param name
                        parts = param.replace('*', ' ').replace('&', ' ').split()
                        if len(parts) >= 2:
                            param_name = parts[-1]
                            param_type = ' '.join(parts[:-1])
                            params.append((param_name, param_type))
                        elif len(parts) == 1:
                            params.append((parts[0], None))
            
            line_start = content[:match.start()].count('\n') + 1
            
            # Extract documentation comment
            docstring = CppParser._extract_comment(content, match.start())
            
            # Calculate complexity
            func_end = CppParser._find_function_end(content, match.end())
            func_body = content[match.end():func_end]
            complexity = 1 + func_body.count('if ') + func_body.count('if(') + func_body.count('for ') + func_body.count('for(') + func_body.count('while ') + func_body.count('while(') + func_body.count('switch ') + func_body.count('switch(')
            
            func_info = MultiLangFunctionInfo(
                name=name,
                language='cpp' if '.cpp' in file_path or '.hpp' in file_path or '.cc' in file_path else 'c',
                file_path=file_path,
                line_start=line_start,
                line_end=line_start + func_body.count('\n'),
                params=params,
                return_type=return_type,
                docstring=docstring,
                complexity=complexity,
                is_async=False,
                visibility='public',
                is_static='static' in return_type,
                decorators=[],
                annotations=[]
            )
            functions.append(func_info)
        
        return functions
    
    @staticmethod
    def _split_params(params_str: str) -> List[str]:
        """Split parameters respecting template brackets"""
        params = []
        current = ""
        depth = 0
        
        for char in params_str:
            if char == '<':
                depth += 1
                current += char
            elif char == '>':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                params.append(current)
                current = ""
            else:
                current += char
        
        if current.strip():
            params.append(current)
        
        return params
    
    @staticmethod
    def _extract_comment(content: str, pos: int) -> Optional[str]:
        """Extract C-style comment or Doxygen comment before function"""
        lines = content[:pos].split('\n')
        doc_lines = []
        in_comment = False
        
        for line in reversed(lines[-15:]):
            line = line.strip()
            if line.endswith('*/'):
                in_comment = True
                continue
            elif in_comment:
                if line.startswith('/*') or line.startswith('/**'):
                    doc_lines.insert(0, line[2:].strip() if line.startswith('/*') else line[3:].strip())
                    break
                elif line.startswith('*'):
                    doc_lines.insert(0, line[1:].strip())
            elif line.startswith('//'):
                doc_lines.insert(0, line[2:].strip())
            elif line and not line.startswith('#'):
                break
        
        return '\n'.join(doc_lines) if doc_lines else None
    
    @staticmethod
    def _find_function_end(content: str, start: int) -> int:
        """Find the end of a C/C++ function by matching braces"""
        brace_count = 1
        pos = start
        in_string = False
        string_char = None
        in_comment = False
        
        while pos < len(content) and brace_count > 0:
            char = content[pos]
            
            # Handle comments
            if not in_string and pos + 1 < len(content):
                if content[pos:pos+2] == '//':
                    # Single line comment - skip to end of line
                    while pos < len(content) and content[pos] != '\n':
                        pos += 1
                    continue
                elif content[pos:pos+2] == '/*':
                    in_comment = True
                    pos += 2
                    continue
                elif content[pos:pos+2] == '*/' and in_comment:
                    in_comment = False
                    pos += 2
                    continue
            
            if in_comment:
                pos += 1
                continue
            
            # Handle strings
            if char in '"\'':
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and content[pos-1] != '\\':
                    in_string = False
            elif not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
            pos += 1
        
        return pos
    
    @staticmethod
    def parse_classes(content: str, file_path: str) -> List[MultiLangClassInfo]:
        """Extract classes/structs from C/C++ code"""
        classes = []
        
        # Match class/struct declarations
        class_pattern = r'''
            ^\s*
            (template\s*<[^>]+>\s*)?                       # Optional template
            (class|struct)\s+                              # class or struct
            (?:__declspec\([^)]+\)\s*)?                    # Optional declspec
            (\w+)                                          # Name
            (?:\s*:\s*(public|private|protected)?\s*([\w:,\s]+))?  # Inheritance
            \s*\{
        '''
        
        for match in re.finditer(class_pattern, content, re.MULTILINE | re.VERBOSE):
            class_type = match.group(2)
            name = match.group(3)
            visibility = match.group(4) or ('public' if class_type == 'struct' else 'private')
            extends = [b.strip() for b in match.group(5).split(',')] if match.group(5) else []
            
            line_start = content[:match.start()].count('\n') + 1
            
            class_info = MultiLangClassInfo(
                name=name,
                language='cpp' if '.cpp' in file_path or '.hpp' in file_path else 'c',
                file_path=file_path,
                line_start=line_start,
                line_end=line_start + 100,
                methods=[],
                fields=[],
                extends=extends,
                implements=[],
                docstring=CppParser._extract_comment(content, match.start()),
                visibility=visibility,
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
            'java': JavaParser,
            'c': CppParser,
            'cpp': CppParser,
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
