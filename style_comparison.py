"""
Documentation Style Comparison Framework
Generates comprehensive comparison tables for all documentation styles
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class AudienceLevel(Enum):
    """Target audience experience level"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
    MIXED = "Mixed"

class VerbosityLevel(Enum):
    """Documentation verbosity level"""
    MINIMAL = "Minimal"
    CONCISE = "Concise"
    MODERATE = "Moderate"
    DETAILED = "Detailed"
    COMPREHENSIVE = "Comprehensive"

class TechnicalDepth(Enum):
    """Technical detail level"""
    HIGH_LEVEL = "High-level Overview"
    STANDARD = "Standard Technical"
    DETAILED = "Detailed Technical"
    COMPREHENSIVE = "Comprehensive Analysis"
    EXPERT = "Expert-level Deep Dive"

@dataclass
class DocumentationStyleProfile:
    """Profile for a documentation style"""
    name: str
    description: str
    target_audience: List[AudienceLevel]
    verbosity: VerbosityLevel
    technical_depth: TechnicalDepth
    structure_type: str  # Narrative, Reference, Hybrid, Visual
    includes_examples: bool
    includes_diagrams: bool
    includes_metrics: bool
    best_for: List[str]
    not_recommended_for: List[str]
    typical_length: str  # Short, Medium, Long, Very Long
    readability_target: str  # Grade level or description
    key_features: List[str]
    output_format: str  # Docstring, Markdown, Mixed
    
