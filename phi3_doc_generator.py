"""
Phi-3-Mini Documentation Generator
Uses Microsoft's Phi-3-Mini-128K model for research-quality documentation generation
Enhanced with Gemini API for whole-codebase context awareness
"""

import torch
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Gemini enhancer
try:
    from gemini_context_enhancer import get_gemini_enhancer
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini context enhancer not available")

class Phi3DocumentationGenerator:
    """Generate high-quality documentation using Microsoft Phi-3-Mini
    
    Enhanced with Gemini API for whole-codebase context validation and enrichment.
    
    Architecture:
    - Phi-3: Backbone - generates initial documentation from local context
    - Gemini: Context validator - enhances with full project awareness
    """
    
    def __init__(self, model_name: str = "microsoft/Phi-3-mini-4k-instruct"):
        """Initialize Phi-3 model and Gemini enhancer
        
        Args:
            model_name: HuggingFace model identifier
        """
        self.model = None
        self.tokenizer = None
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.gemini_enhancer = None
        self.project_context = None  # Store full project context for Gemini
        
        # Initialize Phi-3
        self._initialize_model()
        
        # Initialize Gemini enhancer
        if GEMINI_AVAILABLE:
            try:
                self.gemini_enhancer = get_gemini_enhancer()
                if self.gemini_enhancer.available:
                    logger.info("✅ Gemini context enhancer enabled")
            except Exception as e:
                logger.warning(f"⚠️ Gemini enhancer initialization failed: {e}")
    
    def set_project_context(self, analysis: Dict):
        """Set full project context for Gemini enhancement
        
        Args:
            analysis: Complete project analysis dictionary
        """
        if self.gemini_enhancer and self.gemini_enhancer.available:
            self.project_context = self.gemini_enhancer.build_project_context(analysis)
            logger.info("✅ Project context prepared for Gemini")
    
    def _initialize_model(self):
        """Lazy load model to save memory"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            logger.info(f"Loading Phi-3 model: {self.model_name}")
            logger.info(f"Device: {self.device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.info("✅ Phi-3 model loaded successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load Phi-3 model: {e}")
            logger.warning("Falling back to rule-based generation")
            self.model = None
    
    def generate_function_docstring(
        self,
        function_code: str,
        function_name: str,
        context: Dict[str, Any],
        style: str = "google"
    ) -> str:
        """Generate comprehensive docstring for a function
        
        Architecture:
        1. Phi-3 generates initial documentation (backbone)
        2. Gemini enhances with whole-codebase context (if available)
        
        Args:
            function_code: Full function source code
            function_name: Name of the function
            context: Dict with called_by, calls, file_path, complexity, etc.
            style: Documentation style (google, numpy, sphinx)
            
        Returns:
            High-quality docstring text enhanced with project context
        """
        if not self.model:
            return self._fallback_docstring(function_name, context)
        
        # Step 1: Generate with Phi-3 (backbone)
        prompt = self._build_function_prompt(function_code, function_name, context, style)
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=3072)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.3,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract Phi-3 docstring
            phi3_docstring = self._extract_docstring(generated_text, prompt)
            
            # Step 2: Enhance with Gemini (if available)
            if self.gemini_enhancer and self.gemini_enhancer.available and self.project_context:
                logger.info(f"🔄 Enhancing {function_name} with Gemini context")
                enhanced_docstring = self.gemini_enhancer.enhance_documentation(
                    phi3_docstring,
                    context,
                    self.project_context
                )
                return enhanced_docstring
            
            return phi3_docstring
            
        except Exception as e:
            logger.error(f"Error generating docstring: {e}")
            return self._fallback_docstring(function_name, context)
    
    def _build_function_prompt(
        self,
        function_code: str,
        function_name: str,
        context: Dict[str, Any],
        style: str
    ) -> str:
        """Build prompt for function documentation"""
        
        # Get context information
        called_by = context.get('called_by', [])
        calls = context.get('calls', [])
        complexity = context.get('complexity', 'unknown')
        file_path = context.get('file_path', 'unknown')
        
        called_by_str = ', '.join(called_by[:3]) if called_by else "entry point"
        calls_str = ', '.join(calls[:5]) if calls else "no function calls"
        
        prompt = f"""<|system|>
You are an expert technical writer specializing in code documentation. Generate a comprehensive, accurate docstring in {style} style.
<|end|>
<|user|>
Analyze this function and write a detailed docstring:

```python
{function_code}
```

**Context:**
- Function: {function_name}
- File: {file_path}
- Called by: {called_by_str}
- Calls: {calls_str}
- Complexity: {complexity}

**Requirements:**
1. Brief description (one line)
2. Detailed explanation of functionality
3. All parameters with types and descriptions
4. Return value with type and description
5. Example usage if helpful
6. Notes about edge cases or important behavior

