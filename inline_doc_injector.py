"""
Inline Documentation Injector
Modifies source files to add Google-style docstrings directly
"""

import re
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


class PythonDocInjector:
    """Inject docstrings into Python source code"""
    
    @staticmethod
    def inject_docstrings(content: str, functions: List[Any], classes: List[Any]) -> str:
        """Add docstrings to Python functions and classes"""
        lines = content.split('\n')
        modified_lines = []
        injected_at_lines = set()
        
        # Create map of line numbers to docstrings
        docstring_map = {}
        
        # Process functions
        for func in functions:
            if func.line_start not in injected_at_lines and not func.docstring:
                docstring = PythonDocInjector._generate_function_docstring(func)
                docstring_map[func.line_start] = docstring
        
        # Process classes
        for cls in classes:
            if cls.line_start not in injected_at_lines and not cls.docstring:
                docstring = PythonDocInjector._generate_class_docstring(cls)
                docstring_map[cls.line_start] = docstring
        
        # Inject docstrings
        for i, line in enumerate(lines, 1):
            modified_lines.append(line)
            
            if i in docstring_map:
                indent = len(line) - len(line.lstrip())
                docstring_lines = docstring_map[i].split('\n')
                for doc_line in docstring_lines:
                    modified_lines.append(' ' * (indent + 4) + doc_line)
        
        return '\n'.join(modified_lines)
    
    @staticmethod
    def _generate_function_docstring(func) -> str:
        """Generate Google-style docstring for function"""
        doc_lines = [
            '"""' + func.name.replace('_', ' ').title() + ' function.',
            '',
            'TODO: Add detailed description.',
        ]
        
        if func.params:
            doc_lines.append('')
            doc_lines.append('Args:')
            for param, param_type in func.params:
                type_hint = f' ({param_type})' if param_type else ''
                doc_lines.append(f'    {param}{type_hint}: TODO: Describe {param}.')
        
        if func.return_type or 'return' in str(func):
            doc_lines.append('')
            doc_lines.append('Returns:')
            return_type = func.return_type or 'TODO: Specify return type'
            doc_lines.append(f'    {return_type}: TODO: Describe return value.')
        
        doc_lines.append('"""')
        return '\n'.join(doc_lines)
    
    @staticmethod
    def _generate_class_docstring(cls) -> str:
        """Generate Google-style docstring for class"""
        doc_lines = [
            '"""' + cls.name + ' class.',
            '',
            'TODO: Add detailed description of class purpose.',
        ]
        
        if cls.fields:
            doc_lines.append('')
            doc_lines.append('Attributes:')
            for field, field_type in cls.fields:
                type_hint = f' ({field_type})' if field_type else ''
                doc_lines.append(f'    {field}{type_hint}: TODO: Describe {field}.')
        
        doc_lines.append('"""')
        return '\n'.join(doc_lines)


class BashDocInjector:
    """Inject comments into Bash scripts"""
    
    @staticmethod
    def inject_comments(content: str, functions: List[Any]) -> str:
        """Add comment blocks to Bash functions"""
        lines = content.split('\n')
        modified_lines = []
        injected_at_lines = set()
        
        # Create map of line numbers to comments
        comment_map = {}
        
        for func in functions:
            if func.line_start not in injected_at_lines and not func.docstring:
                comments = BashDocInjector._generate_function_comments(func)
                comment_map[func.line_start] = comments
        
        # Inject comments
        for i, line in enumerate(lines, 1):
            if i in comment_map:
                comment_lines = comment_map[i].split('\n')
                for comment_line in comment_lines:
                    modified_lines.append(comment_line)
            
            modified_lines.append(line)
        
        return '\n'.join(modified_lines)
    
    @staticmethod
    def _generate_function_comments(func) -> str:
        """Generate comment block for Bash function"""
        comments = [
            f'# {func.name} - TODO: Brief description',
            '#',
            '# Description:',
            f'#   TODO: Explain what {func.name} does',
            '#',
        ]
        
        if func.complexity > 1:
            comments.append('# Complexity: Medium' if func.complexity < 5 else '# Complexity: High')
            comments.append('#')
        
        comments.append('# Arguments:')
        comments.append('#   $1: TODO: Describe first argument')
        comments.append('#   $@: All arguments passed to function')
        comments.append('#')
        comments.append('# Returns:')
        comments.append('#   0 on success, non-zero on failure')
        
        return '\n'.join(comments)


