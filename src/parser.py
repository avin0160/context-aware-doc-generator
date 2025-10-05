"""
Multi-language code parser using tree-sitter.
Supports Python, JavaScript, Java, Go, C++, and more.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import tree_sitter
from tree_sitter import Language, Parser
import logging

logger = logging.getLogger(__name__)


class MultiLanguageParser:
    """Universal code parser supporting multiple programming languages."""
    
    SUPPORTED_LANGUAGES = {
        'python': {
            'extensions': ['.py'],
            'language': 'python',
            'grammar_repo': 'tree-sitter-python'
        },
        'javascript': {
            'extensions': ['.js', '.jsx', '.ts', '.tsx'],
            'language': 'javascript', 
            'grammar_repo': 'tree-sitter-javascript'
        },
        'java': {
            'extensions': ['.java'],
            'language': 'java',
            'grammar_repo': 'tree-sitter-java'
        },
        'go': {
            'extensions': ['.go'],
            'language': 'go',
            'grammar_repo': 'tree-sitter-go'
        },
        'cpp': {
            'extensions': ['.cpp', '.cc', '.cxx', '.c', '.h', '.hpp'],
            'language': 'cpp',
            'grammar_repo': 'tree-sitter-cpp'
        }
    }
    
    def __init__(self):
        self.parsers: Dict[str, Parser] = {}
        self.languages: Dict[str, Language] = {}
        self._setup_parsers()
    
    def _setup_parsers(self):
        """Initialize parsers for all supported languages."""
        try:
            from tree_sitter import Language
            
            # Try to import language bindings
            for lang_name, config in self.SUPPORTED_LANGUAGES.items():
                try:
                    if lang_name == 'python':
                        import tree_sitter_python as tsp
                        language = Language(tsp.language())
                    elif lang_name == 'javascript':
                        import tree_sitter_javascript as tsjs
                        language = Language(tsjs.language())
                    elif lang_name == 'java':
                        import tree_sitter_java as tsj
                        language = Language(tsj.language())
                    elif lang_name == 'go':
                        import tree_sitter_go as tsg
                        language = Language(tsg.language())
                    elif lang_name == 'cpp':
                        import tree_sitter_cpp as tscpp
                        language = Language(tscpp.language())
                    
                    parser = Parser()
                    parser.set_language(language)
                    
                    self.languages[lang_name] = language
                    self.parsers[lang_name] = parser
                    logger.info(f"Initialized parser for {lang_name}")
                    
                except ImportError as e:
                    logger.warning(f"Could not import {lang_name} parser: {e}")
                    
        except Exception as e:
            logger.error(f"Error setting up parsers: {e}")
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        file_ext = Path(file_path).suffix.lower()
        
        for lang_name, config in self.SUPPORTED_LANGUAGES.items():
            if file_ext in config['extensions']:
                return lang_name
        
        return None
    
    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a single file and extract structure."""
        try:
            language = self.detect_language(file_path)
            if not language or language not in self.parsers:
                logger.warning(f"Unsupported language for file: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            parser = self.parsers[language]
            tree = parser.parse(bytes(content, 'utf8'))
            
            return {
                'file_path': file_path,
                'language': language,
                'content': content,
                'tree': tree,
                'functions': self._extract_functions(tree, content, language),
                'classes': self._extract_classes(tree, content, language),
                'imports': self._extract_imports(tree, content, language),
                'comments': self._extract_comments(tree, content, language)
            }
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return None
    
    def _extract_functions(self, tree, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract function definitions from the syntax tree."""
        functions = []
        
        query_patterns = {
            'python': '(function_def name: (identifier) @name) @function',
            'javascript': '(function_declaration name: (identifier) @name) @function',
            'java': '(method_declaration name: (identifier) @name) @function',
            'go': '(function_declaration name: (identifier) @name) @function',
            'cpp': '(function_definition declarator: (function_declarator declarator: (identifier) @name)) @function'
        }
        
        if language not in query_patterns:
            return functions
        
        try:
            query = self.languages[language].query(query_patterns[language])
            captures = query.captures(tree.root_node)
            
            for node, capture_name in captures:
                if capture_name == 'function':
                    func_info = self._extract_node_info(node, content)
                    if func_info:
                        functions.append(func_info)
                        
        except Exception as e:
            logger.error(f"Error extracting functions for {language}: {e}")
        
        return functions
    
    def _extract_classes(self, tree, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions from the syntax tree."""
        classes = []
        
        query_patterns = {
            'python': '(class_definition name: (identifier) @name) @class',
            'javascript': '(class_declaration name: (identifier) @name) @class',
            'java': '(class_declaration name: (identifier) @name) @class',
            'go': '(type_declaration (type_spec name: (type_identifier) @name)) @class',
            'cpp': '(class_specifier name: (type_identifier) @name) @class'
        }
        
        if language not in query_patterns:
            return classes
        
        try:
            query = self.languages[language].query(query_patterns[language])
            captures = query.captures(tree.root_node)
            
            for node, capture_name in captures:
                if capture_name == 'class':
                    class_info = self._extract_node_info(node, content)
                    if class_info:
                        classes.append(class_info)
                        
        except Exception as e:
            logger.error(f"Error extracting classes for {language}: {e}")
        
        return classes
    
    def _extract_imports(self, tree, content: str, language: str) -> List[str]:
        """Extract import statements."""
        imports = []
        
        query_patterns = {
            'python': '(import_statement) @import',
            'javascript': '(import_statement) @import',
            'java': '(import_declaration) @import',
            'go': '(import_declaration) @import',
            'cpp': '(preproc_include) @import'
        }
        
        if language not in query_patterns:
            return imports
        
        try:
            query = self.languages[language].query(query_patterns[language])
            captures = query.captures(tree.root_node)
            
            for node, capture_name in captures:
                if capture_name == 'import':
                    import_text = content[node.start_byte:node.end_byte]
                    imports.append(import_text.strip())
                    
        except Exception as e:
            logger.error(f"Error extracting imports for {language}: {e}")
        
        return imports
    
    def _extract_comments(self, tree, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract comments from the code."""
        comments = []
        
        try:
            def traverse_tree(node):
                if node.type == 'comment':
                    comment_text = content[node.start_byte:node.end_byte]
                    comments.append({
                        'text': comment_text,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1]
                    })
                
                for child in node.children:
                    traverse_tree(child)
            
            traverse_tree(tree.root_node)
            
        except Exception as e:
            logger.error(f"Error extracting comments for {language}: {e}")
        
        return comments
    
    def _extract_node_info(self, node, content: str) -> Dict[str, Any]:
        """Extract detailed information from a syntax tree node."""
        try:
            return {
                'name': self._get_node_name(node, content),
                'start_line': node.start_point[0] + 1,
                'end_line': node.end_point[0] + 1,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'text': content[node.start_byte:node.end_byte],
                'type': node.type
            }
        except Exception as e:
            logger.error(f"Error extracting node info: {e}")
            return {}
    
    def _get_node_name(self, node, content: str) -> str:
        """Get the name of a function or class node."""
        try:
            # Look for identifier nodes in children
            for child in node.children:
                if child.type == 'identifier':
                    return content[child.start_byte:child.end_byte]
                # Recursively search in children
                name = self._get_node_name(child, content)
                if name:
                    return name
            return "unknown"
        except:
            return "unknown"
    
    def parse_codebase(self, directory_path: str) -> Dict[str, Any]:
        """Parse an entire codebase directory."""
        results = {
            'files': {},
            'summary': {
                'total_files': 0,
                'languages': set(),
                'total_functions': 0,
                'total_classes': 0
            }
        }
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.vscode', 'build', 'dist'}]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    parsed = self.parse_file(file_path)
                    
                    if parsed:
                        results['files'][file_path] = parsed
                        results['summary']['total_files'] += 1
                        results['summary']['languages'].add(parsed['language'])
                        results['summary']['total_functions'] += len(parsed['functions'])
                        results['summary']['total_classes'] += len(parsed['classes'])
            
            results['summary']['languages'] = list(results['summary']['languages'])
            
        except Exception as e:
            logger.error(f"Error parsing codebase: {e}")
        
        return results


# Factory function for easy instantiation
def create_parser() -> MultiLanguageParser:
    """Create and return a configured multi-language parser."""
    return MultiLanguageParser()