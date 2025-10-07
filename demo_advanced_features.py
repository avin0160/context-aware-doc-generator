#!/usr/bin/env python3
"""
Quick Demo of Advanced Documentation Generator
Demonstrates the new Google-style documentation generation
"""

def demo_google_style():
    """Demonstrate Google-style documentation generation"""
    
    sample_code = '''
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DataConfig:
    """Configuration for data processing operations."""
    batch_size: int = 32
    learning_rate: float = 0.001
    dropout_rate: float = 0.1

class AdvancedDataProcessor:
    """
    Advanced data processing engine for machine learning workflows.
    
    This class provides comprehensive data transformation, validation,
    and analysis capabilities for various data science applications.
    """
    
    def __init__(self, config: DataConfig):
        """
        Initialize the data processor with configuration.
        
        Args:
            config: Configuration object containing processing parameters
        """
        self.config = config
        self.processed_data = None
        self.validation_results = {}
    
    def load_and_validate_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from file and perform comprehensive validation.
        
        Args:
            file_path: Path to the data file (CSV, JSON, or Parquet)
            
        Returns:
            Validated pandas DataFrame ready for processing
            
        Raises:
            ValueError: If data validation fails
            FileNotFoundError: If input file doesn't exist
        """
        try:
            # Load data based on file extension
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                data = pd.read_json(file_path)
            elif file_path.endswith('.parquet'):
                data = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            # Validate data quality
            self._validate_data_quality(data)
            
            return data
            
        except Exception as e:
            raise ValueError(f"Data loading failed: {str(e)}")
    
    def _validate_data_quality(self, data: pd.DataFrame) -> None:
        """
        Perform comprehensive data quality validation.
        
        Args:
            data: DataFrame to validate
            
        Raises:
            ValueError: If validation criteria are not met
        """
        # Check for minimum required columns
        required_columns = ['id', 'timestamp', 'value']
        missing_columns = set(required_columns) - set(data.columns)
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for data completeness
        null_percentage = (data.isnull().sum() / len(data)) * 100
        high_null_columns = null_percentage[null_percentage > 20].index.tolist()
        
        if high_null_columns:
            self.validation_results['high_null_columns'] = high_null_columns
        
        # Store validation results
        self.validation_results.update({
            'total_rows': len(data),
            'total_columns': len(data.columns),
            'null_percentage': null_percentage.to_dict(),
            'data_types': data.dtypes.to_dict()
        })
    
    def transform_features(self, data: pd.DataFrame, 
                          feature_config: Dict[str, str]) -> pd.DataFrame:
        """
        Apply feature transformations based on configuration.
        
        Args:
            data: Input DataFrame to transform
            feature_config: Dictionary mapping column names to transformation types
                           Supported types: 'normalize', 'standardize', 'log', 'sqrt'
        
        Returns:
            DataFrame with transformed features
            
        Example:
            >>> processor = AdvancedDataProcessor(DataConfig())
            >>> config = {'price': 'log', 'quantity': 'normalize'}
            >>> transformed = processor.transform_features(data, config)
        """
        transformed_data = data.copy()
        
        for column, transform_type in feature_config.items():
            if column not in data.columns:
                continue
                
            if transform_type == 'normalize':
                min_val = data[column].min()
                max_val = data[column].max()
                transformed_data[column] = (data[column] - min_val) / (max_val - min_val)
                
            elif transform_type == 'standardize':
                mean_val = data[column].mean()
                std_val = data[column].std()
                transformed_data[column] = (data[column] - mean_val) / std_val
                
            elif transform_type == 'log':
                transformed_data[column] = np.log1p(data[column].abs())
                
            elif transform_type == 'sqrt':
                transformed_data[column] = np.sqrt(data[column].abs())
        
        self.processed_data = transformed_data
        return transformed_data
    
    def generate_summary_statistics(self, data: pd.DataFrame) -> Dict[str, any]:
        """
        Generate comprehensive summary statistics for the dataset.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Dictionary containing detailed statistics and insights
        """
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        categorical_columns = data.select_dtypes(include=['object']).columns
        
        summary = {
            'basic_info': {
                'shape': data.shape,
                'memory_usage': data.memory_usage(deep=True).sum(),
                'numeric_columns': len(numeric_columns),
                'categorical_columns': len(categorical_columns)
            },
            'numeric_stats': {},
            'categorical_stats': {},
            'data_quality': self.validation_results
        }
        
        # Numeric column statistics
        if len(numeric_columns) > 0:
            summary['numeric_stats'] = {
                'describe': data[numeric_columns].describe().to_dict(),
                'correlations': data[numeric_columns].corr().to_dict(),
                'skewness': data[numeric_columns].skew().to_dict()
            }
        
        # Categorical column statistics
        if len(categorical_columns) > 0:
            summary['categorical_stats'] = {}
            for col in categorical_columns:
                summary['categorical_stats'][col] = {
                    'unique_count': data[col].nunique(),
                    'most_frequent': data[col].mode().iloc[0] if not data[col].mode().empty else None,
                    'value_counts': data[col].value_counts().head(10).to_dict()
                }
        
        return summary

def batch_process_datasets(file_paths: List[str], 
                          config: DataConfig,
                          output_dir: str = 'processed_data') -> Dict[str, bool]:
    """
    Process multiple datasets in batch with comprehensive error handling.
    
    Args:
        file_paths: List of file paths to process
        config: Processing configuration
        output_dir: Directory to save processed results
        
    Returns:
        Dictionary mapping file paths to success status
        
    Example:
        >>> config = DataConfig(batch_size=64, learning_rate=0.01)
        >>> files = ['data1.csv', 'data2.csv', 'data3.csv']
        >>> results = batch_process_datasets(files, config)
    """
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    processor = AdvancedDataProcessor(config)
    results = {}
    
    for file_path in file_paths:
        try:
            # Load and validate data
            data = processor.load_and_validate_data(file_path)
            
            # Apply standard transformations
            feature_config = {
                'price': 'log',
                'quantity': 'normalize',
                'score': 'standardize'
            }
            
            transformed_data = processor.transform_features(data, feature_config)
            
            # Generate summary
            summary = processor.generate_summary_statistics(transformed_data)
            
            # Save results
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_processed.csv")
            summary_path = os.path.join(output_dir, f"{base_name}_summary.json")
            
            transformed_data.to_csv(output_path, index=False)
            
            import json
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            results[file_path] = True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            results[file_path] = False
    
    return results

if __name__ == '__main__':
    # Demo configuration
    config = DataConfig(batch_size=32, learning_rate=0.001, dropout_rate=0.1)
    
    # Create sample data for demonstration
    sample_data = pd.DataFrame({
        'id': range(100),
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
        'value': np.random.normal(100, 15, 100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'price': np.random.lognormal(3, 1, 100),
        'quantity': np.random.exponential(5, 100)
    })
    
    # Process the data
    processor = AdvancedDataProcessor(config)
    
    # Save sample data
    sample_data.to_csv('sample_data.csv', index=False)
    
    # Load and process
    loaded_data = processor.load_and_validate_data('sample_data.csv')
    
    # Transform features
    feature_config = {
        'price': 'log',
        'quantity': 'normalize',
        'value': 'standardize'
    }
    
    transformed = processor.transform_features(loaded_data, feature_config)
    
    # Generate summary
    summary = processor.generate_summary_statistics(transformed)
    
    print("✅ Demo completed successfully!")
    print(f"Processed {len(transformed)} rows with {len(transformed.columns)} columns")
    print(f"Data quality score: {len(summary['data_quality'])} metrics tracked")
    '''
    
    try:
        from comprehensive_docs_advanced import DocumentationGenerator
        
        generator = DocumentationGenerator()
        
        print("🚀 Generating Google-style documentation...")
        print("=" * 60)
        
        docs = generator.generate_documentation(
            input_data=sample_code,
            context="Advanced data processing library for machine learning workflows with comprehensive validation, transformation, and batch processing capabilities.",
            doc_style="google",
            input_type="code",
            repo_name="DataProcessor"
        )
        
        print(docs)
        
        # Save the documentation
        with open('demo_google_docs.md', 'w') as f:
            f.write(docs)
        
        print("\n" + "=" * 60)
        print("✅ Google-style documentation generated successfully!")
        print("📄 Saved as: demo_google_docs.md")
        print(f"📊 Documentation length: {len(docs)} characters")
        
    except ImportError as e:
        print(f"❌ Advanced generator not available: {e}")
        print("Please ensure comprehensive_docs_advanced.py is in the same directory")

if __name__ == "__main__":
    demo_google_style()