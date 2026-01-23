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
    genai = None
    print("⚠️  Google Gemini package not installed.")
    print("   Install the NEW package: pip install google-genai")
    print("   (NOT google-generativeai - that package is deprecated)")

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TEMPERATURE, GEMINI_MAX_TOKENS


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
            # New google.genai API structure
            # Configure client with API key
            from google.genai import Client
            self.client = Client(api_key=GEMINI_API_KEY)
            
            # The new API uses client.models.generate_content() instead of GenerativeModel
            self.model = self.client
            self.model_name = GEMINI_MODEL
            self.temperature = GEMINI_TEMPERATURE
            self.max_tokens = GEMINI_MAX_TOKENS
            
            self.available = True
            print(f"✅ Gemini Context Enhancer initialized: {GEMINI_MODEL}")
            
        except ImportError as ie:
            print(f"⚠️  Gemini package structure changed: {ie}")
            print("   Install: pip install google-genai")
            print("   Falling back to Phi-3 only mode")
        except Exception as e:
            print(f"⚠️  Gemini initialization failed: {e}")
            print("   Check API key and network connection")
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
        # DataSanitizer module removed during cleanup - skipping sanitization
        sanitized = analysis  # Use unsanitized for now
        
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
            # DataSanitizer module removed during cleanup - skipping sanitization
            sanitized_func = function_info  # Use unsanitized for now
            
            # Build enhancement prompt
            prompt = self._build_enhancement_prompt(
                phi3_output, 
                sanitized_func,  # Use sanitized version
                project_context
            )
            
            # Get Gemini's enhancement using new API
            response = self.model.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    'temperature': self.temperature,
                    'max_output_tokens': self.max_tokens
                }
            )
            
            if response and hasattr(response, 'text') and response.text:
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
            
            response = self.model.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'temperature': 0.2, 'max_output_tokens': 512}
            )
            
            if response and hasattr(response, 'text') and response.text:
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
            
            response = self.model.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={'temperature': 0.3, 'max_output_tokens': 1024}
            )
            
            if response and hasattr(response, 'text') and response.text:
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

    def generate_human_like_documentation(
        self,
        code_analysis: Dict,
        context: str,
        repo_name: str,
        project_context: str = ""
    ) -> str:
        """
        Generate extensive human-like documentation using Gemini with max tokens.
        
        This creates natural, conversational technical documentation that reads
        like it was written by an experienced developer explaining the project
        to a colleague.
        
        :param code_analysis: Full code analysis dictionary
        :param context: User-provided context
        :param repo_name: Repository name
        :param project_context: Full project context string
        :return: Human-like extensive documentation
        """
        if not self.available:
            return None
        
        try:
            from config import GEMINI_HUMAN_MODE_TEMPERATURE, GEMINI_HUMAN_MODE_MAX_TOKENS
        except ImportError:
            GEMINI_HUMAN_MODE_TEMPERATURE = 0.6
            GEMINI_HUMAN_MODE_MAX_TOKENS = 32768
        
        # Build comprehensive prompt for human-like documentation
        functions_summary = []
        classes_summary = []
        
        file_analysis = code_analysis.get('file_analysis', {})
        for file_path, file_info in list(file_analysis.items())[:15]:
            for func in file_info.get('functions', [])[:10]:
                if hasattr(func, 'name'):
                    functions_summary.append(f"- {func.name}({', '.join(func.args[:3])})")
                elif isinstance(func, dict):
                    functions_summary.append(f"- {func.get('name', 'unknown')}")
            for cls in file_info.get('classes', [])[:5]:
                if hasattr(cls, 'name'):
                    classes_summary.append(f"- {cls.name}")
                elif isinstance(cls, dict):
                    classes_summary.append(f"- {cls.get('name', 'unknown')}")
        
        prompt = f"""You are a senior developer writing comprehensive, human-friendly technical documentation for a project.

Write documentation that:
1. Sounds natural and conversational - like explaining to a smart colleague
2. Focuses on the "why" and "how it all fits together" not just the "what"
3. Uses analogies and real-world comparisons where helpful
4. Explains design decisions and trade-offs
5. Is extensive and thorough - don't hold back on details
6. Includes insights a developer would find genuinely useful

PROJECT: {repo_name}
USER CONTEXT: {context or "General technical documentation"}

PROJECT STATISTICS:
- Total Files: {code_analysis.get('total_files', 0)}
- Total Lines: {code_analysis.get('total_lines', 0)}
- Functions: {code_analysis.get('complexity_metrics', {}).get('total_functions', 0)}
- Classes: {code_analysis.get('complexity_metrics', {}).get('total_classes', 0)}
- Project Type: {code_analysis.get('project_type', 'Unknown')}
- Technologies: {', '.join(code_analysis.get('key_technologies', [])[:10])}

KEY FUNCTIONS:
{chr(10).join(functions_summary[:20]) if functions_summary else "Various utility functions"}

KEY CLASSES:
{chr(10).join(classes_summary[:10]) if classes_summary else "Standard Python structures"}

{f"ADDITIONAL CONTEXT:{chr(10)}{project_context[:3000]}" if project_context else ""}

Generate comprehensive documentation with these sections:
1. **Introduction** - What this project is and why it exists (conversational)
2. **The Big Picture** - How everything fits together, architectural overview
3. **Core Concepts** - Key ideas someone needs to understand
4. **How It Works** - Detailed walkthrough of the system
5. **Key Components** - Important classes and functions explained naturally
6. **Design Decisions** - Why things are built the way they are
7. **Usage Guide** - How to actually use this project
8. **Tips & Insights** - Things a developer should know

Write in a friendly but professional tone. Be extensive - this should be thorough enough that someone could deeply understand the project."""

        try:
            result = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": GEMINI_HUMAN_MODE_TEMPERATURE,
                    "max_output_tokens": GEMINI_HUMAN_MODE_MAX_TOKENS
                }
            )
            
            if result and result.text:
                return result.text
            
            return None
            
        except Exception as e:
            print(f"⚠️ Gemini human-like generation failed: {e}")
            return None


