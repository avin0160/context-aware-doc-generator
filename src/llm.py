"""
LLM handler for documentation generation using Microsoft Phi-3 model.
Supports fine-tuning with QLoRA and generation of context-aware documentation.
"""

import os
import torch
from typing import Dict, List, Optional, Any
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType
import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation."""
    max_length: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True
    pad_token_id: int = None


class Phi3DocumentationGenerator:
    """Documentation generator using Microsoft Phi-3 model with QLoRA fine-tuning."""
    
    def __init__(
        self, 
        model_name: str = "microsoft/Phi-3-mini-4k-instruct",
        device: str = "auto"
    ):
        """
        Initialize the documentation generator.
        
        Args:
            model_name: HuggingFace model name
            device: Device to run the model on
        """
        self.model_name = model_name
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None
        self.config = DocumentationConfig()
        
        self._load_model()
    
    def _load_model(self):
        """Load the tokenizer and model."""
        try:
            logger.info(f"Loading tokenizer for {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.config.pad_token_id = self.tokenizer.eos_token_id
            
            # Configure quantization for efficient inference (skip if disabled for Colab)
            quantization_config = None
            if not os.getenv('DISABLE_QUANTIZATION', '0') == '1':
                try:
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                    logger.info("Quantization enabled")
                except Exception as e:
                    logger.warning(f"Quantization not available, using standard loading: {e}")
                    quantization_config = None
            else:
                logger.info("Quantization disabled for Colab compatibility")
            
            logger.info(f"Loading model {self.model_name}")
            
            # Load model with or without quantization
            load_kwargs = {
                "device_map": "auto",
                "trust_remote_code": True,
                "torch_dtype": torch.float16
            }
            
            if quantization_config is not None:
                load_kwargs["quantization_config"] = quantization_config
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **load_kwargs
            )
            
            logger.info(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def create_lora_config(self) -> LoraConfig:
        """Create LoRA configuration for fine-tuning."""
        return LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
        )
    
    def prepare_for_training(self):
        """Prepare model for LoRA fine-tuning."""
        try:
            lora_config = self.create_lora_config()
            self.model = get_peft_model(self.model, lora_config)
            
            # Enable gradient checkpointing
            self.model.gradient_checkpointing_enable()
            
            logger.info("Model prepared for LoRA training")
            
        except Exception as e:
            logger.error(f"Error preparing model for training: {e}")
            raise
    
    def generate_docstring(
        self, 
        code: str, 
        language: str, 
        context: str = "",
        style: str = "google"
    ) -> str:
        """
        Generate docstring for given code.
        
        Args:
            code: The code to document
            language: Programming language
            context: Additional context from RAG
            style: Documentation style (google, numpy, sphinx)
            
        Returns:
            Generated docstring
        """
        try:
            prompt = self._create_docstring_prompt(code, language, context, style)
            
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    do_sample=self.config.do_sample,
                    pad_token_id=self.config.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode only the new tokens
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            )
            
            return self._clean_docstring(response)
            
        except Exception as e:
            logger.error(f"Error generating docstring: {e}")
            return f'"""\nError generating documentation: {str(e)}\n"""'
    
    def generate_markdown_docs(
        self, 
        parsed_codebase: Dict[str, Any], 
        context: str = ""
    ) -> str:
        """
        Generate comprehensive Markdown documentation.
        
        Args:
            parsed_codebase: Parsed codebase from MultiLanguageParser
            context: Additional context from RAG
            
        Returns:
            Markdown documentation
        """
        """
        Produce a concise, useful Markdown README from the parsed_codebase.

        This implementation avoids over-reliance on the LLM for large, noisy
        API dumps. It extracts function/class signatures and any existing
        docstrings, deduplicates entries, and generates sane sections: title,
        description, installation, usage, API reference, troubleshooting,
        contributing and license placeholders.
        """
        try:
            # Helpers
            import re

            def infer_project_name(files: List[str]) -> str:
                if not files:
                    return "Project"
                # Use parent folder name of the first file
                first = files[0]
                parts = first.replace('\\\\', '/').split('/')
                if len(parts) >= 2:
                    return parts[-2] or parts[-1]
                return parts[-1]

            def extract_signature(node_text: str) -> Optional[str]:
                # Try to extract python def/class signature including return annotation
                m = re.search(r'^(\s*(def|class)\s+[A-Za-z0-9_]+\s*\([^\)]*\)\s*(?:->\s*[^:\s]+)?)[\s:]*', node_text, re.M)
                if m:
                    sig = m.group(1).strip()
                    # Normalize whitespace
                    return ' '.join(sig.split())
                # fallback: first non-empty line
                for line in node_text.splitlines():
                    line = line.strip()
                    if line:
                        return line
                return None

            def extract_docstring(node_text: str) -> Optional[str]:
                # extract triple-quoted docstring (python) and return a cleaned paragraph
                m = re.search(r'^[\s\t]*[rRuU]{0,2}(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', node_text, re.S | re.M)
                if m:
                    doc = m.group(1).strip()
                    # Collapse internal whitespace and limit length but avoid mid-word truncation
                    doc = '\n'.join([ln.strip() for ln in doc.splitlines() if ln.strip()])
                    if len(doc) > 600:
                        cut = doc[:600]
                        # avoid cutting last word
                        cut = cut.rsplit(' ', 1)[0]
                        doc = cut + '...'
                    # Prefer first paragraph/sentence for summary
                    para = doc.split('\n\n')[0]
                    # If very long, take first sentence
                    if len(para) > 300 and '.' in para:
                        para = para.split('.', 1)[0] + '.'
                    return para
                return None

            files = list(parsed_codebase.get('files', {}).keys())
            project_name = infer_project_name(files)
            summary = parsed_codebase.get('summary', {})

            lines: List[str] = []
            # Title & description
            lines.append(f"# {project_name}\n")
            desc = parsed_codebase.get('project_description') or summary.get('description') or (
                f"Auto-generated documentation for `{project_name}`. This README was produced by a local context-aware documentation tool focused on practical usage and clear examples.")
            lines.append(desc + "\n")

            # Features / Summary
            lines.append("## Features\n")
            lines.append(f"- Languages: {', '.join(summary.get('languages', [])) or 'Python'}")
            lines.append(f"- Files: {summary.get('total_files', 0)}")
            lines.append(f"- Functions: {summary.get('total_functions', 0)}")
            lines.append(f"- Classes: {summary.get('total_classes', 0)}")
            if summary.get('key_technologies'):
                lines.append(f"- Key technologies: {', '.join(summary.get('key_technologies'))}")
            lines.append('')

            # Installation
            lines.append("## Installation\n")
            # Detect a requirements.txt or pyproject-like files in parsed files
            req_found = any(p.lower().endswith('requirements.txt') for p in files)
            pyproject_found = any(p.lower().endswith('pyproject.toml') for p in files)
            setup_found = any(p.lower().endswith('setup.py') for p in files)
            env_found = any(p.lower().endswith(('environment.yml', 'environment.yaml')) for p in files)

            if req_found:
                lines.append("Install project dependencies (from requirements.txt):\n")
                lines.append("```\npython -m pip install -r requirements.txt\n```")
            elif pyproject_found or setup_found:
                lines.append("Install in editable/development mode:\n")
                lines.append("```\npython -m pip install -e .\n```")
            elif env_found:
                lines.append("Conda environment detected, create environment:\n")
                lines.append("```\nconda env create -f environment.yml\n```")
            else:
                lines.append("No dependency manifest found. If your project has dependencies, add a `requirements.txt` or `pyproject.toml`. Example:\n")
                lines.append("```\npython -m pip install -r requirements.txt\n```")

            # System requirements and notes
            lines.append('\n### System requirements')
            lines.append('- Python 3.8+ (recommended)')
            lines.append('- Optional: GPU for model fine-tuning; not required for static docs generation')
            lines.append('')

            lines.append("\n## Usage\n")
            # Try to find an entrypoint
            entry_examples = []
            for path, fdata in parsed_codebase.get('files', {}).items():
                content = fdata.get('content', '')
                if 'if __name__' in content or re.search(r'if\s+__name__\s*==\s*["\']__main__["\']', content):
                    entry_examples.append(path)
            if entry_examples:
                lines.append("Run the main module(s):\n")
                for p in entry_examples[:3]:
                    rel = p
                    lines.append("```\npython " + rel + "\n```")
            else:
                # Provide a simple import example using detected functions
                lines.append("No runnable entrypoint detected. Typical usage example:\n")
                # Find a top-level function to demonstrate
                sample_fn = None
                sample_module = None
                for path, fdata in parsed_codebase.get('files', {}).items():
                    funcs = fdata.get('functions', [])
                    if funcs:
                        sample_fn = funcs[0].get('name')
                        sample_module = path.replace('\\\\', '/').replace('/', '.').rsplit('.py', 1)[0]
                        break
                if sample_fn and sample_module:
                    lines.append('```python')
                    lines.append(f'from {sample_module} import {sample_fn}')
                    # Build a mock call with placeholders based on signature if available
                    sig = extract_signature(funcs[0].get('text', '')) if funcs else None
                    if sig and '(' in sig:
                        # attempt to build args placeholder
                        args = sig.split('(', 1)[1].rsplit(')', 1)[0]
                        arg_names = [a.split(':')[0].strip().split('=')[0] for a in args.split(',') if a.strip() and a.split(':')[0].strip() not in ['self']]
                        call_args = ', '.join([f'<{n}>' for n in arg_names]) if arg_names else ''
                    else:
                        call_args = ''
                    lines.append(f'result = {sample_fn}({call_args})')
                    lines.append('print(result)')
                    lines.append('```')
                else:
                    lines.append("```\npython -m your_package.main\n```")

            # API Reference (concise)
            lines.append("\n## API Reference (concise)\n")
            seen_funcs = set()
            seen_classes = set()
            for path, fdata in parsed_codebase.get('files', {}).items():
                functions = fdata.get('functions', [])
                classes = fdata.get('classes', [])
                if not functions and not classes:
                    continue
                lines.append(f"### {path}\n")
                if functions:
                    lines.append("#### Functions\n")
                    for fn in functions:
                        name = fn.get('name', 'unknown')
                        if (path, 'f', name) in seen_funcs:
                            continue
                        seen_funcs.add((path, 'f', name))
                        signature = extract_signature(fn.get('text', '')) or name
                        doc = extract_docstring(fn.get('text', '')) or 'No docstring available.'
                        # Clean signature for display
                        sig_display = signature.replace('\n', ' ').strip()
                        lines.append(f"- **{name}**: `{sig_display}`  \n  - {doc}\n")
                if classes:
                    lines.append("#### Classes\n")
                    for cl in classes:
                        name = cl.get('name', 'unknown')
                        if (path, 'c', name) in seen_classes:
                            continue
                        seen_classes.add((path, 'c', name))
                        signature = extract_signature(cl.get('text', '')) or name
                        doc = extract_docstring(cl.get('text', '')) or 'No docstring available.'
                        sig_display = signature.replace('\n', ' ').strip()
                        lines.append(f"- **{name}**: `{sig_display}`  \n  - {doc}\n")

            # Troubleshooting, Contributing, License
            lines.append("\n## Troubleshooting\n")
            lines.append("- If generation fails, ensure required packages are installed and the repository is parseable.\n")
            lines.append("- Common issues:\n  - Missing dependencies: create a `requirements.txt` or `pyproject.toml`.\n  - Syntax errors in source files: fix parse errors reported in logs.\n  - Large repositories: try running on a subset or increase memory/time limits.\n")

            lines.append("## Contributing\n")
            lines.append("Contributions welcome. Please add a `CONTRIBUTING.md` with project-specific guidelines.\n")

            # Quick contribution suggestions
            lines.append("**Suggested contribution workflow:**\n")
            lines.append("1. Fork the repository\n2. Create a topic branch\n3. Add tests and documentation for changes\n4. Open a PR and describe the use-case\n")

            lines.append("## License\n")
            lines.append("This project does not contain license information in the repository scan. Add a `LICENSE` file to clarify usage.\n")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error generating markdown: {e}")
            # Fallback to original LLM prompt-based approach for last resort
            try:
                prompt = self._create_markdown_prompt(parsed_codebase, context)
                inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_new_tokens=1024,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        do_sample=self.config.do_sample,
                        pad_token_id=self.config.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
                response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
                return self._clean_markdown(response)
            except Exception as e2:
                logger.error(f"Fallback LLM generation also failed: {e2}")
                return f"# Documentation Generation Error\n\n{str(e2)}"
    
    def _create_docstring_prompt(
        self, 
        code: str, 
        language: str, 
        context: str, 
        style: str
    ) -> str:
        """Create prompt for docstring generation."""
        
        style_examples = {
            "google": '''
Example Google-style docstring:
```python
def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle.
    
    Args:
        length (float): The length of the rectangle.
        width (float): The width of the rectangle.
    
    Returns:
        float: The area of the rectangle.
    
    Raises:
        ValueError: If length or width is negative.
    """
    pass
