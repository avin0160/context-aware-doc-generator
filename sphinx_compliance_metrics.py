"""
Sphinx Compliance & Quality Metrics
====================================

Production-grade evaluation system for Sphinx/reST documentation.
Gate-based validation with objective quality scoring.

Metric Hierarchy:
1. Compliance Score (GATE) - Binary pass/fail
2. Evidence Coverage (PRIMARY) - Objective parameter coverage
3. Consistency Score - Cross-reference validation
4. Non-Tautology Score - Information density
5. Brevity Efficiency - Token usage optimization
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ComplianceResult:
    """Binary gate results for documentation compliance"""
    sphinx_format: bool
    forbidden_language: bool
    epistemic_discipline: bool
    
    @property
    def passed(self) -> bool:
        """Gate passed only if ALL checks pass"""
        return all([self.sphinx_format, self.forbidden_language, self.epistemic_discipline])
    
    def __str__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"""
Compliance Gate: {status}
  - Sphinx Format: {'✅' if self.sphinx_format else '❌'}
  - Forbidden Language: {'✅' if self.forbidden_language else '❌'}
  - Epistemic Discipline: {'✅' if self.epistemic_discipline else '❌'}
"""


@dataclass
class QualityScores:
    """Quality metrics (only evaluated if compliance passes)"""
    evidence_coverage: float  # 0.0-1.0
    consistency: float        # 0.0-1.0
    non_tautology: float      # 0.0-1.0
    brevity_efficiency: float # 0.0-1.0
    
    @property
    def overall_quality(self) -> float:
        """Weighted average (evidence coverage is most important)"""
        return (
            0.50 * self.evidence_coverage +
            0.20 * self.consistency +
            0.20 * self.non_tautology +
            0.10 * self.brevity_efficiency
        )
    
    def __str__(self) -> str:
        return f"""
Quality Scores:
  - Evidence Coverage: {self.evidence_coverage:.2%} (weight: 50%)
  - Consistency: {self.consistency:.2%} (weight: 20%)
  - Non-Tautology: {self.non_tautology:.2%} (weight: 20%)
  - Brevity Efficiency: {self.brevity_efficiency:.2%} (weight: 10%)
  
  Overall Quality: {self.overall_quality:.2%}
