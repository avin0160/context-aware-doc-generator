"""
Technical Documentation Quality Metrics
Specialized evaluation for technical/API documentation quality
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import statistics


class TechnicalDocumentationEvaluator:
    """Comprehensive evaluation metrics for technical documentation quality"""
    
    @staticmethod
    def evaluate_structure(doc: str) -> Dict[str, Any]:
        """Evaluate documentation structure and organization
        
        Checks for:
        - Proper sections (overview, parameters, returns, examples, etc.)
        - Hierarchical organization
        - Consistent formatting
        
        Returns:
            Dictionary with structure scores
        """
        sections_found = {
            'overview': bool(re.search(r'(overview|description|summary|purpose)', doc, re.I)),
            'parameters': bool(re.search(r'(parameters?|arguments?|args?|:param)', doc, re.I)),
            'returns': bool(re.search(r'(returns?|outputs?|:return|:rtype)', doc, re.I)),
            'examples': bool(re.search(r'(examples?|usage|demo)', doc, re.I)),
            'exceptions': bool(re.search(r'(raises?|exceptions?|errors?|:raises)', doc, re.I)),
            'notes': bool(re.search(r'(notes?|warnings?|important|see also)', doc, re.I))
        }
        
        # Check for Sphinx directives
        sphinx_directives = {
            ':param': len(re.findall(r':param\s+\w+:', doc)),
            ':type': len(re.findall(r':type\s+\w+:', doc)),
            ':return': len(re.findall(r':returns?:', doc)),
            ':rtype': len(re.findall(r':rtype:', doc)),
            ':raises': len(re.findall(r':raises?\s+\w+:', doc))
        }
        
        # Structure score based on found sections
        essential_sections = ['parameters', 'returns']
        optional_sections = ['overview', 'examples', 'exceptions', 'notes']
        
        essential_score = sum(sections_found[s] for s in essential_sections) / len(essential_sections)
        optional_score = sum(sections_found[s] for s in optional_sections) / len(optional_sections)
        
        structure_score = (essential_score * 0.7) + (optional_score * 0.3)
        
        return {
            'score': structure_score,
            'sections_found': sections_found,
            'sphinx_directives': sphinx_directives,
            'has_proper_structure': structure_score >= 0.6
        }
    
    @staticmethod
    def evaluate_parameter_documentation(doc: str, actual_params: List[str]) -> Dict[str, Any]:
        """Evaluate quality of parameter documentation
        
        Args:
            doc: Documentation text
            actual_params: List of actual function parameters from code
            
        Returns:
            Dictionary with parameter documentation scores
        """
        # Find documented parameters
        param_pattern = r':param\s+(\w+):\s*(.+?)(?=\n|:type|:param|:return|$)'
        type_pattern = r':type\s+(\w+):\s*(.+?)(?=\n|:param|:type|:return|$)'
        
        documented_params = {m.group(1): m.group(2).strip() for m in re.finditer(param_pattern, doc, re.MULTILINE)}
        documented_types = {m.group(1): m.group(2).strip() for m in re.finditer(type_pattern, doc, re.MULTILINE)}
        
        # Filter out self/cls
        relevant_params = [p for p in actual_params if p not in ['self', 'cls']]
        
        if not relevant_params:
            return {
                'coverage': 1.0,
                'type_coverage': 1.0,
                'quality_score': 1.0,
                'documented_count': 0,
                'missing_params': [],
                'description_quality': 1.0
            }
        
        # Coverage: what percentage of params are documented
        documented_count = sum(1 for p in relevant_params if p in documented_params)
        coverage = documented_count / len(relevant_params)
        
        # Type coverage: what percentage have types
        typed_count = sum(1 for p in relevant_params if p in documented_types)
        type_coverage = typed_count / len(relevant_params)
        
        # Description quality
        description_scores = []
        for param in relevant_params:
            if param in documented_params:
                desc = documented_params[param]
                # Good description: not tautological, > 10 chars, not generic
                score = 0.0
                if len(desc) > 10:
                    score += 0.4
                if not desc.lower().startswith(f"{param}"):
                    score += 0.3
                if any(word in desc.lower() for word in ['for', 'to', 'that', 'which', 'whether']):
                    score += 0.3
                description_scores.append(min(1.0, score))
        
        description_quality = statistics.mean(description_scores) if description_scores else 0.0
        
        # Missing parameters
        missing_params = [p for p in relevant_params if p not in documented_params]
        
        # Overall quality score
        quality_score = (coverage * 0.4) + (type_coverage * 0.3) + (description_quality * 0.3)
        
        return {
            'coverage': coverage,
            'type_coverage': type_coverage,
            'quality_score': quality_score,
            'documented_count': documented_count,
            'missing_params': missing_params,
            'description_quality': description_quality,
            'documented_params': list(documented_params.keys()),
            'typed_params': list(documented_types.keys())
        }
    
    @staticmethod
    def evaluate_type_accuracy(doc: str) -> Dict[str, Any]:
        """Evaluate type annotation quality and accuracy
        
        Checks for:
        - Specific vs generic types
        - Proper type syntax
        - Consistency
        
        Returns:
            Dictionary with type quality metrics
        """
        # Find all type annotations
        type_pattern = r':type\s+\w+:\s*(.+?)(?=\n|:)'
        types_found = [m.group(1).strip() for m in re.finditer(type_pattern, doc, re.MULTILINE)]
        
        if not types_found:
            return {
                'specificity_score': 0.0,
                'generic_count': 0,
                'specific_count': 0,
                'quality_score': 0.0
            }
        
        # Generic/vague types
        generic_types = {'Any', 'object', 'type', 'Any type'}
        vague_descriptions = {'value', 'data', 'parameter', 'argument', 'object'}
        
        generic_count = 0
        specific_count = 0
        specificity_scores = []
        
        for type_annotation in types_found:
            # Check if it's generic
            is_generic = (
                type_annotation in generic_types or
                any(vague in type_annotation.lower() for vague in vague_descriptions)
            )
            
            if is_generic:
                generic_count += 1
                specificity_scores.append(0.0)
            else:
                specific_count += 1
                # Score based on specificity
                score = 0.5  # Base score for non-generic
                
                # Bonus for detailed types
                if any(specific in type_annotation for specific in ['List[', 'Dict[', 'Tuple[', 'Optional[']):
                    score += 0.3
                if re.search(r'\w+\.\w+', type_annotation):  # Module qualified
                    score += 0.2
                
                specificity_scores.append(min(1.0, score))
        
        specificity_score = statistics.mean(specificity_scores)
        
        return {
            'specificity_score': specificity_score,
            'generic_count': generic_count,
            'specific_count': specific_count,
            'quality_score': specificity_score,
            'total_types': len(types_found)
        }
    
    @staticmethod
    def evaluate_description_quality(doc: str, function_name: str) -> Dict[str, Any]:
        """Evaluate quality of function/class descriptions
        
        Checks for:
        - Non-tautological descriptions
        - Meaningful content
        - Technical accuracy indicators
        
        Returns:
            Dictionary with description quality metrics
        """
        # Extract main description (first paragraph)
        lines = [l.strip() for l in doc.split('\n') if l.strip() and not l.strip().startswith(':')]
        if not lines:
            return {'score': 0.0, 'is_tautological': True, 'is_meaningful': False}
        
        main_desc = ' '.join(lines[:3])  # First 3 lines
        
        # Check for tautological descriptions
        func_words = set(function_name.lower().replace('_', ' ').split())
        desc_words = set(w.lower() for w in re.findall(r'\w+', main_desc))
        
        # Remove common filler words
        filler = {'the', 'a', 'an', 'this', 'that', 'for', 'to', 'of', 'in', 'on', 'and', 'or'}
        func_words -= filler
        desc_words -= filler
        
        overlap = len(func_words & desc_words) / max(len(func_words), 1)
        is_tautological = overlap > 0.7 and len(desc_words) <= len(func_words) * 1.5
        
        # Check for meaningful content
        meaningful_indicators = [
            len(main_desc) > 30,  # Sufficient length
            len(desc_words) > len(func_words),  # More than just rephrasing name
            any(word in main_desc.lower() for word in ['by', 'using', 'through', 'via', 'when', 'if']),  # Technical detail
            not main_desc.lower().startswith(function_name.lower()),  # Not just restating name
        ]
        is_meaningful = sum(meaningful_indicators) >= 3
        
        # Calculate score
        score = 0.0
        if not is_tautological:
            score += 0.5
        if is_meaningful:
            score += 0.5
        
        return {
            'score': score,
            'is_tautological': is_tautological,
            'is_meaningful': is_meaningful,
            'word_overlap': overlap,
            'description_length': len(main_desc)
        }
    
    @staticmethod
    def evaluate_technical_accuracy(doc: str) -> Dict[str, Any]:
        """Evaluate technical accuracy indicators
        
        Checks for:
        - Presence of technical terminology
        - Specific vs vague language
        - Concrete vs abstract descriptions
        
        Returns:
            Dictionary with technical accuracy metrics
        """
        # Technical terminology indicators
        technical_terms = [
            'algorithm', 'function', 'method', 'class', 'object', 'instance',
            'parameter', 'argument', 'return', 'value', 'type', 'data',
            'process', 'compute', 'calculate', 'generate', 'parse', 'validate',
            'initialize', 'construct', 'implement', 'execute', 'invoke',
            'exception', 'error', 'handle', 'raise', 'catch'
        ]
        
        term_count = sum(1 for term in technical_terms if term in doc.lower())
        term_density = term_count / max(len(doc.split()), 1)
        
        # Check for specific vs vague language
        vague_terms = ['thing', 'stuff', 'something', 'somehow', 'various', 'several', 'multiple']
        vague_count = sum(1 for term in vague_terms if term in doc.lower())
        
        # Check for concrete descriptions
        concrete_indicators = [
            bool(re.search(r'\d+', doc)),  # Contains numbers
            bool(re.search(r'(true|false|none|null)', doc, re.I)),  # Contains literals
            bool(re.search(r'[<>=!]+', doc)),  # Contains operators
            bool(re.search(r'\[\w+\]', doc)),  # Contains type parameters like List[int]
        ]
        
        concreteness_score = sum(concrete_indicators) / len(concrete_indicators)
        
        # Technical accuracy score
        accuracy_score = (
            min(1.0, term_density * 20) * 0.4 +  # Term density (capped at 5%)
            (1.0 - min(1.0, vague_count / 5)) * 0.3 +  # Inverse vague count
            concreteness_score * 0.3
        )
        
        return {
            'score': accuracy_score,
            'technical_term_count': term_count,
            'term_density': term_density,
            'vague_term_count': vague_count,
            'concreteness_score': concreteness_score
        }
    
    @staticmethod
    def evaluate_sphinx_compliance(doc: str) -> Dict[str, Any]:
        """Evaluate Sphinx/reST format compliance
        
        Checks for:
        - Proper Sphinx directives
        - Correct syntax
        - No forbidden patterns
        
        Returns:
            Dictionary with Sphinx compliance metrics
        """
        issues = []
        warnings = []
        
        # Check for forbidden patterns
        if re.search(r'\*\*Example:\*\*', doc):
            issues.append("Contains '**Example:**' pattern (forbidden in Sphinx docstrings)")
        
        # Check for Markdown instead of reST
        if re.search(r'^#{2,}\s+\w+', doc, re.MULTILINE):
            issues.append("Contains Markdown headers (##, ###) instead of reST format")
        
        if re.search(r'```\w+', doc):
            issues.append("Contains Markdown code blocks (```) instead of reST '.. code-block::'")
        
        # Check for proper Sphinx directive format
        param_count = len(re.findall(r':param\s+\w+:', doc))
        type_count = len(re.findall(r':type\s+\w+:', doc))
        
        if param_count > 0 and type_count == 0:
            warnings.append("Has :param but no :type directives")
        elif type_count > 0 and param_count == 0:
            issues.append("Has :type but no :param directives")
        elif param_count > 0 and type_count > 0 and param_count != type_count:
            warnings.append(f"Mismatched :param ({param_count}) and :type ({type_count}) counts")
        
        # Check for return documentation
        has_return = bool(re.search(r':returns?:', doc))
        has_rtype = bool(re.search(r':rtype:', doc))
        
        if has_return and not has_rtype:
            warnings.append("Has :return but no :rtype")
        elif has_rtype and not has_return:
            warnings.append("Has :rtype but no :return")
        
        compliance_score = 1.0 - (len(issues) * 0.2 + len(warnings) * 0.1)
        compliance_score = max(0.0, compliance_score)
        
        return {
            'score': compliance_score,
            'issues': issues,
            'warnings': warnings,
            'is_compliant': len(issues) == 0,
            'directive_counts': {
                'param': param_count,
                'type': type_count,
                'return': 1 if has_return else 0,
                'rtype': 1 if has_rtype else 0
            }
        }
    
    @classmethod
    def evaluate_comprehensive(
        cls,
        doc: str,
        function_name: str = "",
        actual_params: List[str] = None,
        code_lines: int = 10
    ) -> Dict[str, Any]:
        """Comprehensive technical documentation evaluation
        
        Args:
            doc: Documentation text
            function_name: Name of the function/class being documented
            actual_params: List of actual parameters from code
            code_lines: Number of lines in the documented code
            
        Returns:
            Complete evaluation dictionary with all metrics
        """
        if actual_params is None:
            actual_params = []
        
        results = {
            'length': {
                'characters': len(doc),
                'words': len(doc.split()),
                'lines': len([l for l in doc.split('\n') if l.strip()])
            }
        }
        
        # Run all evaluations
        results['structure'] = cls.evaluate_structure(doc)
        results['parameters'] = cls.evaluate_parameter_documentation(doc, actual_params)
        results['types'] = cls.evaluate_type_accuracy(doc)
        results['description'] = cls.evaluate_description_quality(doc, function_name)
        results['technical_accuracy'] = cls.evaluate_technical_accuracy(doc)
        results['sphinx_compliance'] = cls.evaluate_sphinx_compliance(doc)
        
        # Calculate overall technical quality score
        overall_score = (
            results['structure']['score'] * 0.15 +
            results['parameters']['quality_score'] * 0.25 +
            results['types']['quality_score'] * 0.15 +
            results['description']['score'] * 0.15 +
            results['technical_accuracy']['score'] * 0.15 +
            results['sphinx_compliance']['score'] * 0.15
        )
        
        results['overall_technical_quality'] = overall_score
        
        # Generate quality level
        if overall_score >= 0.8:
            quality_level = "Excellent"
        elif overall_score >= 0.6:
            quality_level = "Good"
        elif overall_score >= 0.4:
            quality_level = "Fair"
        else:
            quality_level = "Poor"
        
        results['quality_level'] = quality_level
        
        return results
    
    @staticmethod
    def format_report(results: Dict[str, Any]) -> str:
        """Format comprehensive evaluation as readable report
        
        Args:
            results: Results from evaluate_comprehensive
            
        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 70)
        report.append("📊 TECHNICAL DOCUMENTATION QUALITY EVALUATION")
        report.append("=" * 70)
        
        # Overall Score
        overall = results['overall_technical_quality']
        quality = results['quality_level']
        report.append(f"\n🎯 Overall Technical Quality: {overall:.1%} ({quality})")
        report.append("")
        
        # Structure
        struct = results['structure']
        report.append("📐 Structure & Organization:")
        report.append(f"   Score: {struct['score']:.1%}")
        report.append(f"   Sections: {sum(struct['sections_found'].values())}/6 found")
        if struct['sphinx_directives']:
            total_directives = sum(struct['sphinx_directives'].values())
            report.append(f"   Sphinx Directives: {total_directives} total")
        
        # Parameters
        params = results['parameters']
        report.append(f"\n📝 Parameter Documentation:")
        report.append(f"   Coverage: {params['coverage']:.1%} ({params['documented_count']} documented)")
        report.append(f"   Type Coverage: {params['type_coverage']:.1%}")
        report.append(f"   Description Quality: {params['description_quality']:.1%}")
        if params['missing_params']:
            report.append(f"   ⚠️  Missing: {', '.join(params['missing_params'])}")
        
        # Types
        types = results['types']
        if types['total_types'] > 0:
            report.append(f"\n🏷️  Type Quality:")
            report.append(f"   Specificity: {types['specificity_score']:.1%}")
            report.append(f"   Specific: {types['specific_count']}, Generic: {types['generic_count']}")
        
        # Description
        desc = results['description']
        report.append(f"\n📖 Description Quality:")
        report.append(f"   Score: {desc['score']:.1%}")
        report.append(f"   Tautological: {'Yes ⚠️' if desc['is_tautological'] else 'No ✓'}")
        report.append(f"   Meaningful: {'Yes ✓' if desc['is_meaningful'] else 'No ⚠️'}")
        
        # Technical Accuracy
        tech = results['technical_accuracy']
        report.append(f"\n🔬 Technical Accuracy:")
        report.append(f"   Score: {tech['score']:.1%}")
        report.append(f"   Technical Terms: {tech['technical_term_count']}")
        report.append(f"   Concreteness: {tech['concreteness_score']:.1%}")
        
        # Sphinx Compliance
        sphinx = results['sphinx_compliance']
        report.append(f"\n✨ Sphinx Compliance:")
        report.append(f"   Score: {sphinx['score']:.1%}")
        report.append(f"   Compliant: {'Yes ✓' if sphinx['is_compliant'] else 'No ⚠️'}")
        if sphinx['issues']:
            report.append("   Issues:")
            for issue in sphinx['issues']:
                report.append(f"      - {issue}")
        if sphinx['warnings']:
            report.append("   Warnings:")
            for warning in sphinx['warnings']:
                report.append(f"      - {warning}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


# Convenience function for quick evaluation
def evaluate_technical_docs(
    doc: str,
    function_name: str = "",
    parameters: List[str] = None
) -> str:
    """Quick evaluation of technical documentation with formatted report
    
    Args:
        doc: Documentation string
        function_name: Name of function/class
        parameters: List of parameter names
        
    Returns:
        Formatted evaluation report
    """
    evaluator = TechnicalDocumentationEvaluator()
    results = evaluator.evaluate_comprehensive(doc, function_name, parameters or [])
    return evaluator.format_report(results)
