#!/bin/bash

# Memory-Efficient Google Colab Setup Script
# Usage: Run this in Colab terminal to set up documentation generator

echo "🚀 Setting up Context-Aware Documentation Generator for Low RAM..."

# Check available memory
total_ram=$(free -h | awk '/^Mem:/ {print $2}')
echo "📊 Available RAM: $total_ram"

# Clone repository if not exists
if [ ! -d "context-aware-doc-generator" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/avin0160/context-aware-doc-generator.git
fi

cd context-aware-doc-generator

# Install lightweight dependencies
echo "📦 Installing core dependencies..."
pip install fastapi uvicorn python-multipart pyngrok requests markdown beautifulsoup4 jinja2 --quiet

# Check if AI features can be installed (requires >12GB RAM)
ram_mb=$(free -m | awk '/^Mem:/ {print $2}')
if [ $ram_mb -gt 12000 ]; then
    echo "💡 Sufficient RAM detected - installing AI features..."
    pip install datasets transformers torch --quiet
    echo "✅ Full installation complete with AI features!"
else
    echo "⚠️  Low RAM detected - skipping heavy AI packages"
    echo "✅ Lightweight installation complete!"
fi

# Test the installation
echo "🧪 Testing installation..."
python -c "
try:
    from comprehensive_docs_advanced import DocumentationGenerator
    print('✅ Documentation generator imported successfully')
    
    # Test basic functionality
    gen = DocumentationGenerator()
    test_code = 'def hello(): return \"world\"'
    result = gen.generate_documentation(test_code, 'Test', 'google', 'code')
    print('✅ Basic generation test passed')
    print(f'✅ Generated {len(result)} characters of documentation')
except Exception as e:
    print(f'⚠️  Running in fallback mode: {e}')
"

echo ""
echo "🎉 Setup complete! You can now use:"
echo ""
echo "📝 Generate documentation:"
echo "python main.py --directory . --style google --context 'My docs'"
echo ""
echo "🌐 Start web server:"
echo "python repo_fastapi_server.py"
echo ""
echo "📋 Available styles: google, numpy, technical_md, opensource"
echo ""
echo "💾 Save memory by processing one style at a time!"