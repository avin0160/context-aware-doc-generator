# Google Colab Terminal Commands - Memory Optimized

## 🚀 Quick Terminal Setup

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/avin0160/context-aware-doc-generator.git
cd context-aware-doc-generator

# Check available memory
free -h

# Install lightweight dependencies only
pip install fastapi uvicorn python-multipart pyngrok requests markdown beautifulsoup4
```

### Step 2: Generate Documentation (Terminal Commands)

#### Basic Documentation Generation
```bash
# Google style (inline documentation)
python main.py --directory . --style google --context "My project documentation" --output google_style.md

# NumPy style (scientific documentation with visuals)
python main.py --directory . --style numpy --context "Scientific documentation" --output numpy_style.md

# Technical markdown (comprehensive analysis)
python main.py --directory . --style technical_md --context "Technical documentation" --output technical_docs.md

# Open source style (contributor-focused)
python main.py --directory . --style opensource --context "Open source project" --output opensource_docs.md
```

#### Document External Repositories
```bash
# Document a GitHub repository
python main.py --url https://github.com/username/repository --style google --context "External repo docs"

# Document with specific context
python main.py --url https://github.com/pytorch/pytorch --style technical_md --context "PyTorch framework analysis"
```

#### Advanced Usage
```bash
# Generate all styles (one by one to save memory)
for style in google numpy technical_md opensource; do
    echo "Generating $style documentation..."
    python main.py --directory . --style $style --context "Multi-style documentation" --output "${style}_docs.md"
    sleep 2  # Brief pause between generations
done

# Check generated files
ls -la *.md

# Preview documentation
head -50 google_docs.md
```

### Step 3: Start Web Server (Optional)
```bash
# Start the web interface (if you have enough RAM)
python repo_fastapi_server.py

# Or start with specific port
uvicorn repo_fastapi_server:app --host 0.0.0.0 --port 8000
```

### Step 4: Memory Management
```bash
# Check memory usage
ps aux | grep python
free -h

# Kill processes if needed
pkill -f "python.*repo_fastapi_server"

# Clean up temporary files
rm -f *.log *.tmp
```

## 🔧 Memory-Efficient Commands

### Lightweight Documentation (No AI Features)
```bash
# Simple documentation without heavy processing
python -c "
from comprehensive_docs_advanced import DocumentationGenerator
import os

# Basic generator without heavy AI features
try:
    generator = DocumentationGenerator()
    print('Generator loaded successfully')
except Exception as e:
    print(f'Using fallback mode: {e}')
"

# Generate basic documentation
python main.py --directory . --style google --context "Basic documentation" --output basic_docs.md
```

### Process Large Repositories in Chunks
```bash
# Process only specific files to save memory
python main.py --directory ./src --style technical_md --context "Source code analysis" --output src_docs.md

# Process individual files
for file in *.py; do
    echo "Processing $file..."
    python -c "
import sys
from comprehensive_docs_advanced import DocumentationGenerator
gen = DocumentationGenerator()
with open('$file', 'r') as f:
    content = f.read()
result = gen.generate_documentation(content, 'File analysis: $file', 'google', 'code')
with open('${file%.py}_docs.md', 'w') as out:
    out.write(result)
print('Processed $file')
"
done
```

### Monitor Resources
```bash
# Real-time memory monitoring
watch -n 1 'free -h && ps aux | grep python | head -5'

# Check disk space
df -h

# Monitor CPU usage
top -n 1 | grep python
```

## 📁 File Management

### View Generated Documentation
```bash
# List all generated files
ls -la *.md

# Quick preview of each style
echo "=== GOOGLE STYLE ==="
head -20 google_docs.md

echo "=== NUMPY STYLE ==="
head -20 numpy_docs.md

echo "=== TECHNICAL STYLE ==="
head -20 technical_docs.md
```

### Download Results
```bash
# Create archive of all documentation
tar -czf documentation_results.tar.gz *.md

# Or create individual archives
for style in google numpy technical_md opensource; do
    if [ -f "${style}_docs.md" ]; then
        tar -czf "${style}_documentation.tar.gz" "${style}_docs.md"
    fi
done

# List archives
ls -la *.tar.gz
```

## 🚨 Troubleshooting

### Memory Issues
```bash
# If you get memory errors, try these:

# 1. Clear Python cache
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 2. Restart Python kernel (in Colab)
import os
os._exit(00)

# 3. Use smaller test data
mkdir test_small
cp main.py test_small/
python main.py --directory test_small --style google --context "Small test"
```

### Import Errors
```bash
# If modules are missing:
pwd
ls -la
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall if needed
pip install --force-reinstall fastapi uvicorn python-multipart
```

### Performance Issues
```bash
# Process smaller chunks
split_size=5  # Process 5 files at a time
find . -name "*.py" | head -$split_size | while read file; do
    echo "Processing $file"
    python main.py --directory $(dirname "$file") --style google --context "Chunk processing"
done
```

## 💡 Pro Tips for Colab

1. **Use `!` prefix for shell commands in Colab cells**
2. **Run one documentation style at a time to save memory**
3. **Use `%cd` to change directories in Colab**
4. **Monitor memory with `!free -h` before running heavy operations**
5. **Save intermediate results frequently**

### Example Colab Cell:
```python
# Complete workflow in one cell
!cd context-aware-doc-generator
!python main.py --directory . --style google --context "My documentation" --output final_docs.md
!head -30 final_docs.md  # Preview results

# Download the result
from google.colab import files
files.download('final_docs.md')
```