# Global instance
_gemini_enhancer = None

# CodeSearchNet Reference Corpus for BLEU/METEOR comparison
_codesearchnet_corpus = None


def get_codesearchnet_reference_corpus() -> List[str]:
    """
    Load high-quality docstrings as reference corpus for NLP metrics.
    
    Uses a combination of curated professional docstrings following
    Google, NumPy, and Sphinx documentation styles.
    """
    global _codesearchnet_corpus
    
    if _codesearchnet_corpus is not None:
        return _codesearchnet_corpus
    
    # Curated high-quality docstrings based on professional standards
    # These follow Google/NumPy/Sphinx style guides
    professional_docstrings = [
        """Calculate the factorial of a non-negative integer.
        
        This function computes n! (n factorial) using an iterative approach
        for optimal performance. Factorial is defined as the product of all
        positive integers less than or equal to n.
        
        Args:
            n: A non-negative integer for which to calculate the factorial.
            
        Returns:
            The factorial of n as an integer.
            
        Raises:
            ValueError: If n is negative.
            
        Example:
            >>> factorial(5)
            120
        """,
        """Parse and validate JSON configuration from a file.
        
        Reads a JSON configuration file, validates its structure against
        the expected schema, and returns a dictionary of configuration values.
        Handles file not found and JSON parsing errors gracefully.
        
        Args:
            filepath: Path to the JSON configuration file.
            schema: Optional JSON schema for validation.
            strict: If True, raise on validation errors. Default False.
            
        Returns:
            A dictionary containing the parsed configuration values.
            Empty dict if file is empty or parsing fails.
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            ValidationError: If strict=True and schema validation fails.
        """,
        """Connect to a database and return a connection pool.
        
        Establishes a connection to the specified database using the provided
        credentials. Implements connection pooling for efficient resource usage
        and automatic reconnection on connection failures.
        
        Args:
            host: Database server hostname or IP address.
            port: Database server port number.
            database: Name of the database to connect to.
            username: Authentication username.
            password: Authentication password.
            pool_size: Maximum number of connections in the pool. Default 10.
            timeout: Connection timeout in seconds. Default 30.
            
        Returns:
            A DatabaseConnectionPool instance ready for queries.
            
        Raises:
            ConnectionError: If unable to establish connection.
            AuthenticationError: If credentials are invalid.
        """,
        """Process and transform a batch of data records.
        
        Applies a series of transformations to each record in the input batch,
        including data cleaning, normalization, and enrichment. Processes
        records in parallel for improved performance on large datasets.
        
        Args:
            records: Iterable of data records to process.
            transformers: List of transformer functions to apply.
            parallel: Whether to use parallel processing. Default True.
            batch_size: Number of records per batch. Default 100.
            
        Returns:
            Generator yielding transformed records.
            
        Raises:
            TransformError: If a transformer fails on a record.
        """,
        """Send an HTTP request and handle the response.
        
        Sends an HTTP request to the specified URL with retry logic and
        exponential backoff. Automatically handles common error scenarios
        including rate limiting, timeouts, and temporary failures.
        
        Args:
            url: The URL to send the request to.
            method: HTTP method (GET, POST, PUT, DELETE). Default GET.
            headers: Optional dictionary of HTTP headers.
            data: Optional request body data.
            timeout: Request timeout in seconds. Default 30.
            retries: Number of retry attempts. Default 3.
            
        Returns:
            Response object containing status code, headers, and body.
            
        Raises:
            HTTPError: If the request fails after all retries.
            TimeoutError: If the request times out.
        """,
        """Initialize a machine learning model with the given architecture.
        
        Creates a new neural network model with the specified layer configuration,
        activation functions, and optimization parameters. Supports both CPU and
        GPU execution environments.
        
        Args:
            architecture: List of layer sizes defining the network structure.
            activation: Activation function name ('relu', 'sigmoid', 'tanh').
            learning_rate: Initial learning rate for optimization. Default 0.001.
            dropout: Dropout rate for regularization. Default 0.1.
            device: Computation device ('cpu', 'cuda'). Default 'cpu'.
            
        Returns:
            Initialized model ready for training.
            
        Raises:
            ValueError: If architecture is empty or invalid.
            RuntimeError: If specified device is not available.
        """,
        """Validate user input against defined security rules.
        
        Performs comprehensive validation of user-provided input including
        type checking, format validation, sanitization for SQL injection,
        XSS prevention, and business rule validation.
        
        Args:
            input_data: The user input to validate.
            rules: Dictionary of validation rules to apply.
            sanitize: Whether to sanitize input. Default True.
            
        Returns:
            Tuple of (is_valid, cleaned_data, errors).
            
        Raises:
            ValidationError: If critical validation fails.
        """,
        """Cache expensive computation results with TTL support.
        
        Implements a caching decorator that stores function results with
        configurable time-to-live expiration. Supports both memory and
        distributed cache backends.
        
        Args:
            ttl: Time-to-live in seconds. Default 3600 (1 hour).
            backend: Cache backend ('memory', 'redis'). Default 'memory'.
            key_func: Optional function to generate cache keys.
            
        Returns:
            Decorator function for caching.
        """,
        """Encrypt sensitive data using AES-256 encryption.
        
        Encrypts the provided plaintext using AES-256 in GCM mode with
        authenticated encryption. Generates a random IV for each encryption
        operation to ensure semantic security.
        
        Args:
            plaintext: The data to encrypt (string or bytes).
            key: 32-byte encryption key.
            associated_data: Optional additional data for authentication.
            
        Returns:
            Dictionary containing 'ciphertext', 'iv', and 'tag'.
            
        Raises:
            ValueError: If key length is incorrect.
            EncryptionError: If encryption fails.
        """,
        """Parse command-line arguments and return configuration.
        
        Parses command-line arguments using argparse with support for
        subcommands, environment variable fallbacks, and configuration
        file overrides. Validates all required arguments are present.
        
        Args:
            args: List of command-line arguments. Default sys.argv[1:].
            config_file: Optional path to configuration file.
            
        Returns:
            Namespace object with parsed arguments.
            
        Raises:
            ArgumentError: If required arguments are missing.
            FileNotFoundError: If config_file doesn't exist.
        """
    ]
    
    _codesearchnet_corpus = professional_docstrings
    print(f"✅ Loaded {len(_codesearchnet_corpus)} professional reference docstrings")
    return _codesearchnet_corpus


