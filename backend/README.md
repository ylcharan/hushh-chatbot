# RAG Chatbot Backend

An intelligent chatbot backend powered by OpenAI GPT models and RAG (Retrieval Augmented Generation) technology. This system combines semantic search with large language models to provide accurate, context-aware responses based on your knowledge base.

## Features

- 🤖 **OpenAI Integration** - Uses GPT-3.5-turbo for intelligent responses
- 🔍 **Semantic Search** - Vector embeddings for finding relevant knowledge
- 💾 **Knowledge Base Management** - Easy CRUD operations for knowledge entries
- 💬 **Session Management** - Track conversations and maintain context
- 📊 **Chat History** - Store and retrieve conversation history
- 🔄 **Fallback Mode** - Works with limited functionality without OpenAI API key

## Quick Start

### Option 1: Automated Setup (Recommended)

**macOS/Linux:**
```bash
./quick_start.sh
```

**Windows:**
```bash
quick_start.bat
```

### Option 2: Manual Setup

1. **Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure OpenAI API Key**
```bash
python setup_openai.py
```
Get your API key from: https://platform.openai.com/api-keys

3. **Seed Knowledge Base**
```bash
python seed_knowledge.py
```

4. **Start Server**
```bash
python app.py
# OR with startup checks:
python start.py
```

The server will start at `http://localhost:5001`

## Testing

Run the comprehensive test suite:
```bash
python test_chatbot.py
```

This tests:
- Embedding generation
- Database operations
- Knowledge retrieval
- Chat response generation
- OpenAI API connection

## API Endpoints

### Health & Info
- `GET /` - Welcome message with endpoint list
- `GET /api/health` - Health check

### Chat
- `POST /api/chat` - Send a message to the chatbot
  ```json
  {
    "message": "What are your business hours?",
    "session_id": "optional-session-id"
  }
  ```

- `GET /api/chat/history/<session_id>` - Get chat history

### Knowledge Base
- `GET /api/knowledge` - List all knowledge entries
- `GET /api/knowledge/<id>` - Get specific entry
- `POST /api/knowledge` - Add new knowledge entry
  ```json
  {
    "title": "Knowledge Title",
    "content": "Detailed content...",
    "category": "general"
  }
  ```
- `PUT /api/knowledge/<id>` - Update entry
- `DELETE /api/knowledge/<id>` - Delete entry

### Sessions
- `POST /api/sessions` - Create new session
- `GET /api/sessions/<session_id>` - Get session info

## Architecture

### RAG Pipeline

1. **User Query** → Embedding generation
2. **Semantic Search** → Find relevant knowledge (cosine similarity)
3. **Context Retrieval** → Top-K most relevant entries
4. **LLM Generation** → OpenAI GPT with context + chat history
5. **Response** → Intelligent, context-aware answer

### Components

- **app.py** - Flask REST API server
- **rag_service.py** - RAG pipeline and OpenAI integration
- **database.py** - SQLite database operations
- **seed_knowledge.py** - Sample knowledge data
- **setup_openai.py** - Interactive OpenAI setup
- **start.py** - Comprehensive startup script
- **test_chatbot.py** - Test suite
- **example_usage.py** - Usage examples

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo  # optional
DATABASE_PATH=chatbot.db     # optional
```

### RAG Parameters

Edit `rag_service.py` to customize:

- **Embedding Model** - Default: `all-MiniLM-L6-v2`
- **Top-K Results** - Default: 3 most relevant entries
- **Similarity Threshold** - Default: 0.3
- **Max Tokens** - Default: 800
- **Temperature** - Default: 0.7

## Adding Your Own Knowledge

### Via API (Recommended)
```bash
curl -X POST http://localhost:5001/api/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Your Knowledge Title",
    "content": "Your detailed content here...",
    "category": "general"
  }'
```

### Via Python Script
```python
from database import Database
from rag_service import RAGService

db = Database()
rag = RAGService()

embedding = rag.generate_embedding("Your content")
db.add_knowledge(
    title="Your Title",
    content="Your content",
    embedding=embedding,
    category="general"
)
```

### Via Example Script
```bash
python example_usage.py
# Select option 1: Add Knowledge
```

## Troubleshooting

**Problem:** OpenAI API key not configured
- **Solution:** Run `python setup_openai.py`

**Problem:** Knowledge base is empty
- **Solution:** Run `python seed_knowledge.py`

**Problem:** Module not found errors
- **Solution:** Run `pip install -r requirements.txt`

**Problem:** Slow responses
- **Solution:** Check internet connection, verify OpenAI API key

**Problem:** Rate limit exceeded
- **Solution:** Wait and retry, or upgrade OpenAI plan

## Costs

OpenAI API costs (approximate):
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- Average message: ~500-1000 tokens
- Cost per message: ~$0.001-$0.002

Free tier: $5 credits (~2,500-5,000 messages)

## Dependencies

- Flask - Web framework
- Flask-CORS - Cross-origin support
- python-dotenv - Environment variables
- sentence-transformers - Embedding generation
- numpy - Vector operations
- openai - OpenAI API client

## Files

```
backend/
├── app.py                    # Main Flask application
├── rag_service.py           # RAG pipeline & OpenAI
├── database.py              # Database operations
├── seed_knowledge.py        # Sample data seeder
├── setup_openai.py          # OpenAI configuration
├── start.py                 # Startup script with checks
├── test_chatbot.py          # Test suite
├── example_usage.py         # Usage examples
├── quick_start.sh           # Quick start (Unix)
├── quick_start.bat          # Quick start (Windows)
├── requirements.txt         # Python dependencies
├── SETUP_INSTRUCTIONS.txt   # Detailed setup guide
└── README.md               # This file
```

## Next Steps

1. Start the frontend: `cd ../frontend && npm run dev`
2. Access web interface at `http://localhost:3000`
3. Customize knowledge base with your data
4. Integrate via API into your systems

## Support

For detailed setup instructions, see `SETUP_INSTRUCTIONS.txt`

For usage examples, run `python example_usage.py`

