"""
Real Documentation Quality Metrics

These metrics measure actual documentation quality without requiring reference comparison.
Based on research from CodeSearchNet, CodeBERT papers, and industry best practices.

Metrics Categories:
1. Coverage Metrics - What percentage of code elements are documented
2. Completeness Metrics - Are all required documentation sections present  
3. Quality Metrics - Is the documentation actually useful (non-trivial, specific)
4. Readability Metrics - Standard readability scores (Flesch-Kincaid, etc.)
5. Consistency Metrics - Is the documentation style consistent
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter


@dataclass
class CoverageMetrics:
    """Coverage-based metrics - objective and measurable"""
    total_functions: int
    documented_functions: int
    total_classes: int
    documented_classes: int
    total_parameters: int
    documented_parameters: int
    total_return_types: int
    documented_return_types: int
    
    @property
    def function_coverage(self) -> float:
        return self.documented_functions / max(self.total_functions, 1)
    
    @property
    def class_coverage(self) -> float:
        return self.documented_classes / max(self.total_classes, 1)
    
    @property
    def parameter_coverage(self) -> float:
        return self.documented_parameters / max(self.total_parameters, 1)
    
    @property
    def return_type_coverage(self) -> float:
        return self.documented_return_types / max(self.total_return_types, 1)
    
    @property
    def overall_coverage(self) -> float:
        """Weighted average of all coverage metrics"""
        return (
            self.function_coverage * 0.4 +
            self.class_coverage * 0.2 +
            self.parameter_coverage * 0.25 +
            self.return_type_coverage * 0.15
        )


@dataclass
class CompletenessMetrics:
    """Completeness metrics - are required sections present"""
    has_module_docstring: bool
    has_description: bool
    has_parameters_section: bool
    has_returns_section: bool
    has_examples: bool
    has_raises_section: bool
    has_type_hints: bool
    has_usage_notes: bool
    
    @property
    def completeness_score(self) -> float:
        """Score based on presence of documentation sections"""
        weights = {
            'has_description': 0.25,
            'has_parameters_section': 0.20,
            'has_returns_section': 0.15,
            'has_examples': 0.15,
            'has_type_hints': 0.10,
            'has_raises_section': 0.05,
            'has_usage_notes': 0.05,
            'has_module_docstring': 0.05,
        }
        
        score = 0.0
        for field, weight in weights.items():
            if getattr(self, field):
                score += weight
        return score


@dataclass
class ReadabilityMetrics:
    """Standard readability metrics"""
    flesch_reading_ease: float  # 0-100, higher = easier
    flesch_kincaid_grade: float  # US grade level
    automated_readability_index: float
    avg_sentence_length: float
    avg_word_length: float
    technical_term_density: float  # % of technical terms
    
    @property
    def readability_score(self) -> float:
        """Normalized readability score (0-1)"""
        # Flesch Reading Ease: 60-70 is ideal for technical docs
        if 50 <= self.flesch_reading_ease <= 70:
            fre_score = 1.0
        elif 40 <= self.flesch_reading_ease < 50:
            fre_score = 0.8
        elif 70 < self.flesch_reading_ease <= 80:
            fre_score = 0.9
        else:
            fre_score = max(0, min(1, self.flesch_reading_ease / 100))
        
        # Flesch-Kincaid Grade: 8-12 is ideal for technical docs
        if 8 <= self.flesch_kincaid_grade <= 12:
            fkg_score = 1.0
        elif 6 <= self.flesch_kincaid_grade < 8:
            fkg_score = 0.8
        elif 12 < self.flesch_kincaid_grade <= 14:
            fkg_score = 0.85
        else:
            fkg_score = max(0, 1 - abs(self.flesch_kincaid_grade - 10) / 10)
        
        return (fre_score * 0.5 + fkg_score * 0.5)


@dataclass 
class QualityMetrics:
    """Quality heuristics - is the documentation actually useful"""
    non_trivial_descriptions: float  # % that aren't just repeating function name
    specific_type_annotations: float  # % using specific types vs 'Any'
    concrete_examples: float  # % of examples that are runnable
    param_descriptions_quality: float  # Are param descriptions informative
    consistent_style: float  # Style consistency across docs
    
    @property
    def quality_score(self) -> float:
        return (
            self.non_trivial_descriptions * 0.30 +
            self.specific_type_annotations * 0.20 +
            self.concrete_examples * 0.20 +
            self.param_descriptions_quality * 0.15 +
            self.consistent_style * 0.15
        )


class DocumentationQualityEvaluator:
    """
    Evaluate documentation quality using real, meaningful metrics.
    
    Unlike BLEU/ROUGE which require reference comparison, these metrics
    evaluate the documentation on its own merits.
    """
    
    # Technical terms commonly found in good documentation
    TECHNICAL_TERMS = {
        'function', 'method', 'class', 'module', 'parameter', 'argument',
        'return', 'returns', 'raises', 'exception', 'error', 'type', 'int',
        'str', 'list', 'dict', 'bool', 'float', 'none', 'true', 'false',
        'optional', 'required', 'default', 'example', 'usage', 'note',
        'warning', 'deprecated', 'see', 'also', 'reference', 'api',
        'object', 'instance', 'attribute', 'property', 'value', 'key',
        'index', 'iterator', 'generator', 'async', 'await', 'callback',
        'handler', 'listener', 'event', 'request', 'response', 'data',
        'input', 'output', 'result', 'configuration', 'settings', 'options'
    }
    
    # Generic/vague terms that indicate low quality
    VAGUE_TERMS = {
        'stuff', 'thing', 'do', 'does', 'something', 'somehow',
        'various', 'misc', 'miscellaneous', 'etc', 'other'
    }
    
    # Tautological patterns (description just repeats name)
    TAUTOLOGY_PATTERNS = [
        r'(\w+)\s+(?:that\s+)?(?:is\s+)?(?:a\s+)?(?:the\s+)?\1',
        r'(?:this|the)\s+(\w+)\s+(?:method|function|class)',
        r'(\w+)\s+for\s+\1ing'
    ]
    
    def __init__(self):
        self.results = {}
    
    def evaluate_documentation(self, 
                               documentation: str, 
                               code_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive documentation quality evaluation.
        
        Args:
            documentation: The generated documentation text
            code_analysis: Optional dict with function_count, class_count, etc.
            
        Returns:
            Dictionary with all metrics and overall score
        """
        # Calculate all metrics
        coverage = self._calculate_coverage(documentation, code_analysis)
        completeness = self._calculate_completeness(documentation)
        readability = self._calculate_readability(documentation)
        quality = self._calculate_quality(documentation)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            coverage, completeness, readability, quality
        )
        
        return {
            'coverage': {
                'function_coverage': coverage.function_coverage,
                'class_coverage': coverage.class_coverage,
                'parameter_coverage': coverage.parameter_coverage,
                'return_type_coverage': coverage.return_type_coverage,
                'overall': coverage.overall_coverage,
                'details': {
                    'total_functions': coverage.total_functions,
                    'documented_functions': coverage.documented_functions,
                    'total_classes': coverage.total_classes,
                    'documented_classes': coverage.documented_classes,
                }
            },
            'completeness': {
                'score': completeness.completeness_score,
                'has_description': completeness.has_description,
                'has_parameters': completeness.has_parameters_section,
                'has_returns': completeness.has_returns_section,
                'has_examples': completeness.has_examples,
                'has_type_hints': completeness.has_type_hints,
            },
            'readability': {
                'score': readability.readability_score,
                'flesch_reading_ease': readability.flesch_reading_ease,
                'flesch_kincaid_grade': readability.flesch_kincaid_grade,
                'avg_sentence_length': readability.avg_sentence_length,
                'technical_term_density': readability.technical_term_density,
            },
            'quality': {
                'score': quality.quality_score,
                'non_trivial_descriptions': quality.non_trivial_descriptions,
                'specific_types': quality.specific_type_annotations,
                'concrete_examples': quality.concrete_examples,
                'consistent_style': quality.consistent_style,
            },
            'overall_score': overall_score,
            'grade': self._score_to_grade(overall_score),
            'validity': 'valid' if (code_analysis is None or 
                                   code_analysis.get('function_count', 1) > 0 or
                                   code_analysis.get('class_count', 1) > 0) else 'invalid'
        }
    
    def _calculate_coverage(self, doc: str, code_analysis: Dict = None) -> CoverageMetrics:
        """Calculate documentation coverage metrics"""
        
        # Extract counts from code analysis if provided
        if code_analysis:
            total_functions = code_analysis.get('function_count', 0)
            total_classes = code_analysis.get('class_count', 0)
            total_parameters = code_analysis.get('parameter_count', 0)
        else:
            # Estimate from documentation
            total_functions = len(re.findall(r'(?:def|function|method)\s+\w+', doc, re.I))
            total_classes = len(re.findall(r'(?:class)\s+\w+', doc, re.I))
            total_parameters = len(re.findall(r':param\s+\w+|@param\s+\w+|Args:\s*\n(?:\s+\w+)', doc, re.I))
        
        # Count documented items
        documented_functions = len(re.findall(
            r'(?:def|function|method|##?\s*(?:Function|Method))\s+\w+.*?(?:description|:|\n\s+[A-Z])',
            doc, re.I | re.DOTALL
        ))
        
        documented_classes = len(re.findall(
            r'(?:class|##?\s*Class)\s+\w+.*?(?:description|:|\n\s+[A-Z])',
            doc, re.I | re.DOTALL
        ))
        
        documented_parameters = len(re.findall(
            r':param\s+\w+:|@param\s+\w+|Args:\s*\n\s+\w+:',
            doc, re.I
        ))
        
        documented_return_types = len(re.findall(
            r':returns?:|:rtype:|@returns?|Returns:\s*\n',
            doc, re.I
        ))
        
        return CoverageMetrics(
            total_functions=max(total_functions, 1),
            documented_functions=min(documented_functions, total_functions) if total_functions > 0 else documented_functions,
            total_classes=max(total_classes, 1),
            documented_classes=min(documented_classes, total_classes) if total_classes > 0 else documented_classes,
            total_parameters=max(total_parameters, 1),
            documented_parameters=documented_parameters,
            total_return_types=max(total_functions, 1),
            documented_return_types=documented_return_types
        )
    
    def _calculate_completeness(self, doc: str) -> CompletenessMetrics:
        """Calculate documentation completeness metrics"""
        doc_lower = doc.lower()
        
        return CompletenessMetrics(
            has_module_docstring=bool(re.search(r'^""".*?"""', doc, re.DOTALL) or 
                                     re.search(r'^#.*?module|overview|description', doc_lower, re.MULTILINE)),
            has_description=bool(re.search(r'description|overview|summary|purpose|what\s+(?:this|it)\s+does', doc_lower)),
            has_parameters_section=bool(re.search(r'args?:|parameters?:|:param\s|@param\s', doc_lower)),
            has_returns_section=bool(re.search(r'returns?:|:returns?|@returns?|yields?:', doc_lower)),
            has_examples=bool(re.search(r'examples?:|usage:|>>>|```(?:python|py)|sample', doc_lower)),
            has_raises_section=bool(re.search(r'raises?:|exceptions?:|:raises|@throws', doc_lower)),
            has_type_hints=bool(re.search(r':type\s|:\s*\w+\[|->|:\s*(?:int|str|float|bool|list|dict|any)', doc_lower)),
            has_usage_notes=bool(re.search(r'notes?:|warnings?:|important:|tips?:|see\s+also', doc_lower))
        )
    
    def _calculate_readability(self, doc: str) -> ReadabilityMetrics:
        """Calculate readability metrics using standard formulas"""
        
        # Clean text for analysis
        clean_text = re.sub(r'```.*?```', '', doc, flags=re.DOTALL)  # Remove code blocks
        clean_text = re.sub(r'`[^`]+`', '', clean_text)  # Remove inline code
        clean_text = re.sub(r'[#*_\[\]]', '', clean_text)  # Remove markdown
        
        # Count sentences, words, syllables
        sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if s.strip() and len(s.split()) > 2]
        words = re.findall(r'\b[a-zA-Z]+\b', clean_text)
        
        num_sentences = max(len(sentences), 1)
        num_words = max(len(words), 1)
        num_syllables = sum(self._count_syllables(w) for w in words)
        
        # Flesch Reading Ease
        # Formula: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        avg_sentence_len = num_words / num_sentences
        avg_syllables_per_word = num_syllables / num_words
        
        flesch_reading_ease = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables_per_word)
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))
        
        # Flesch-Kincaid Grade Level
        # Formula: 0.39*(words/sentences) + 11.8*(syllables/words) - 15.59
        flesch_kincaid_grade = (0.39 * avg_sentence_len) + (11.8 * avg_syllables_per_word) - 15.59
        flesch_kincaid_grade = max(0, flesch_kincaid_grade)
        
        # Automated Readability Index
        # Formula: 4.71*(chars/words) + 0.5*(words/sentences) - 21.43
        num_chars = sum(len(w) for w in words)
        avg_word_len = num_chars / num_words
        ari = (4.71 * avg_word_len) + (0.5 * avg_sentence_len) - 21.43
        ari = max(0, ari)
        
        # Technical term density
        words_lower = [w.lower() for w in words]
        technical_count = sum(1 for w in words_lower if w in self.TECHNICAL_TERMS)
        technical_density = technical_count / num_words
        
        return ReadabilityMetrics(
            flesch_reading_ease=round(flesch_reading_ease, 1),
            flesch_kincaid_grade=round(flesch_kincaid_grade, 1),
            automated_readability_index=round(ari, 1),
            avg_sentence_length=round(avg_sentence_len, 1),
            avg_word_length=round(avg_word_len, 1),
            technical_term_density=round(technical_density, 3)
        )
    
    def _calculate_quality(self, doc: str) -> QualityMetrics:
        """Calculate documentation quality heuristics"""
        
        # Non-trivial descriptions: Check if descriptions aren't just repeating names
        descriptions = re.findall(r'(?:def|function|method|class)\s+(\w+).*?(?:"""|\'\'\')(.+?)(?:"""|\'\'\')|\s+(\w+):\s*(.+?)(?:\n|$)', doc, re.DOTALL | re.I)
        
        non_trivial_count = 0
        total_descriptions = 0
        
        for match in descriptions:
            name = match[0] or match[2]
            desc = match[1] or match[3]
            if name and desc:
                total_descriptions += 1
                # Check if description is more than just the name
                desc_words = set(re.findall(r'\w+', desc.lower()))
                name_words = set(re.findall(r'\w+', self._split_camel_case(name).lower()))
                
                # If description has words beyond the name words, it's non-trivial
                if len(desc_words - name_words - {'the', 'a', 'an', 'is', 'are', 'this', 'that'}) >= 3:
                    non_trivial_count += 1
        
        non_trivial_ratio = non_trivial_count / max(total_descriptions, 1)
        
        # Specific type annotations (not just 'Any' or 'object')
        type_annotations = re.findall(r':type\s+\w+:\s*(\w+)|:\s*(\w+(?:\[[\w,\s]+\])?)\s*[,)]|->?\s*(\w+)', doc)
        generic_types = {'any', 'object', 'type', 'auto'}
        
        specific_count = 0
        total_types = 0
        for match in type_annotations:
            type_str = (match[0] or match[1] or match[2]).lower()
            if type_str:
                total_types += 1
                if type_str not in generic_types:
                    specific_count += 1
        
        specific_types_ratio = specific_count / max(total_types, 1)
        
        # Concrete examples (check for actual code examples)
        examples = re.findall(r'```.*?```|>>>.*?(?:\n(?!>>>)|\Z)', doc, re.DOTALL)
        concrete_examples = sum(1 for ex in examples if len(ex) > 20 and ('(' in ex or '=' in ex))
        example_ratio = concrete_examples / max(len(examples), 1) if examples else 0.5
        
        # Consistent style (check for formatting consistency)
        param_styles = {
            'sphinx': len(re.findall(r':param\s+\w+:', doc)),
            'google': len(re.findall(r'Args:\s*\n', doc)),
            'numpy': len(re.findall(r'Parameters\s*\n-+', doc)),
        }
        dominant_style = max(param_styles.values()) if param_styles else 0
        total_style = sum(param_styles.values())
        style_consistency = dominant_style / max(total_style, 1) if total_style > 0 else 0.7
        
        return QualityMetrics(
            non_trivial_descriptions=round(non_trivial_ratio, 3),
            specific_type_annotations=round(specific_types_ratio, 3),
            concrete_examples=round(example_ratio, 3),
            param_descriptions_quality=round(non_trivial_ratio * 0.8 + specific_types_ratio * 0.2, 3),
            consistent_style=round(style_consistency, 3)
        )
    
    def _calculate_overall_score(self,
                                 coverage: CoverageMetrics,
                                 completeness: CompletenessMetrics,
                                 readability: ReadabilityMetrics,
                                 quality: QualityMetrics) -> float:
        """Calculate weighted overall score"""
        
        # Weights based on importance for documentation quality
        weights = {
            'coverage': 0.30,      # How much is documented
            'completeness': 0.25,  # Are sections present
            'quality': 0.25,       # Is it actually useful
            'readability': 0.20   # Is it readable
        }
        
        overall = (
            coverage.overall_coverage * weights['coverage'] +
            completeness.completeness_score * weights['completeness'] +
            quality.quality_score * weights['quality'] +
            readability.readability_score * weights['readability']
        )
        
        return round(overall, 4)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 0.90:
            return 'A+'
        elif score >= 0.85:
            return 'A'
        elif score >= 0.80:
            return 'A-'
        elif score >= 0.75:
            return 'B+'
        elif score >= 0.70:
            return 'B'
        elif score >= 0.65:
            return 'B-'
        elif score >= 0.60:
            return 'C+'
        elif score >= 0.55:
            return 'C'
        elif score >= 0.50:
            return 'C-'
        elif score >= 0.40:
            return 'D'
        else:
            return 'F'
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllables in a word using standard algorithm"""
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            count -= 1
        
        # Every word has at least one syllable
        return max(count, 1)
    
    def _split_camel_case(self, name: str) -> str:
        """Split camelCase/PascalCase into words"""
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', name)


def evaluate_documentation_quality(documentation: str, code_analysis: Dict = None) -> Dict[str, Any]:
    """
    Convenience function to evaluate documentation quality.
    
    Args:
        documentation: The generated documentation text
        code_analysis: Optional dict with function_count, class_count, parameter_count
        
    Returns:
        Dictionary with all quality metrics
    """
    evaluator = DocumentationQualityEvaluator()
    return evaluator.evaluate_documentation(documentation, code_analysis)


# Quick test
if __name__ == "__main__":
    test_doc = """
    # Calculator Module
    
    This module provides mathematical operations for numerical calculations.
    
    ## Class: Calculator
    
    A calculator class that performs arithmetic operations.
    
    ### Method: add
    
    Adds two numbers together and returns the sum.
    
    Args:
        a (int): The first number to add
        b (int): The second number to add
        
    Returns:
        int: The sum of a and b
        
    Raises:
        TypeError: If inputs are not numeric
        
    Examples:
        >>> calc = Calculator()
        >>> calc.add(2, 3)
        5
    """
    
    result = evaluate_documentation_quality(test_doc, {'function_count': 5, 'class_count': 1})
    
    print("Documentation Quality Report")
    print("=" * 50)
    print(f"Overall Score: {result['overall_score']:.1%} (Grade: {result['grade']})")
    print(f"\nCoverage: {result['coverage']['overall']:.1%}")
    print(f"Completeness: {result['completeness']['score']:.1%}")
    print(f"Readability: {result['readability']['score']:.1%}")
    print(f"Quality: {result['quality']['score']:.1%}")
    print(f"\nFlesch-Kincaid Grade: {result['readability']['flesch_kincaid_grade']}")
    print(f"Flesch Reading Ease: {result['readability']['flesch_reading_ease']}")
