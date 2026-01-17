"""
Standalone Script: Inject Sphinx Documentation Inline
Adds docstrings directly into Python source files
"""

import sys
import os
import argparse
import ast
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from inline_doc_injector import PythonDocInjector
from sphinx_compliance_metrics import DocumentationEvaluator


@dataclass
class FunctionInfo:
    name: str
    line_start: int
    args: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    has_return: bool = False


@dataclass
class ClassInfo:
    name: str
    line_start: int
    attributes: List[str]
    docstring: Optional[str]


class SimpleParser:
    """Simple AST-based parser for function and class extraction"""
    
    @staticmethod
    def parse_code(content: str, filename: str = '<string>'):
        """Parse Python code and extract functions/classes
        
        :param content: Source code content
        :type content: str
        :param filename: Source filename
        :type filename: str
        :return: Dict with functions and classes
        :rtype: dict
        """
        try:
            tree = ast.parse(content, filename)
        except SyntaxError as e:
            print(f"[ERROR] Syntax error: {e}")
            return None
        
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for return statements
                has_return = any(isinstance(stmt, ast.Return) and stmt.value is not None 
                                for stmt in ast.walk(node))
                
                func_info = FunctionInfo(
                    name=node.name,
                    line_start=node.lineno,
                    args=[arg.arg for arg in node.args.args],
                    return_type=ast.unparse(node.returns) if node.returns else None,
                    docstring=ast.get_docstring(node),
                    has_return=has_return
                )
                functions.append(func_info)
            
            elif isinstance(node, ast.ClassDef):
                # Extract attributes from __init__
                attributes = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                        for stmt in item.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                                        if target.value.id == 'self':
                                            attributes.append(target.attr)
                
                class_info = ClassInfo(
                    name=node.name,
                    line_start=node.lineno,
                    attributes=attributes,
                    docstring=ast.get_docstring(node)
                )
                classes.append(class_info)
        
        return {
            'functions': functions,
            'classes': classes,
            'filename': filename
        }



def inject_docs_into_file(file_path: str, output_path: str = None, style: str = 'sphinx', validate: bool = True):
    """Inject documentation into a Python file
    
    :param file_path: Path to source file
    :type file_path: str
    :param output_path: Optional output path (default: overwrite original)
    :type output_path: str
    :param style: Documentation style ('sphinx' or 'google')
    :type style: str
    :param validate: Run compliance validation
    :type validate: bool
    :return: Success status and statistics
    :rtype: tuple
    """
    print(f"\n{'='*60}")
    print(f"INJECTING {style.upper()} DOCUMENTATION INTO:")
    print(f"  {file_path}")
    print(f"{'='*60}\n")
    
    # Read source file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse code
    parser = SimpleParser()
    parsed_data = parser.parse_code(content, file_path)
    
    if not parsed_data:
        print("[ERROR] Failed to parse file")
        return False, {}
    
    functions = parsed_data.get('functions', [])
    classes = parsed_data.get('classes', [])
    
    print(f"Parsed:")
    print(f"  Functions: {len(functions)}")
    print(f"  Classes: {len(classes)}")
    
    # Count items needing docstrings
    funcs_needing_docs = sum(1 for f in functions if not f.docstring)
    classes_needing_docs = sum(1 for c in classes if not c.docstring)
    
    if funcs_needing_docs == 0 and classes_needing_docs == 0:
        print("\n[INFO] All functions and classes already have docstrings!")
        return True, {'functions': 0, 'classes': 0}
    
    print(f"\nInjecting docstrings into:")
    print(f"  Functions: {funcs_needing_docs}")
    print(f"  Classes: {classes_needing_docs}")
    
    # Inject docstrings
    modified_content = PythonDocInjector.inject_docstrings(
        content, functions, classes, style=style
    )
    
    # Write output
    output_file = output_path or file_path
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"\n[SUCCESS] Documentation injected into: {output_file}")
    
    # Validation
    if validate and style == 'sphinx':
        print("\n" + "="*60)
        print("VALIDATING SPHINX COMPLIANCE")
        print("="*60)
        
        evaluator = DocumentationEvaluator()
        
        # Re-parse to get injected docstrings
        reparsed = parser.parse_code(modified_content, file_path)
        validated_items = 0
        passed_items = 0
        
        for func in reparsed.get('functions', []):
            if func.docstring:
                validated_items += 1
                result = evaluator.evaluate(func.docstring)
                if result.accepted:
                    passed_items += 1
                    quality_pct = result.quality.overall_quality * 100 if result.quality else 0.0
                    print(f"  [PASS] {func.name}: {quality_pct:.1f}% quality")
                else:
                    print(f"  [FAIL] {func.name}: Failed compliance gates")
        
        for cls in reparsed.get('classes', []):
            if cls.docstring:
                validated_items += 1
                result = evaluator.evaluate(cls.docstring)
                if result.accepted:
                    passed_items += 1
                    quality_pct = result.quality.overall_quality * 100 if result.quality else 0.0
                    print(f"  [PASS] {cls.name}: {quality_pct:.1f}% quality")
                else:
                    print(f"  [FAIL] {cls.name}: Failed compliance gates")
        
        pass_rate = (passed_items / validated_items * 100) if validated_items > 0 else 0
        print(f"\nValidation: {passed_items}/{validated_items} passed ({pass_rate:.1f}%)")
    
    stats = {
        'functions': funcs_needing_docs,
        'classes': classes_needing_docs,
        'validated': validated_items if validate else 0,
        'passed': passed_items if validate else 0
    }
    
    return True, stats


def main():
    parser = argparse.ArgumentParser(
        description='Inject Sphinx or Google-style docstrings into Python files'
    )
    parser.add_argument('file', help='Python file to process')
    parser.add_argument('-o', '--output', help='Output file (default: overwrite input)')
    parser.add_argument('-s', '--style', choices=['sphinx', 'google'], 
                       default='sphinx', help='Documentation style')
    parser.add_argument('--no-validate', action='store_true', 
                       help='Skip validation')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"[ERROR] File not found: {args.file}")
        sys.exit(1)
    
    success, stats = inject_docs_into_file(
        args.file,
        args.output,
        args.style,
        validate=not args.no_validate
    )
    
    if success:
        print(f"\n{'='*60}")
        print("INJECTION COMPLETE")
        print(f"{'='*60}")
        print(f"Functions documented: {stats.get('functions', 0)}")
        print(f"Classes documented: {stats.get('classes', 0)}")
        if stats.get('validated', 0) > 0:
            print(f"Validation pass rate: {stats.get('passed', 0)}/{stats.get('validated', 0)}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
