"""
Setup script to configure OpenAI API key
Run this before starting the chatbot for the first time
"""

import os
from pathlib import Path

def setup_openai():
    """Interactive setup for OpenAI API key"""
    
    print("=" * 70)
    print("OpenAI API Setup")
    print("=" * 70)
    print()
    print("This chatbot uses OpenAI's GPT models to generate intelligent responses.")
    print("You need an OpenAI API key to use this feature.")
    print()
    print("To get your API key:")
    print("  1. Visit: https://platform.openai.com/api-keys")
    print("  2. Sign in or create an account")
    print("  3. Click 'Create new secret key'")
    print("  4. Copy the key (it starts with 'sk-')")
    print()
    print("=" * 70)
    print()
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print()
        print("⚠️  No API key provided. The chatbot will work with limited functionality.")
        print("   You can add the API key later by setting the OPENAI_API_KEY environment variable.")
        print()
        return False
    
    # Validate API key format
    if not api_key.startswith('sk-'):
        print()
        print("⚠️  Warning: API key should start with 'sk-'")
        print("   The key you entered might be invalid.")
        proceed = input("   Do you want to continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("   Setup cancelled.")
            return False
    
    # Create .env file
    env_path = Path(__file__).parent / '.env'
    
    try:
        with open(env_path, 'w') as f:
            f.write(f"# OpenAI API Configuration\n")
            f.write(f"OPENAI_API_KEY={api_key}\n")
            f.write(f"\n")
            f.write(f"# Optional: Specify OpenAI model (default: gpt-3.5-turbo)\n")
            f.write(f"# OPENAI_MODEL=gpt-3.5-turbo\n")
            f.write(f"\n")
            f.write(f"# Optional: Database path (default: chatbot.db)\n")
            f.write(f"# DATABASE_PATH=chatbot.db\n")
        
        print()
        print("✅ OpenAI API key saved successfully!")
        print(f"   Configuration saved to: {env_path}")
        print()
        print("Next steps:")
        print("  1. Run: python seed_knowledge.py (to populate the knowledge base)")
        print("  2. Run: python app.py (to start the chatbot server)")
        print()
        return True
        
    except Exception as e:
        print()
        print(f"❌ Error saving configuration: {e}")
        print()
        print("Alternative: Set the environment variable manually:")
        print(f"   export OPENAI_API_KEY='{api_key}'")
        print()
        return False

def check_existing_setup():
    """Check if OpenAI is already configured"""
    
    # Check environment variable
    if os.getenv('OPENAI_API_KEY'):
        print()
        print("✅ OpenAI API key is already configured via environment variable.")
        print()
        return True
    
    # Check .env file
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                if 'OPENAI_API_KEY=' in content and 'sk-' in content:
                    print()
                    print("✅ OpenAI API key is already configured in .env file.")
                    print()
                    return True
        except:
            pass
    
    return False

if __name__ == "__main__":
    if check_existing_setup():
        reconfigure = input("Do you want to reconfigure? (y/n): ").strip().lower()
        if reconfigure != 'y':
            print("Setup cancelled.")
            exit(0)
    
    setup_openai()

