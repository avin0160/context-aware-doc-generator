#!/usr/bin/env python3
"""
Colab-optimized configuration for Context-Aware Documentation Generator
Disables quantization and optimizes for Colab environment
"""

import os
import sys
from pathlib import Path

def setup_colab_environment():
    """Configure environment for optimal Colab performance."""
    
    # Disable quantization for Colab compatibility
    os.environ['DISABLE_QUANTIZATION'] = '1'
    os.environ['USE_CPU_ONLY'] = '0'  # Use GPU if available, but no quantization
    
    # Set memory optimization
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'
    
    # Disable bitsandbytes warnings
    os.environ['BITSANDBYTES_NOWELCOME'] = '1'
    
    # Optimize transformers
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
    
    print("✅ Colab environment configured for optimal performance")
    print("   • Quantization disabled for compatibility")
    print("   • Memory optimization enabled")
    print("   • GPU usage optimized")

def create_colab_llm():
    """Create LLM instance optimized for Colab."""
    from src.llm import SimpleLLMGenerator
    
    # Use simple LLM without quantization
    return SimpleLLMGenerator()

def create_colab_components():
    """Create all system components optimized for Colab."""
    setup_colab_environment()
    
    from src.parser import create_parser
    from src.rag import create_rag_system
    from src.git_handler import create_git_handler
    
    return {
        'parser': create_parser(),
        'rag_system': create_rag_system(),
        'git_handler': create_git_handler(),
        'llm': create_colab_llm()
    }

if __name__ == "__main__":
    setup_colab_environment()
    print("Colab environment ready!")