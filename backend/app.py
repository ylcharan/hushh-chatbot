from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from database import Database
from rag_service import RAGService
from scraper_service import ScraperService
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os
import json
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize services
print("\n" + "=" * 70)
print("Initializing Hushh AI ChatBot Backend")
print("=" * 70 + "\n")

db = Database()
rag_service = RAGService()
scraper_service = ScraperService()

print("\n" + "=" * 70)
print("Backend initialization complete!")
print("=" * 70 + "\n")

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to Hushh AI API',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'chat': '/api/chat',
            'knowledge': '/api/knowledge',
            'sessions': '/api/sessions'
        }
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Hushh AI Backend',
        'database': 'connected',
        'rag_service': 'active'
    })

# ============ Knowledge Base Endpoints ============

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    """Get all knowledge base entries"""
    try:
        knowledge = db.get_all_knowledge()
        return jsonify({
            'success': True,
            'count': len(knowledge),
            'knowledge': knowledge
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<knowledge_id>', methods=['GET'])
def get_knowledge_by_id(knowledge_id):
    """Get a specific knowledge base entry"""
    try:
        knowledge = db.get_knowledge_by_id(knowledge_id)
        if knowledge:
            return jsonify({
                'success': True,
                'knowledge': knowledge
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Knowledge entry not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge', methods=['POST'])
def add_knowledge():
    """Add a new knowledge base entry (legacy - text only)"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Title and content are required'
            }), 400
        
        title = data['title']
        content = data['content']
        category = data.get('category', 'general')
        
        # Generate embedding for the content
        embedding = rag_service.generate_embedding(content)
        
        # Add to database with source type
        knowledge_id = db.add_knowledge(
            title, content, embedding, category,
            source_type='text',
            source_url=None,
            metadata={}
        )
        
        return jsonify({
            'success': True,
            'message': 'Knowledge added successfully',
            'id': knowledge_id
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<knowledge_id>', methods=['PUT'])
def update_knowledge(knowledge_id):
    """Update a knowledge base entry"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # If content is updated, regenerate embedding
        embedding = None
        if 'content' in data:
            embedding = rag_service.generate_embedding(data['content'])
        
        success = db.update_knowledge(
            knowledge_id,
            title=data.get('title'),
            content=data.get('content'),
            embedding=embedding,
            category=data.get('category')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Knowledge updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Knowledge entry not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/knowledge/<knowledge_id>', methods=['DELETE'])
def delete_knowledge(knowledge_id):
    """Delete a knowledge base entry"""
    try:
        success = db.delete_knowledge(knowledge_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Knowledge deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Knowledge entry not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============ Chat Endpoints ============

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with RAG"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id')
        
        # Create or get session
        if not session_id:
            session_id = str(uuid.uuid4())
            db.create_session(session_id)
        else:
            # Update session activity
            db.update_session_activity(session_id)
        
        # Get knowledge base with embeddings
        knowledge_base = db.get_all_knowledge_with_embeddings()
        
        # Get chat history for context
        chat_history = db.get_chat_history(session_id, limit=10)
        
        # Generate response using RAG
        response, context_used = rag_service.generate_chat_response(
            user_message,
            knowledge_base,
            chat_history
        )
        
        # Save to chat history
        db.add_chat_message(session_id, user_message, response, context_used)
        
        return jsonify({
            'success': True,
            'response': response,
            'session_id': session_id,
            'context_used': context_used,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Handle chat messages with streaming RAG response"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id')
        
        # Create or get session
        if not session_id:
            session_id = str(uuid.uuid4())
            db.create_session(session_id)
        else:
            # Update session activity
            db.update_session_activity(session_id)
        
        # Get knowledge base with embeddings
        knowledge_base = db.get_all_knowledge_with_embeddings()
        
        # Get chat history for context
        chat_history = db.get_chat_history(session_id, limit=10)
        
        def generate():
            """Generator function for streaming response"""
            full_response = ""
            context_used = []
            
            try:
                for chunk in rag_service.generate_chat_response_stream(
                    user_message,
                    knowledge_base,
                    chat_history
                ):
                    if chunk['type'] == 'context':
                        context_used = chunk['context']
                        # Send session_id and context first
                        yield f"data: {json.dumps({'type': 'init', 'session_id': session_id, 'context': context_used})}\n\n"
                    elif chunk['type'] == 'content':
                        full_response += chunk['content']
                        yield f"data: {json.dumps({'type': 'content', 'content': chunk['content']})}\n\n"
                    elif chunk['type'] == 'done':
                        # Save to chat history
                        db.add_chat_message(session_id, user_message, full_response, context_used)
                        yield f"data: {json.dumps({'type': 'done', 'timestamp': datetime.now().isoformat()})}\n\n"
            except Exception as e:
                print(f"Error in streaming: {e}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = db.get_chat_history(session_id, limit)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'count': len(history),
            'history': history
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============ Session Endpoints ============

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        db.create_session(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session information"""
    try:
        session = db.get_session(session_id)
        
        if session:
            return jsonify({
                'success': True,
                'session': session
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============ Scraper Endpoints ============

@app.route('/api/scraper/text', methods=['POST'])
def scrape_text():
    """Process text content and add to knowledge base"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        text_content = data['content']
        title = data.get('title')
        category = data.get('category', 'general')
        
        # Validate
        is_valid, error_msg = scraper_service.validate_source('text', text_content)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Process text
        result = scraper_service.process_text_content(text_content, title)
        
        # Generate embedding
        embedding = rag_service.generate_embedding(result['content'])
        
        # Add to database
        knowledge_id = db.add_knowledge(
            result['title'],
            result['content'],
            embedding,
            category,
            source_type=result['source_type'],
            source_url=result['source_url'],
            metadata=result['metadata']
        )
        
        return jsonify({
            'success': True,
            'message': 'Text content added successfully',
            'id': knowledge_id,
            'title': result['title']
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scraper/url', methods=['POST'])
def scrape_url():
    """Scrape website URL and add to knowledge base"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data['url']
        category = data.get('category', 'general')
        max_depth = data.get('max_depth', 0)  # Default: only scrape the given page
        extract_links = data.get('extract_links', False)
        
        # Validate
        is_valid, error_msg = scraper_service.validate_source('url', url)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Scrape website
        results = scraper_service.scrape_website(url, max_depth, extract_links)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No content could be extracted from the URL'
            }), 400
        
        # Process each scraped page
        knowledge_ids = []
        for result in results:
            # Generate embedding
            embedding = rag_service.generate_embedding(result['content'])
            
            # Add to database
            knowledge_id = db.add_knowledge(
                result['title'],
                result['content'],
                embedding,
                category,
                source_type=result['source_type'],
                source_url=result['source_url'],
                metadata=result['metadata']
            )
            knowledge_ids.append({
                'id': knowledge_id,
                'title': result['title'],
                'url': result['source_url']
            })
        
        return jsonify({
            'success': True,
            'message': f'Successfully scraped and added {len(knowledge_ids)} page(s)',
            'count': len(knowledge_ids),
            'entries': knowledge_ids
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scraper/file', methods=['POST'])
def scrape_file():
    """Process uploaded file and add to knowledge base"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Get additional parameters
        category = request.form.get('category', 'general')
        custom_title = request.form.get('title')
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Validate file type
        is_valid, error_msg = scraper_service.validate_source('file', filename)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Read file content
        file_content = file.read()
        
        # Process file
        result = scraper_service.process_file(
            file_content=file_content,
            filename=filename
        )
        
        # Use custom title if provided
        if custom_title:
            result['title'] = custom_title
        
        # Generate embedding
        embedding = rag_service.generate_embedding(result['content'])
        
        # Add to database
        knowledge_id = db.add_knowledge(
            result['title'],
            result['content'],
            embedding,
            category,
            source_type=result['source_type'],
            source_url=result['source_url'],
            metadata=result['metadata']
        )
        
        return jsonify({
            'success': True,
            'message': 'File processed and added successfully',
            'id': knowledge_id,
            'title': result['title'],
            'filename': filename
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scraper/supported-types', methods=['GET'])
def get_supported_types():
    """Get list of supported file types"""
    try:
        supported_types = scraper_service.get_supported_file_types()
        return jsonify({
            'success': True,
            'supported_types': supported_types
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============ Legacy Endpoints (for compatibility) ============

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        'data': 'Sample data from backend',
        'timestamp': '2025-11-20'
    })

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.get_json()
    return jsonify({
        'message': 'Data received successfully',
        'received': data
    }), 201

if __name__ == '__main__':
    print("Starting Hushh AI Backend...")
    print("Initializing database and RAG service...")
    app.run(debug=True, host='0.0.0.0', port=5001)

