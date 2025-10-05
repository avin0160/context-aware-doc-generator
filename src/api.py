"""
FastAPI backend for the Context-Aware Code Documentation Generator.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pathlib import Path
import logging

# Local imports
from src.parser import create_parser
from src.rag import create_rag_system
from src.llm import create_documentation_generator
from src.git_handler import create_git_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Context-Aware Code Documentation Generator",
    description="Generate intelligent documentation for codebases using RAG and LLM",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components (initialized on startup)
parser = None
rag_system = None
doc_generator = None
git_handler = None


# Pydantic models
class RepoRequest(BaseModel):
    """Request model for repository processing."""
    repo_url: str
    branch: str = "main"
    doc_style: str = "google"


class DocumentationResponse(BaseModel):
    """Response model for documentation generation."""
    success: bool
    message: str
    repo_info: Optional[Dict[str, Any]] = None
    docstrings: Optional[Dict[str, str]] = None
    markdown_docs: Optional[str] = None
    processing_stats: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    components: Dict[str, bool]


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global parser, rag_system, doc_generator, git_handler
    
    try:
        logger.info("Initializing components...")
        
        # Initialize parser
        parser = create_parser()
        logger.info("✓ Parser initialized")
        
        # Initialize RAG system
        rag_system = create_rag_system()
        logger.info("✓ RAG system initialized")
        
        # Initialize documentation generator
        doc_generator = create_documentation_generator()
        logger.info("✓ Documentation generator initialized")
        
        # Initialize Git handler
        git_handler = create_git_handler()
        logger.info("✓ Git handler initialized")
        
        logger.info("All components initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Context-Aware Code Documentation Generator API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    components_status = {
        "parser": parser is not None,
        "rag_system": rag_system is not None,
        "doc_generator": doc_generator is not None,
        "git_handler": git_handler is not None
    }
    
    all_healthy = all(components_status.values())
    
    return HealthResponse(
        status="healthy" if all_healthy else "unhealthy",
        components=components_status
    )


@app.post("/generate-docs/repo", response_model=DocumentationResponse)
async def generate_docs_from_repo(
    request: RepoRequest,
    background_tasks: BackgroundTasks
):
    """Generate documentation from a GitHub repository."""
    try:
        logger.info(f"Processing repository: {request.repo_url}")
        
        # Clone repository
        repo_path = git_handler.clone_repository(request.repo_url, request.branch)
        
        # Get repository info
        repo_info = git_handler.get_repository_info(repo_path)
        
        # Parse codebase
        logger.info("Parsing codebase...")
        parsed_codebase = parser.parse_codebase(repo_path)
        
        # Build RAG index
        logger.info("Building RAG index...")
        code_chunks = rag_system.prepare_code_chunks(parsed_codebase)
        rag_system.build_index(code_chunks)
        
        # Generate documentation
        logger.info("Generating documentation...")
        docstrings = {}
        
        # Generate docstrings for functions and classes
        for file_path, file_data in parsed_codebase['files'].items():
            file_docstrings = {}
            
            # Document functions
            for func in file_data['functions']:
                context = rag_system.get_context_for_documentation(
                    func.get('text', ''), 'function'
                )
                docstring = doc_generator.generate_docstring(
                    func.get('text', ''),
                    file_data['language'],
                    context,
                    request.doc_style
                )
                file_docstrings[f"function_{func.get('name', 'unknown')}"] = docstring
            
            # Document classes
            for cls in file_data['classes']:
                context = rag_system.get_context_for_documentation(
                    cls.get('text', ''), 'class'
                )
                docstring = doc_generator.generate_docstring(
                    cls.get('text', ''),
                    file_data['language'],
                    context,
                    request.doc_style
                )
                file_docstrings[f"class_{cls.get('name', 'unknown')}"] = docstring
            
            if file_docstrings:
                docstrings[file_path] = file_docstrings
        
        # Generate markdown documentation
        context = f"Repository: {request.repo_url}\nLanguages: {', '.join(repo_info.get('languages', []))}"
        markdown_docs = doc_generator.generate_markdown_docs(parsed_codebase, context)
        
        # Processing statistics
        processing_stats = {
            "files_processed": parsed_codebase['summary']['total_files'],
            "functions_documented": parsed_codebase['summary']['total_functions'],
            "classes_documented": parsed_codebase['summary']['total_classes'],
            "languages": parsed_codebase['summary']['languages'],
            "rag_chunks": len(code_chunks)
        }
        
        # Schedule cleanup
        background_tasks.add_task(git_handler.cleanup, repo_path)
        
        return DocumentationResponse(
            success=True,
            message="Documentation generated successfully",
            repo_info=repo_info,
            docstrings=docstrings,
            markdown_docs=markdown_docs,
            processing_stats=processing_stats
        )
        
    except Exception as e:
        logger.error(f"Error processing repository: {e}")
        return DocumentationResponse(
            success=False,
            message=f"Error processing repository: {str(e)}"
        )


@app.post("/generate-docs/upload", response_model=DocumentationResponse)
async def generate_docs_from_upload(
    file: UploadFile = File(...),
    doc_style: str = "google",
    background_tasks: BackgroundTasks = None
):
    """Generate documentation from uploaded ZIP file."""
    try:
        logger.info(f"Processing uploaded file: {file.filename}")
        
        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")
        
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_zip_path = temp_file.name
        
        # Extract ZIP
        extracted_path = git_handler.extract_zip_archive(temp_zip_path)
        
        # Get directory info
        repo_info = git_handler.get_repository_info(extracted_path)
        
        # Parse codebase
        logger.info("Parsing codebase...")
        parsed_codebase = parser.parse_codebase(extracted_path)
        
        # Build RAG index
        logger.info("Building RAG index...")
        code_chunks = rag_system.prepare_code_chunks(parsed_codebase)
        rag_system.build_index(code_chunks)
        
        # Generate documentation (similar to repo processing)
        logger.info("Generating documentation...")
        docstrings = {}
        
        for file_path, file_data in parsed_codebase['files'].items():
            file_docstrings = {}
            
            for func in file_data['functions']:
                context = rag_system.get_context_for_documentation(
                    func.get('text', ''), 'function'
                )
                docstring = doc_generator.generate_docstring(
                    func.get('text', ''),
                    file_data['language'],
                    context,
                    doc_style
                )
                file_docstrings[f"function_{func.get('name', 'unknown')}"] = docstring
            
            for cls in file_data['classes']:
                context = rag_system.get_context_for_documentation(
                    cls.get('text', ''), 'class'
                )
                docstring = doc_generator.generate_docstring(
                    cls.get('text', ''),
                    file_data['language'],
                    context,
                    doc_style
                )
                file_docstrings[f"class_{cls.get('name', 'unknown')}"] = docstring
            
            if file_docstrings:
                docstrings[file_path] = file_docstrings
        
        # Generate markdown documentation
        context = f"Uploaded file: {file.filename}\nLanguages: {', '.join(repo_info.get('languages', []))}"
        markdown_docs = doc_generator.generate_markdown_docs(parsed_codebase, context)
        
        processing_stats = {
            "files_processed": parsed_codebase['summary']['total_files'],
            "functions_documented": parsed_codebase['summary']['total_functions'],
            "classes_documented": parsed_codebase['summary']['total_classes'],
            "languages": parsed_codebase['summary']['languages'],
            "rag_chunks": len(code_chunks)
        }
        
        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(cleanup_files, [temp_zip_path, extracted_path])
        
        return DocumentationResponse(
            success=True,
            message="Documentation generated successfully",
            repo_info=repo_info,
            docstrings=docstrings,
            markdown_docs=markdown_docs,
            processing_stats=processing_stats
        )
        
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        return DocumentationResponse(
            success=False,
            message=f"Error processing upload: {str(e)}"
        )


async def cleanup_files(file_paths: List[str]):
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up {file_path}: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )