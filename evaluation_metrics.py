"""
Evaluation Metrics for Documentation Quality
Implements BLEU, ROUGE, and Readability metrics
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import statistics

class BLEUScore:
    """Calculate BLEU score for documentation quality"""
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words"""
        return re.findall(r'\w+', text.lower())
    
    @staticmethod
    def calculate_ngrams(tokens: List[str], n: int) -> Counter:
        """Generate n-grams from tokens"""
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i:i+n]))
        return Counter(ngrams)
    
    @classmethod
    def calculate(cls, reference: str, candidate: str, max_n: int = 4) -> float:
        """
        Calculate BLEU score
        
        Args:
            reference: Reference documentation (gold standard)
            candidate: Generated documentation
            max_n: Maximum n-gram size (default 4)
        
        Returns:
            BLEU score (0-1)
        """
        ref_tokens = cls.tokenize(reference)
        cand_tokens = cls.tokenize(candidate)
        
        if not cand_tokens:
            return 0.0
        
        # Calculate brevity penalty
        bp = 1.0
        if len(cand_tokens) < len(ref_tokens):
            bp = math.exp(1 - len(ref_tokens) / len(cand_tokens))
        
        # Calculate precision for each n-gram
        precisions = []
        for n in range(1, max_n + 1):
            ref_ngrams = cls.calculate_ngrams(ref_tokens, n)
            cand_ngrams = cls.calculate_ngrams(cand_tokens, n)
            
            if not cand_ngrams:
                precisions.append(0.0)
                continue
            
            # Count matching n-grams
            matches = sum((cand_ngrams & ref_ngrams).values())
            total = sum(cand_ngrams.values())
            
            precision = matches / total if total > 0 else 0.0
            precisions.append(precision)
        
        # Calculate geometric mean of precisions
        if all(p > 0 for p in precisions):
            geo_mean = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
        else:
            geo_mean = 0.0
        
        bleu = bp * geo_mean
        return bleu

class ROUGEScore:
    """Calculate ROUGE scores for documentation quality"""
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words"""
        return re.findall(r'\w+', text.lower())
    
    @classmethod
    def rouge_n(cls, reference: str, candidate: str, n: int = 1) -> Dict[str, float]:
        """
        Calculate ROUGE-N score
        
        Args:
            reference: Reference documentation
            candidate: Generated documentation
            n: N-gram size
        
        Returns:
            Dict with precision, recall, and f1 scores
        """
        ref_tokens = cls.tokenize(reference)
        cand_tokens = cls.tokenize(candidate)
        
        # Generate n-grams
        ref_ngrams = BLEUScore.calculate_ngrams(ref_tokens, n)
        cand_ngrams = BLEUScore.calculate_ngrams(cand_tokens, n)
        
        # Calculate matches
        matches = sum((ref_ngrams & cand_ngrams).values())
        
        # Calculate precision, recall, F1
        precision = matches / sum(cand_ngrams.values()) if cand_ngrams else 0.0
        recall = matches / sum(ref_ngrams.values()) if ref_ngrams else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    @classmethod
    def rouge_l(cls, reference: str, candidate: str) -> Dict[str, float]:
        """
        Calculate ROUGE-L (Longest Common Subsequence)
        
        Args:
            reference: Reference documentation
            candidate: Generated documentation
        
        Returns:
            Dict with precision, recall, and f1 scores
        """
        ref_tokens = cls.tokenize(reference)
        cand_tokens = cls.tokenize(candidate)
        
        # Calculate LCS
        lcs_length = cls._lcs_length(ref_tokens, cand_tokens)
        
        # Calculate precision, recall, F1
        precision = lcs_length / len(cand_tokens) if cand_tokens else 0.0
        recall = lcs_length / len(ref_tokens) if ref_tokens else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    @staticmethod
    def _lcs_length(seq1: List[str], seq2: List[str]) -> int:
        """Calculate length of longest common subsequence"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    @classmethod
    def calculate_all(cls, reference: str, candidate: str) -> Dict[str, Any]:
        """Calculate all ROUGE metrics"""
        return {
            'rouge-1': cls.rouge_n(reference, candidate, n=1),
            'rouge-2': cls.rouge_n(reference, candidate, n=2),
            'rouge-l': cls.rouge_l(reference, candidate)
        }