class JavaScriptDocInjector:
    """Inject JSDoc comments into JavaScript/TypeScript"""
    
    @staticmethod
    def inject_jsdoc(content: str, functions: List[Any], classes: List[Any]) -> str:
        """Add JSDoc comments to JavaScript functions and classes"""
        lines = content.split('\n')
        modified_lines = []
        injected_at_lines = set()
        
        # Create map of line numbers to JSDoc
        jsdoc_map = {}
        
        for func in functions:
            if func.line_start not in injected_at_lines and not func.docstring:
                jsdoc = JavaScriptDocInjector._generate_function_jsdoc(func)
                jsdoc_map[func.line_start] = jsdoc
        
        for cls in classes:
            if cls.line_start not in injected_at_lines and not cls.docstring:
                jsdoc = JavaScriptDocInjector._generate_class_jsdoc(cls)
                jsdoc_map[cls.line_start] = jsdoc
        
        # Inject JSDoc
        for i, line in enumerate(lines, 1):
            if i in jsdoc_map:
                indent = len(line) - len(line.lstrip())
                jsdoc_lines = jsdoc_map[i].split('\n')
                for jsdoc_line in jsdoc_lines:
                    modified_lines.append(' ' * indent + jsdoc_line)
            
            modified_lines.append(line)
        
        return '\n'.join(modified_lines)
    
    @staticmethod
    def _generate_function_jsdoc(func) -> str:
        """Generate JSDoc comment for function"""
        jsdoc_lines = [
            '/**',
            f' * {func.name} - TODO: Brief description',
            ' *',
        ]
        
        if func.params:
            for param, param_type in func.params:
                type_hint = param_type or 'any'
                jsdoc_lines.append(f' * @param {{{type_hint}}} {param} - TODO: Describe {param}')
        
        if func.return_type:
            jsdoc_lines.append(f' * @returns {{{func.return_type}}} TODO: Describe return value')
        else:
            jsdoc_lines.append(' * @returns {void}')
        
        if func.is_async:
            jsdoc_lines.append(' * @async')
        
        jsdoc_lines.append(' */')
        return '\n'.join(jsdoc_lines)
    
    @staticmethod
    def _generate_class_jsdoc(cls) -> str:
        """Generate JSDoc comment for class"""
        jsdoc_lines = [
            '/**',
            f' * {cls.name} class - TODO: Brief description',
            ' *',
        ]
        
        if cls.extends:
            jsdoc_lines.append(f' * @extends {cls.extends[0]}')
        
        if cls.fields:
            for field, field_type in cls.fields[:5]:
                type_hint = field_type or 'any'
                jsdoc_lines.append(f' * @property {{{type_hint}}} {field} - TODO: Describe {field}')
        
        jsdoc_lines.append(' */')
        return '\n'.join(jsdoc_lines)


class InlineDocInjector:
    """Main injector that handles all languages"""
    
    def __init__(self):
        self.injectors = {
            'python': PythonDocInjector(),
            'bash': BashDocInjector(),
            'javascript': JavaScriptDocInjector(),
            'typescript': JavaScriptDocInjector(),
        }
    
    def inject_documentation(self, file_path: str, content: str, file_analysis: Dict[str, Any]) -> Optional[str]:
        """Inject inline documentation into source file"""
        language = file_analysis.get('language', 'unknown')
        
        if language not in self.injectors:
            return None  # Unsupported language
        
        functions = file_analysis.get('functions', [])
        classes = file_analysis.get('classes', [])
        
        # Don't modify if already has good documentation
        if language == 'python':
            documented_funcs = sum(1 for f in functions if f.docstring)
            if functions and documented_funcs / len(functions) > 0.7:
                return None  # Already well documented
        
        # Inject based on language
        if language == 'python':
            return PythonDocInjector.inject_docstrings(content, functions, classes)
        elif language == 'bash':
            return BashDocInjector.inject_comments(content, functions)
        elif language in ['javascript', 'typescript']:
            return JavaScriptDocInjector.inject_jsdoc(content, functions, classes)
        
        return None
    
    def process_repository(self, file_contents: Dict[str, str], analysis: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """Process entire repository and save modified files"""
        modified_files = {}
        
        for file_path, content in file_contents.items():
            if file_path not in analysis['file_analysis']:
                continue
            
            file_analysis = analysis['file_analysis'][file_path]
            modified_content = self.inject_documentation(file_path, content, file_analysis)
            
            if modified_content:
                # Save to output directory
                output_path = os.path.join(output_dir, file_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                modified_files[file_path] = output_path
        
        return modified_files
