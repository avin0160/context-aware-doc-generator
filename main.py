#!/usr/bin/env python3
"""
Main CLI interface for the Context-Aware Code Documentation Generator.
"""

import argparse
import sys
import os
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.parser import create_parser
from src.rag import create_rag_system
from src.llm import create_documentation_generator
from src.git_handler import create_git_handler
from comprehensive_docs import generate_comprehensive_documentation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_codebase_generic(
    source_path: str,
    is_repo: bool = False,
    branch: str = "main",
    output_dir: str = "docs_output",
    doc_style: str = "technical",
    context: str = ""
):
    """
    Process codebase using generic documentation system
    """
    try:
        git_handler = create_git_handler()
        
        # Get codebase path
        if is_repo:
            logger.info(f"Cloning repository: {source_path}")
            codebase_path = git_handler.clone_repository(source_path, branch)
        else:
            codebase_path = source_path
        
        if not os.path.exists(codebase_path):
            raise FileNotFoundError(f"Path does not exist: {codebase_path}")
        
        # Read all Python files
        file_contents = {}
        for root, dirs, files in os.walk(codebase_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            relative_path = os.path.relpath(file_path, codebase_path)
                            file_contents[relative_path] = f.read()
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
        
        logger.info(f"Found {len(file_contents)} Python files")
        
        # Generate documentation using generic system
        logger.info("Generating generic documentation...")
        documentation = generate_comprehensive_documentation(
            file_contents, 
            context or "Repository analysis", 
            doc_style,
            codebase_path
        )
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save documentation
        output_file = os.path.join(output_dir, f"documentation_{doc_style}.md")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        logger.info(f"Documentation saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing codebase: {e}")
        raise

def process_codebase(
    source_path: str,
    is_repo: bool = False,
    branch: str = "main",
    output_dir: str = "docs_output",
    doc_style: str = "technical"
):
    """
    Process a codebase and generate documentation.
    
    Args:
        source_path: Path to codebase or repository URL
        is_repo: Whether source_path is a repository URL
        branch: Git branch to use (if repository)
        output_dir: Output directory for documentation
        doc_style: Documentation style (google, numpy, sphinx)
    """
    try:
        # Initialize components
        logger.info("Initializing components...")
        parser = create_parser()
        rag_system = create_rag_system()
        doc_generator = create_documentation_generator()
        git_handler = create_git_handler()
        
        # Get codebase path
        if is_repo:
            logger.info(f"Cloning repository: {source_path}")
            codebase_path = git_handler.clone_repository(source_path, branch)
        else:
            codebase_path = source_path
        
        if not os.path.exists(codebase_path):
            raise FileNotFoundError(f"Path does not exist: {codebase_path}")
        
        # Parse codebase
        logger.info("Parsing codebase...")
        parsed_codebase = parser.parse_codebase(codebase_path)
        
        logger.info(f"Found {parsed_codebase['summary']['total_files']} files")
        logger.info(f"Languages: {', '.join(parsed_codebase['summary']['languages'])}")
        logger.info(f"Functions: {parsed_codebase['summary']['total_functions']}")
        logger.info(f"Classes: {parsed_codebase['summary']['total_classes']}")
        
        # Build RAG index
        logger.info("Building RAG index...")
        code_chunks = rag_system.prepare_code_chunks(parsed_codebase)
        rag_system.build_index(code_chunks)
        logger.info(f"Built index with {len(code_chunks)} chunks")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate docstrings
        logger.info("Generating docstrings...")
        docstrings_output = {}
        
        for file_path, file_data in parsed_codebase['files'].items():
            file_docstrings = {}
            
            # Document functions
            for func in file_data['functions']:
                logger.info(f"Documenting function: {func.get('name', 'unknown')}")
                context = rag_system.get_context_for_documentation(
                    func.get('text', ''), 'function'
                )
                docstring = doc_generator.generate_docstring(
                    func.get('text', ''),
                    file_data['language'],
                    context,
                    doc_style
                )
                file_docstrings[f"function_{func.get('name', 'unknown')}"] = {
                    'docstring': docstring,
                    'line': func.get('start_line', 0),
                    'original_code': func.get('text', '')
                }
            
            # Document classes
            for cls in file_data['classes']:
                logger.info(f"Documenting class: {cls.get('name', 'unknown')}")
                context = rag_system.get_context_for_documentation(
                    cls.get('text', ''), 'class'
                )
                docstring = doc_generator.generate_docstring(
                    cls.get('text', ''),
                    file_data['language'],
                    context,
                    doc_style
                )
                file_docstrings[f"class_{cls.get('name', 'unknown')}"] = {
                    'docstring': docstring,
                    'line': cls.get('start_line', 0),
                    'original_code': cls.get('text', '')
                }
            
            if file_docstrings:
                docstrings_output[file_path] = file_docstrings
        
        # Save docstrings to file
        docstrings_file = os.path.join(output_dir, "generated_docstrings.json")
        import json
        with open(docstrings_file, 'w') as f:
            json.dump(docstrings_output, f, indent=2)
        logger.info(f"Saved docstrings to: {docstrings_file}")
        
        # Generate markdown documentation
        logger.info("Generating markdown documentation...")
        context = f"Codebase analysis\nLanguages: {', '.join(parsed_codebase['summary']['languages'])}"
        markdown_docs = doc_generator.generate_markdown_docs(parsed_codebase, context)
        
        # Save markdown documentation
        readme_file = os.path.join(output_dir, "README.md")
        with open(readme_file, 'w') as f:
            f.write(markdown_docs)
        logger.info(f"Saved markdown documentation to: {readme_file}")
        
        # Generate summary report
        summary_file = os.path.join(output_dir, "generation_summary.md")
        with open(summary_file, 'w') as f:
            f.write("# Documentation Generation Summary\n\n")
            f.write(f"**Source:** {source_path}\n")
            f.write(f"**Documentation Style:** {doc_style}\n")
            f.write(f"**Output Directory:** {output_dir}\n\n")
            f.write("## Statistics\n\n")
            f.write(f"- **Files Processed:** {parsed_codebase['summary']['total_files']}\n")
            f.write(f"- **Functions Documented:** {parsed_codebase['summary']['total_functions']}\n")
            f.write(f"- **Classes Documented:** {parsed_codebase['summary']['total_classes']}\n")
            f.write(f"- **Languages:** {', '.join(parsed_codebase['summary']['languages'])}\n")
            f.write(f"- **RAG Chunks:** {len(code_chunks)}\n\n")
            f.write("## Generated Files\n\n")
            f.write(f"- `generated_docstrings.json`: Individual docstrings for functions and classes\n")
            f.write(f"- `README.md`: Comprehensive project documentation\n")
            f.write(f"- `generation_summary.md`: This summary file\n")
        
        logger.info(f"Saved summary to: {summary_file}")
        
        # Cleanup if repository was cloned
        if is_repo:
            git_handler.cleanup(codebase_path)
        
        logger.info("✅ Documentation generation completed successfully!")
        logger.info(f"📁 Output directory: {output_dir}")
        
    except Exception as e:
        logger.error(f"❌ Error during processing: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Context-Aware Code Documentation Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate docs for a local directory
  python main.py /path/to/codebase --output docs_output
  
  # Generate docs for a GitHub repository
  python main.py https://github.com/user/repo --repo --output docs_output
  
  # Use specific branch and documentation style
  python main.py https://github.com/user/repo --repo --branch develop --style numpy
        """
    )
    
    parser.add_argument(
        "source",
        help="Path to codebase directory or GitHub repository URL"
    )
    
    parser.add_argument(
        "--repo",
        action="store_true",
        help="Treat source as a GitHub repository URL"
    )
    
    parser.add_argument(
        "--branch",
        default="main",
        help="Git branch to use (default: main)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        default="docs_output",
        help="Output directory for generated documentation (default: docs_output)"
    )
    
    parser.add_argument(
        "--style",
        choices=["technical", "api", "user_guide", "tutorial", "comprehensive"],
        default="technical",
        help="Documentation style (default: technical)"
    )
    
    parser.add_argument(
        "--context",
        default="",
        help="Additional context about the project"
    )
    
    parser.add_argument(
        "--use-generic",
        action="store_true",
        help="Use generic documentation system instead of RAG-based system"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Process the codebase
    if args.use_generic:
        process_codebase_generic(
            source_path=args.source,
            is_repo=args.repo,
            branch=args.branch,
            output_dir=args.output,
            doc_style=args.style,
            context=args.context
        )
    else:
        # Use generic system by default (old RAG system as fallback)
        try:
            process_codebase_generic(
                source_path=args.source,
                is_repo=args.repo,
                branch=args.branch,
                output_dir=args.output,
                doc_style=args.style,
                context=args.context
            )
        except Exception as e:
            logger.warning(f"Generic system failed: {e}, falling back to original system")
            process_codebase(
                source_path=args.source,
                is_repo=args.repo,
                branch=args.branch,
                output_dir=args.output,
                doc_style=args.style
            )


if __name__ == "__main__":
    main()