Generate ONLY the docstring text (no function signature):
<|end|>
<|assistant|>
"""
        return prompt
    
    def _extract_docstring(self, generated_text: str, prompt: str) -> str:
        """Extract clean docstring from generated text"""
        # Remove the prompt
        if prompt in generated_text:
            result = generated_text.replace(prompt, "").strip()
        else:
            result = generated_text.strip()
        
        # Clean up common issues
        result = result.strip('`"\' \n')
        
        # If starts with def or class, extract just the docstring
        if result.startswith('def ') or result.startswith('class '):
            lines = result.split('\n')
            in_docstring = False
            docstring_lines = []
            
            for line in lines:
                if '"""' in line or "'''" in line:
                    if not in_docstring:
                        in_docstring = True
                        docstring_lines.append(line.strip('"\''))
                    else:
                        break
                elif in_docstring:
                    docstring_lines.append(line)
            
            result = '\n'.join(docstring_lines).strip()
        
        return result
    
    def generate_class_docstring(
        self,
        class_code: str,
        class_name: str,
        methods: List[str],
        context: Dict[str, Any],
        style: str = "google"
    ) -> str:
        """Generate comprehensive docstring for a class
        
        Args:
            class_code: Full class source code
            class_name: Name of the class
            methods: List of method names in the class
            context: Dict with inheritance, file_path, etc.
            style: Documentation style
            
        Returns:
            High-quality class docstring
        """
        if not self.model:
            return self._fallback_class_docstring(class_name, methods, context)
        
        prompt = self._build_class_prompt(class_code, class_name, methods, context, style)
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=3072)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.3,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            docstring = self._extract_docstring(generated_text, prompt)
            return docstring
            
        except Exception as e:
            logger.error(f"Error generating class docstring: {e}")
            return self._fallback_class_docstring(class_name, methods, context)
    
    def _build_class_prompt(
        self,
        class_code: str,
        class_name: str,
        methods: List[str],
        context: Dict[str, Any],
        style: str
    ) -> str:
        """Build prompt for class documentation"""
        
        inherits = context.get('bases', [])
        inherits_str = ', '.join(inherits) if inherits else "object"
        methods_str = ', '.join(methods[:10]) if methods else "no methods"
        
        prompt = f"""<|system|>
You are an expert technical writer. Generate a comprehensive class docstring in {style} style.
<|end|>
<|user|>
Analyze this class and write a detailed docstring:

```python
{class_code[:1000]}  # First 1000 chars
```

**Context:**
- Class: {class_name}
- Inherits from: {inherits_str}
- Methods: {methods_str}

**Requirements:**
1. Brief description of class purpose
2. Detailed explanation of functionality
3. Key attributes
4. Usage examples
5. Design patterns if applicable

Generate ONLY the docstring text:
<|end|>
<|assistant|>
"""
        return prompt
    
    def _fallback_docstring(self, function_name: str, context: Dict[str, Any]) -> str:
        """Generate basic docstring when model unavailable"""
        calls = context.get('calls', [])
        complexity = context.get('complexity', 1)
        
        description = f"{function_name.replace('_', ' ').title()} function."
        
        if calls:
            description += f"\n\nCalls: {', '.join(calls[:3])}."
        
        if complexity > 5:
            description += "\n\nNote: This is a complex function with high cyclomatic complexity."
        
        return description
    
    def _fallback_class_docstring(
        self,
        class_name: str,
        methods: List[str],
        context: Dict[str, Any]
    ) -> str:
        """Generate basic class docstring when model unavailable"""
        description = f"{class_name} class."
        
        if methods:
            public_methods = [m for m in methods if not m.startswith('_')]
            if public_methods:
                description += f"\n\nProvides methods: {', '.join(public_methods[:5])}."
        
        return description
    
    def enhance_existing_docstring(
        self,
        existing_docstring: str,
        function_code: str,
        context: Dict[str, Any]
    ) -> str:
        """Enhance an existing docstring with better details
        
        Args:
            existing_docstring: Current docstring
            function_code: Function source code
            context: Additional context
            
        Returns:
            Enhanced docstring
        """
        if not self.model or not existing_docstring:
            return existing_docstring
        
        prompt = f"""<|system|>
You are an expert technical writer. Enhance this docstring with better details.
<|end|>
<|user|>
Improve this docstring:

Current docstring:
{existing_docstring}

Function code:
```python
{function_code}
```

Make it more comprehensive while keeping the core meaning. Add:
- Better parameter descriptions
- Return value details
- Usage examples
- Edge cases

Generate the improved docstring:
<|end|>
<|assistant|>
"""
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=3072)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            enhanced = self._extract_docstring(generated_text, prompt)
            return enhanced if enhanced else existing_docstring
            
        except Exception as e:
            logger.error(f"Error enhancing docstring: {e}")
            return existing_docstring
