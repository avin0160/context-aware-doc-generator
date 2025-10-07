"""
Google Colab Setup for Context-Aware Documentation Generator
===========================================================

Run this cell first to set up the documentation generator in Google Colab
"""

# Install required packages
import subprocess
import sys
import os

def install_packages():
    """Install all required packages for the documentation generator"""
    packages = [
        'fastapi==0.104.1',
        'uvicorn[standard]==0.24.0',
        'python-multipart==0.0.6',
        'pyngrok==7.0.0',
        'requests==2.31.0',
        'datasets==2.14.6',
        'transformers==4.35.2',
        'torch==2.1.1',
        'GitPython==3.1.40',
        'zipfile36==0.1.3',
        'markdown==3.5.1',
        'beautifulsoup4==4.12.2',
        'pygments==2.16.1',
        'jinja2==3.1.2'
    ]
    
    print("🔧 Installing required packages...")
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ All packages installed successfully!")

def setup_ngrok():
    """Setup ngrok for public URL access"""
    print("🌐 Setting up ngrok...")
    
    # You need to get your ngrok authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
    authtoken = input("Enter your ngrok authtoken (get it from https://dashboard.ngrok.com/get-started/your-authtoken): ")
    
    if authtoken:
        os.system(f'ngrok authtoken {authtoken}')
        print("✅ ngrok configured successfully!")
    else:
        print("⚠️  ngrok authtoken not provided. Public URL will not be available.")

def clone_repository():
    """Clone the documentation generator repository"""
    print("📥 Cloning documentation generator repository...")
    
    # Clone from your GitHub repository
    repo_url = "https://github.com/avin0160/context-aware-doc-generator.git"
    
    if os.path.exists("context-aware-doc-generator"):
        print("Repository already exists, pulling latest changes...")
        os.chdir("context-aware-doc-generator")
        os.system("git pull")
        os.chdir("..")
    else:
        os.system(f"git clone {repo_url}")
    
    print("✅ Repository setup complete!")

if __name__ == "__main__":
    print("🚀 Setting up Context-Aware Documentation Generator for Google Colab")
    print("=" * 70)
    
    # Install packages
    install_packages()
    
    # Setup ngrok
    setup_ngrok()
    
    # Clone repository
    clone_repository()
    
    print("\n🎉 Setup complete! You can now run the documentation generator.")
    print("\nNext steps:")
    print("1. Run the server: %cd context-aware-doc-generator && python repo_fastapi_server.py")
    print("2. Or use CLI: python main.py --directory /path/to/repo --style google")