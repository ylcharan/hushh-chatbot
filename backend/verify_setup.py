"""
Setup verification script
Run this to check if all dependencies are installed correctly
"""

import sys

def check_imports():
    """Check if all required packages can be imported"""
    print("Checking Python dependencies...\n")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'sentence_transformers': 'Sentence Transformers',
        'numpy': 'NumPy',
        'openai': 'OpenAI',
        'sqlite3': 'SQLite3 (built-in)'
    }
    
    all_good = True
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {name} - OK")
        except ImportError:
            print(f"✗ {name} - MISSING")
            all_good = False
    
    return all_good

def check_database():
    """Check if database can be initialized"""
    print("\n\nChecking database initialization...\n")
    
    try:
        from database import Database
        db = Database('test_verify.db')
        print("✓ Database initialization - OK")
        
        # Clean up test database
        import os
        if os.path.exists('test_verify.db'):
            os.remove('test_verify.db')
        
        return True
    except Exception as e:
        print(f"✗ Database initialization - FAILED: {e}")
        return False

def check_rag_service():
    """Check if RAG service can be initialized"""
    print("\n\nChecking RAG service...\n")
    
    try:
        from rag_service import RAGService
        print("Initializing RAG service (this may take a moment)...")
        rag = RAGService()
        print("✓ RAG service initialization - OK")
        
        # Test embedding generation
        print("\nTesting embedding generation...")
        test_text = "This is a test sentence."
        embedding = rag.generate_embedding(test_text)
        print(f"✓ Embedding generation - OK (dimension: {len(embedding)})")
        
        return True
    except Exception as e:
        print(f"✗ RAG service - FAILED: {e}")
        return False

def check_python_version():
    """Check Python version"""
    print("Checking Python version...\n")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version_str} - OK")
        return True
    else:
        print(f"✗ Python {version_str} - OUTDATED (need 3.8+)")
        return False

def main():
    print("=" * 60)
    print("RAG Chatbot Backend - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_imports),
        ("Database", check_database),
        ("RAG Service", check_rag_service)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name}: {status}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 All checks passed! Your setup is ready.")
        print("\nYou can now run:")
        print("  python app.py")
        print("\nOptionally, seed the database with sample data:")
        print("  python seed_knowledge.py")
    else:
        print("⚠️  Some checks failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