class ReadabilityMetrics:
    """Calculate readability metrics for documentation"""
    
    @staticmethod
    def count_syllables(word: str) -> int:
        """Estimate syllables in a word"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    @classmethod
    def flesch_reading_ease(cls, text: str) -> float:
        """
        Calculate Flesch Reading Ease score
        
        Score interpretation:
        90-100: Very Easy (5th grade)
        80-89: Easy (6th grade)
        70-79: Fairly Easy (7th grade)
        60-69: Standard (8th-9th grade)
        50-59: Fairly Difficult (10th-12th grade)
        30-49: Difficult (College)
        0-29: Very Difficult (College graduate)
        
        Returns:
            Flesch Reading Ease score (0-100)
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return 0.0
        
        syllables = sum(cls.count_syllables(word) for word in words)
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        
        # Clamp between 0-100
        return max(0.0, min(100.0, score))
    
    @classmethod
    def flesch_kincaid_grade(cls, text: str) -> float:
        """
        Calculate Flesch-Kincaid Grade Level
        
        Returns:
            Grade level (e.g., 8.0 = 8th grade)
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return 0.0
        
        syllables = sum(cls.count_syllables(word) for word in words)
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)
        
        grade = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
        
        return max(0.0, grade)
    
    @classmethod
    def gunning_fog_index(cls, text: str) -> float:
        """
        Calculate Gunning Fog Index
        
        Returns:
            Grade level required to understand the text
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return 0.0
        
        # Count complex words (3+ syllables)
        complex_words = sum(1 for word in words if cls.count_syllables(word) >= 3)
        
        avg_sentence_length = len(words) / len(sentences)
        percent_complex = (complex_words / len(words)) * 100
        
        fog_index = 0.4 * (avg_sentence_length + percent_complex)
        
        return fog_index
    
    @classmethod
    def smog_index(cls, text: str) -> float:
        """
        Calculate SMOG (Simple Measure of Gobbledygook) Index
        
        Returns:
            Years of education needed to understand the text
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text)
        
        if len(sentences) < 30:
            # SMOG requires at least 30 sentences, use approximation
            return cls.flesch_kincaid_grade(text)
        
        # Count polysyllabic words (3+ syllables)
        polysyllabic_count = sum(1 for word in words if cls.count_syllables(word) >= 3)
        
        smog = 1.0430 * math.sqrt(polysyllabic_count * (30 / len(sentences))) + 3.1291
        
        return smog
    
    @classmethod
    def calculate_all(cls, text: str) -> Dict[str, float]:
        """Calculate all readability metrics"""
        return {
            'flesch_reading_ease': cls.flesch_reading_ease(text),
            'flesch_kincaid_grade': cls.flesch_kincaid_grade(text),
            'gunning_fog_index': cls.gunning_fog_index(text),
            'smog_index': cls.smog_index(text)
        }

class DocumentationQualityMetrics:
    """Comprehensive documentation quality assessment"""
    
    @staticmethod
    def calculate_completeness(doc: str, function_params: List[str]) -> float:
        """
        Calculate documentation completeness
        
        Checks if:
        - All parameters are documented
        - Return value is documented
        - Examples are provided
        - Exceptions/errors are documented
        
        Returns:
            Completeness score (0-1)
        """
        score = 0.0
        max_score = 4.0
        
        # Check parameter documentation
        param_documented = sum(1 for param in function_params if param.lower() in doc.lower())
        if function_params:
            score += (param_documented / len(function_params))
        else:
            score += 1.0  # No params to document
        
        # Check return documentation
        if any(keyword in doc.lower() for keyword in ['return', 'returns', 'output', 'result']):
            score += 1.0
        
        # Check examples
        if any(keyword in doc.lower() for keyword in ['example', '>>>', 'usage', 'demo']):
            score += 1.0
        
        # Check error/exception documentation
        if any(keyword in doc.lower() for keyword in ['raise', 'error', 'exception', 'throws']):
            score += 1.0
        
        return score / max_score
    
    @staticmethod
    def calculate_clarity(doc: str) -> float:
        """
        Calculate documentation clarity
        
        Based on:
        - Readability score
        - Average sentence length
        - Use of technical jargon
        
        Returns:
            Clarity score (0-1)
        """
        readability = ReadabilityMetrics.flesch_reading_ease(doc)
        
        # Normalize Flesch score to 0-1 (50-100 = good, 0-50 = poor)
        normalized_readability = min(1.0, max(0.0, (readability - 50) / 50))
        
        # Check sentence length
        sentences = re.split(r'[.!?]+', doc)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # Optimal sentence length: 15-20 words
            length_score = 1.0 - abs(17.5 - avg_sentence_length) / 17.5
            length_score = max(0.0, min(1.0, length_score))
        else:
            length_score = 0.5
        
        clarity = (normalized_readability + length_score) / 2
        return clarity
    
    @staticmethod
    def calculate_conciseness(doc: str, code_lines: int) -> float:
        """
        Calculate documentation conciseness
        
        Good documentation is thorough but not verbose
        Ratio of documentation lines to code lines
        
        Returns:
            Conciseness score (0-1)
        """
        doc_lines = len([line for line in doc.split('\n') if line.strip()])
        
        if code_lines == 0:
            return 0.5
        
        ratio = doc_lines / code_lines
        
        # Optimal ratio: 0.5-1.5 (half to 1.5x the code)
        if 0.5 <= ratio <= 1.5:
            return 1.0
        elif ratio < 0.5:
            return ratio / 0.5  # Under-documented
        else:
            return max(0.0, 1.0 - (ratio - 1.5) / 2.0)  # Over-documented
    
    @classmethod
    def evaluate_documentation(cls, doc: str, reference: Optional[str] = None, 
                               function_params: List[str] = [], 
                               code_lines: int = 10) -> Dict[str, Any]:
        """
        Comprehensive documentation evaluation
        
        Args:
            doc: Generated documentation
            reference: Reference documentation (optional, for BLEU/ROUGE)
            function_params: List of function parameters
            code_lines: Number of lines in the code being documented
        
        Returns:
            Dictionary with all metrics
        """
        metrics = {
            'readability': ReadabilityMetrics.calculate_all(doc),
            'completeness': cls.calculate_completeness(doc, function_params),
            'clarity': cls.calculate_clarity(doc),
            'conciseness': cls.calculate_conciseness(doc, code_lines),
            'length': {
                'characters': len(doc),
                'words': len(doc.split()),
                'lines': len(doc.split('\n'))
            }
        }
        
        # Add BLEU and ROUGE if reference is provided
        if reference:
            metrics['bleu'] = BLEUScore.calculate(reference, doc)
            metrics['rouge'] = ROUGEScore.calculate_all(reference, doc)
        
        # Calculate overall score
        overall = (
            (metrics['readability']['flesch_reading_ease'] / 100) * 0.2 +
            metrics['completeness'] * 0.3 +
            metrics['clarity'] * 0.3 +
            metrics['conciseness'] * 0.2
        )
        metrics['overall_score'] = overall
        
        return metrics


class METEORScore:
    """METEOR (Metric for Evaluation of Translation with Explicit ORdering)
    
    Better correlation with human judgment than BLEU.
    Considers synonyms, stemming, and word order.
    """
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text"""
        return re.findall(r'\w+', text.lower())
    
    @classmethod
    def calculate(cls, reference: str, candidate: str, alpha: float = 0.9, beta: float = 3.0) -> float:
        """Calculate METEOR score
        
        Args:
            reference: Reference text
            candidate: Generated text
            alpha: Weight for precision vs recall
            beta: Weight for fragmentation penalty
            
        Returns:
            METEOR score (0-1)
        """
        ref_tokens = cls.tokenize(reference)
        cand_tokens = cls.tokenize(candidate)
        
        if not ref_tokens or not cand_tokens:
            return 0.0
        
        # Calculate matches (exact matches for now - can add synonyms/stemming)
        ref_matched = set()
        cand_matched = set()
        chunks = 0
        
        # Find exact matches
        for i, cand_token in enumerate(cand_tokens):
            for j, ref_token in enumerate(ref_tokens):
                if cand_token == ref_token and j not in ref_matched:
                    ref_matched.add(j)
                    cand_matched.add(i)
                    chunks += 1
                    break
        
        matches = len(ref_matched)
        
        if matches == 0:
            return 0.0
        
        # Precision and Recall
        precision = matches / len(cand_tokens)
        recall = matches / len(ref_tokens)
        
        # F-mean
        if precision + recall == 0:
            return 0.0
        
        f_mean = (precision * recall) / (alpha * precision + (1 - alpha) * recall)
        
        # Fragmentation penalty
        fragmentation = chunks / matches if matches > 0 else 1.0
        penalty = 0.5 * (fragmentation ** beta)
        
        meteor = f_mean * (1 - penalty)
        
        return max(0.0, min(1.0, meteor))


