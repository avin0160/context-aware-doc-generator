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
            from tree_sitter import Language, Parser
            
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
                    
                    parser = Parser(language)
                    
                    self.languages[lang_name] = language
                    self.parsers[lang_name] = parser
                    logger.info(f"Initialized parser for {lang_name}")
                    
                except ImportError as e:
                    logger.warning(f"Could not import {lang_name} parser: {e}")
                except Exception as e:
                    logger.warning(f"Could not setup {lang_name} parser: {e}")
                    
        except Exception as e:
            logger.error(f"Error setting up parsers: {e}")
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        file_ext = Path(file_path).suffix.lower()
        
        for lang_name, config in self.SUPPORTED_LANGUAGES.items():
            if file_ext in config['extensions']:
                return lang_name
        
        return None
    
    def parse_code(self, code: str, language: str) -> Optional[Dict[str, Any]]:
        """Parse code string directly."""
        try:
            if language not in self.parsers:
                logger.warning(f"Unsupported language: {language}")
                return None
            
            parser = self.parsers[language]
            tree = parser.parse(bytes(code, 'utf8'))
            
            return {
                'language': language,
                'content': code,
                'tree': tree,
                'functions': self._extract_functions(tree, code, language),
                'classes': self._extract_classes(tree, code, language),
                'imports': self._extract_imports(tree, code, language),
                'comments': self._extract_comments(tree, code, language)
            }
            
        except Exception as e:
            logger.error(f"Error parsing code: {e}")
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
        
        # Simple node type matching for different languages
        function_types = {
            'python': ['function_def'],
            'javascript': ['function_declaration', 'function_expression'],
            'java': ['method_declaration'],
            'go': ['function_declaration'],
            'cpp': ['function_definition']
        }
        
        if language not in function_types:
            return functions
        
        try:
            # Walk the tree and find function nodes
            def walk_tree(node):
                if node.type in function_types[language]:
                    func_info = self._extract_node_info(node, content)
                    if func_info:
                        functions.append(func_info)
                
                for child in node.children:
                    walk_tree(child)
            
            walk_tree(tree.root_node)
                        
        except Exception as e:
            logger.error(f"Error extracting functions for {language}: {e}")
        
        return functions
    
    def _extract_classes(self, tree, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions from the syntax tree."""
        classes = []
        
        # Simple node type matching for different languages
        class_types = {
            'python': ['class_definition'],
            'javascript': ['class_declaration'],
            'java': ['class_declaration'],
            'go': ['type_declaration'],
            'cpp': ['class_specifier']
        }
        
        if language not in class_types:
            return classes
        
        try:
            # Walk the tree and find class nodes
            def walk_tree(node):
                if node.type in class_types[language]:
                    class_info = self._extract_node_info(node, content)
                    if class_info:
                        classes.append(class_info)
                
                for child in node.children:
                    walk_tree(child)
            
            walk_tree(tree.root_node)
                        
        except Exception as e:
            logger.error(f"Error extracting classes for {language}: {e}")
        
        return classes
    
    def _extract_imports(self, tree, content: str, language: str) -> List[str]:
        """Extract import statements."""
        imports = []
        
        # Simple node type matching for different languages
        import_types = {
            'python': ['import_statement', 'import_from_statement'],
            'javascript': ['import_statement'],
            'java': ['import_declaration'],
            'go': ['import_declaration'],
            'cpp': ['preproc_include']
        }
        
        if language not in import_types:
            return imports
        
        try:
            # Walk the tree and find import nodes
            def walk_tree(node):
                if node.type in import_types[language]:
                    import_text = content[node.start_byte:node.end_byte]
                    imports.append(import_text.strip())
                
                for child in node.children:
                    walk_tree(child)
            
            walk_tree(tree.root_node)
                    
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
            # For Python: function_def and class_definition have direct identifier children
            # For JavaScript: function_declaration and class_declaration have direct identifier children
            
            # Look for direct identifier children first
            for child in node.children:
                if child.type == 'identifier':
                    name = content[child.start_byte:child.end_byte].strip()
                    if name and name != 'unknown':
                        return name
            
            # Alternative: look for specific patterns
            if node.type in ['function_def', 'function_declaration']:
                # Try to find the second child (usually the name after 'def' or 'function')
                if len(node.children) > 1 and node.children[1].type == 'identifier':
                    name = content[node.children[1].start_byte:node.children[1].end_byte].strip()
                    if name:
                        return name
            
            elif node.type in ['class_definition', 'class_declaration']:
                # Try to find the second child (usually the name after 'class')
                if len(node.children) > 1 and node.children[1].type == 'identifier':
                    name = content[node.children[1].start_byte:node.children[1].end_byte].strip()
                    if name:
                        return name
            
            # Last resort: extract from node text and try to parse
            node_text = content[node.start_byte:node.end_byte]
            if node.type in ['function_def', 'function_declaration']:
                # Try to extract function name with regex
                import re
                match = re.search(r'(?:def|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)', node_text)
                if match:
                    return match.group(1)
            elif node.type in ['class_definition', 'class_declaration']:
                # Try to extract class name with regex
                import re
                match = re.search(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', node_text)
                if match:
                    return match.group(1)
            
            return "unknown"
        except Exception as e:
            logger.debug(f"Error getting node name: {e}")
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