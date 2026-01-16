"""
Multi-Language Documentation Testing Framework
Tests all documentation styles across multiple programming languages
"""

import os
import json
from typing import Dict, List, Any
from multi_language_analyzer import MultiLanguageAnalyzer
from evaluation_metrics import DocumentationQualityMetrics, ReadabilityMetrics
from style_comparison import DocumentationStyleComparator

class DocumentationTester:
    """Test documentation generation across languages and styles"""
    
    def __init__(self):
        self.analyzer = MultiLanguageAnalyzer()
        self.results = {}
    
    def test_all_styles_all_languages(self, samples_dir: str) -> Dict[str, Any]:
        """
        Test all documentation styles on all sample files
        
        Args:
            samples_dir: Directory containing sample code files
        
        Returns:
            Comprehensive test results
        """
        results = {
            'summary': {},
            'by_language': {},
            'by_style': {},
            'metrics_comparison': {}
        }
        
        # Find all sample files
        sample_files = self._find_sample_files(samples_dir)
        
        print(f"Found {len(sample_files)} sample files")
        
        for file_path, language in sample_files:
            print(f"\nTesting {language}: {os.path.basename(file_path)}")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Analyze the file
            analysis = self.analyzer.analyze_file(file_path, content)
            
            if language not in results['by_language']:
                results['by_language'][language] = {
                    'files_tested': 0,
                    'functions_found': 0,
                    'classes_found': 0,
                    'documentation_generated': {}
                }
            
            results['by_language'][language]['files_tested'] += 1
            results['by_language'][language]['functions_found'] += len(analysis['functions'])
            results['by_language'][language]['classes_found'] += len(analysis['classes'])
            
            # Test each function/class with each documentation style
            for func in analysis['functions']:
                self._test_function_documentation(func, results)
        
        # Calculate summary statistics
        results['summary'] = self._calculate_summary(results)
        
        return results
    
    def _find_sample_files(self, samples_dir: str) -> List[tuple]:
        """Find all sample code files in directory"""
        from multi_language_analyzer import LanguageDetector
        
        sample_files = []
        
        if not os.path.exists(samples_dir):
            print(f"Warning: {samples_dir} does not exist")
            return sample_files
        
        for filename in os.listdir(samples_dir):
            file_path = os.path.join(samples_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                language = LanguageDetector.detect(filename, content)
                if language != 'unknown':
                    sample_files.append((file_path, language))
        
        return sample_files
    
    def _test_function_documentation(self, func, results: Dict):
        """Test documentation generation for a function"""
        # This would integrate with the actual documentation generator
        # For now, we'll create sample documentation
        
        sample_docs = {
            'google': self._generate_sample_doc(func, 'google'),
            'numpy': self._generate_sample_doc(func, 'numpy'),
            'technical_md': self._generate_sample_doc(func, 'technical_md'),
            'opensource': self._generate_sample_doc(func, 'opensource'),
            'api': self._generate_sample_doc(func, 'api'),
        }
        
        # Evaluate each style
        for style, doc in sample_docs.items():
            if style not in results['by_style']:
                results['by_style'][style] = {
                    'total_generated': 0,
                    'avg_readability': 0,
                    'avg_completeness': 0,
                    'avg_length': 0,
                    'scores': []
                }
            
            # Calculate metrics
            params = [p[0] for p in func.params]
            metrics = DocumentationQualityMetrics.evaluate_documentation(
                doc,
                function_params=params,
                code_lines=func.line_end - func.line_start + 1
            )
            
            results['by_style'][style]['total_generated'] += 1
            results['by_style'][style]['scores'].append(metrics)
    
    def _generate_sample_doc(self, func, style: str) -> str:
        """Generate sample documentation (placeholder)"""
        # This is a simplified version - would integrate with actual generator
        
        if style == 'google':
            return f"""
{func.name}({', '.join([p[0] for p in func.params])})

Brief description of what this function does.

Args:
{chr(10).join([f'    {p[0]}: Description of {p[0]}' for p in func.params])}

Returns:
    {func.return_type or 'None'}: Description of return value

Example:
    >>> {func.name}(...)
    result
"""
        elif style == 'numpy':
            return f"""
{func.name}

Detailed description of the function.

Parameters
----------
{chr(10).join([f'{p[0]} : {p[1] or "type"}' + chr(10) + f'    Description of {p[0]}' for p in func.params])}

Returns
-------
{func.return_type or 'None'}
    Description of return value

Examples
--------
>>> {func.name}(...)
result
"""
        elif style == 'api':
            params_str = ', '.join([f"{p[0]}: {p[1] or 'any'}" for p in func.params])
            return f"{func.name}({params_str}) -> {func.return_type or 'None'}"
        
        # Default
        return f"Function {func.name} with {len(func.params)} parameters"
    
    def _calculate_summary(self, results: Dict) -> Dict:
        """Calculate summary statistics"""
        summary = {
            'total_languages': len(results['by_language']),
            'total_styles': len(results['by_style']),
            'total_functions_tested': 0,
            'best_style_by_readability': None,
            'best_style_by_completeness': None,
            'style_rankings': []
        }
        
        # Aggregate function counts
        for lang_data in results['by_language'].values():
            summary['total_functions_tested'] += lang_data['functions_found']
        
        # Calculate average scores for each style
        style_averages = []
        for style, data in results['by_style'].items():
            if data['scores']:
                avg_readability = sum(
                    s['readability']['flesch_reading_ease'] for s in data['scores']
                ) / len(data['scores'])
                
                avg_completeness = sum(
                    s['completeness'] for s in data['scores']
                ) / len(data['scores'])
                
                avg_overall = sum(
                    s['overall_score'] for s in data['scores']
                ) / len(data['scores'])
                
                style_averages.append({
                    'style': style,
                    'avg_readability': avg_readability,
                    'avg_completeness': avg_completeness,
                    'avg_overall': avg_overall
                })
        
        # Find best styles
        if style_averages:
            best_readability = max(style_averages, key=lambda x: x['avg_readability'])
            summary['best_style_by_readability'] = best_readability['style']
            
            best_completeness = max(style_averages, key=lambda x: x['avg_completeness'])
            summary['best_style_by_completeness'] = best_completeness['style']
            
            # Overall rankings
            style_averages.sort(key=lambda x: x['avg_overall'], reverse=True)
            summary['style_rankings'] = [s['style'] for s in style_averages]
        
        return summary
    
    def generate_report(self, results: Dict, output_file: str):
        """Generate comprehensive test report"""
        lines = []
        
        lines.append("# Multi-Language Documentation Testing Report\n")
        lines.append(f"## Summary\n")
        lines.append(f"- **Languages Tested:** {results['summary']['total_languages']}")
        lines.append(f"- **Documentation Styles:** {results['summary']['total_styles']}")
        lines.append(f"- **Functions Tested:** {results['summary']['total_functions_tested']}")
        lines.append(f"- **Best for Readability:** {results['summary'].get('best_style_by_readability', 'N/A')}")
        lines.append(f"- **Best for Completeness:** {results['summary'].get('best_style_by_completeness', 'N/A')}\n")
        
        # Language breakdown
        lines.append("## Language Breakdown\n")
        lines.append("| Language | Files | Functions | Classes |")
        lines.append("|----------|-------|-----------|---------|")
        for lang, data in results['by_language'].items():
            lines.append(
                f"| {lang} | {data['files_tested']} | "
                f"{data['functions_found']} | {data['classes_found']} |"
            )
        
        # Style performance
        lines.append("\n## Documentation Style Performance\n")
        lines.append("| Style | Docs Generated | Avg Readability | Avg Completeness | Overall Score |")
        lines.append("|-------|----------------|-----------------|------------------|---------------|")
        
        for style, data in results['by_style'].items():
            if data['scores']:
                avg_read = sum(s['readability']['flesch_reading_ease'] for s in data['scores']) / len(data['scores'])
                avg_comp = sum(s['completeness'] for s in data['scores']) / len(data['scores'])
                avg_overall = sum(s['overall_score'] for s in data['scores']) / len(data['scores'])
                
                lines.append(
                    f"| {style} | {data['total_generated']} | "
                    f"{avg_read:.1f} | {avg_comp:.2f} | {avg_overall:.2f} |"
                )
        
        # Style rankings
        if results['summary'].get('style_rankings'):
            lines.append("\n## Overall Style Rankings\n")
            for i, style in enumerate(results['summary']['style_rankings'], 1):
                lines.append(f"{i}. {style}")
        
        # Write report
        report_content = '\n'.join(lines)
        with open(output_file, 'w') as f:
            f.write(report_content)
        
        print(f"\nReport saved to: {output_file}")
        return report_content

def main():
    """Run comprehensive documentation tests"""
    print("=" * 80)
    print("MULTI-LANGUAGE DOCUMENTATION TESTING FRAMEWORK")
    print("=" * 80)
    
    tester = DocumentationTester()
    
    # Test on sample files
    samples_dir = 'samples'
    print(f"\nTesting documentation generation on samples in: {samples_dir}")
    
    results = tester.test_all_styles_all_languages(samples_dir)
    
    # Generate report
    report = tester.generate_report(results, 'documentation_test_report.md')
    
    # Generate style comparison
    print("\nGenerating style comparison table...")
    comparison = DocumentationStyleComparator.generate_comparison_table()
    with open('style_comparison_table.md', 'w') as f:
        f.write(comparison)
    print("Style comparison saved to: style_comparison_table.md")
    
    # Test style recommendation
    print("\n" + "=" * 80)
    print("STYLE RECOMMENDATION EXAMPLES")
    print("=" * 80)
    
    test_cases = [
        {
            'name': 'Beginner Tutorial',
            'requirements': {
                'audience': 'beginner',
                'needs_examples': True,
                'project_type': 'tutorial'
            }
        },
        {
            'name': 'API Documentation',
            'requirements': {
                'audience': 'intermediate',
                'needs_examples': False,
                'project_type': 'api'
            }
        },
        {
            'name': 'Scientific Library',
            'requirements': {
                'audience': 'advanced',
                'needs_examples': True,
                'needs_metrics': True,
                'project_type': 'scientific'
            }
        },
        {
            'name': 'System Architecture',
            'requirements': {
                'audience': 'expert',
                'needs_diagrams': True,
                'needs_metrics': True,
                'project_type': 'architecture'
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        recommendations = DocumentationStyleComparator.recommend_style(test_case['requirements'])
        print(f"Recommended styles: {', '.join(recommendations)}")
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