"""


@dataclass
class EvaluationReport:
    """Complete evaluation report"""
    compliance: ComplianceResult
    quality: Optional[QualityScores]
    details: Dict[str, Any]
    
    @property
    def accepted(self) -> bool:
        """Documentation accepted only if compliance passes"""
        return self.compliance.passed
    
    def __str__(self) -> str:
        report = str(self.compliance)
        if self.quality:
            report += str(self.quality)
        
        if self.details:
            report += "\nDetails:\n"
            for key, value in self.details.items():
                report += f"  - {key}: {value}\n"
        
        return report


class SphinxComplianceValidator:
    """
    Gate 1: Sphinx Format Compliance (Binary)
    
    Validates strict Sphinx/reST formatting rules.
    """
    
    REQUIRED_FIELDS = [':param:', ':type:', ':return:', ':rtype:']
    
    @staticmethod
    def validate_format(doc: str) -> Tuple[bool, List[str]]:
        """
        Check Sphinx format compliance.
        
        :param doc: Documentation string to validate
        :type doc: str
        :return: (passed, list of violations)
        :rtype: Tuple[bool, List[str]]
        """
        violations = []
        
        # Check for Markdown formatting
        if re.search(r'#{1,6}\s+\w+', doc):  # Markdown headers
            violations.append("Contains Markdown headers (## or ###)")
        
        if re.search(r'\*\*\w+\*\*', doc) and ':' not in doc:  # Markdown bold without Sphinx fields
            violations.append("Contains Markdown bold formatting")
        
        if re.search(r'^\s*[-*+]\s+\w+', doc, re.MULTILINE):  # Markdown bullets
            violations.append("Contains Markdown bullet lists (use proper reST)")
        
        # Check for Sphinx field markers (if parameters exist)
        if 'def ' in doc or 'param' in doc.lower():
            has_sphinx_fields = any(field in doc for field in SphinxComplianceValidator.REQUIRED_FIELDS)
            if not has_sphinx_fields:
                violations.append("Missing Sphinx field markers (:param:, :type:, :return:)")
        
        # Check for prose outside docstrings
        lines = doc.split('\n')
        in_docstring = False
        for line in lines:
            stripped = line.strip()
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
            elif not in_docstring and stripped and not stripped.startswith(('class ', 'def ', '#')):
                if not any(field in stripped for field in SphinxComplianceValidator.REQUIRED_FIELDS):
                    violations.append(f"Prose outside docstring: {stripped[:50]}")
                    break
        
        return (len(violations) == 0, violations)


class ForbiddenLanguageValidator:
    """
    Gate 2: Forbidden Language Check (Binary)
    
    Rejects quality judgments, invented examples, and fluff.
    """
    
    FORBIDDEN_PATTERNS = [
        # Quality judgments
        r'\b(well[- ]designed|maintainable|robust|elegant|powerful|flexible|efficient|optimized)\b',
        
        # Usage phrases
        r'\b(this (function|method|class) is used (to|for))\b',
        r'\b(used to (perform|handle|manage|process))\b',
        
        # Example blocks (unless marked as public API)
        r'example:',
        r'>>> ',
        r'for example[,:]',
        
        # Architectural summaries
        r'\b(architecture|design pattern|follows.*pattern)\b',
        
        # Function name restatement
        # Detected by semantic analysis, not regex
    ]
    
    @staticmethod
    def validate_language(doc: str) -> Tuple[bool, List[str]]:
        """
        Check for forbidden language patterns.
        
        :param doc: Documentation string to validate
        :type doc: str
        :return: (passed, list of violations)
        :rtype: Tuple[bool, List[str]]
        """
        violations = []
        doc_lower = doc.lower()
        
        for pattern in ForbiddenLanguageValidator.FORBIDDEN_PATTERNS:
            matches = re.finditer(pattern, doc_lower, re.IGNORECASE)
            for match in matches:
                violations.append(f"Forbidden pattern: '{match.group()}'")
        
        return (len(violations) == 0, violations)
    
    @staticmethod
    def check_tautology(func_name: str, description: str) -> bool:
        """
        Check if description is just a restatement of the function name.
        
        :param func_name: Function or class name
        :type func_name: str
        :param description: First line of docstring
        :type description: str
        :return: True if tautological (BAD)
        :rtype: bool
        """
        # Normalize names: snake_case/camelCase to words
        name_words = set(re.findall(r'[A-Z][a-z]+|[a-z]+', func_name.replace('_', '')))
        desc_words = set(re.findall(r'\b\w+\b', description.lower()))
        
        # If description is just rearranged function name words
        if name_words and name_words.issubset(desc_words):
            # Check if description adds meaningful information
            meaningful_words = desc_words - name_words - {
                'a', 'an', 'the', 'is', 'are', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with'
            }
            if len(meaningful_words) < 2:
                return True  # Tautology detected
        
        return False


class EpistemicDisciplineValidator:
    """
    Gate 3: Epistemic Discipline Check (Binary)
    
    Ensures claims are evidence-based, not invented.
    """
    
    SPECULATION_MARKERS = [
        r'\b(probably|likely|might|could|possibly|perhaps|seems to|appears to)\b',
        r'\b(should (be|handle|manage|process))\b',
        r'\b(expected to|assumed to|supposed to)\b',
    ]
    
    INVENTION_PATTERNS = [
        r'raises:?\s+\w+Error',  # Invented exceptions
        r'returns:?\s+(True|False|None) (if|when)',  # Invented return semantics
    ]
    
    @staticmethod
    def validate_discipline(doc: str, observed_info: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """
        Check epistemic discipline.
        
        :param doc: Documentation string to validate
        :type doc: str
        :param observed_info: Parser-extracted information (params, return type, etc.)
        :type observed_info: Optional[Dict]
        :return: (passed, list of violations)
        :rtype: Tuple[bool, List[str]]
        """
        violations = []
        doc_lower = doc.lower()
        
        # Check for speculation
        for pattern in EpistemicDisciplineValidator.SPECULATION_MARKERS:
            matches = re.finditer(pattern, doc_lower, re.IGNORECASE)
            for match in matches:
                violations.append(f"Speculation detected: '{match.group()}'")
        
        # Check for invented behavior
        for pattern in EpistemicDisciplineValidator.INVENTION_PATTERNS:
            matches = re.finditer(pattern, doc, re.IGNORECASE)
            for match in matches:
                # Only flag if NOT in observed_info
                if observed_info:
                    # This would need parser data to verify
                    pass
                violations.append(f"Potentially invented: '{match.group()}'")
        
        # Check: internal functions treated as public API
        if 'public api' in doc_lower or 'external use' in doc_lower:
            if observed_info and observed_info.get('is_private', False):
                violations.append("Internal function documented as public API")
        
        return (len(violations) == 0, violations)


class EvidenceCoverageCalculator:
    """
    Metric 2: Evidence Coverage Score (Primary Quality Metric)
    
    Measures how well observable facts are documented.
    """
    
    @staticmethod
    def calculate(doc: str, observed_info: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate evidence coverage.
        
        :param doc: Generated documentation
        :type doc: str
        :param observed_info: Parser-extracted facts (parameters, attributes, return type)
        :type observed_info: Dict
        :return: (coverage_score, details)
        :rtype: Tuple[float, Dict[str, Any]]
        """
        total_observable = 0
        correctly_documented = 0
        details = {'missing': [], 'incorrect': [], 'correct': []}
        
        # Check parameters
        observed_params = observed_info.get('parameters', [])
        total_observable += len(observed_params)
        
        for param in observed_params:
            param_pattern = rf':param\s+{re.escape(param)}:'
            if re.search(param_pattern, doc):
                correctly_documented += 1
                details['correct'].append(f"param:{param}")
            else:
                details['missing'].append(f"param:{param}")
        
        # Check return type (if exists)
        if observed_info.get('has_return', False):
            total_observable += 1
            if ':return:' in doc or ':rtype:' in doc:
                correctly_documented += 1
                details['correct'].append("return")
            else:
                details['missing'].append("return")
        
        # Check attributes (for classes)
        observed_attrs = observed_info.get('attributes', [])
        total_observable += len(observed_attrs)
        
        for attr in observed_attrs:
            if attr in doc:
                correctly_documented += 1
                details['correct'].append(f"attr:{attr}")
            else:
                details['missing'].append(f"attr:{attr}")
        
        # Calculate coverage
        if total_observable == 0:
            coverage = 1.0  # No observable facts = trivial coverage
        else:
            coverage = correctly_documented / total_observable
        
        details['total_observable'] = total_observable
        details['correctly_documented'] = correctly_documented
        
        return (coverage, details)