class CodeBLEU:
    """CodeBLEU - BLEU variant optimized for code and technical documentation
    
    Combines:
    - N-gram match (like BLEU)
    - Weighted n-grams (keywords get higher weight)
    - Syntax match (code structure)
    - Dataflow match (semantic similarity)
    """
    
    CODE_KEYWORDS = {
        'def', 'class', 'return', 'if', 'else', 'for', 'while', 'try', 'except',
        'import', 'from', 'as', 'with', 'lambda', 'yield', 'async', 'await',
        'self', 'super', 'init', 'str', 'int', 'float', 'bool', 'list', 'dict',
        'true', 'false', 'none', 'and', 'or', 'not', 'in', 'is'
    }
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize preserving code structure"""
        # Split on whitespace and punctuation but keep meaningful symbols
        tokens = re.findall(r'\w+|[(){}[\],.:;]', text.lower())
        return tokens
    
    @staticmethod
    def calculate_weighted_ngrams(tokens: List[str], n: int, ref_tokens: List[str]) -> Tuple[Counter, float]:
        """Calculate n-grams with keyword weighting"""
        ngrams = Counter()
        total_weight = 0.0
        
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            
            # Weight: higher for code keywords
            weight = 1.0
            for token in ngram:
                if token in CodeBLEU.CODE_KEYWORDS:
                    weight += 0.5
            
            ngrams[ngram] += weight
            total_weight += weight
        
        return ngrams, total_weight
    
    @classmethod
    def calculate(cls, reference: str, candidate: str, weights: List[float] = [0.25, 0.25, 0.25, 0.25]) -> float:
        """Calculate CodeBLEU score
        
        Args:
            reference: Reference documentation/code
            candidate: Generated documentation/code
            weights: Weights for [ngram, syntax, dataflow, keywords]
            
        Returns:
            CodeBLEU score (0-1)
        """
        ref_tokens = cls.tokenize(reference)
        cand_tokens = cls.tokenize(candidate)
        
        if not ref_tokens or not cand_tokens:
            return 0.0
        
        # 1. Weighted n-gram match (1-4 grams)
        ngram_scores = []
        for n in range(1, 5):
            ref_ngrams, ref_weight = cls.calculate_weighted_ngrams(ref_tokens, n, ref_tokens)
            cand_ngrams, cand_weight = cls.calculate_weighted_ngrams(cand_tokens, n, ref_tokens)
            
            clipped_count = 0.0
            for ngram, count in cand_ngrams.items():
                clipped_count += min(count, ref_ngrams.get(ngram, 0))
            
            precision = clipped_count / cand_weight if cand_weight > 0 else 0
            ngram_scores.append(precision)
        
        # Geometric mean of n-gram precisions
        if all(s > 0 for s in ngram_scores):
            ngram_match = math.exp(sum(math.log(s) for s in ngram_scores) / len(ngram_scores))
        else:
            ngram_match = 0.0
        
        # 2. Syntax match (simple: matching brackets/parentheses)
        ref_syntax = Counter([t for t in ref_tokens if t in '(){}[]'])
        cand_syntax = Counter([t for t in cand_tokens if t in '(){}[]'])
        
        syntax_match = 0.0
        if ref_syntax:
            matches = sum(min(ref_syntax[k], cand_syntax[k]) for k in ref_syntax)
            syntax_match = matches / sum(ref_syntax.values())
        
        # 3. Dataflow match (keyword coverage)
        ref_keywords = set(t for t in ref_tokens if t in cls.CODE_KEYWORDS)
        cand_keywords = set(t for t in cand_tokens if t in cls.CODE_KEYWORDS)
        
        dataflow_match = 0.0
        if ref_keywords:
            dataflow_match = len(ref_keywords & cand_keywords) / len(ref_keywords)
        
        # 4. Keyword bonus
        keyword_match = len(cand_keywords & ref_keywords) / max(len(cand_keywords | ref_keywords), 1)
        
        # Weighted combination
        code_bleu = (
            weights[0] * ngram_match +
            weights[1] * syntax_match +
            weights[2] * dataflow_match +
            weights[3] * keyword_match
        )
        
        return max(0.0, min(1.0, code_bleu))


class ComprehensiveEvaluator:
    """Comprehensive evaluation combining all metrics"""
    
    @staticmethod
    def evaluate_all(
        generated: str,
        reference: Optional[str] = None,
        function_params: Optional[List[str]] = None,
        code_lines: int = 10,
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluate documentation with all available metrics
        
        Args:
            generated: Generated documentation
            reference: Reference documentation (for comparison metrics)
            function_params: Function parameters (for completeness check)
            code_lines: Number of code lines
            code: Original code (for code-specific metrics)
            
        Returns:
            Dictionary with all metric scores
        """
        results = {
            'generated_length': len(generated),
            'generated_words': len(generated.split()),
            'generated_lines': len(generated.split('\n'))
        }
        
        # Basic quality metrics
        quality_results = DocumentationQualityEvaluator.evaluate_documentation(
            generated,
            reference,
            function_params or [],
            code_lines
        )
        results.update(quality_results)
        
        # Comparison metrics (if reference provided)
        if reference:
            results['bleu'] = BLEUScore.calculate(reference, generated)
            results['rouge'] = ROUGEScore.calculate_all(reference, generated)
            results['meteor'] = METEORScore.calculate(reference, generated)
            
            # CodeBLEU if code is provided
            if code:
                # Combine code and documentation for CodeBLEU
                ref_combined = f"{code}\n{reference}"
                gen_combined = f"{code}\n{generated}"
                results['code_bleu'] = CodeBLEU.calculate(ref_combined, gen_combined)
        
        # Calculate aggregate score
        scores = []
        if 'bleu' in results:
            scores.append(results['bleu'])
        if 'rouge' in results:
            scores.append(results['rouge']['rouge-l']['f'])
        if 'meteor' in results:
            scores.append(results['meteor'])
        if 'code_bleu' in results:
            scores.append(results['code_bleu'])
        
        if scores:
            results['aggregate_score'] = sum(scores) / len(scores)
        
        return results
    
    @staticmethod
    def format_report(results: Dict[str, Any]) -> str:
        """Format evaluation results as readable report"""
        report = ["=" * 60]
        report.append("📊 DOCUMENTATION QUALITY EVALUATION REPORT")
        report.append("=" * 60)
        
        # Comparison Metrics
        if 'bleu' in results:
            report.append("\n🔹 Comparison Metrics (vs Reference):")
            report.append(f"  BLEU Score:      {results['bleu']:.4f}")
            if 'meteor' in results:
                report.append(f"  METEOR Score:    {results['meteor']:.4f}")
            if 'rouge' in results:
                report.append(f"  ROUGE-L F1:      {results['rouge']['rouge-l']['f']:.4f}")
            if 'code_bleu' in results:
                report.append(f"  CodeBLEU:        {results['code_bleu']:.4f}")
        
        # Quality Metrics
        if 'completeness' in results:
            report.append("\n🔹 Intrinsic Quality:")
            report.append(f"  Completeness:    {results['completeness']:.2%}")
            report.append(f"  Clarity:         {results['clarity']:.2%}")
            report.append(f"  Conciseness:     {results['conciseness']:.2%}")
        
        # Readability
        if 'readability' in results:
            report.append("\n🔹 Readability:")
            r = results['readability']
            report.append(f"  Flesch Reading:  {r['flesch_reading_ease']:.1f}")
            report.append(f"  Grade Level:     {r['flesch_kincaid_grade']:.1f}")
        
        # Overall
        if 'aggregate_score' in results:
            report.append("\n" + "=" * 60)
            report.append(f"⭐ OVERALL SCORE: {results['aggregate_score']:.2%}")
            report.append("=" * 60)
        
        return '\n'.join(report)
