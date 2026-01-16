#!/usr/bin/env python3
"""
Setup script for Context-Aware Documentation Generator
Run this after transferring project files to a new machine
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False

def create_venv():
    """Create virtual environment"""
    if os.path.exists('venv'):
        print("⚠️  Virtual environment already exists. Skipping...")
        return True
    return run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")

def get_pip_command():
    """Get the appropriate pip command based on OS"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\pip"
    else:
        return "venv/bin/pip"

def get_python_command():
    """Get the appropriate python command based on OS"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\python"
    else:
        return "venv/bin/python"

def install_dependencies():
    """Install Python dependencies"""
    pip_cmd = get_pip_command()
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['models', 'output', 'temp', '.cache']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created directory: {dir_name}")
        else:
            print(f"⚠️  Directory already exists: {dir_name}")
    return True

def download_models():
    """Prompt to download models"""
    print("\n📦 Model Download Options:")
    print("   Models will be downloaded automatically on first use")
    print("   To pre-download models, run:")
    python_cmd = get_python_command()
    print(f"   {python_cmd} -c \"from src.parser import CodeParser; CodeParser()\"")
    print(f"   {python_cmd} -c \"from src.llm import DocumentationGenerator; DocumentationGenerator()\"")

def main():
    """Main setup function"""
    print_header("Context-Aware Documentation Generator - Setup")
    print(f"System: charvaka")
    print(f"Author: team-8")
    
    # Check Python version
    print_header("Step 1: Checking Python Version")
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    print_header("Step 2: Creating Virtual Environment")
    if not create_venv():
        sys.exit(1)
    
    # Create necessary directories
    print_header("Step 3: Creating Directories")
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    print_header("Step 4: Installing Dependencies")
    if not install_dependencies():
        print("\n⚠️  Some dependencies failed to install.")
        print("   You may need to install them manually or check for errors.")
    
    # Model download info
    print_header("Step 5: Model Setup")
    download_models()
    
    # Final instructions
    print_header("Setup Complete!")
    print("🎉 Your environment is ready!")
    print("\nTo activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\nTo start the application:")
    print("   streamlit run src/frontend.py")
    print("   OR")
    print("   python start_web.py")
    
    print("\nFor API server:")
    print("   python start_api.py")
    
    print("\nFor CLI usage:")
    print("   python main.py --help")
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()
