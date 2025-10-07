#!/usr/bin/env python3
"""
Comprehensive Test Suite for Advanced Documentation Generator
Tests all new features: Google/NumPy/Technical MD/Open Source styles,
multi-input handling, dependency analysis, and CodeSearchNet integration
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def test_all_documentation_styles():
    """Test all documentation styles with sample code"""
    
    print("🧪 Testing All Documentation Styles")
    print("=" * 50)
    
    # Sample test code
    test_code = '''
import numpy as np
import pandas as pd
from flask import Flask, jsonify
from typing import List, Dict, Optional

app = Flask(__name__)

class DataProcessor:
    """
    Advanced data processing engine for machine learning workflows.
    
    This class provides comprehensive data transformation and analysis
    capabilities for various data science applications.
    """
    
    def __init__(self, config: Dict[str, any]):
        """Initialize the data processor with configuration."""
        self.config = config
        self.processed_data = None
    
    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform input data using configured parameters.
        
        Args:
            data: Input pandas DataFrame to transform
            
        Returns:
            Transformed DataFrame with processed features
        """
        multiplier = self.config.get('multiplier', 1.0)
        data_transformed = data * multiplier
        self.processed_data = data_transformed
        return data_transformed
    
    def analyze_patterns(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analyze statistical patterns in the data."""
        return {
            'mean': data.mean().mean(),
            'std': data.std().mean(),
            'correlation': data.corr().mean().mean()
        }

@app.route('/api/data/<dataset_id>')
def get_processed_data(dataset_id: str) -> Dict:
    """
    API endpoint to retrieve processed data for a specific dataset.
    
    Args:
        dataset_id: Unique identifier for the dataset
        
    Returns:
        JSON response containing processed data and metadata
    """
    processor = DataProcessor({'multiplier': 2.0})
    
    # Load sample data
    sample_data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, 100),
        'feature2': np.random.normal(0, 1, 100)
    })
    
    # Process data
    processed = processor.transform_data(sample_data)
    patterns = processor.analyze_patterns(processed)
    
    return jsonify({
        'dataset_id': dataset_id,
        'processed_data': processed.to_dict(),
        'patterns': patterns,
        'status': 'success'
    })

def calculate_model_accuracy(predictions: List[float], 
                           actual: List[float]) -> float:
    """
    Calculate model accuracy using mean absolute error.
    
    Args:
        predictions: Model predictions
        actual: Actual values
        
    Returns:
        Accuracy score (1 - normalized MAE)
    """
    if len(predictions) != len(actual):
        raise ValueError("Predictions and actual values must have same length")
    
    mae = np.mean(np.abs(np.array(predictions) - np.array(actual)))
    max_val = max(max(predictions), max(actual))
    normalized_mae = mae / max_val if max_val > 0 else 0
    
    return 1 - normalized_mae

def setup_database_connection(host: str, port: int = 5432) -> Optional[object]:
    """Setup database connection with error handling."""
    try:
        # Simulated database connection
        connection = {
            'host': host,
            'port': port,
            'status': 'connected'
        }
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    '''
    
    try:
        from comprehensive_docs_advanced import DocumentationGenerator
        
        generator = DocumentationGenerator()
        
        # Test all styles
        styles = [
            'google',
            'numpy', 
            'technical_md',
            'opensource',
            'api',
            'comprehensive'
        ]
        
        context = "Advanced Flask web application with data science capabilities, featuring machine learning data processing, statistical analysis, and RESTful API endpoints for dataset management."
        
        results = {}
        
        for style in styles:
            print(f"\n📝 Testing {style.upper()} style...")
            
            try:
                docs = generator.generate_documentation(
                    test_code,
                    context,
                    style,
                    'code',
                    'MLWebApp'
                )
                
                results[style] = {
                    'success': True,
                    'length': len(docs),
                    'preview': docs[:200] + "..." if len(docs) > 200 else docs
                }
                
                print(f"✅ {style}: Generated {len(docs)} characters")
                print(f"Preview: {docs[:100]}...")
                
            except Exception as e:
                results[style] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"❌ {style}: Failed - {e}")
        
        return results
        
    except ImportError as e:
        print(f"❌ Advanced generator not available: {e}")
        return None

def test_multi_input_processing():
    """Test multiple input types: code, git repos, zip files"""
    
    print("\\n🔄 Testing Multi-Input Processing")
    print("=" * 50)
    
    try:
        from comprehensive_docs_advanced import MultiInputHandler
        
        # Test 1: Code input
        print("\\n📄 Testing code input...")
        test_code = '''
def hello_world():
    """Simple greeting function."""
    return "Hello, World!"
        '''
        
        result = MultiInputHandler.process_input(test_code, 'code')
        print(f"✅ Code input: {len(result)} files processed")
        
        # Test 2: Git repo (if network available)
        print("\\n🌐 Testing git repository input...")
        try:
            # Use a small, reliable test repository
            test_repo = "https://github.com/octocat/Hello-World.git"
            
            # Only test if git is available
            git_test = subprocess.run(['git', '--version'], 
                                    capture_output=True, text=True)
            
            if git_test.returncode == 0:
                result = MultiInputHandler.process_input(test_repo, 'git')
                print(f"✅ Git input: {len(result)} files processed")
            else:
                print("⚠️ Git not available, skipping git test")
                
        except Exception as e:
            print(f"⚠️ Git test failed (expected): {e}")
        
        return True
        
    except ImportError:
        print("❌ Multi-input handler not available")
        return False

def test_dependency_analysis():
    """Test inter-file and inter-function dependency analysis"""
    
    print("\\n🔗 Testing Dependency Analysis")
    print("=" * 50)
    
    # Multi-file test case
    test_files = {
        'main.py': '''
from models import User, Database
from utils import validate_email, send_notification

def main():
    """Main application entry point."""
    db = Database()
    user = create_user("test@example.com")
    process_user(user, db)

def create_user(email):
    """Create a new user with validation."""
    if validate_email(email):
        return User(email)
    return None

def process_user(user, database):
    """Process user and send notifications."""
    database.save(user)
    send_notification(user.email)
        ''',
        
        'models.py': '''
class User:
    """User model class."""
    def __init__(self, email):
        self.email = email
    
    def get_profile(self):
        """Get user profile data."""
        return {"email": self.email}

class Database:
    """Database connection class."""
    def __init__(self):
        self.connection = None
    
    def save(self, user):
        """Save user to database."""
        pass
    
    def load(self, email):
        """Load user from database."""
        return User(email)
        ''',
        
        'utils.py': '''
import re

def validate_email(email):
    """Validate email address format."""
    pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'
    return re.match(pattern, email) is not None

def send_notification(email):
    """Send notification to user email."""
    print(f"Notification sent to {email}")

def format_name(name):
    """Format user name properly."""
    return name.strip().title()
        '''
    }
    
    try:
        from comprehensive_docs_advanced import AdvancedRepositoryAnalyzer
        
        analyzer = AdvancedRepositoryAnalyzer()
        analysis = analyzer.analyze_repository_comprehensive(test_files)
        
        print(f"📊 Analysis Results:")
        print(f"   - Files: {analysis['total_files']}")
        print(f"   - Functions: {analysis['complexity_metrics']['total_functions']}")
        print(f"   - Classes: {analysis['complexity_metrics']['total_classes']}")
        print(f"   - Project Type: {analysis['project_type']}")
        print(f"   - Key Technologies: {analysis['key_technologies']}")
        print(f"   - Call Graph Edges: {len(analysis['call_graph']['edges'])}")
        print(f"   - Documentation Coverage: {analysis['quality_metrics']['documentation_coverage']:.1f}%")
        
        # Test specific dependency detection
        print(f"\\n🔍 Dependency Details:")
        for file_path, file_info in analysis['file_analysis'].items():
            print(f"   {file_path}:")
            print(f"     - Functions: {len(file_info['functions'])}")
            print(f"     - Imports: {len(file_info['imports'])}")
            print(f"     - Function calls: {len(file_info['function_calls'])}")
        
        return True
        
    except ImportError:
        print("❌ Advanced repository analyzer not available")
        return False

def test_quality_metrics():
    """Test code quality and complexity metrics"""
    
    print("\\n📈 Testing Quality Metrics")
    print("=" * 50)
    
    # Complex test code
    complex_code = '''
def complex_function(data, options):
    """Complex function with high cyclomatic complexity."""
    result = []
    
    for item in data:
        if item.get('active'):
            if item.get('priority') == 'high':
                if item.get('category') in ['urgent', 'critical']:
                    try:
                        processed = process_urgent_item(item)
                        if processed:
                            result.append(processed)
                    except ProcessingError as e:
                        if options.get('ignore_errors'):
                            continue
                        else:
                            raise e
                elif item.get('category') == 'normal':
                    result.append(process_normal_item(item))
            elif item.get('priority') == 'low':
                if options.get('include_low_priority'):
                    result.append(process_low_item(item))
        else:
            if options.get('include_inactive'):
                result.append(process_inactive_item(item))
    
    return result

class SimpleClass:
    """Well-documented simple class."""
    
    def __init__(self, name):
        """Initialize with name."""
        self.name = name
    
    def get_name(self):
        """Return the name."""
        return self.name

def undocumented_function():
    # This function has no docstring
    return "test"
    '''
    
    try:
        from comprehensive_docs_advanced import AdvancedRepositoryAnalyzer
        
        analyzer = AdvancedRepositoryAnalyzer()
        analysis = analyzer.analyze_repository_comprehensive({'test.py': complex_code})
        
        print(f"📊 Quality Metrics:")
        print(f"   - Average Complexity: {analysis['complexity_metrics']['average_function_complexity']:.1f}")
        print(f"   - Maximum Complexity: {analysis['complexity_metrics']['max_complexity']}")
        print(f"   - Documentation Coverage: {analysis['quality_metrics']['documentation_coverage']:.1f}%")
        print(f"   - Functions per File: {analysis['quality_metrics']['functions_per_file']:.1f}")
        
        # Find high complexity functions
        high_complexity = []
        for file_info in analysis['file_analysis'].values():
            for func in file_info['functions']:
                if func.complexity > 5:
                    high_complexity.append((func.name, func.complexity))
        
        if high_complexity:
            print(f"\\n⚠️ High Complexity Functions:")
            for name, complexity in high_complexity:
                print(f"     - {name}: {complexity}")
        
        return True
        
    except ImportError:
        print("❌ Quality metrics not available")
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    
    print("🚀 COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Documentation styles
    print("\\n" + "=" * 60)
    results['styles'] = test_all_documentation_styles()
    
    # Test 2: Multi-input processing
    print("\\n" + "=" * 60)
    results['multi_input'] = test_multi_input_processing()
    
    # Test 3: Dependency analysis
    print("\\n" + "=" * 60)
    results['dependencies'] = test_dependency_analysis()
    
    # Test 4: Quality metrics
    print("\\n" + "=" * 60)
    results['quality'] = test_quality_metrics()
    
    # Summary
    print("\\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for test_name, result in results.items():
        if isinstance(result, dict):
            # Style tests
            if test_name == 'styles' and result:
                for style, style_result in result.items():
                    total_tests += 1
                    if style_result.get('success'):
                        passed_tests += 1
                        print(f"✅ {style} documentation style")
                    else:
                        print(f"❌ {style} documentation style: {style_result.get('error', 'Unknown error')}")
        elif result:
            total_tests += 1
            passed_tests += 1
            print(f"✅ {test_name} test")
        else:
            total_tests += 1
            print(f"❌ {test_name} test")
    
    print(f"\\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Advanced documentation generator is fully functional.")
    elif passed_tests > total_tests * 0.7:
        print("✅ Most tests passed. System is largely functional with some limitations.")
    else:
        print("⚠️ Several tests failed. System may have significant issues.")
    
    return results

if __name__ == "__main__":
    run_comprehensive_tests()