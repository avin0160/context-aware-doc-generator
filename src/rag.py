"""
RAG (Retrieval-Augmented Generation) system for code documentation.
Uses sentence transformers for embeddings and FAISS for similarity search.
"""

import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CodeRAGSystem:
    """RAG system for retrieving relevant code context for documentation generation."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the RAG system.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.encoder = None
        self.index = None
        self.code_chunks = []
        self.chunk_metadata = []
        self.is_trained = False
        
        self._load_encoder()
    
    def _load_encoder(self):
        """Load the sentence transformer model."""
        try:
            self.encoder = SentenceTransformer(self.model_name)
            logger.info(f"Loaded encoder: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load encoder: {e}")
            raise
    
    def prepare_code_chunks(self, parsed_codebase: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepare code chunks for embedding from parsed codebase.
        
        Args:
            parsed_codebase: Output from MultiLanguageParser.parse_codebase()
            
        Returns:
            List of code chunks with metadata
        """
        chunks = []
        
        for file_path, file_data in parsed_codebase['files'].items():
            try:
                # Add file-level chunk
                file_chunk = {
                    'type': 'file',
                    'content': self._create_file_summary(file_data),
                    'metadata': {
                        'file_path': file_path,
                        'language': file_data['language'],
                        'functions_count': len(file_data['functions']),
                        'classes_count': len(file_data['classes'])
                    }
                }
                chunks.append(file_chunk)
                
                # Add function chunks
                for func in file_data['functions']:
                    func_chunk = {
                        'type': 'function',
                        'content': self._create_function_context(func, file_data),
                        'metadata': {
                            'file_path': file_path,
                            'language': file_data['language'],
                            'name': func.get('name', 'unknown'),
                            'start_line': func.get('start_line', 0),
                            'end_line': func.get('end_line', 0)
                        }
                    }
                    chunks.append(func_chunk)
                
                # Add class chunks
                for cls in file_data['classes']:
                    class_chunk = {
                        'type': 'class',
                        'content': self._create_class_context(cls, file_data),
                        'metadata': {
                            'file_path': file_path,
                            'language': file_data['language'],
                            'name': cls.get('name', 'unknown'),
                            'start_line': cls.get('start_line', 0),
                            'end_line': cls.get('end_line', 0)
                        }
                    }
                    chunks.append(class_chunk)
                    
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                continue
        
        return chunks
    
    def _create_file_summary(self, file_data: Dict[str, Any]) -> str:
        """Create a summary of the file for embedding."""
        summary_parts = [
            f"File: {Path(file_data['file_path']).name}",
            f"Language: {file_data['language']}",
            f"Functions: {len(file_data['functions'])}",
            f"Classes: {len(file_data['classes'])}"
        ]
        
        if file_data['imports']:
            summary_parts.append(f"Imports: {', '.join(file_data['imports'][:5])}")
        
        # Add function names
        func_names = [f.get('name', 'unknown') for f in file_data['functions'][:10]]
        if func_names:
            summary_parts.append(f"Function names: {', '.join(func_names)}")
        
        # Add class names
        class_names = [c.get('name', 'unknown') for c in file_data['classes'][:10]]
        if class_names:
            summary_parts.append(f"Class names: {', '.join(class_names)}")
        
        return "\n".join(summary_parts)
    
    def _create_function_context(self, func: Dict[str, Any], file_data: Dict[str, Any]) -> str:
        """Create contextual description of a function for embedding."""
        context_parts = [
            f"Function: {func.get('name', 'unknown')}",
            f"Language: {file_data['language']}",
            f"File: {Path(file_data['file_path']).name}"
        ]
        
        # Add the actual function code (truncated if too long)
        func_code = func.get('text', '')
        if len(func_code) > 1000:
            func_code = func_code[:1000] + "..."
        
        context_parts.append(f"Code:\n{func_code}")
        
        # Add surrounding context (imports, nearby functions)
        if file_data['imports']:
            context_parts.append(f"File imports: {', '.join(file_data['imports'][:3])}")
        
        return "\n".join(context_parts)
    
    def _create_class_context(self, cls: Dict[str, Any], file_data: Dict[str, Any]) -> str:
        """Create contextual description of a class for embedding."""
        context_parts = [
            f"Class: {cls.get('name', 'unknown')}",
            f"Language: {file_data['language']}",
            f"File: {Path(file_data['file_path']).name}"
        ]
        
        # Add the actual class code (truncated if too long)
        class_code = cls.get('text', '')
        if len(class_code) > 1500:
            class_code = class_code[:1500] + "..."
        
        context_parts.append(f"Code:\n{class_code}")
        
        # Add surrounding context
        if file_data['imports']:
            context_parts.append(f"File imports: {', '.join(file_data['imports'][:3])}")
        
        return "\n".join(context_parts)
    
    def build_index(self, code_chunks: List[Dict[str, Any]]):
        """
        Build FAISS index from code chunks.
        
        Args:
            code_chunks: List of code chunks with content and metadata
        """
        try:
            self.code_chunks = code_chunks
            self.chunk_metadata = [chunk['metadata'] for chunk in code_chunks]
            
            # Extract content for embedding
            texts = [chunk['content'] for chunk in code_chunks]
            
            logger.info(f"Encoding {len(texts)} code chunks...")
            embeddings = self.encoder.encode(texts, show_progress_bar=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            self.is_trained = True
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
            
        except Exception as e:
            logger.error(f"Error building index: {e}")
            raise
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant code chunks.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant code chunks with scores
        """
        if not self.is_trained:
            raise ValueError("Index not built. Call build_index() first.")
        
        try:
            # Encode query
            query_embedding = self.encoder.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0 and idx < len(self.code_chunks):
                    result = {
                        'chunk': self.code_chunks[idx],
                        'score': float(score),
                        'rank': i + 1
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def save_index(self, index_path: str):
        """Save the FAISS index and metadata to disk."""
        try:
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{index_path}.faiss")
            
            # Save metadata
            metadata = {
                'code_chunks': self.code_chunks,
                'chunk_metadata': self.chunk_metadata,
                'model_name': self.model_name
            }
            
            with open(f"{index_path}.pkl", 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Saved index to {index_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def load_index(self, index_path: str):
        """Load the FAISS index and metadata from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{index_path}.faiss")
            
            # Load metadata
            with open(f"{index_path}.pkl", 'rb') as f:
                metadata = pickle.load(f)
            
            self.code_chunks = metadata['code_chunks']
            self.chunk_metadata = metadata['chunk_metadata']
            
            # Verify model compatibility
            if metadata['model_name'] != self.model_name:
                logger.warning(f"Model mismatch: saved={metadata['model_name']}, current={self.model_name}")
            
            self.is_trained = True
            logger.info(f"Loaded index from {index_path}")
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            raise
    
    def get_context_for_documentation(self, target_code: str, target_type: str = "function") -> str:
        """
        Get relevant context for documenting a piece of code.
        
        Args:
            target_code: The code to document
            target_type: Type of code (function, class, file)
            
        Returns:
            Relevant context string
        """
        if not self.is_trained:
            return ""
        
        try:
            # Create search query
            query_parts = [
                f"Similar {target_type}s",
                f"Related functionality",
                target_code[:200]  # Include part of the actual code
            ]
            query = "\n".join(query_parts)
            
            # Search for relevant chunks
            results = self.search(query, k=3)
            
            # Build context
            context_parts = []
            for result in results:
                chunk = result['chunk']
                score = result['score']
                
                if score > 0.3:  # Only include relevant results
                    context_parts.append(f"Related {chunk['type']} (score: {score:.2f}):")
                    context_parts.append(chunk['content'][:300] + "...")
                    context_parts.append("")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return ""


# Factory function
def create_rag_system(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> CodeRAGSystem:
    """Create and return a configured RAG system."""
    return CodeRAGSystem(model_name)