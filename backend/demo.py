#!/usr/bin/env python3
"""
Interactive demo of the RAG chatbot
Run this to see the chatbot in action from the command line
"""

from database import Database
from rag_service import RAGService
from dotenv import load_dotenv
import uuid
import sys

# Load environment variables
load_dotenv()

def print_header():
    """Print demo header"""
    print("\n" + "=" * 70)
    print("RAG CHATBOT - INTERACTIVE DEMO")
    print("=" * 70)
    print("\nThis demo shows the chatbot responding to your questions.")
    print("The chatbot uses your knowledge base to provide accurate answers.")
    print("\nCommands:")
    print("  - Type your question and press Enter")
    print("  - Type 'quit' or 'exit' to end the demo")
    print("  - Type 'history' to see conversation history")
    print("  - Type 'new' to start a new conversation")
    print("=" * 70 + "\n")

def print_response(response, context):
    """Print chatbot response with context"""
    print("\n" + "-" * 70)
    print("🤖 Chatbot:")
    print("-" * 70)
    print(response)
    
    if context:
        print("\n📚 Knowledge used:")
        for i, ctx in enumerate(context, 1):
            print(f"  {i}. {ctx['title']} (relevance: {ctx['similarity']:.1%})")
    
    print("-" * 70 + "\n")

def main():
    """Run interactive demo"""
    
    # Initialize
    try:
        db = Database()
        rag = RAGService()
    except Exception as e:
        print(f"\n❌ Error initializing chatbot: {e}")
        print("\nPlease make sure:")
        print("  1. Dependencies are installed: pip install -r requirements.txt")
        print("  2. OpenAI is configured: python setup_openai.py")
        sys.exit(1)
    
    # Check knowledge base
    knowledge_base = db.get_all_knowledge_with_embeddings()
    
    if not knowledge_base:
        print("\n⚠️  Knowledge base is empty!")
        print("Run 'python seed_knowledge.py' to add sample knowledge.")
        sys.exit(1)
    
    print(f"\n✓ Loaded {len(knowledge_base)} knowledge entries")
    
    # Create session
    session_id = str(uuid.uuid4())
    db.create_session(session_id)
    
    # Print header
    print_header()
    
    # Suggest some questions
    print("💡 Try asking:")
    print("  - What are your business hours?")
    print("  - Tell me about your pricing plans")
    print("  - What languages do you support?")
    print("  - How do I get started?")
    print()
    
    message_count = 0
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Check for commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for trying the chatbot demo!")
                print(f"Total messages in this session: {message_count}")
                break
            
            if user_input.lower() == 'history':
                history = db.get_chat_history(session_id)
                print(f"\n📜 Conversation History ({len(history)} messages):")
                print("-" * 70)
                for msg in history:
                    print(f"\nYou: {msg['user_message']}")
                    print(f"Bot: {msg['bot_response'][:100]}...")
                print("-" * 70 + "\n")
                continue
            
            if user_input.lower() == 'new':
                session_id = str(uuid.uuid4())
                db.create_session(session_id)
                message_count = 0
                print("\n✨ Started new conversation\n")
                continue
            
            # Get chat history for context
            chat_history = db.get_chat_history(session_id, limit=10)
            
            # Generate response
            print("\n🤔 Thinking...")
            response, context = rag.generate_chat_response(
                query=user_input,
                knowledge_base=knowledge_base,
                chat_history=chat_history,
                top_k=3
            )
            
            # Save to history
            db.add_chat_message(session_id, user_input, response, context)
            message_count += 1
            
            # Print response
            print_response(response, context)
        
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.\n")

if __name__ == "__main__":
    main()