class ConsistencyCalculator:
    """
    Metric 3: Consistency Score
    
    Validates internal consistency (param names, types, cross-references).
    """
    
    @staticmethod
    def calculate(doc: str, observed_info: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate consistency score.
        
        :param doc: Generated documentation
        :type doc: str
        :param observed_info: Parser-extracted information
        :type observed_info: Dict
        :return: (consistency_score, details)
        :rtype: Tuple[float, Dict[str, Any]]
        """
        inconsistencies = 0
        total_references = 0
        details = {'inconsistencies': []}
        
        # Check parameter name consistency
        observed_params = observed_info.get('parameters', [])
        param_mentions = re.findall(r':param\s+(\w+):', doc)
        
        total_references += len(param_mentions)
        for mentioned_param in param_mentions:
            if mentioned_param not in observed_params:
                inconsistencies += 1
                details['inconsistencies'].append(f"Parameter '{mentioned_param}' not in signature")
        
        # Check type consistency (same param mentioned multiple times)
        param_types = {}
        type_mentions = re.findall(r':param\s+(\w+):.*?:type\s+\1:\s*(\w+)', doc, re.DOTALL)
        
        for param, param_type in type_mentions:
            if param in param_types:
                if param_types[param] != param_type:
                    inconsistencies += 1
                    details['inconsistencies'].append(
                        f"Type inconsistency: {param} typed as both {param_types[param]} and {param_type}"
                    )
            else:
                param_types[param] = param_type
            total_references += 1
        
        # Calculate consistency
        if total_references == 0:
            consistency = 1.0  # No references = trivial consistency
        else:
            consistency = 1 - (inconsistencies / total_references)
        
        return (consistency, details)


class NonTautologyCalculator:
    """
    Metric 4: Non-Tautology Score
    
    Measures information density (penalizes restating function names).
    """
    
    @staticmethod
    def calculate(doc: str, symbol_name: str) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate non-tautology score.
        
        :param doc: Generated documentation
        :type doc: str
        :param symbol_name: Function or class name
        :type symbol_name: str
        :return: (non_tautology_score, details)
        :rtype: Tuple[float, Dict[str, Any]]
        """
        # Extract sentences (docstring first line + description sentences)
        sentences = re.split(r'[.!?]\s+', doc)
        sentences = [s.strip() for s in sentences if s.strip() and not s.strip().startswith(':')]
        
        tautological = 0
        details = {'tautologies': [], 'total_sentences': len(sentences)}
        
        for sentence in sentences:
            if ForbiddenLanguageValidator.check_tautology(symbol_name, sentence):
                tautological += 1
                details['tautologies'].append(sentence[:60])
        
        if len(sentences) == 0:
            return (1.0, details)  # No sentences = no tautology
        
        non_tautology = 1 - (tautological / len(sentences))
        return (non_tautology, details)


class BrevityCalculator:
    """
    Metric 5: Brevity Efficiency
    
    Measures token usage efficiency (after correctness validated).
    """
    
    @staticmethod
    def calculate(doc: str, max_tokens: int = 512) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate brevity efficiency.
        
        :param doc: Generated documentation
        :type doc: str
        :param max_tokens: Maximum allowed tokens
        :type max_tokens: int
        :return: (brevity_score, details)
        :rtype: Tuple[float, Dict[str, Any]]
        """
        # Simple token approximation (words + punctuation)
        tokens_used = len(doc.split()) + doc.count('\n')
        
        details = {
            'tokens_used': tokens_used,
            'max_tokens': max_tokens,
            'utilization': tokens_used / max_tokens if max_tokens > 0 else 0
        }
        
        if tokens_used > max_tokens:
            # Over limit = penalty
            brevity = 0.0
        else:
            # Under limit = good (but not TOO sparse)
            utilization = tokens_used / max_tokens
            if utilization < 0.1:
                # Too sparse = under-documented
                brevity = utilization * 10  # Scale up
            else:
                brevity = 1 - utilization
        
        return (brevity, details)


class DocumentationEvaluator:
    """
    Complete evaluation pipeline.
    
    Gate-based validation with objective quality scoring.
    """
    
    def __init__(self, max_tokens: int = 512):
        """
        Initialize evaluator.
        
        :param max_tokens: Maximum tokens for brevity calculation
        :type max_tokens: int
        """
        self.max_tokens = max_tokens
    
    def evaluate(
        self,
        doc: str,
        observed_info: Optional[Dict] = None,
        symbol_name: Optional[str] = None
    ) -> EvaluationReport:
        """
        Run complete evaluation.
        
        :param doc: Generated documentation
        :type doc: str
        :param observed_info: Parser-extracted facts (parameters, return, attributes)
        :type observed_info: Optional[Dict]
        :param symbol_name: Function/class name for tautology check
        :type symbol_name: Optional[str]
        :return: Complete evaluation report
        :rtype: EvaluationReport
        """
        # GATE 1: Sphinx Format Compliance
        sphinx_pass, sphinx_violations = SphinxComplianceValidator.validate_format(doc)
        
        # GATE 2: Forbidden Language
        lang_pass, lang_violations = ForbiddenLanguageValidator.validate_language(doc)
        
        # GATE 3: Epistemic Discipline
        epistemic_pass, epistemic_violations = EpistemicDisciplineValidator.validate_discipline(
            doc, observed_info
        )
        
        compliance = ComplianceResult(
            sphinx_format=sphinx_pass,
            forbidden_language=lang_pass,
            epistemic_discipline=epistemic_pass
        )
        
        details = {
            'sphinx_violations': sphinx_violations,
            'language_violations': lang_violations,
            'epistemic_violations': epistemic_violations
        }
        
        # Only evaluate quality if compliance passes
        quality = None
        if compliance.passed:
            # Metric 2: Evidence Coverage
            evidence_score, evidence_details = EvidenceCoverageCalculator.calculate(
                doc, observed_info or {}
            )
            details['evidence'] = evidence_details
            
            # Metric 3: Consistency
            consistency_score, consistency_details = ConsistencyCalculator.calculate(
                doc, observed_info or {}
            )
            details['consistency'] = consistency_details
            
            # Metric 4: Non-Tautology
            tautology_score, tautology_details = NonTautologyCalculator.calculate(
                doc, symbol_name or 'unknown'
            )
            details['tautology'] = tautology_details
            
            # Metric 5: Brevity
            brevity_score, brevity_details = BrevityCalculator.calculate(doc, self.max_tokens)
            details['brevity'] = brevity_details
            
            quality = QualityScores(
                evidence_coverage=evidence_score,
                consistency=consistency_score,
                non_tautology=tautology_score,
                brevity_efficiency=brevity_score
            )
        
        return EvaluationReport(compliance=compliance, quality=quality, details=details)
    
    def batch_evaluate(
        self,
        docs: List[Tuple[str, Dict, str]]
    ) -> List[EvaluationReport]:
        """
        Evaluate multiple documentation strings.
        
        :param docs: List of (doc, observed_info, symbol_name) tuples
        :type docs: List[Tuple[str, Dict, str]]
        :return: List of evaluation reports
        :rtype: List[EvaluationReport]
        """
        return [self.evaluate(doc, info, name) for doc, info, name in docs]
    
    def aggregate_results(self, reports: List[EvaluationReport]) -> Dict[str, Any]:
        """
        Aggregate results across multiple evaluations.
        
        :param reports: List of evaluation reports
        :type reports: List[EvaluationReport]
        :return: Aggregate statistics
        :rtype: Dict[str, Any]
        """
        total = len(reports)
        passed = sum(1 for r in reports if r.compliance.passed)
        
        aggregate = {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': passed / total if total > 0 else 0,
            'avg_quality': 0,
            'quality_breakdown': {}
        }
        
        # Only average quality for passed reports
        passed_reports = [r for r in reports if r.quality]
        if passed_reports:
            aggregate['avg_quality'] = sum(r.quality.overall_quality for r in passed_reports) / len(passed_reports)
            aggregate['quality_breakdown'] = {
                'evidence_coverage': sum(r.quality.evidence_coverage for r in passed_reports) / len(passed_reports),
                'consistency': sum(r.quality.consistency for r in passed_reports) / len(passed_reports),
                'non_tautology': sum(r.quality.non_tautology for r in passed_reports) / len(passed_reports),
                'brevity_efficiency': sum(r.quality.brevity_efficiency for r in passed_reports) / len(passed_reports),
            }
        
        return aggregate


# Example usage
if __name__ == '__main__':
    evaluator = DocumentationEvaluator(max_tokens=512)
    
    # Test case: Good Sphinx documentation
    good_doc = '''
    """
    Advances the game state by one frame.
    
    :param delta_time: Time elapsed since the previous frame, in seconds
    :type delta_time: float
    :return: None
    :rtype: None
    """
    '''
    
    observed = {
        'parameters': ['delta_time'],
        'has_return': True,
        'attributes': []
    }
    
    report = evaluator.evaluate(good_doc, observed, 'update')
    print(report)
    
    # Test case: Bad documentation (quality judgments)
    bad_doc = '''
    """
    This function is used to update the game state efficiently.
    Well-designed method that handles frame updates.
    
    Example:
        >>> update(0.016)
    """
    '''
    
    report2 = evaluator.evaluate(bad_doc, observed, 'update')
    print(report2)
