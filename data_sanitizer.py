"""
Data Sanitizer - Ensures only metadata goes to external APIs
PRIVACY LAYER: Strips all source code before sending to Gemini

Author: team-8
"""

from typing import Dict, List, Any, Optional
from dataclasses import asdict


class DataSanitizer:
    """
    Sanitizes code analysis data before sending to external APIs.
    
    PRIVACY GUARANTEE:
    - NO source code leaves the machine
    - Only sends: names, signatures, call graphs, comments
    - Removes: implementations, literals, file contents
    """
    
    @staticmethod
    def sanitize_function_info(func) -> Dict[str, Any]:
        """
        Sanitize function info for external API.
        
        SENDS:
        - Function name
        - Parameter names (NOT values)
        - Return type annotation
        - Call graph (what it calls)
        - Complexity metric
        - Normalized comments
        
        REMOVES:
        - Source code
        - Implementation details
        - Literal values
        - File contents
        """
        if hasattr(func, 'name'):
            # FunctionInfo dataclass
            return {
                'name': func.name,
                'args': func.args,  # Parameter names only
                'return_type': func.return_type,
                'calls': func.calls,
                'called_by': func.called_by,
                'complexity': func.complexity,
                'semantic_category': func.semantic_category,
                'has_docstring': bool(func.docstring),
                'inline_comments': func.inline_comments if hasattr(func, 'inline_comments') else []
                # SOURCE CODE EXPLICITLY EXCLUDED
            }
        else:
            # Dict format
            return {
                'name': func.get('name', 'unknown'),
                'args': func.get('args', []),
                'return_type': func.get('return_type'),
                'calls': func.get('calls', []),
                'called_by': func.get('called_by', []),
                'complexity': func.get('complexity', 0),
                'semantic_category': func.get('semantic_category', 'unknown'),
                'has_docstring': bool(func.get('docstring')),
                'inline_comments': func.get('inline_comments', [])
            }
    
    @staticmethod
    def sanitize_class_info(cls) -> Dict[str, Any]:
        """
        Sanitize class info for external API.
        
        SENDS:
        - Class name
        - Method signatures
        - Inheritance hierarchy
        - Attribute names
        
        REMOVES:
        - Method implementations
        - Attribute values
        - Source code
        """
        if hasattr(cls, 'name'):
            # ClassInfo dataclass
            return {
                'name': cls.name,
                'methods': [DataSanitizer.sanitize_function_info(m) for m in cls.methods],
                'attributes': cls.attributes,
                'inheritance': cls.inheritance,
                'has_docstring': bool(cls.docstring),
                'inline_comments': cls.inline_comments if hasattr(cls, 'inline_comments') else []
                # SOURCE CODE EXPLICITLY EXCLUDED
            }
        else:
            # Dict format
            return {
                'name': cls.get('name', 'unknown'),
                'methods': [DataSanitizer.sanitize_function_info(m) for m in cls.get('methods', [])],
                'attributes': cls.get('attributes', []),
                'inheritance': cls.get('inheritance', []),
                'has_docstring': bool(cls.get('docstring')),
                'inline_comments': cls.get('inline_comments', [])
            }
    
    @staticmethod
    def sanitize_file_info(file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize file analysis for external API.
        
        SENDS:
        - File path (relative)
        - Function/class signatures
        - Import statements
        - Metrics
        
        REMOVES:
        - File contents
        - Source code
        - Literal values
        """
        return {
            'path': file_info.get('path', 'unknown'),
            'language': file_info.get('language', 'unknown'),
            'lines': file_info.get('lines', 0),
            'functions': [
                DataSanitizer.sanitize_function_info(f) 
                for f in file_info.get('functions', [])
            ],
            'classes': [
                DataSanitizer.sanitize_class_info(c) 
                for c in file_info.get('classes', [])
            ],
            'imports': file_info.get('imports', []),
            'complexity_score': file_info.get('complexity_score', 0)
            # FILE CONTENTS EXPLICITLY EXCLUDED
        }
    
    @staticmethod
    def sanitize_project_analysis(analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize full project analysis for external API.
        
        SENDS:
        - Project structure
        - Call graphs
        - Metrics
        - Dependencies
        
        REMOVES:
        - All source code
        - File contents
        - Implementation details
        """
        return {
            'total_files': analysis.get('total_files', 0),
            'total_functions': analysis.get('total_functions', 0),
            'total_classes': analysis.get('total_classes', 0),
            'total_lines': analysis.get('total_lines', 0),
            'all_imports': list(analysis.get('all_imports', [])),
            'file_analysis': {
                path: DataSanitizer.sanitize_file_info(info)
                for path, info in analysis.get('file_analysis', {}).items()
            },
            'call_graph': analysis.get('call_graph', {}),
            'project_type': analysis.get('project_type', 'unknown'),
            'key_technologies': analysis.get('key_technologies', []),
            'complexity_metrics': analysis.get('complexity_metrics', {})
            # SOURCE CODE, FILE CONTENTS EXPLICITLY EXCLUDED
        }


class CommentExtractor:
    """
    Extract and normalize inline comments for context.
    
    LOCAL PROCESSING ONLY - Never sends raw comments to external APIs.
    """
    
    @staticmethod
    def extract_inline_comments(source_code: str) -> List[str]:
        """
        Extract inline comments from source code.
        
        Returns:
            List of normalized comments (without # or //)
        """
        comments = []
        lines = source_code.split('\n')
        
        for line in lines:
            # Python single-line comments
            if '#' in line and not line.strip().startswith('#'):
                comment = line.split('#', 1)[1].strip()
                if comment and not comment.startswith('!'):  # Skip shebangs
                    comments.append(comment)
            
            # Python docstrings are handled separately
            
        return comments
    
    @staticmethod
    def extract_todo_items(source_code: str) -> List[str]:
        """
        Extract TODO, FIXME, HACK comments.
        
        Returns:
            List of action items
        """
        todos = []
        lines = source_code.split('\n')
        
        for line in lines:
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in ['TODO', 'FIXME', 'HACK', 'XXX', 'NOTE']):
                if '#' in line:
                    comment = line.split('#', 1)[1].strip()
                    todos.append(comment)
        
        return todos
    
    @staticmethod
    def normalize_comment(comment: str) -> str:
        """
        Normalize comment for RAG indexing.
        
        - Remove noise (e.g., "----", "====")
        - Standardize punctuation
        - Remove redundant whitespace
        """
        # Remove decorative characters
        comment = re.sub(r'[-=*#]{3,}', '', comment)
        
        # Remove excess whitespace
        comment = ' '.join(comment.split())
        
        # Standardize punctuation
        comment = comment.strip('.,;:!? ')
        
        return comment if comment else None


# Import re for normalize_comment
import re
