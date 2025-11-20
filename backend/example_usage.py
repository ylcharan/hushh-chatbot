#!/usr/bin/env python3
"""
Example script showing how to use the RAG chatbot programmatically
"""

from database import Database
from rag_service import RAGService
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

def example_add_knowledge():
    """Example: Add knowledge to the database"""
    print("\n" + "=" * 70)
    print("Example 1: Adding Knowledge to the Database")
    print("=" * 70 + "\n")
    
    db = Database()
    rag = RAGService()
    
    # Define your knowledge
    knowledge_entries = [
        {
            "title": "Return Policy",
            "content": """Our return policy allows customers to return products within 30 days 
            of purchase for a full refund. Items must be unused and in original packaging. 
            To initiate a return, contact our support team with your order number.""",
            "category": "policy"
        },
        {
            "title": "Shipping Information",
            "content": """We offer free shipping on orders over $50. Standard shipping takes 
            3-5 business days. Express shipping (1-2 days) is available for an additional fee. 
            International shipping is available to most countries.""",
            "category": "shipping"
        }
    ]
    
    for entry in knowledge_entries:
        # Generate embedding for the content
        embedding = rag.generate_embedding(entry['content'])
        
        # Add to database
        knowledge_id = db.add_knowledge(
            title=entry['title'],
            content=entry['content'],
            embedding=embedding,
            category=entry['category']
        )
        
        print(f"✓ Added: {entry['title']} (ID: {knowledge_id})")
    
    print("\nKnowledge entries added successfully!")

def example_query_chatbot():
    """Example: Query the chatbot"""
    print("\n" + "=" * 70)
    print("Example 2: Querying the Chatbot")
    print("=" * 70 + "\n")
    
    db = Database()
    rag = RAGService()
    
    # Get all knowledge with embeddings
    knowledge_base = db.get_all_knowledge_with_embeddings()
    
    if not knowledge_base:
        print("⚠️  No knowledge in database. Run 'python seed_knowledge.py' first.")
        return
    
    print(f"Loaded {len(knowledge_base)} knowledge entries\n")
    
    # Example queries
    queries = [
        "What are your business hours?",
        "How much does your service cost?",
        "What languages do you support?",
        "Tell me about your API"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        print("-" * 70)
        
        # Generate response
        response, context = rag.generate_chat_response(
            query=query,
            knowledge_base=knowledge_base,
            chat_history=None,
            top_k=3
        )
        
        # Show context used
        if context:
            print(f"Context used ({len(context)} entries):")
            for ctx in context:
                print(f"  - {ctx['title']} (similarity: {ctx['similarity']:.3f})")
        
        # Show response
        print(f"\nResponse:")
        print(response)
        print("\n" + "=" * 70 + "\n")

def example_conversation():
    """Example: Multi-turn conversation with context"""
    print("\n" + "=" * 70)
    print("Example 3: Multi-turn Conversation")
    print("=" * 70 + "\n")
    
    db = Database()
    rag = RAGService()
    
    # Create a session
    session_id = str(uuid.uuid4())
    db.create_session(session_id)
    print(f"Created session: {session_id}\n")
    
    # Get knowledge base
    knowledge_base = db.get_all_knowledge_with_embeddings()
    
    if not knowledge_base:
        print("⚠️  No knowledge in database.")
        return
    
    # Simulate a conversation
    conversation = [
        "What are your pricing plans?",
        "What's included in the Professional plan?",
        "Do you offer discounts for annual subscriptions?"
    ]
    
    for user_message in conversation:
        print(f"User: {user_message}")
        
        # Get chat history for context
        chat_history = db.get_chat_history(session_id, limit=10)
        
        # Generate response
        response, context = rag.generate_chat_response(
            query=user_message,
            knowledge_base=knowledge_base,
            chat_history=chat_history,
            top_k=3
        )
        
        # Save to chat history
        db.add_chat_message(session_id, user_message, response, context)
        
        print(f"Bot: {response}")
        print("-" * 70 + "\n")
    
    # Show full conversation history
    print("Full conversation history:")
    history = db.get_chat_history(session_id)
    print(f"Total messages: {len(history)}")

def example_search_knowledge():
    """Example: Search knowledge base"""
    print("\n" + "=" * 70)
    print("Example 4: Semantic Search in Knowledge Base")
    print("=" * 70 + "\n")
    
    db = Database()
    rag = RAGService()
    
    # Get all knowledge
    knowledge_base = db.get_all_knowledge_with_embeddings()
    
    if not knowledge_base:
        print("⚠️  No knowledge in database.")
        return
    
    # Search queries
    search_queries = [
        "pricing and costs",
        "technical documentation",
        "customer support contact"
    ]
    
    for query in search_queries:
        print(f"Search: '{query}'")
        
        # Retrieve relevant context
        results = rag.retrieve_relevant_context(
            query=query,
            knowledge_base=knowledge_base,
            top_k=5,
            threshold=0.2
        )
        
        if results:
            print(f"Found {len(results)} relevant entries:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     Category: {result['category']}")
                print(f"     Similarity: {result['similarity']:.3f}")
                print(f"     Preview: {result['content'][:100]}...")
        else:
            print("  No relevant entries found")
        
        print()

def example_manage_knowledge():
    """Example: Update and delete knowledge"""
    print("\n" + "=" * 70)
    print("Example 5: Managing Knowledge Entries")
    print("=" * 70 + "\n")
    
    db = Database()
    rag = RAGService()
    
    # Add a test entry
    print("Adding test entry...")
    embedding = rag.generate_embedding("This is a test entry for demonstration")
    knowledge_id = db.add_knowledge(
        title="Test Entry",
        content="This is a test entry for demonstration",
        embedding=embedding,
        category="test"
    )
    print(f"✓ Added entry with ID: {knowledge_id}\n")
    
    # Update the entry
    print("Updating entry...")
    new_content = "This is an updated test entry with new information"
    new_embedding = rag.generate_embedding(new_content)
    
    success = db.update_knowledge(
        knowledge_id=knowledge_id,
        title="Updated Test Entry",
        content=new_content,
        embedding=new_embedding,
        category="test-updated"
    )
    
    if success:
        print(f"✓ Updated entry {knowledge_id}\n")
    
    # Retrieve and display
    print("Retrieving updated entry...")
    entry = db.get_knowledge_by_id(knowledge_id)
    if entry:
        print(f"  Title: {entry['title']}")
        print(f"  Category: {entry['category']}")
        print(f"  Content: {entry['content']}\n")
    
    # Delete the entry
    print("Deleting test entry...")
    success = db.delete_knowledge(knowledge_id)
    if success:
        print(f"✓ Deleted entry {knowledge_id}")

def main():
    """Run all examples"""
    print("=" * 70)
    print("RAG Chatbot - Usage Examples")
    print("=" * 70)
    
    examples = [
        ("Add Knowledge", example_add_knowledge),
        ("Query Chatbot", example_query_chatbot),
        ("Conversation", example_conversation),
        ("Search Knowledge", example_search_knowledge),
        ("Manage Knowledge", example_manage_knowledge)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  {len(examples) + 1}. Run all examples")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect an example (0-6): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            
            choice_num = int(choice)
            
            if choice_num == len(examples) + 1:
                # Run all examples
                for name, func in examples:
                    func()
                break
            elif 1 <= choice_num <= len(examples):
                # Run selected example
                examples[choice_num - 1][1]()
            else:
                print("Invalid choice. Please try again.")
        
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

