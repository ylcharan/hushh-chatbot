#!/usr/bin/env python3
"""
Test script to verify the chatbot is working correctly
"""

import os
from dotenv import load_dotenv
from database import Database
from rag_service import RAGService

def test_embedding_generation():
    """Test if embeddings can be generated"""
    print("\n" + "=" * 70)
    print("Test 1: Embedding Generation")
    print("=" * 70)
    
    try:
        rag = RAGService()
        test_text = "This is a test sentence for embedding generation."
        embedding = rag.generate_embedding(test_text)
        
        print(f"✓ Generated embedding with dimension: {len(embedding)}")
        print(f"✓ First 5 values: {embedding[:5]}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\n" + "=" * 70)
    print("Test 2: Database Operations")
    print("=" * 70)
    
    try:
        db = Database()
        
        # Test adding knowledge
        print("Testing add knowledge...")
        rag = RAGService()
        test_embedding = rag.generate_embedding("Test content")
        
        knowledge_id = db.add_knowledge(
            title="Test Entry",
            content="This is a test knowledge entry",
            embedding=test_embedding,
            category="test"
        )
        print(f"✓ Added test knowledge with ID: {knowledge_id}")
        
        # Test retrieving knowledge
        print("Testing retrieve knowledge...")
        knowledge = db.get_knowledge_by_id(knowledge_id)
        if knowledge:
            print(f"✓ Retrieved knowledge: {knowledge['title']}")
        
        # Test deleting knowledge
        print("Testing delete knowledge...")
        success = db.delete_knowledge(knowledge_id)
        if success:
            print(f"✓ Deleted test knowledge")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_knowledge_retrieval():
    """Test knowledge retrieval with similarity search"""
    print("\n" + "=" * 70)
    print("Test 3: Knowledge Retrieval (Semantic Search)")
    print("=" * 70)
    
    try:
        db = Database()
        rag = RAGService()
        
        # Get all knowledge
        knowledge_base = db.get_all_knowledge_with_embeddings()
        
        if not knowledge_base:
            print("⚠️  No knowledge entries found in database")
            print("   Run: python seed_knowledge.py")
            return False
        
        print(f"✓ Found {len(knowledge_base)} knowledge entries")
        
        # Test retrieval
        test_query = "What are your business hours?"
        print(f"\nTest query: '{test_query}'")
        
        relevant_context = rag.retrieve_relevant_context(test_query, knowledge_base, top_k=3)
        
        if relevant_context:
            print(f"✓ Found {len(relevant_context)} relevant entries:")
            for i, ctx in enumerate(relevant_context, 1):
                print(f"  {i}. {ctx['title']} (similarity: {ctx['similarity']:.3f})")
        else:
            print("⚠️  No relevant context found")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_chat_response():
    """Test full chat response generation"""
    print("\n" + "=" * 70)
    print("Test 4: Chat Response Generation")
    print("=" * 70)
    
    try:
        db = Database()
        rag = RAGService()
        
        knowledge_base = db.get_all_knowledge_with_embeddings()
        
        if not knowledge_base:
            print("⚠️  No knowledge entries found")
            return False
        
        test_queries = [
            "What are your business hours?",
            "Tell me about your pricing plans",
            "What languages do you support?"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            response, context = rag.generate_chat_response(query, knowledge_base)
            
            print(f"Context used: {len(context)} entries")
            if context:
                print(f"  - {context[0]['title']} (similarity: {context[0]['similarity']:.3f})")
            
            print(f"\nResponse preview:")
            response_preview = response[:200] + "..." if len(response) > 200 else response
            print(f"  {response_preview}")
            print("-" * 70)
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n" + "=" * 70)
    print("Test 5: OpenAI API Connection")
    print("=" * 70)
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or not api_key.strip() or api_key.startswith('your_'):
        print("⚠️  OpenAI API key not configured")
        print("   The chatbot will work with limited functionality")
        print("   Run: python setup_openai.py")
        return False
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test successful' if you can read this."}],
            max_tokens=10
        )
        
        print("✓ OpenAI API connection successful")
        print(f"✓ Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("RAG Chatbot - System Tests")
    print("=" * 70)
    
    results = {
        "Embedding Generation": test_embedding_generation(),
        "Database Operations": test_database_operations(),
        "Knowledge Retrieval": test_knowledge_retrieval(),
        "Chat Response": test_chat_response(),
        "OpenAI Connection": test_openai_connection()
    }
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! The chatbot is ready to use.")
        print("   Run: python app.py (or python start.py)")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

