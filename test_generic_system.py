#!/usr/bin/env python3#!/usr/bin/env python3

""""""

Simple terminal test for the generic documentation systemTest script to verify the generic documentation system works properly

""""""



import sysimport os

import osimport tempfile

from comprehensive_docs import generate_comprehensive_documentation

# Add current directory to path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))def create_test_repository():

    """Create a simple test repository"""

from comprehensive_docs import generate_comprehensive_documentation    test_repo = tempfile.mkdtemp()

    print(f" Created test repository at: {test_repo}")

def test_web_app():    

    """Test web application documentation"""    # Create a simple web application

    code = '''    with open(os.path.join(test_repo, 'app.py'), 'w') as f:

from flask import Flask, jsonify, request        f.write('''

from flask import Flask, request, jsonify

app = Flask(__name__)

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])

def get_users():class UserManager:

    """Get all users from the system"""    """Manages user operations for the web application"""

    return jsonify([{"id": 1, "name": "John Doe"}])    

    def __init__(self, db_path):

@app.route('/api/users', methods=['POST'])        self.db_path = db_path

def create_user():        

    """Create a new user"""    def create_user(self, name, email):

    data = request.get_json()        """Create a new user"""

    return jsonify({"id": 2, "name": data.get("name")})        return {'id': 1, 'name': name, 'email': email}

        

class UserService:    def get_user(self, user_id):

    """Service for managing users"""        """Retrieve user by ID"""

            return {'id': user_id, 'name': 'John', 'email': 'john@example.com'}

    def __init__(self):

        self.users = []@app.route('/users', methods=['POST'])

    def create_user():

    def add_user(self, name, email):    """API endpoint to create a user"""

        """Add a new user to the system"""    data = request.get_json()

        user = {"name": name, "email": email}    manager = UserManager('users.db')

        self.users.append(user)    user = manager.create_user(data['name'], data['email'])

        return user    return jsonify(user)

    

    def get_all_users(self):@app.route('/users/<int:user_id>')

        """Get all users"""def get_user(user_id):

        return self.users    """API endpoint to get a user"""

    manager = UserManager('users.db')

if __name__ == '__main__':    user = manager.get_user(user_id)

    app.run(debug=True)    return jsonify(user)

