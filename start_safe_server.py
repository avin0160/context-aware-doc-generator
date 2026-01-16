"""
Safe Start Script for FastAPI Server
Starts server with minimal dependencies and maximum error handling
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("🔧 SAFE START MODE")
print("=" * 70)

# Test imports one by one
print("📦 Loading FastAPI...")
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    print("✅ FastAPI loaded")
except ImportError as e:
    print(f"❌ FastAPI not installed: {e}")
    print("   Run: pip install fastapi uvicorn")
    input("Press Enter to exit...")
    sys.exit(1)

print("📦 Loading uvicorn...")
try:
    import uvicorn
    print("✅ Uvicorn loaded")
except ImportError as e:
    print(f"❌ Uvicorn not installed: {e}")
    print("   Run: pip install uvicorn")
    input("Press Enter to exit...")
    sys.exit(1)

# Create minimal app
print("📦 Creating FastAPI app...")
app = FastAPI(title="Context-Aware Documentation Generator (Safe Mode)")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Server is running in safe mode"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "mode": "safe",
        "python_version": sys.version
    }

print("✅ Minimal server created")

# Try to import documentation system
doc_generator = None
print("\n📦 Attempting to load documentation system...")
try:
    from comprehensive_docs_advanced import DocumentationGenerator
    doc_generator = DocumentationGenerator()
    print("✅ Documentation system loaded")
except Exception as e:
    print(f"⚠️ Documentation system not available: {e}")
    print("   Server will run without documentation features")

if doc_generator:
    @app.get("/status")
    async def status():
        return {
            "status": "ready",
            "doc_generator": "available",
            "mode": "full"
        }
else:
    @app.get("/status")
    async def status():
        return {
            "status": "limited",
            "doc_generator": "unavailable",
            "mode": "safe"
        }

def start_safe_server():
    """Start server with maximum error handling"""
    print("\n" + "=" * 70)
    print("🚀 Starting server in SAFE MODE")
    print("=" * 70)
    print("\n📍 Server will run on: http://localhost:8000")
    print("📍 Health check: http://localhost:8000/health")
    print("📍 Status check: http://localhost:8000/status")
    print("\n⚠️ Press Ctrl+C to stop")
    print("=" * 70 + "\n")
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        start_safe_server()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