class DocumentationStyleComparator:
    """Generate comprehensive comparisons between documentation styles"""
    
    # Define profiles for all 8 documentation styles
    STYLE_PROFILES = {
        'google': DocumentationStyleProfile(
            name='Google Style',
            description='Clean, structured docstrings following Google Python Style Guide',
            target_audience=[AudienceLevel.INTERMEDIATE, AudienceLevel.ADVANCED],
            verbosity=VerbosityLevel.MODERATE,
            technical_depth=TechnicalDepth.STANDARD,
            structure_type='Reference',
            includes_examples=True,
            includes_diagrams=False,
            includes_metrics=False,
            best_for=[
                'Python projects',
                'Internal APIs',
                'Team collaboration',
                'IDE integration',
                'Code reviews'
            ],
            not_recommended_for=[
                'Non-Python projects',
                'Public documentation websites',
                'Beginner tutorials',
                'Complex system architecture'
            ],
            typical_length='Medium',
            readability_target='10th-12th grade',
            key_features=[
                'Args/Returns/Raises sections',
                'Type annotations',
                'Example code blocks',
                'Clear parameter descriptions',
                'Consistent formatting'
            ],
            output_format='Docstring'
        ),
        
        'numpy': DocumentationStyleProfile(
            name='NumPy Style',
            description='Detailed scientific documentation with parameter tables',
            target_audience=[AudienceLevel.ADVANCED, AudienceLevel.EXPERT],
            verbosity=VerbosityLevel.DETAILED,
            technical_depth=TechnicalDepth.DETAILED,
            structure_type='Reference',
            includes_examples=True,
            includes_diagrams=False,
            includes_metrics=False,
            best_for=[
                'Scientific computing',
                'Data science libraries',
                'Mathematical functions',
                'Research code',
                'Academic projects'
            ],
            not_recommended_for=[
                'Simple utility functions',
                'Web applications',
                'Quick scripts',
                'Beginner-friendly docs'
            ],
            typical_length='Long',
            readability_target='College graduate',
            key_features=[
                'Parameter tables',
                'Mathematical notation support',
                'Detailed type information',
                'References section',
                'Notes and warnings'
            ],
            output_format='Docstring'
        ),
        
        'technical_md': DocumentationStyleProfile(
            name='Technical Markdown',
            description='Comprehensive technical documentation in Markdown format',
            target_audience=[AudienceLevel.INTERMEDIATE, AudienceLevel.ADVANCED, AudienceLevel.EXPERT],
            verbosity=VerbosityLevel.COMPREHENSIVE,
            technical_depth=TechnicalDepth.COMPREHENSIVE,
            structure_type='Hybrid',
            includes_examples=True,
            includes_diagrams=False,
            includes_metrics=True,
            best_for=[
                'API documentation',
                'Technical specifications',
                'Design documents',
                'Architecture reviews',
                'Documentation websites'
            ],
            not_recommended_for=[
                'Quick reference',
                'IDE tooltips',
                'Inline code comments',
                'Beginner tutorials'
            ],
            typical_length='Very Long',
            readability_target='College level',
            key_features=[
                'Markdown formatting',
                'Complexity metrics',
                'Dependencies section',
                'Edge cases',
                'Performance notes',
                'Security considerations'
            ],
            output_format='Markdown'
        ),
        
        'opensource': DocumentationStyleProfile(
            name='Open Source',
            description='Community-friendly documentation for open source projects',
            target_audience=[AudienceLevel.BEGINNER, AudienceLevel.INTERMEDIATE, AudienceLevel.MIXED],
            verbosity=VerbosityLevel.MODERATE,
            technical_depth=TechnicalDepth.STANDARD,
            structure_type='Narrative',
            includes_examples=True,
            includes_diagrams=False,
            includes_metrics=False,
            best_for=[
                'Open source libraries',
                'Community projects',
                'Public APIs',
                'Getting started guides',
                'Contributor documentation'
            ],
            not_recommended_for=[
                'Internal enterprise code',
                'Highly specialized systems',
                'Security-sensitive code',
                'Low-level implementations'
            ],
            typical_length='Medium',
            readability_target='8th-10th grade',
            key_features=[
                'Friendly tone',
                'Real-world examples',
                'Common use cases',
                'Troubleshooting tips',
                'Related resources'
            ],
            output_format='Mixed'
        ),
        
        'api': DocumentationStyleProfile(
            name='API Reference',
            description='Concise API reference documentation',
            target_audience=[AudienceLevel.INTERMEDIATE, AudienceLevel.ADVANCED],
            verbosity=VerbosityLevel.MINIMAL,
            technical_depth=TechnicalDepth.STANDARD,
            structure_type='Reference',
            includes_examples=False,
            includes_diagrams=False,
            includes_metrics=False,
            best_for=[
                'REST APIs',
                'SDK documentation',
                'Function libraries',
                'Quick reference',
                'Auto-generated docs'
            ],
            not_recommended_for=[
                'Complex algorithms',
                'System design',
                'Beginner tutorials',
                'Architectural documentation'
            ],
            typical_length='Short',
            readability_target='Professional developers',
            key_features=[
                'One-line summaries',
                'Type signatures',
                'Return values',
                'HTTP methods (for REST)',
                'Status codes'
            ],
            output_format='Docstring'
        ),
        
        'visual_flow': DocumentationStyleProfile(
            name='Visual Flow',
            description='Comprehensive documentation with ASCII diagrams and visual representations',
            target_audience=[AudienceLevel.INTERMEDIATE, AudienceLevel.ADVANCED, AudienceLevel.EXPERT],
            verbosity=VerbosityLevel.COMPREHENSIVE,
            technical_depth=TechnicalDepth.COMPREHENSIVE,
            structure_type='Visual',
            includes_examples=True,
            includes_diagrams=True,
            includes_metrics=True,
            best_for=[
                'System architecture',
                'Complex workflows',
                'State machines',
                'Data flow visualization',
                'Module interactions',
                'Understanding complex code'
            ],
            not_recommended_for=[
                'Simple functions',
                'Quick reference',
                'Mobile viewing',
                'Print documentation'
            ],
            typical_length='Very Long',
            readability_target='Visual learners, all levels',
            key_features=[
                'ASCII diagrams',
                'State machines',
                'Execution flow charts',
                'Module interaction diagrams',
                'Data flow visualization',
                'Metrics panels',
                'Call hierarchy trees'
            ],
            output_format='Markdown'
        ),
        
        'repoagent': DocumentationStyleProfile(
            name='RepoAgent Style',
            description='Structured documentation with ClassDef/FunctionDef sections',
            target_audience=[AudienceLevel.INTERMEDIATE, AudienceLevel.ADVANCED],
            verbosity=VerbosityLevel.CONCISE,
            technical_depth=TechnicalDepth.DETAILED,
            structure_type='Reference',
            includes_examples=False,
            includes_diagrams=False,
            includes_metrics=False,
            best_for=[
                'Large codebases',
                'Repository documentation',
                'Code understanding',
                'AI/ML training data',
                'Code navigation'
            ],
            not_recommended_for=[
                'User-facing docs',
                'Tutorials',
                'Getting started guides',
                'End-user documentation'
            ],
            typical_length='Medium',
            readability_target='Developers familiar with codebase',
            key_features=[
                'ClassDef sections',
                'FunctionDef sections',
                'Object-oriented focus',
                'Structured format',
                'Relationship mapping'
            ],
            output_format='Structured Text'
        ),
        
        'hybrid': DocumentationStyleProfile(
            name='Hybrid RepoAgent+Metrics',
            description='Combines RepoAgent structure with comprehensive metrics',
            target_audience=[AudienceLevel.ADVANCED, AudienceLevel.EXPERT],
            verbosity=VerbosityLevel.DETAILED,
            technical_depth=TechnicalDepth.EXPERT,
            structure_type='Hybrid',
            includes_examples=True,
            includes_diagrams=False,
            includes_metrics=True,
            best_for=[
                'Code quality analysis',
                'Technical debt assessment',
                'Refactoring planning',
                'Architecture review',
                'Performance optimization'
            ],
            not_recommended_for=[
                'Beginner documentation',
                'User manuals',
                'Quick reference',
                'Tutorial content'
            ],
            typical_length='Long',
            readability_target='Senior developers, architects',
            key_features=[
                'Complexity metrics',
                'Coupling analysis',
                'Coverage statistics',
                'Maintainability index',
                'Code quality scores',
                'Structured sections'
            ],
            output_format='Mixed'
        ),
        
        'human_friendly': DocumentationStyleProfile(
            name='Human-Friendly',
            description='Conversational documentation with practical tips and real examples',
            target_audience=[AudienceLevel.BEGINNER, AudienceLevel.INTERMEDIATE, AudienceLevel.MIXED],
            verbosity=VerbosityLevel.DETAILED,
            technical_depth=TechnicalDepth.STANDARD,
            structure_type='Narrative',
            includes_examples=True,
            includes_diagrams=False,
            includes_metrics=False,
            best_for=[
                'Learning resources',
                'Onboarding documentation',
                'Tutorial content',
                'Getting started guides',
                'Developer education'
            ],
            not_recommended_for=[
                'API reference',
                'Technical specifications',
                'Low-level system docs',
                'Formal documentation'
            ],
            typical_length='Long',
            readability_target='6th-8th grade',
            key_features=[
                'Conversational tone',
                'Practical examples',
                'Pro tips',
                '"What it does" sections',
                '"When to use" guidance',
                'Real-world scenarios',
                'Developer insights'
            ],
            output_format='Markdown'
        )
    }
    
    @classmethod
    def generate_comparison_table(cls, format='markdown') -> str:
        """Generate comprehensive comparison table"""
        if format == 'markdown':
            return cls._generate_markdown_table()
        elif format == 'html':
            return cls._generate_html_table()
        else:
            return cls._generate_text_table()
    
    @classmethod
    def _generate_markdown_table(cls) -> str:
        """Generate Markdown comparison table"""
        lines = []
        lines.append("# Documentation Styles Comprehensive Comparison\n")
        lines.append("## Overview Table\n")
        
        # Main comparison table
        lines.append("| Style | Target Audience | Verbosity | Technical Depth | Examples | Diagrams | Metrics |")
        lines.append("|-------|----------------|-----------|-----------------|----------|----------|---------|")
        
        for style_key, profile in cls.STYLE_PROFILES.items():
            audience = ", ".join([a.value for a in profile.target_audience])
            lines.append(
                f"| **{profile.name}** | {audience} | {profile.verbosity.value} | "
                f"{profile.technical_depth.value} | {'✅' if profile.includes_examples else '❌'} | "
                f"{'✅' if profile.includes_diagrams else '❌'} | {'✅' if profile.includes_metrics else '❌'} |"
            )
        
        # Detailed sections for each style
        lines.append("\n## Detailed Style Profiles\n")
        
        for style_key, profile in cls.STYLE_PROFILES.items():
            lines.append(f"### {profile.name}\n")
            lines.append(f"**Description:** {profile.description}\n")
            lines.append(f"**Structure Type:** {profile.structure_type}\n")
            lines.append(f"**Typical Length:** {profile.typical_length}\n")
            lines.append(f"**Readability Target:** {profile.readability_target}\n")
            lines.append(f"**Output Format:** {profile.output_format}\n")
            
            lines.append("\n**Key Features:**")
            for feature in profile.key_features:
                lines.append(f"- {feature}")
            
            lines.append("\n**Best For:**")
            for use_case in profile.best_for:
                lines.append(f"- {use_case}")
            
            lines.append("\n**Not Recommended For:**")
            for use_case in profile.not_recommended_for:
                lines.append(f"- {use_case}")
            
            lines.append("\n---\n")
        
        # Use case matrix
        lines.append("## Use Case Matrix\n")
        lines.append("| Use Case | Recommended Styles | Avoid |")
        lines.append("|----------|-------------------|-------|")
        
        use_cases = {
            'API Documentation': (['API Reference', 'Technical Markdown'], ['Visual Flow', 'Human-Friendly']),
            'Beginner Tutorials': (['Human-Friendly', 'Open Source'], ['NumPy', 'Hybrid']),
            'Scientific Computing': (['NumPy', 'Technical Markdown'], ['API Reference', 'Open Source']),
            'System Architecture': (['Visual Flow', 'Technical Markdown'], ['API Reference', 'Google']),
            'Code Quality Analysis': (['Hybrid', 'Technical Markdown'], ['Open Source', 'Human-Friendly']),
            'Open Source Projects': (['Open Source', 'Google'], ['RepoAgent', 'Hybrid']),
            'Quick Reference': (['API Reference', 'Google'], ['Visual Flow', 'NumPy']),
            'Team Collaboration': (['Google', 'Technical Markdown'], ['Human-Friendly', 'Visual Flow']),
            'Learning Resources': (['Human-Friendly', 'Open Source'], ['API Reference', 'RepoAgent']),
            'Enterprise Internal': (['Technical Markdown', 'Google'], ['Open Source', 'Human-Friendly'])
        }
        
        for use_case, (recommended, avoid) in use_cases.items():
            lines.append(f"| {use_case} | {', '.join(recommended)} | {', '.join(avoid)} |")
        
        # Metrics comparison
        lines.append("\n## Documentation Characteristics\n")
        lines.append("| Style | Avg Length (chars) | Readability Score | Completeness | Learning Curve |")
        lines.append("|-------|-------------------|------------------|--------------|----------------|")
        
        characteristics = {
            'Google Style': (1500, 'Medium (60-70)', 'High', 'Low'),
            'NumPy Style': (2500, 'Low (40-50)', 'Very High', 'Medium'),
            'Technical Markdown': (3500, 'Medium (50-60)', 'Very High', 'High'),
            'Open Source': (2000, 'High (70-80)', 'Medium', 'Low'),
            'API Reference': (500, 'High (70-80)', 'Medium', 'Very Low'),
            'Visual Flow': (5000, 'Visual (varies)', 'Very High', 'Medium'),
            'RepoAgent Style': (1000, 'Medium (60-70)', 'High', 'Medium'),
            'Hybrid RepoAgent+Metrics': (2500, 'Low (50-60)', 'Very High', 'High'),
            'Human-Friendly': (3000, 'Very High (75-85)', 'High', 'Very Low')
        }
        
        for style, (length, readability, completeness, learning) in characteristics.items():
            lines.append(f"| {style} | ~{length} | {readability} | {completeness} | {learning} |")
        
        return '\n'.join(lines)
    
    @classmethod
    def compare_styles(cls, style1: str, style2: str) -> Dict[str, Any]:
        """Compare two specific documentation styles"""
        if style1 not in cls.STYLE_PROFILES or style2 not in cls.STYLE_PROFILES:
            return {'error': 'Invalid style name'}
        
        profile1 = cls.STYLE_PROFILES[style1]
        profile2 = cls.STYLE_PROFILES[style2]
        
        comparison = {
            'style1': profile1.name,
            'style2': profile2.name,
            'similarities': [],
            'differences': {},
            'recommendation': ''
        }
        
        # Find similarities
        if profile1.verbosity == profile2.verbosity:
            comparison['similarities'].append(f"Same verbosity level ({profile1.verbosity.value})")
        if profile1.technical_depth == profile2.technical_depth:
            comparison['similarities'].append(f"Same technical depth ({profile1.technical_depth.value})")
        if profile1.includes_examples == profile2.includes_examples:
            comparison['similarities'].append("Both include/exclude examples")
        
        # Find differences
        comparison['differences']['verbosity'] = {
            'style1': profile1.verbosity.value,
            'style2': profile2.verbosity.value
        }
        comparison['differences']['technical_depth'] = {
            'style1': profile1.technical_depth.value,
            'style2': profile2.technical_depth.value
        }
        comparison['differences']['typical_length'] = {
            'style1': profile1.typical_length,
            'style2': profile2.typical_length
        }
        
        # Generate recommendation
        if profile1.verbosity.value < profile2.verbosity.value:
            comparison['recommendation'] = f"Use {profile1.name} for concise docs, {profile2.name} for detailed docs"
        else:
            comparison['recommendation'] = f"Use {profile2.name} for concise docs, {profile1.name} for detailed docs"
        
        return comparison
    
    @classmethod
    def recommend_style(cls, requirements: Dict[str, Any]) -> List[str]:
        """
        Recommend documentation styles based on requirements
        
        Args:
            requirements: Dict with keys like 'audience', 'needs_examples', 'needs_diagrams', etc.
        
        Returns:
            List of recommended style names
        """
        recommendations = []
        
        audience = requirements.get('audience', 'intermediate').lower()
        needs_examples = requirements.get('needs_examples', False)
        needs_diagrams = requirements.get('needs_diagrams', False)
        needs_metrics = requirements.get('needs_metrics', False)
        project_type = requirements.get('project_type', '').lower()
        
        for style_key, profile in cls.STYLE_PROFILES.items():
            score = 0
            
            # Check audience match
            if 'beginner' in audience and AudienceLevel.BEGINNER in profile.target_audience:
                score += 3
            elif 'intermediate' in audience and AudienceLevel.INTERMEDIATE in profile.target_audience:
                score += 3
            elif 'advanced' in audience and AudienceLevel.ADVANCED in profile.target_audience:
                score += 3
            
            # Check features
            if needs_examples and profile.includes_examples:
                score += 2
            if needs_diagrams and profile.includes_diagrams:
                score += 2
            if needs_metrics and profile.includes_metrics:
                score += 2
            
            # Check project type
            if project_type:
                if project_type in ' '.join(profile.best_for).lower():
                    score += 3
            
            if score >= 5:  # Threshold for recommendation
                recommendations.append((profile.name, score))
        
        # Sort by score and return top 3
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in recommendations[:3]]
