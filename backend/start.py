#!/usr/bin/env python3
"""
Comprehensive startup script for the RAG Chatbot
Checks all requirements and starts the server
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('dotenv', 'python-dotenv'),
        ('sentence_transformers', 'sentence-transformers'),
        ('numpy', 'numpy'),
        ('openai', 'openai')
    ]
    
    missing = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"✓ {package_name} installed")
        except ImportError:
            print(f"❌ {package_name} not installed")
            missing.append(package_name)
    
    if missing:
        print("\n⚠️  Missing dependencies detected!")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def check_openai_config():
    """Check if OpenAI is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or not api_key.strip() or api_key.startswith('your_'):
        print("⚠️  OpenAI API key not configured")
        print("   The chatbot will work with limited functionality")
        print("   To enable full AI capabilities, run: python setup_openai.py")
        return False
    
    print("✓ OpenAI API key configured")
    return True

def check_database():
    """Check if database exists and is initialized"""
    db_path = Path('chatbot.db')
    
    if not db_path.exists():
        print("⚠️  Database not found - will be created on first run")
        return False
    
    print("✓ Database exists")
    
    # Check if database has knowledge entries
    try:
        from database import Database
        db = Database()
        knowledge = db.get_all_knowledge()
        
        if len(knowledge) == 0:
            print("⚠️  Knowledge base is empty")
            print("   Run: python seed_knowledge.py (to add sample data)")
            return False
        else:
            print(f"✓ Knowledge base has {len(knowledge)} entries")
            return True
    except Exception as e:
        print(f"⚠️  Could not check database: {e}")
        return False

def run_server():
    """Start the Flask server"""
    print("\n" + "=" * 70)
    print("Starting RAG Chatbot Server...")
    print("=" * 70 + "\n")
    
    from app import app
    
    print("Server is running at: http://localhost:5001")
    print("API endpoints available at: http://localhost:5001/api/")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

def main():
    """Main startup routine"""
    print("=" * 70)
    print("RAG Chatbot - Startup Check")
    print("=" * 70)
    print()
    
    # Run all checks
    checks_passed = True
    
    print("Checking Python version...")
    if not check_python_version():
        checks_passed = False
    print()
    
    print("Checking dependencies...")
    if not check_dependencies():
        checks_passed = False
    print()
    
    print("Checking OpenAI configuration...")
    openai_configured = check_openai_config()
    print()
    
    print("Checking database...")
    db_ready = check_database()
    print()
    
    # Decide whether to proceed
    if not checks_passed:
        print("=" * 70)
        print("❌ Critical checks failed. Please fix the issues above.")
        print("=" * 70)
        sys.exit(1)
    
    if not openai_configured:
        print("=" * 70)
        print("⚠️  OpenAI not configured - chatbot will have limited functionality")
        proceed = input("Do you want to start anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("\nSetup cancelled. Run 'python setup_openai.py' to configure OpenAI.")
            sys.exit(0)
        print()
    
    if not db_ready:
        print("=" * 70)
        print("⚠️  Knowledge base is empty or not initialized")
        seed = input("Do you want to seed the knowledge base now? (y/n): ").strip().lower()
        if seed == 'y':
            print("\nSeeding knowledge base...")
            try:
                from seed_knowledge import seed_knowledge_base
                seed_knowledge_base()
            except Exception as e:
                print(f"❌ Error seeding database: {e}")
                sys.exit(1)
        print()
    
    # Start the server
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Server stopped by user")
        print("=" * 70)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

