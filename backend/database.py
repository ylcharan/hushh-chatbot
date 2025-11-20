import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.db = None
        self.init_database()
    
    def init_database(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            firebase_admin.get_app()
            print("✓ Firebase already initialized")
        except ValueError:
            # Initialize Firebase
            firebase_config_path = os.getenv('FIREBASE_CONFIG_PATH', 'firebase-config.json')
            
            if os.path.exists(firebase_config_path):
                cred = credentials.Certificate(firebase_config_path)
                firebase_admin.initialize_app(cred)
                print(f"✓ Firebase initialized with config: {firebase_config_path}")
            else:
                # Try to initialize with environment variables
                firebase_config = {
                    "type": os.getenv('FIREBASE_TYPE', 'service_account'),
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                    "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
                }
                
                if firebase_config['project_id']:
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                    print("✓ Firebase initialized with environment variables")
                else:
                    print("⚠️  Firebase not configured. Please set up firebase-config.json or environment variables.")
                    raise Exception("Firebase configuration not found")
        
        self.db = firestore.client()
    
    # Knowledge Base Operations
    def add_knowledge(self, title: str, content: str, embedding: List[float], category: str = 'general',
                     source_type: str = 'text', source_url: str = None, metadata: Dict = None) -> str:
        """Add a new knowledge base entry"""
        doc_ref = self.db.collection('knowledge_base').document()
        
        data = {
            'title': title,
            'content': content,
            'embedding': embedding,
            'category': category,
            'source_type': source_type,  # 'text', 'url', or 'file'
            'source_url': source_url,  # Original URL if scraped from web
            'metadata': metadata or {},  # Additional metadata about the source
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(data)
        return doc_ref.id
    
    def get_all_knowledge(self) -> List[Dict]:
        """Get all knowledge base entries"""
        try:
            docs = self.db.collection('knowledge_base').stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                # Remove embedding from general listing
                if 'embedding' in data:
                    del data['embedding']
                results.append(data)
            
            # Sort by created_at in Python (handle both datetime and timestamp objects)
            results.sort(key=lambda x: x.get('created_at') or datetime.min, reverse=True)
            
            return results
        except Exception as e:
            print(f"Error fetching knowledge base: {e}")
            return []
    
    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict]:
        """Get a specific knowledge base entry"""
        doc_ref = self.db.collection('knowledge_base').document(knowledge_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_all_knowledge_with_embeddings(self) -> List[Dict]:
        """Get all knowledge base entries with embeddings"""
        docs = self.db.collection('knowledge_base').stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        
        return results
    
    def update_knowledge(self, knowledge_id: str, title: str = None, content: str = None, 
                        embedding: List[float] = None, category: str = None,
                        source_type: str = None, source_url: str = None, metadata: Dict = None) -> bool:
        """Update a knowledge base entry"""
        doc_ref = self.db.collection('knowledge_base').document(knowledge_id)
        
        if not doc_ref.get().exists:
            return False
        
        updates = {'updated_at': firestore.SERVER_TIMESTAMP}
        
        if title is not None:
            updates['title'] = title
        if content is not None:
            updates['content'] = content
        if embedding is not None:
            updates['embedding'] = embedding
        if category is not None:
            updates['category'] = category
        if source_type is not None:
            updates['source_type'] = source_type
        if source_url is not None:
            updates['source_url'] = source_url
        if metadata is not None:
            updates['metadata'] = metadata
        
        if len(updates) > 1:  # More than just updated_at
            doc_ref.update(updates)
            return True
        
        return False
    
    def delete_knowledge(self, knowledge_id: str) -> bool:
        """Delete a knowledge base entry"""
        doc_ref = self.db.collection('knowledge_base').document(knowledge_id)
        
        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False
    
    # Chat History Operations
    def add_chat_message(self, session_id: str, user_message: str, 
                        bot_response: str, context_used: List[Dict] = None) -> str:
        """Add a chat message to history"""
        doc_ref = self.db.collection('chat_history').document()
        
        data = {
            'session_id': session_id,
            'user_message': user_message,
            'bot_response': bot_response,
            'context_used': context_used if context_used else [],
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(data)
        return doc_ref.id
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a session"""
        try:
            # Query with filter and order_by requires a composite index
            # For now, we'll fetch all messages for the session and sort in Python
            docs = (self.db.collection('chat_history')
                    .where(filter=firestore.FieldFilter('session_id', '==', session_id))
                    .stream())
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            # Sort by created_at in Python (handle both datetime and timestamp objects)
            results.sort(key=lambda x: x.get('created_at') or datetime.min)
            
            # Return only the requested limit
            return results[:limit]
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            # Return empty list on error
            return []
    
    # Session Operations
    def create_session(self, session_id: str) -> bool:
        """Create a new session"""
        doc_ref = self.db.collection('sessions').document(session_id)
        
        # Check if session already exists
        if doc_ref.get().exists:
            return False
        
        data = {
            'session_id': session_id,
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_activity': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(data)
        return True
    
    def update_session_activity(self, session_id: str) -> bool:
        """Update the last activity timestamp for a session"""
        doc_ref = self.db.collection('sessions').document(session_id)
        
        if doc_ref.get().exists:
            doc_ref.update({'last_activity': firestore.SERVER_TIMESTAMP})
            return True
        return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information"""
        doc_ref = self.db.collection('sessions').document(session_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