```''',
            "numpy": '''
Example NumPy-style docstring:
```python
def calculate_area(length, width):
    """
    Calculate the area of a rectangle.
    
    Parameters
    ----------
    length : float
        The length of the rectangle.
    width : float
        The width of the rectangle.
    
    Returns
    -------
    float
        The area of the rectangle.
    """
    pass
```'''
        }
        
        context_section = f"\n\nRelevant context:\n{context}" if context else ""
        
        prompt = f"""You are an expert code documentation generator. Generate a high-quality {style}-style docstring for the following {language} code.

{style_examples.get(style, style_examples["google"])}

Code to document:
```{language}
{code}
```{context_section}

Generate only the docstring content (without code fences or explanations):"""
        
        return prompt
    
    def _create_markdown_prompt(self, parsed_codebase: Dict[str, Any], context: str) -> str:
        """Create prompt for Markdown documentation generation."""
        
        # Create summary
        summary = parsed_codebase.get('summary', {})
        total_files = summary.get('total_files', 0)
        languages = summary.get('languages', [])
        total_functions = summary.get('total_functions', 0)
        total_classes = summary.get('total_classes', 0)
        
        # Get sample files for overview
        sample_files = list(parsed_codebase.get('files', {}).keys())[:5]
        
        context_section = f"\n\nAdditional context:\n{context}" if context else ""
        
        prompt = f"""You are an expert technical writer. Generate comprehensive Markdown documentation for this codebase.

Codebase Summary:
- Total files: {total_files}
- Languages: {', '.join(languages)}
- Total functions: {total_functions}
- Total classes: {total_classes}

Sample files:
{chr(10).join(f"- {file}" for file in sample_files)}

Generate a professional README.md with the following sections:
1. Project title and description
2. Features
3. Installation
4. Usage examples
5. API documentation
6. Contributing guidelines
7. License{context_section}

Generate the complete Markdown documentation:"""
        
        return prompt
    
    def _clean_docstring(self, response: str) -> str:
        """Clean and format the generated docstring."""
        # Remove common artifacts
        response = response.strip()
        
        # Ensure proper docstring format
        if not response.startswith('"""') and not response.startswith("'''"):
            response = f'"""\n{response}\n"""'
        
        return response
    
    def _clean_markdown(self, response: str) -> str:
        """Clean and format the generated markdown."""
        return response.strip()
    
    def create_training_dataset(self, examples: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Create training dataset for fine-tuning.
        
        Args:
            examples: List of training examples with 'input' and 'output' keys
            
        Returns:
            Formatted training dataset
        """
        formatted_examples = []
        
        for example in examples:
            formatted_example = {
                "text": f"<|user|>\n{example['input']}<|end|>\n<|assistant|>\n{example['output']}<|end|>"
            }
            formatted_examples.append(formatted_example)
        
        return formatted_examples
    
    def save_model(self, output_dir: str):
        """Save the fine-tuned model."""
        try:
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)
            logger.info(f"Model saved to {output_dir}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise


# Factory function
def create_documentation_generator(
    model_name: str = "microsoft/Phi-3-mini-4k-instruct"
) -> Phi3DocumentationGenerator:
    """Create and return a configured documentation generator."""
    return Phi3DocumentationGenerator(model_name)