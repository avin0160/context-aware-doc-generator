# 🚀 Streamlined Web Interface - Google Colab with ngrok

## 🌐 Web Interface Setup (Recommended)

### Quick Setup Commands:
```bash
# Clone the repository
git clone https://github.com/avin0160/context-aware-doc-generator.git
cd context-aware-doc-generator

# Start the web server with ngrok tunnel
python fastapi_server.py

# Install web dependencies
pip install fastapi uvicorn pyngrok python-multipart

# Start web server
python web_app.py &

# Install and run ngrok (get free token from ngrok.com)
wget https://bin.equinox.io/c/bkuykdwz8Xn/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
chmod +x ngrok

# Expose to web (replace YOUR_TOKEN with ngrok authtoken)
# ./ngrok config add-authtoken YOUR_TOKEN
./ngrok http 8000
```

**Copy the ngrok URL (https://xxxxx.ngrok.io) and use the web interface!**

### Web Interface Features:
- 📁 **Upload ZIP/Python files**
- 📝 **Paste code directly** 
- 🔗 **Analyze GitHub repositories**
- 🎯 **Repository-specific documentation** (Flask → web docs, pandas → data science docs)
- 📊 **Multiple styles**: Technical, User Guide, API, Tutorial
- 💾 **Download & Preview** generated documentation

---

## Option 2: Terminal Commands (Basic Testing)

### Step 1: Setup
```bash
# Clone the repository
git clone https://github.com/avin0160/context-aware-doc-generator.git
cd context-aware-doc-generator

# Install dependencies if needed
pip install flask fastapi uvicorn --quiet
```

### Step 2: Run Complete Test
```bash
# Run the comprehensive test system
python complete_test.py
```

### Step 3: Check Results
```bash
# List generated documentation files
ls -la sample_*.md

# Preview each documentation type
echo "=== WEB APPLICATION DOCUMENTATION ==="
head -50 sample_web_technical.md

echo -e "\n=== DATA SCIENCE DOCUMENTATION ==="
head -50 sample_datascience_technical.md

echo -e "\n=== CLI TOOL DOCUMENTATION ==="
head -50 sample_cli_technical.md
```

### Step 4: Test with Real Repository (Optional)
```bash
# Test with the requests library
git clone https://github.com/requests/requests.git /tmp/test_real_repo
cd /tmp/test_real_repo

# Create a simple test script for real repository
cat > test_real_repo.py << 'EOF'
import sys
import os
sys.path.insert(0, '/content/context-aware-doc-generator')

from comprehensive_docs import generate_comprehensive_documentation

# Read some files from requests library
file_contents = {}
base_path = "/tmp/test_real_repo/src/requests"

for root, dirs, files in os.walk(base_path):
    dirs[:] = []  # Don't recurse into subdirectories
    
    for file in files[:3]:  # Limit to first 3 files
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    file_contents[os.path.relpath(filepath, "/tmp/test_real_repo")] = f.read()
            except:
                continue

print(f"Files to analyze: {list(file_contents.keys())}")

if file_contents:
    # Generate documentation
    doc = generate_comprehensive_documentation(
        file_contents, 
        'Popular HTTP library for Python', 
        'technical', 
        '/tmp/test_real_repo'
    )
    
    # Save and preview
    with open('/content/context-aware-doc-generator/sample_requests_technical.md', 'w') as f:
        f.write(doc)
    
    print("Generated documentation preview (first 800 characters):")
    print("=" * 60)
    print(doc[:800])
    print("=" * 60)
    
    # Check for library-specific content
    doc_lower = doc.lower()
    if 'requests' in doc_lower or 'http' in doc_lower:
        print("✅ SUCCESS: Generated requests-specific documentation!")
    else:
        print("❌ Issue: Documentation may not be repository-specific")
else:
    print("❌ Could not read files from the repository")
EOF

# Run the real repository test
cd /content/context-aware-doc-generator
python /tmp/test_real_repo/test_real_repo.py
```

## 🎯 What You Should See (Success Indicators)

### Expected Output from complete_test.py:
```
🚀 Testing Complete Generic Documentation System
============================================================

📱 Test 1: Web Application Repository
   📁 Files: ['app.py', 'models.py', 'utils.py']
   📊 Analysis for web application:
   ✅ SUCCESS: Found web application-specific content: ['flask', 'user', 'api', 'route']
   ✅ No hardcoded database content detected
   📏 Generated XXXX characters of documentation
   💾 Documentation saved for inspection

🔬 Test 2: Data Science Project
   📁 Files: ['analysis.py', 'preprocessing.py']
   📊 Analysis for data science:
   ✅ SUCCESS: Found data science-specific content: ['pandas', 'numpy', 'model', 'data']
   ✅ No hardcoded database content detected
   📏 Generated XXXX characters of documentation
   💾 Documentation saved for inspection

⚡ Test 3: Command Line Tool
   📁 Files: ['main.py', 'utils.py']
   📊 Analysis for CLI tool:
   ✅ SUCCESS: Found CLI tool-specific content: ['argparse', 'command', 'cli', 'main']
   ✅ No hardcoded database content detected
   📏 Generated XXXX characters of documentation
   💾 Documentation saved for inspection

🎉 All tests completed!
```

### Generated Documentation Should Contain:
- **Web App**: Flask routes, UserManager class, API endpoints, authentication
- **Data Science**: pandas DataFrames, sklearn models, data analysis methods
- **CLI Tool**: argparse commands, file processing, command-line interface

### ❌ FAILURE Indicators (Report if you see these):
- Any mentions of "B+tree", "database index", "btree node", "leaf node"
- All documentation looking identical regardless of repository type
- Error messages during generation
- Generic content that doesn't match the repository being analyzed

## 🛠️ Advanced Testing (Optional)

Test the enhanced semantic analysis:

```bash
# Create and run semantic analysis test
cat > test_semantic.py << 'EOF'
from enhanced_ast_analyzer import EnhancedCodeAnalyzer
import tempfile
import os

analyzer = EnhancedCodeAnalyzer()

# Create a test Python file
test_code = '''
class UserRepository:
    """Repository for managing user data operations"""
    
    def get_user_by_id(self, user_id: int):
        """Retrieve user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: dict):
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        return user
'''

# Analyze with enhanced semantic understanding
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    temp_file = f.name

analysis = analyzer.analyze_python_file(temp_file)
print("Semantic Analysis Results:")
print(f"- File type: {analysis['semantic_type']}")
print(f"- Classes found: {[c['name'] + ' (' + c['semantic_type'] + ')' for c in analysis['classes']]}")
print(f"- Functions found: {[f['name'] + ' (' + f['semantic_type'] + ')' for f in analysis['functions']]}")

os.unlink(temp_file)
EOF

python test_semantic.py
```

## 🔧 Troubleshooting

### If you get syntax errors:
```bash
python emergency_fix.py
```

### If documentation looks generic:
Check that the repository contains actual Python code and not just empty files.

## 📊 Performance Expectations

- **Small repositories** (< 10 files): ~5-10 seconds
- **Medium repositories** (10-50 files): ~15-30 seconds  
- **Large repositories** (50+ files): ~30-60 seconds

## 🎯 What to Report Back

Run the complete test and report:

1. **Did `complete_test.py` run successfully?**
2. **What specific content appears in each sample documentation?**
   - Web app mentions Flask/API? ✅
   - Data science mentions pandas/models? ✅  
   - CLI mentions argparse/commands? ✅
3. **Any hardcoded database content?** (Should be ❌ None)
4. **Real repository test results?** (requests library specific content?)
5. **Any error messages?**

This system generates truly repository-specific documentation using semantic analysis! 🚀