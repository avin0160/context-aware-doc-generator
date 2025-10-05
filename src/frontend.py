"""
Streamlit frontend for the Context-Aware Code Documentation Generator.
"""

import streamlit as st
import requests
import json
import zipfile
import io
from typing import Dict, Any, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Context-Aware Doc Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin: 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #cce7ff;
        border: 1px solid #b3d9ff;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if the API is running and healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def display_header():
    """Display the main header and description."""
    st.markdown('<h1 class="main-header">📚 Context-Aware Code Documentation Generator</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    Generate intelligent, context-aware documentation for your codebases using advanced AI. 
    This tool analyzes your code structure, applies RAG (Retrieval-Augmented Generation) for context understanding, 
    and uses fine-tuned language models to create comprehensive documentation.
    """)
    
    # API Status
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if check_api_health():
            st.success("🟢 API is running and healthy")
        else:
            st.error("🔴 API is not responding. Please start the FastAPI server.")
            st.code("python -m uvicorn src.api:app --reload", language="bash")


def sidebar_config():
    """Configure the sidebar with options."""
    st.sidebar.markdown("## ⚙️ Configuration")
    
    # Documentation style
    doc_style = st.sidebar.selectbox(
        "Documentation Style",
        ["google", "numpy", "sphinx"],
        help="Choose the documentation style for generated docstrings"
    )
    
    # Processing options
    st.sidebar.markdown("### Processing Options")
    include_private = st.sidebar.checkbox("Include private methods", value=False)
    include_tests = st.sidebar.checkbox("Include test files", value=False)
    
    # Model information
    st.sidebar.markdown("### 🤖 Model Information")
    st.sidebar.info("""
    **Parser**: tree-sitter (multi-language)
    **Embeddings**: all-MiniLM-L6-v2
    **LLM**: Microsoft Phi-3-mini-4k-instruct
    **RAG**: FAISS similarity search
    """)
    
    return {
        "doc_style": doc_style,
        "include_private": include_private,
        "include_tests": include_tests
    }


def process_repository(repo_url: str, branch: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a GitHub repository."""
    payload = {
        "repo_url": repo_url,
        "branch": branch,
        "doc_style": config["doc_style"]
    }
    
    try:
        with st.spinner("🔄 Processing repository... This may take a few minutes."):
            response = requests.post(
                f"{API_BASE_URL}/generate-docs/repo",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. The repository might be too large or the server is busy.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def process_upload(uploaded_file, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process an uploaded ZIP file."""
    try:
        files = {"file": (uploaded_file.name, uploaded_file, "application/zip")}
        data = {"doc_style": config["doc_style"]}
        
        with st.spinner("🔄 Processing uploaded file... This may take a few minutes."):
            response = requests.post(
                f"{API_BASE_URL}/generate-docs/upload",
                files=files,
                data=data,
                timeout=300
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. The file might be too large or contain too many files.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def display_results(result: Dict[str, Any]):
    """Display the processing results."""
    if not result["success"]:
        st.error(f"❌ {result['message']}")
        return
    
    st.success(f"✅ {result['message']}")
    
    # Repository Information
    if result.get("repo_info"):
        st.markdown('<div class="section-header">📊 Repository Information</div>', 
                    unsafe_allow_html=True)
        
        repo_info = result["repo_info"]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", repo_info.get("files_count", 0))
        with col2:
            st.metric("Size (MB)", repo_info.get("total_size_mb", 0))
        with col3:
            st.metric("Languages", len(repo_info.get("languages", [])))
        with col4:
            st.metric("Directories", repo_info.get("directories_count", 0))
        
        if repo_info.get("languages"):
            st.write("**Programming Languages:**", ", ".join(repo_info["languages"]))
    
    # Processing Statistics
    if result.get("processing_stats"):
        st.markdown('<div class="section-header">📈 Processing Statistics</div>', 
                    unsafe_allow_html=True)
        
        stats = result["processing_stats"]
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Files Processed", stats.get("files_processed", 0))
        with col2:
            st.metric("Functions Documented", stats.get("functions_documented", 0))
        with col3:
            st.metric("Classes Documented", stats.get("classes_documented", 0))
        with col4:
            st.metric("RAG Chunks", stats.get("rag_chunks", 0))
    
    # Generated Documentation
    tabs = st.tabs(["📝 Generated Docstrings", "📄 Markdown Documentation"])
    
    with tabs[0]:
        if result.get("docstrings"):
            st.markdown('<div class="section-header">Generated Docstrings</div>', 
                        unsafe_allow_html=True)
            
            docstrings = result["docstrings"]
            
            # Create expandable sections for each file
            for file_path, file_docstrings in docstrings.items():
                with st.expander(f"📁 {file_path}"):
                    for item_name, docstring in file_docstrings.items():
                        st.markdown(f"**{item_name}:**")
                        st.code(docstring, language="python")
                        st.markdown("---")
        else:
            st.info("No docstrings were generated.")
    
    with tabs[1]:
        if result.get("markdown_docs"):
            st.markdown('<div class="section-header">Markdown Documentation</div>', 
                        unsafe_allow_html=True)
            
            # Display markdown
            st.markdown(result["markdown_docs"])
            
            # Download button
            st.download_button(
                label="📥 Download README.md",
                data=result["markdown_docs"],
                file_name="README.md",
                mime="text/markdown"
            )
        else:
            st.info("No markdown documentation was generated.")


def main():
    """Main Streamlit application."""
    display_header()
    
    # Sidebar configuration
    config = sidebar_config()
    
    # Main content
    st.markdown('<div class="section-header">🚀 Generate Documentation</div>', 
                unsafe_allow_html=True)
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["GitHub Repository", "Upload ZIP File"],
        horizontal=True
    )
    
    if input_method == "GitHub Repository":
        st.markdown("### 🔗 GitHub Repository")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            repo_url = st.text_input(
                "Repository URL",
                placeholder="https://github.com/username/repository",
                help="Enter the full GitHub repository URL"
            )
        with col2:
            branch = st.text_input("Branch", value="main", help="Repository branch to analyze")
        
        if st.button("🔍 Generate Documentation", type="primary"):
            if repo_url:
                result = process_repository(repo_url, branch, config)
                if result:
                    display_results(result)
            else:
                st.warning("⚠️ Please enter a repository URL")
    
    else:  # Upload ZIP File
        st.markdown("### 📁 Upload ZIP File")
        
        uploaded_file = st.file_uploader(
            "Choose a ZIP file",
            type=["zip"],
            help="Upload a ZIP file containing your codebase"
        )
        
        if uploaded_file is not None:
            st.info(f"📁 Selected file: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            if st.button("🔍 Generate Documentation", type="primary"):
                result = process_upload(uploaded_file, config)
                if result:
                    display_results(result)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Built with ❤️ using Streamlit, FastAPI, and Microsoft Phi-3</p>
        <p>Powered by tree-sitter, sentence-transformers, and FAISS</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()