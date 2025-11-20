import sqlite3
import json
from database import Database
import os

def migrate_sqlite_to_firebase():
    """Migrate data from SQLite to Firebase Firestore"""
    
    sqlite_db_path = 'chatbot.db'
    
    if not os.path.exists(sqlite_db_path):
        print("No SQLite database found (chatbot.db). Nothing to migrate.")
        return
    
    print("\n" + "="*70)
    print("SQLite to Firebase Migration")
    print("="*70 + "\n")
    
    print("⚠️  This will copy all data from SQLite to Firebase.")
    print("   Your SQLite database will not be deleted.")
    
    confirm = input("\nContinue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    # Connect to SQLite
    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Initialize Firebase
    print("\nInitializing Firebase...")
    firebase_db = Database()
    print("✓ Firebase connected")
    
    # Migrate knowledge base
    print("\nMigrating knowledge base...")
    cursor.execute('SELECT * FROM knowledge_base')
    knowledge_entries = cursor.fetchall()
    
    knowledge_count = 0
    for entry in knowledge_entries:
        title = entry['title']
        content = entry['content']
        embedding = json.loads(entry['embedding']) if entry['embedding'] else []
        category = entry['category'] or 'general'
        
        firebase_db.add_knowledge(title, content, embedding, category)
        knowledge_count += 1
        print(f"  ✓ Migrated: {title}")
    
    print(f"\n✓ Migrated {knowledge_count} knowledge entries")
    
    # Migrate sessions
    print("\nMigrating sessions...")
    cursor.execute('SELECT * FROM sessions')
    sessions = cursor.fetchall()
    
    session_count = 0
    for session in sessions:
        session_id = session['session_id']
        try:
            firebase_db.create_session(session_id)
            session_count += 1
        except:
            pass  # Session might already exist
    
    print(f"✓ Migrated {session_count} sessions")
    
    # Migrate chat history
    print("\nMigrating chat history...")
    cursor.execute('SELECT * FROM chat_history')
    messages = cursor.fetchall()
    
    message_count = 0
    for msg in messages:
        session_id = msg['session_id']
        user_message = msg['user_message']
        bot_response = msg['bot_response']
        context_used = json.loads(msg['context_used']) if msg['context_used'] else []
        
        firebase_db.add_chat_message(session_id, user_message, bot_response, context_used)
        message_count += 1
    
    print(f"✓ Migrated {message_count} chat messages")
    
    conn.close()
    
    print("\n" + "="*70)
    print("Migration Complete!")
    print("="*70)
    print(f"\nSummary:")
    print(f"  - Knowledge entries: {knowledge_count}")
    print(f"  - Sessions: {session_count}")
    print(f"  - Chat messages: {message_count}")
    print(f"\nYour SQLite database (chatbot.db) has been preserved.")
    print(f"You can delete it manually if you no longer need it.")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        migrate_sqlite_to_firebase()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Make sure Firebase is properly configured before migrating.")

