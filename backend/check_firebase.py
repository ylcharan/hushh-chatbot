import os
import json
from dotenv import load_dotenv

load_dotenv()

def check_firebase_config():
    """Check if Firebase is properly configured"""
    
    print("\n" + "="*70)
    print("Firebase Configuration Check")
    print("="*70 + "\n")
    
    config_found = False
    
    # Check for firebase-config.json
    firebase_config_path = os.getenv('FIREBASE_CONFIG_PATH', 'firebase-config.json')
    
    if os.path.exists(firebase_config_path):
        print(f"✓ Found: {firebase_config_path}")
        try:
            with open(firebase_config_path, 'r') as f:
                config = json.load(f)
                if 'project_id' in config:
                    print(f"✓ Project ID: {config['project_id']}")
                    print(f"✓ Client Email: {config.get('client_email', 'N/A')}")
                    config_found = True
                else:
                    print("⚠️  Warning: Invalid firebase-config.json format")
        except json.JSONDecodeError:
            print("⚠️  Error: firebase-config.json is not valid JSON")
        except Exception as e:
            print(f"⚠️  Error reading firebase-config.json: {e}")
    else:
        print(f"✗ Not found: {firebase_config_path}")
    
    # Check for environment variables
    print("\nEnvironment Variables:")
    env_vars = {
        'FIREBASE_PROJECT_ID': os.getenv('FIREBASE_PROJECT_ID'),
        'FIREBASE_CLIENT_EMAIL': os.getenv('FIREBASE_CLIENT_EMAIL'),
        'FIREBASE_PRIVATE_KEY': os.getenv('FIREBASE_PRIVATE_KEY'),
    }
    
    env_configured = True
    for key, value in env_vars.items():
        if value:
            if key == 'FIREBASE_PRIVATE_KEY':
                print(f"✓ {key}: [SET]")
            else:
                print(f"✓ {key}: {value}")
        else:
            print(f"✗ {key}: Not set")
            env_configured = False
    
    if env_configured:
        config_found = True
    
    print("\n" + "="*70)
    
    if config_found:
        print("✓ Firebase is configured!")
        print("\nYou can now run: python app.py")
    else:
        print("✗ Firebase is NOT configured")
        print("\nTo configure Firebase:")
        print("1. Run: python setup_firebase.py")
        print("2. Or place firebase-config.json in this directory")
        print("3. Or set environment variables in .env file")
        print("\nSee FIREBASE_SETUP.md for detailed instructions")
    
    print("="*70 + "\n")
    
    return config_found

if __name__ == "__main__":
    check_firebase_config()

