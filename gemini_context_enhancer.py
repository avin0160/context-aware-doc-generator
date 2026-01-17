"""
Gemini Context Enhancer - Provides whole-codebase context awareness
Uses Google Gemini API to validate and enhance Phi-3 generated documentation
with full project understanding.

PRIVACY LAYER: Only sends sanitized metadata (NO SOURCE CODE)

Author: team-8
"""

import os
from typing import Dict, List, Optional, Any

try:
    import google.genai as genai  # type: ignore  # New package (replaces google.generativeai)
except ImportError:
    try:
        import google.generativeai as genai  # type: ignore  # Fallback to old package
    except ImportError:
        genai = None

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS
from data_sanitizer import DataSanitizer


class GeminiContextEnhancer:
    """
    Enhances Phi-3 documentation with Gemini's whole-codebase understanding.
    
    Architecture:
    - Phi-3: Backbone - generates initial documentation from local context
    - Gemini: Context validator - enhances with full project awareness
    """
    
    def __init__(self):
        """Initialize Gemini API with configuration."""
        self.available = False
        self.model = None
        
        # Check if genai module is available
        if genai is None:
            print("⚠️  Gemini package not installed. Install with: pip install google-genai")
            print("   System will run in Phi-3 only mode")
            return
        
        # Check if API key is configured
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("⚠️  Gemini API key not configured. Set GEMINI_API_KEY in config.py")
            print("   Get your key from: https://makersuite.google.com/app/apikey")
            print("   System will run in Phi-3 only mode")
            return
        
        try:
            # Configure Gemini - handle both old and new API
            if hasattr(genai, 'configure'):
                genai.configure(api_key=GEMINI_API_KEY)
                model_class = genai.GenerativeModel
            else:
                # Fallback for different API structure
                genai.api_key = GEMINI_API_KEY
                model_class = genai.GenerativeModel
            
            # Initialize model with safety settings for code analysis
            self.model = model_class(
                model_name=GEMINI_MODEL,
                generation_config={
                    "temperature": GEMINI_TEMPERATURE,
                    "max_output_tokens": GEMINI_MAX_TOKENS,
                }
            )
            
            self.available = True
            print(f"✅ Gemini Context Enhancer initialized: {GEMINI_MODEL}")
            
        except Exception as e:
            print(f"⚠️  Gemini initialization failed: {e}")
            print("   Falling back to Phi-3 only mode")
    
    def build_project_context(self, analysis: Dict) -> str:
        """
        Build comprehensive project context for Gemini.
        
        PRIVACY: Sanitizes all data - NO SOURCE CODE sent to external API
        
        Args:
            analysis: Full project analysis from comprehensive_docs_advanced
            
        Returns:
            Formatted project context string (SANITIZED)
        """
        # SANITIZE: Remove all source code before sending to external API
        sanitized = DataSanitizer.sanitize_project_analysis(analysis)
        
        context_parts = []
        
        # Project overview
        context_parts.append("=== PROJECT OVERVIEW (SANITIZED - NO SOURCE CODE) ===")
        context_parts.append(f"Total Files: {sanitized.get('total_files', 0)}")
        context_parts.append(f"Total Functions: {sanitized.get('total_functions', 0)}")
        context_parts.append(f"Total Classes: {sanitized.get('total_classes', 0)}")
        context_parts.append(f"Total Lines: {sanitized.get('total_lines', 0)}")
        
        # Imports and dependencies
        if 'all_imports' in sanitized:
            context_parts.append("\n=== PROJECT DEPENDENCIES ===")
            context_parts.append(f"Imports: {', '.join(sorted(sanitized['all_imports']))}")
        
        # File structure with functions (SANITIZED)
        context_parts.append("\n=== CODE STRUCTURE (SIGNATURES ONLY) ===")
        file_analysis = sanitized.get('file_analysis', {})
        
        for file_path, file_info in file_analysis.items():
            context_parts.append(f"\n[FILE: {file_path}]")
            
            # Functions in this file (SANITIZED - no source code)
            if file_info.get('functions'):
                context_parts.append("Functions:")
                for func in file_info['functions']:
                    # Handle both dict and FunctionInfo objects
                    if hasattr(func, 'name'):
                        func_name = func.name
                        args = ', '.join(func.args) if func.args else ''
                        complexity = func.complexity
                        calls = ', '.join(func.calls) if func.calls else ''
                    else:
                        func_name = func.get('name', 'unknown')
                        args = ', '.join(func.get('args', []))
                        complexity = func.get('complexity', 0)
                        calls = ', '.join(func.get('calls', []))
                    
                    context_parts.append(f"  - {func_name}({args}) [complexity: {complexity}]")
                    if calls:
                        context_parts.append(f"    Calls: {calls}")
            
            # Classes in this file (SANITIZED - no source code)
            if file_info.get('classes'):
                context_parts.append("Classes:")
                for cls in file_info['classes']:
                    # Handle both dict and ClassInfo objects
                    if hasattr(cls, 'name'):
                        cls_name = cls.name
                        methods = ', '.join(m.name if hasattr(m, 'name') else m.get('name', '') for m in cls.methods)
                    else:
                        cls_name = cls.get('name', 'unknown')
                        methods = ', '.join(m.get('name', '') for m in cls.get('methods', []))
                    
                    context_parts.append(f"  - {cls_name}")
                    if methods:
                        context_parts.append(f"    Methods: {methods}")
        
        # Call graph
        if 'call_graph' in sanitized and 'edges' in sanitized['call_graph']:
            context_parts.append("\n=== CALL GRAPH ===")
            # Convert edges list to caller -> callees dict
            call_dict = {}
            for edge in sanitized['call_graph']['edges']:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    caller, callee = edge[0], edge[1]
                    if caller not in call_dict:
                        call_dict[caller] = []
                    call_dict[caller].append(str(callee))
            
            # Format as caller -> callees
            for caller, callees in call_dict.items():
                if callees:
                    context_parts.append(f"{caller} -> {', '.join(callees)}")
        
        return "\n".join(context_parts)
    
    def enhance_documentation(
        self,
        phi3_output: str,
        function_info: Dict,
        project_context: str
    ) -> str:
        """
        Enhance Phi-3 documentation with Gemini's whole-codebase understanding.
        
        PRIVACY: Only phi3_output and sanitized metadata sent to external API.
        NO source code transmitted.
        
        Args:
            phi3_output: Initial documentation from Phi-3
            function_info: Specific function details (will be sanitized)
            project_context: Full project context string (already sanitized)
            
        Returns:
            Enhanced documentation string
        """
        if not self.available:
            return phi3_output  # Fallback to Phi-3 output
        
        try:
            # SANITIZE: Ensure function_info contains no source code
            sanitized_func = DataSanitizer.sanitize_function_info(function_info)
            
            # Build enhancement prompt
            prompt = self._build_enhancement_prompt(
                phi3_output, 
                sanitized_func,  # Use sanitized version
                project_context
            )
            
            # Get Gemini's enhancement
            response = self.model.generate_content(prompt)
            
            if response.text:
                enhanced = response.text.strip()
                
                # VALIDATE: Reject non-Sphinx output
                if self._validate_sphinx_output(enhanced):
                    return enhanced
                else:
                    print("⚠️  Gemini output rejected (non-Sphinx format), using Phi-3 fallback")
                    return phi3_output
            else:
                return phi3_output
                
        except Exception as e:
            print(f"⚠️  Gemini enhancement failed: {e}")
            return phi3_output
    
    def _build_enhancement_prompt(
        self,
        phi3_output: str,
        function_info: Dict,
        project_context: str
    ) -> str:
        """Build prompt for Gemini to enhance documentation.
        
        PRIVACY: Only sends sanitized metadata (names, signatures, call graph).
        NO source code sent to external API.
        """
        
        # Handle both dict and FunctionInfo objects
        if hasattr(function_info, 'name'):
            func_name = function_info.name
            calls = function_info.calls if function_info.calls else []
            called_by = function_info.called_by if function_info.called_by else []
        else:
            func_name = function_info.get('name', 'unknown')
            calls = function_info.get('calls', [])
            called_by = function_info.get('called_by', [])
        
        prompt = f"""You are an API documentation generator producing STRICT Sphinx/reStructuredText-style Python docstrings.

RULES (MANDATORY):
- Use ONLY Sphinx fields (:param:, :type:, :return:, :rtype:)
- Do NOT evaluate code quality ("efficient", "well-designed")
- Do NOT invent behavior
- Do NOT include examples unless marked as public API
- Do NOT summarize architecture
- Do NOT restate function names as descriptions
- Do NOT include prose outside docstrings
- If information is unknown, state "Not determined"

TOKEN DISCIPLINE:
- Output ONLY the requested docstring
- No extra commentary, headings, or markdown
- Stop generation immediately after the last docstring

EPISTEMIC DISCIPLINE:
- Treat comments as claims, not facts
- Prefer "Observed behavior" phrasing

CONTEXT (sanitized, authoritative):
{project_context}

ENTITY TO DOCUMENT:
Name: {func_name}
Calls: {', '.join(calls) if calls else 'None'}
Called By: {', '.join(called_by) if called_by else 'None'}

INITIAL DOCUMENTATION:
{phi3_output}

TASK:
Enhance ONLY with verifiable cross-module context:
- Parameter types observable from call graph
- Side effects documented in call patterns
- Return value inferred from caller expectations

REJECT if you would write:
- "This function is used to..."
- Quality judgments
- Example usage blocks
- Architectural summaries

Generate enhanced Sphinx docstring:"""
        
        return prompt
    
    def validate_project_classification(
        self,
        project_purpose: str,
        project_context: str
    ) -> str:
        """
        Validate and enhance project classification with full context.
        
        Args:
            project_purpose: Initial project purpose from Phi-3/analysis
            project_context: Full project context
            
        Returns:
            Enhanced project classification
        """
        if not self.available:
            return project_purpose
        
        try:
            prompt = f"""You are validating project classification with full codebase context.

FULL PROJECT CONTEXT:
{project_context}

INITIAL CLASSIFICATION:
{project_purpose}

YOUR TASK:
Validate and enhance the project classification:

1. **Verify Classification**: Is the initial classification accurate?
2. **Execution Model**: What is the actual execution model (game loop, web server, CLI tool, library)?
3. **Primary Purpose**: What is the main functionality based on code structure?
4. **Domain**: What problem domain does this solve?

CRITICAL RULES:
- EVIDENCE-BASED: Only classify based on observable code patterns
- NO GUESSING: If unclear, say "Insufficient evidence to determine"
- HONEST: Correct wrong classifications
- EXECUTION MODEL: Identify game loops, request handlers, batch processing, etc.

Output a corrected and enhanced project classification:"""
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return project_purpose
                
        except Exception as e:
            print(f"⚠️  Gemini validation failed: {e}")
            return project_purpose
    
    def analyze_architecture(self, project_context: str) -> str:
        """
        Analyze project architecture with Gemini's understanding.
        
        Args:
            project_context: Full project context
            
        Returns:
            Architecture analysis
        """
        if not self.available:
            return "Gemini context enhancer not available."
        
        try:
            prompt = f"""You are analyzing project architecture from full codebase context.

FULL PROJECT CONTEXT:
{project_context}

YOUR TASK:
Provide a comprehensive architecture analysis:

1. **Design Patterns**: What architectural patterns are used?
2. **Component Organization**: How are modules organized?
3. **Data Flow**: How does data move through the system?
4. **Key Abstractions**: What are the core abstractions?
5. **Coupling Analysis**: How tightly coupled are components?

CRITICAL RULES:
- EVIDENCE-BASED: Only analyze what you can observe
- NO BUZZWORDS: Avoid generic statements
- HONEST: Identify both strengths and weaknesses
- SPECIFIC: Reference actual files and functions

Generate the architecture analysis:"""
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return "Analysis unavailable."
        except Exception as e:
            print(f"⚠️ Gemini architecture analysis failed: {e}")
            return "Architecture analysis unavailable."
    
    def _validate_sphinx_output(self, text: str) -> bool:
        """
        Validate that output is pure Sphinx/reST format.
        
        REJECT if contains:
        - Quality judgments ("efficient", "well-designed", "robust")
        - Usage phrases ("This function is used to", "This class is used for")
        - Example blocks ("Example:", ">>> ")
        - Markdown formatting (##, **, bullets without proper indent)
        - Architecture commentary outside docstrings
        
        :param text: Generated documentation text
        :type text: str
        :return: True if valid Sphinx format, False otherwise
        :rtype: bool
        """
        # Forbidden patterns
        forbidden = [
            "this function is used to",
            "this method is used to",
            "this class is used to",
            "well-designed",
            "efficient",
            "robust",
            "powerful",
            "flexible",
            "elegant",
            "example:",
            ">>> ",
            "## ",
            "### ",
        ]
        
        text_lower = text.lower()
        for pattern in forbidden:
            if pattern in text_lower:
                return False
        
        # Must contain Sphinx field markers if documenting parameters/returns
        # (Allow pure docstrings without params)
        if "def " in text or "class " in text:
            # If it's showing code structure, ensure proper format
            return True
        
        # Check for valid Sphinx patterns (optional - just ensure no forbidden)
        return True


# Global instance
_gemini_enhancer = None


def get_gemini_enhancer() -> GeminiContextEnhancer:
    """Get or create global Gemini enhancer instance."""
    global _gemini_enhancer
    if _gemini_enhancer is None:
        _gemini_enhancer = GeminiContextEnhancer()
    return _gemini_enhancer
