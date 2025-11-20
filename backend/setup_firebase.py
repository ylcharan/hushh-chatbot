import os
import json

def setup_firebase():
    print("\n" + "="*70)
    print("Firebase Configuration Setup")
    print("="*70 + "\n")
    
    print("You need a Firebase service account key to use Firestore.")
    print("Follow these steps:")
    print("\n1. Go to Firebase Console: https://console.firebase.google.com/")
    print("2. Select your project (or create a new one)")
    print("3. Go to Project Settings > Service Accounts")
    print("4. Click 'Generate New Private Key'")
    print("5. Save the JSON file as 'firebase-config.json' in this directory")
    print("\nAlternatively, you can set environment variables in .env file:")
    print("  FIREBASE_PROJECT_ID")
    print("  FIREBASE_PRIVATE_KEY")
    print("  FIREBASE_CLIENT_EMAIL")
    print("  etc.")
    
    print("\n" + "="*70)
    
    choice = input("\nDo you want to:\n1. Use firebase-config.json file\n2. Set environment variables\n\nEnter choice (1 or 2): ")
    
    if choice == "1":
        print("\nPlease place your firebase-config.json file in the backend directory.")
        print("The file should be downloaded from Firebase Console.")
        
        if os.path.exists('firebase-config.json'):
            print("\n✓ firebase-config.json found!")
            
            # Verify it's valid JSON
            try:
                with open('firebase-config.json', 'r') as f:
                    config = json.load(f)
                    if 'project_id' in config:
                        print(f"✓ Project ID: {config['project_id']}")
                        print("\n✓ Firebase configuration is ready!")
                    else:
                        print("\n⚠️  Warning: firebase-config.json doesn't look like a valid service account key")
            except json.JSONDecodeError:
                print("\n⚠️  Error: firebase-config.json is not valid JSON")
        else:
            print("\n⚠️  firebase-config.json not found. Please add it to continue.")
    
    elif choice == "2":
        print("\nAdd these variables to your .env file:")
        print("\nFIREBASE_PROJECT_ID=your-project-id")
        print("FIREBASE_PRIVATE_KEY_ID=your-private-key-id")
        print('FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"')
        print("FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com")
        print("FIREBASE_CLIENT_ID=your-client-id")
        print("FIREBASE_CLIENT_CERT_URL=your-cert-url")
        
        print("\n✓ Update your .env file with the values from your service account JSON")
    
    print("\n" + "="*70)
    print("Setup Complete!")
    print("="*70 + "\n")

if __name__ == "__main__":
    setup_firebase()