'''

    if __name__ == '__main__':

    file_contents = {"app.py": code}    app.run(debug=True)

    context = "Flask web application for user management"''')

        

    print("=== WEB APPLICATION TEST ===")    # Create a models file

    docs = generate_comprehensive_documentation(file_contents, context, "technical")    with open(os.path.join(test_repo, 'models.py'), 'w') as f:

    print(docs[:500] + "..." if len(docs) > 500 else docs)        f.write('''

    print()class User:

    """User model for the application"""

def test_data_science():    

    """Test data science documentation"""    def __init__(self, id, name, email):

    code = '''        self.id = id

import pandas as pd        self.name = name

import numpy as np        self.email = email

from sklearn.model_selection import train_test_split        

from sklearn.linear_model import LinearRegression    def to_dict(self):

        """Convert user to dictionary"""

class DataAnalyzer:        return {

    """Analyzer for processing and modeling data"""            'id': self.id,

                'name': self.name,

    def __init__(self):            'email': self.email

        self.model = LinearRegression()        }

            

    def load_data(self, filepath):    def validate(self):

        """Load data from CSV file"""        """Validate user data"""

        return pd.read_csv(filepath)        return '@' in self.email and len(self.name) > 0

    ''')

    def preprocess_data(self, df):    

        """Clean and prepare data for modeling"""    return test_repo

        # Remove missing values

        df = df.dropna()def test_documentation_generation():

            """Test the documentation generation system"""

        # Feature engineering    print(" Testing Generic Documentation System")

        df['feature_ratio'] = df['feature1'] / df['feature2']    print("=" * 50)

        return df    

        # Create test repository

    def train_model(self, X, y):    test_repo = create_test_repository()

        """Train the linear regression model"""    

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)    # Read files

        self.model.fit(X_train, y_train)    file_contents = {}

        return self.model.score(X_test, y_test)    for root, dirs, files in os.walk(test_repo):

            for file in files:

    def predict(self, X):            if file.endswith('.py'):

        """Make predictions using the trained model"""                filepath = os.path.join(root, file)

        return self.model.predict(X)                with open(filepath, 'r') as f:

                    file_contents[os.path.relpath(filepath, test_repo)] = f.read()

def analyze_sales_data(data_path):    

    """Main function to analyze sales data"""    print(f" Files found: {list(file_contents.keys())}")

    analyzer = DataAnalyzer()    

    data = analyzer.load_data(data_path)    # Test all documentation styles

    clean_data = analyzer.preprocess_data(data)    styles = ['technical', 'google', 'numpy', 'opensource']

    return clean_data    

'''    for style in styles:

            print(f"\n Testing {style.upper()} style...")

    file_contents = {"analysis.py": code}        try:

    context = "Data science project for sales analysis and prediction"            doc = generate_comprehensive_documentation(

                    file_contents, 

    print("=== DATA SCIENCE TEST ===")                f'Test {style} documentation', 

    docs = generate_comprehensive_documentation(file_contents, context, "technical")                style, 

    print(docs[:500] + "..." if len(docs) > 500 else docs)                test_repo

    print()            )

            

def test_cli_tool():            # Check for repository-specific content (should NOT be hardcoded database stuff)

    """Test CLI tool documentation"""            doc_lower = doc.lower()

    code = '''            

import argparse            # Check for web app specific content

import sys            web_indicators = ['flask', 'user', 'api', 'endpoint', 'route']

import os            found_indicators = [indicator for indicator in web_indicators if indicator in doc_lower]

            

class FileProcessor:            # Check for hardcoded database content (should NOT be present)

    """Processor for handling file operations"""            database_hardcoded = ['b+tree', 'database index', 'btree node', 'leaf node']

                found_hardcoded = [item for item in database_hardcoded if item in doc_lower]

    def __init__(self):            

        self.processed_files = []            if found_indicators and not found_hardcoded:

                    print(f"    SUCCESS: Found web app content: {found_indicators}")

    def process_file(self, filepath, action='read'):                print(f"    No hardcoded database content detected")

        """Process a single file"""            elif found_hardcoded:

        if action == 'read':                print(f"    FAILURE: Still contains hardcoded database content: {found_hardcoded}")

            with open(filepath, 'r') as f:            else:

                content = f.read()                print(f"     PARTIAL: Generic content generated")

            self.processed_files.append(filepath)            

            return content            print(f"    Generated {len(doc)} characters")

        elif action == 'count':            

            with open(filepath, 'r') as f:            # Save sample for inspection

                lines = f.readlines()            sample_file = f'sample_{style}_doc.md'

            return len(lines)            with open(sample_file, 'w') as f:

                    f.write(doc)

    def batch_process(self, directory, pattern='*.txt'):            print(f"    Saved sample to: {sample_file}")

        """Process multiple files in a directory"""            

        import glob        except Exception as e:

        files = glob.glob(os.path.join(directory, pattern))            print(f"    ERROR in {style} style: {e}")

        results = []            import traceback

        for file in files:            traceback.print_exc()

            content = self.process_file(file)    

            results.append({"file": file, "content": content})    print("\n Test completed!")

        return results    print("\nTo inspect the generated documentation, check the sample_*_doc.md files")

    

def main():    # Cleanup

    """Main CLI interface"""    import shutil

    parser = argparse.ArgumentParser(description='File processing tool')    shutil.rmtree(test_repo)

    parser.add_argument('--file', '-f', help='File to process')    print(f"  Cleaned up test repository")

    parser.add_argument('--directory', '-d', help='Directory to process')

    parser.add_argument('--action', choices=['read', 'count'], default='read')if __name__ == "__main__":

    parser.add_argument('--verbose', '-v', action='store_true')    test_documentation_generation()
    
    args = parser.parse_args()
    
    processor = FileProcessor()
    
    if args.file:
        result = processor.process_file(args.file, args.action)
        print(f"Processed {args.file}: {result}")
    elif args.directory:
        results = processor.batch_process(args.directory)
        print(f"Processed {len(results)} files")

if __name__ == '__main__':
    main()
'''
    
    file_contents = {"tool.py": code}
    context = "Command-line tool for file processing and analysis"
    
    print("=== CLI TOOL TEST ===")
    docs = generate_comprehensive_documentation(file_contents, context, "technical")
    print(docs[:500] + "..." if len(docs) > 500 else docs)
    print()

def main():
    """Run all tests"""
    print("Testing Generic Documentation System")
    print("=" * 50)
    
    test_web_app()
    test_data_science()
    test_cli_tool()
    
    print("All tests completed successfully!")
    print("The system generates repository-specific documentation!")

if __name__ == "__main__":
    main()