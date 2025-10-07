# Context-Aware Documentation Generator - Google Colab Guide

## 🚀 Quick Start in Google Colab

### 1. Memory-Optimized Setup Cell
```python
# Run this cell first - optimized for low RAM environments
!git clone https://github.com/avin0160/context-aware-doc-generator.git
%cd context-aware-doc-generator

# Install core packages only (memory efficient)
!pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6
!pip install pyngrok==7.0.0 requests==2.31.0 markdown==3.5.1 beautifulsoup4==4.12.2

# Optional: Install AI features only if you have enough RAM (>12GB)
import psutil
ram_gb = psutil.virtual_memory().total / (1024**3)
print(f"Available RAM: {ram_gb:.1f} GB")

if ram_gb > 12:
    print("Installing AI features...")
    !pip install datasets==2.14.6 transformers==4.35.2 torch==2.1.1
    print("✅ Full setup complete with AI features!")
else:
    print("⚠️ Low RAM detected - running in lightweight mode")
    print("✅ Basic setup complete!")
```

### 2. Configure ngrok (for public access)
```python
# Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
from pyngrok import ngrok
import os

# Set your ngrok authtoken
authtoken = "YOUR_NGROK_AUTHTOKEN_HERE"  # Replace with your actual token
ngrok.set_auth_token(authtoken)

print("✅ ngrok configured!")
```

### 3. Start the FastAPI Server
```python
import subprocess
import threading
import time
from pyngrok import ngrok

def start_server():
    """Start the FastAPI server in background"""
    subprocess.run(["python", "repo_fastapi_server.py"])

# Start server in background thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Wait a moment for server to start
time.sleep(10)

# Create public tunnel
public_url = ngrok.connect(8000)
print(f"🌐 Public URL: {public_url}")
print(f"🔐 Password: nOtE7thIs")
print("\n✅ Server is running! Open the URL above to access the documentation generator.")
```

### 4. Terminal Commands for Documentation Generation
```python
# Memory-efficient CLI documentation generation

# Example 1: Document current repository (lightweight)
!python main.py --directory . --style google --context "Google Colab documentation example"

# Example 2: Document small GitHub repository
!python main.py --url https://github.com/user/small-repo --style numpy --context "External repository documentation"

# Example 3: Test different styles (one at a time to save memory)
print("📝 Generating Google style documentation...")
!python main.py --directory . --style google --context "Google style test" --output google_docs.md

print("📝 Generating NumPy style documentation...")
!python main.py --directory . --style numpy --context "NumPy style test" --output numpy_docs.md

print("📝 Generating Technical documentation...")
!python main.py --directory . --style technical_md --context "Technical analysis" --output technical_docs.md

print("✅ All documentation generated!")
```

### 5. Interactive Documentation Generation
```python
# Interactive function to generate documentation
from comprehensive_docs_advanced import DocumentationGenerator

def generate_docs_interactive():
    """Interactive documentation generation"""
    print("🤖 Context-Aware Documentation Generator")
    print("=" * 50)
    
    # Initialize generator
    generator = DocumentationGenerator()
    
    # Get user input
    repo_path = input("Enter repository path (or '.' for current): ").strip() or "."
    style = input("Enter style (google/numpy/technical_md/opensource/api/comprehensive): ").strip() or "google"
    context = input("Enter context description: ").strip() or "Documentation generation"
    
    print(f"\n📝 Generating {style} documentation for {repo_path}...")
    
    try:
        # Generate documentation
        result = generator.generate_repository_documentation(repo_path, context, style)
        
        # Save result
        output_file = f"documentation_{style}.md"
        with open(output_file, 'w') as f:
            f.write(result)
        
        print(f"✅ Documentation saved to {output_file}")
        print(f"📄 Preview (first 500 characters):")
        print("-" * 50)
        print(result[:500] + "...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Run interactive generator
generate_docs_interactive()
```

### 6. Batch Documentation Generation
```python
# Generate documentation for multiple repositories
repositories = [
    {
        "url": "https://github.com/user/repo1",
        "style": "google",
        "context": "Web application documentation"
    },
    {
        "url": "https://github.com/user/repo2", 
        "style": "numpy",
        "context": "Data science project documentation"
    },
    {
        "path": ".",
        "style": "technical_md",
        "context": "Current project technical documentation"
    }
]

for i, repo in enumerate(repositories):
    print(f"\n📝 Processing repository {i+1}/{len(repositories)}...")
    
    if "url" in repo:
        !python main.py --url {repo["url"]} --style {repo["style"]} --context "{repo["context"]}"
    else:
        !python main.py --directory {repo["path"]} --style {repo["style"]} --context "{repo["context"]}"
    
    print(f"✅ Repository {i+1} completed!")
```

### 7. Advanced Features Demo
```python
# Demonstrate advanced features
from comprehensive_docs_advanced import DocumentationGenerator, SemanticAnalyzer

# Initialize components
generator = DocumentationGenerator()
analyzer = SemanticAnalyzer()

# Analyze current project
print("🔍 Analyzing current project...")
project_type = analyzer.detect_project_type(".")
technologies = analyzer.detect_technologies(".")

print(f"📊 Project Type: {project_type}")
print(f"🛠️  Technologies: {', '.join(technologies)}")

# Generate comprehensive documentation
print("\n📝 Generating comprehensive documentation...")
result = generator.generate_repository_documentation(
    ".", 
    "Complete project analysis and documentation", 
    "comprehensive"
)

# Save with timestamp
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"comprehensive_docs_{timestamp}.md"

with open(output_file, 'w') as f:
    f.write(result)

print(f"✅ Comprehensive documentation saved to {output_file}")

# Display file info
import os
file_size = os.path.getsize(output_file)
print(f"📄 File size: {file_size:,} bytes")
```

## 🎯 Available Documentation Styles

- **google**: Google-style docstrings and formatting
- **numpy**: NumPy/SciPy documentation style  
- **technical_md**: Technical markdown with detailed analysis
- **opensource**: Open source project documentation
- **api**: API reference documentation
- **comprehensive**: Complete analysis with all features

## 🔧 Troubleshooting

### Common Issues:
```python
# Check if server is running
import requests
try:
    response = requests.get("http://localhost:8000/test")
    print("✅ Server is running!")
    print(response.json())
except:
    print("❌ Server is not running. Run the server setup cell again.")

# Check installed packages
!pip list | grep -E "fastapi|transformers|datasets"

# Check ngrok status
from pyngrok import ngrok
tunnels = ngrok.get_tunnels()
print(f"Active tunnels: {len(tunnels)}")
for tunnel in tunnels:
    print(f"🌐 {tunnel.public_url}")
```

## 📱 Mobile Access

The generated public URL works on mobile devices. Share the ngrok URL with the password `nOtE7thIs` to access from any device.

## 💾 Saving Results

```python
# Download generated documentation
from google.colab import files

# List generated files
!ls -la *.md *.html

# Download specific file
files.download('documentation_google.md')

# Or download all documentation files
!zip -r documentation_results.zip *.md *.html
files.download('documentation_results.zip')
```