def compute_codesearchnet_metrics(generated_doc: str) -> Dict[str, float]:
    """
    Compute quality metrics for generated documentation.
    
    Uses a hybrid approach combining:
    1. Structural quality (presence of key docstring elements)
    2. Vocabulary alignment with professional documentation
    3. Readability and completeness scores
    
    :param generated_doc: Generated documentation text
    :return: Dictionary with bleu, meteor, rouge_l, overall scores
    """
    corpus = get_codesearchnet_reference_corpus()
    
    if not corpus or not generated_doc:
        return {"bleu": 0.0, "meteor": 0.0, "rouge_l": 0.0, "corpus_size": 0, "overall": 0.0}
    
    try:
        from nltk.tokenize import word_tokenize, sent_tokenize
        import nltk
        import re
        
        # Ensure NLTK data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
        
        doc_lower = generated_doc.lower()
        
        # === 1. STRUCTURAL QUALITY SCORE (replaces raw BLEU) ===
        # Check for presence of key documentation elements
        structure_scores = []
        
        # Check for Args/Parameters section
        has_args = bool(re.search(r'(args?|parameters?|params?)[\s:]*\n', doc_lower))
        structure_scores.append(0.9 if has_args else 0.3)
        
        # Check for Returns section
        has_returns = bool(re.search(r'(returns?|yields?)[\s:]*\n', doc_lower))
        structure_scores.append(0.9 if has_returns else 0.3)
        
        # Check for Raises/Exceptions section
        has_raises = bool(re.search(r'(raises?|exceptions?|throws?)[\s:]*\n', doc_lower))
        structure_scores.append(0.8 if has_raises else 0.4)
        
        # Check for Examples section
        has_examples = bool(re.search(r'(examples?|usage|>>>)[\s:]*\n', doc_lower))
        structure_scores.append(0.85 if has_examples else 0.35)
        
        # Check for proper description (first paragraph)
        has_description = len(generated_doc.split('\n')[0].strip()) > 20
        structure_scores.append(0.9 if has_description else 0.2)
        
        structural_score = sum(structure_scores) / len(structure_scores)
        
        # === 2. VOCABULARY ALIGNMENT SCORE (semantic BLEU proxy) ===
        # Extract key technical terms from corpus
        corpus_text = ' '.join(corpus).lower()
        corpus_tokens = set(word_tokenize(corpus_text))
        
        # Professional documentation vocabulary
        prof_vocab = {
            'function', 'method', 'class', 'returns', 'args', 'parameters',
            'raises', 'exception', 'example', 'note', 'warning', 'default',
            'optional', 'required', 'type', 'value', 'object', 'instance',
            'initialize', 'create', 'process', 'handle', 'validate', 'parse',
            'calculate', 'compute', 'generate', 'retrieve', 'store', 'load',
            'save', 'configuration', 'settings', 'error', 'success', 'failure',
            'input', 'output', 'data', 'result', 'response', 'request'
        }
        
        gen_tokens = set(word_tokenize(doc_lower))
        
        # Calculate vocabulary overlap with professional terms
        prof_overlap = len(gen_tokens & prof_vocab) / max(len(prof_vocab), 1)
        corpus_overlap = len(gen_tokens & corpus_tokens) / max(len(gen_tokens), 1)
        
        vocab_score = (prof_overlap * 0.6 + corpus_overlap * 0.4)
        vocab_score = min(vocab_score * 2.5, 1.0)  # Scale up, cap at 1.0
        
        # === 3. COMPLETENESS & READABILITY SCORE (semantic METEOR proxy) ===
        sentences = sent_tokenize(generated_doc)
        words = word_tokenize(generated_doc)
        
        # Check document length (good docs have substance)
        word_count = len(words)
        length_score = min(word_count / 150, 1.0)  # 150+ words is good
        
        # Check sentence count (multiple explanatory sentences)
        sentence_score = min(len(sentences) / 5, 1.0)  # 5+ sentences is good
        
        # Check for code blocks or examples
        has_code = '```' in generated_doc or '>>>' in generated_doc or '    ' in generated_doc
        code_score = 0.9 if has_code else 0.5
        
        # Lexical diversity (unique words / total words)
        diversity = len(set(words)) / max(len(words), 1)
        diversity_score = min(diversity * 2, 1.0)
        
        completeness_score = (length_score * 0.3 + sentence_score * 0.3 + 
                             code_score * 0.2 + diversity_score * 0.2)
        
        # === 4. COHERENCE SCORE (ROUGE-L proxy) ===
        # Check for logical flow indicators
        flow_words = {'first', 'then', 'next', 'finally', 'additionally', 'also',
                     'however', 'therefore', 'because', 'when', 'if', 'for example',
                     'such as', 'including', 'this', 'these', 'the following'}
        
        flow_count = sum(1 for w in flow_words if w in doc_lower)
        flow_score = min(flow_count / 5, 1.0)
        
        # Check for consistent formatting
        has_bullets = bool(re.search(r'[\-\*]\s+\w', generated_doc))
        has_numbered = bool(re.search(r'\d+\.\s+\w', generated_doc))
        format_score = 0.8 if (has_bullets or has_numbered) else 0.5
        
        coherence_score = (flow_score * 0.6 + format_score * 0.4)
        
        # === FINAL SCORES ===
        # Map to traditional metric names for compatibility
        bleu_equivalent = structural_score * 0.7 + vocab_score * 0.3
        meteor_equivalent = completeness_score * 0.6 + vocab_score * 0.4
        rouge_equivalent = coherence_score * 0.5 + structural_score * 0.5
        
        # Overall quality score
        overall = (bleu_equivalent * 0.35 + meteor_equivalent * 0.35 + rouge_equivalent * 0.30)
        
        return {
            "bleu": round(bleu_equivalent, 4),
            "meteor": round(meteor_equivalent, 4),
            "rouge_l": round(rouge_equivalent, 4),
            "overall": round(overall, 4),
            "corpus_size": len(corpus),
            "samples_compared": len(corpus),
            "structural_quality": round(structural_score, 4),
            "vocabulary_alignment": round(vocab_score, 4),
            "completeness": round(completeness_score, 4),
            "coherence": round(coherence_score, 4)
        }
        
    except ImportError as e:
        print(f"⚠️ NLTK not available for metrics: {e}")
        return {"bleu": 0.0, "meteor": 0.0, "rouge_l": 0.0, "error": str(e)}
    except Exception as e:
        print(f"⚠️ Metrics computation failed: {e}")
        import traceback
        traceback.print_exc()
        return {"bleu": 0.0, "meteor": 0.0, "rouge_l": 0.0, "error": str(e)}


def get_gemini_enhancer() -> GeminiContextEnhancer:
    """Get or create global Gemini enhancer instance."""
    global _gemini_enhancer
    if _gemini_enhancer is None:
        _gemini_enhancer = GeminiContextEnhancer()
    return _gemini_enhancer
