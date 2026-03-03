# Configuration file for the Context-Aware Documentation Generator

# Personal Information
AUTHOR_NAME = "t8"
AUTHOR_EMAIL = "NA"
GITHUB_USERNAME = "NA"
SYSTEM_NAME = "charvaka"
LAPTOP_NAME = "charvaka"

# Project Information
PROJECT_NAME = "Context-Aware Code Documentation Generator"
PROJECT_DESCRIPTION = "An intelligent system that analyzes codebases and generates comprehensive documentation using AI"
PROJECT_VERSION = "1.0.0"

# Repository Information
REPO_URL = f"https://github.com/{GITHUB_USERNAME}/context-aware-doc-generator"

# Paths and Directories
OUTPUT_DIR = "output"
TEMP_DIR = "temp"
MODELS_DIR = "models"
CACHE_DIR = ".cache"

# Model Configuration
DEFAULT_MODEL = "microsoft/Phi-3-mini-4k-instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# QLoRA Configuration
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "v_proj"]

# Training Configuration
BATCH_SIZE = 4
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
MAX_LENGTH = 512
GRADIENT_ACCUMULATION_STEPS = 4

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your actual API key
GEMINI_MODEL = "models/gemini-2.5-flash"  # Using latest stable flash model
GEMINI_TEMPERATURE = 0.4  # Slightly higher for more natural/human-like output
GEMINI_MAX_TOKENS = 25000  # Good balance of detail and speed

# Gemini Human-Like Mode Configuration
GEMINI_HUMAN_MODE_TEMPERATURE = 0.6  # More creative, conversational
GEMINI_HUMAN_MODE_MAX_TOKENS = 65536  # Maximum for 50+ page extensive documentation

# Phi-3 Model Configuration
PHI3_MODEL = "microsoft/Phi-3-mini-4k-instruct"
TRANSFORMERS_MIN_VERSION = "4.41.0"  # Minimum transformers version for Phi-3 support

# Streamlit Configuration
STREAMLIT_PORT = 8501

# RAG Configuration
EMBEDDING_DIM = 384
TOP_K_RESULTS = 5
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Documentation Styles (for markdown generation)
DOC_STYLES = ["technical_comprehensive", "user_guide", "opensource"]
DEFAULT_DOC_STYLE = "technical_comprehensive"  # User-friendly technical guide

# Supported Languages
SUPPORTED_LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala"
}

# System Information Functions
def get_system_name():
    """Get the configured system name"""
    return SYSTEM_NAME

def get_author_info():
    """Get author information"""
    return {
        "name": AUTHOR_NAME,
        "email": AUTHOR_EMAIL,
        "github": GITHUB_USERNAME,
        "system": SYSTEM_NAME
    }

def get_project_metadata():
    """Get complete project metadata"""
    return {
        "name": PROJECT_NAME,
        "description": PROJECT_DESCRIPTION,
        "version": PROJECT_VERSION,
        "author": AUTHOR_NAME,
        "repository": REPO_URL,
        "system": SYSTEM_NAME
    }
