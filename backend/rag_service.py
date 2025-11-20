import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RAGService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize RAG service with sentence transformer for embeddings
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        print("Initializing RAG Service...")
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
        print(f"✓ Embedding model loaded: {model_name} (dimension: {self.embedding_dimension})")
        
        # Initialize OpenAI client
        self.openai_client = None
        api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key and api_key.strip() and not api_key.startswith('your_'):
            try:
                self.openai_client = OpenAI(api_key=api_key)
                # Test the connection
                self.openai_client.models.list()
                print("✓ OpenAI API connected successfully")
                self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
                print(f"✓ Using model: {self.openai_model}")
            except Exception as e:
                print(f"⚠️  Warning: OpenAI API connection failed: {e}")
                print("   Falling back to simple response mode")
                self.openai_client = None
        else:
            print("⚠️  OpenAI API key not configured")
            print("   Chatbot will work with limited functionality")
            print("   Run 'python setup_openai.py' to configure OpenAI")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for given text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def retrieve_relevant_context(self, query: str, knowledge_base: List[Dict], 
                                  top_k: int = 3, threshold: float = 0.3) -> List[Dict]:
        """
        Retrieve most relevant knowledge base entries for a query
        
        Args:
            query: User query
            knowledge_base: List of knowledge base entries with embeddings
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant knowledge base entries with similarity scores
        """
        if not knowledge_base:
            return []
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Calculate similarities
        results = []
        for entry in knowledge_base:
            if not entry.get('embedding'):
                continue
            
            similarity = self.cosine_similarity(query_embedding, entry['embedding'])
            
            if similarity >= threshold:
                results.append({
                    'id': entry['id'],
                    'title': entry['title'],
                    'content': entry['content'],
                    'category': entry.get('category', 'general'),
                    'similarity': similarity
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def generate_response_with_context(self, query: str, context: List[Dict], 
                                      chat_history: List[Dict] = None) -> str:
        """
        Generate a response using retrieved context
        
        Args:
            query: User query
            context: Retrieved relevant context
            chat_history: Previous chat messages
            
        Returns:
            Generated response
        """
        if self.openai_client:
            return self._generate_with_openai(query, context, chat_history)
        else:
            return self._generate_simple_response(query, context)
    
    def _build_messages(self, query: str, context: List[Dict], 
                       chat_history: List[Dict] = None) -> List[Dict]:
        """Build messages array for OpenAI API"""
        # Build context string from retrieved knowledge
        context_str = ""
        if context:
            context_parts = []
            for ctx in context:
                context_parts.append(f"[{ctx['title']}]\n{ctx['content']}")
            context_str = "\n\n".join(context_parts)
        
        # Build system message with clear instructions
        system_message = (
            "You are a friendly and helpful customer support representative. Your goal is to assist customers in a warm, conversational, and natural way. "
            "Speak like a real person would - use a smooth, approachable tone and avoid sounding robotic or overly formal. "
            "\n\n"
            "Guidelines:\n"
            "- Be warm and empathetic - show you care about helping them\n"
            "- Use natural language - contractions (I'm, you'll, it's) and casual phrases are great\n"
            "- Keep responses concise but helpful - get to the point while being friendly\n"
            "- Use the knowledge base information provided, but present it naturally in your own words\n"
            "- If you don't have enough information, be honest and offer to help in other ways\n"
            "- Add personality - use phrases like 'Happy to help!', 'Great question!', 'I've got you covered'\n"
            "- Break up longer responses with bullet points or short paragraphs for easy reading\n"
            "- End with a helpful note or ask if they need anything else when appropriate"
        )
        
        # Build messages array
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add recent chat history for context (last 5 exchanges)
        if chat_history:
            for msg in chat_history[-5:]:
                messages.append({"role": "user", "content": msg['user_message']})
                messages.append({"role": "assistant", "content": msg['bot_response']})
        
        # Add current query with context
        if context_str:
            user_message = f"Context from knowledge base:\n\n{context_str}\n\n---\n\nUser question: {query}"
        else:
            user_message = query
        
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _generate_with_openai(self, query: str, context: List[Dict], 
                             chat_history: List[Dict] = None) -> str:
        """Generate response using OpenAI API"""
        try:
            messages = self._build_messages(query, context, chat_history)
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                temperature=0.8,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0.5,
                presence_penalty=0.6
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return self._generate_simple_response(query, context)
    
    def generate_chat_response_stream(self, query: str, knowledge_base: List[Dict], 
                                     chat_history: List[Dict] = None, 
                                     top_k: int = 3):
        """
        Complete RAG pipeline with streaming: retrieve context and generate streaming response
        
        Args:
            query: User query
            knowledge_base: List of knowledge base entries
            chat_history: Previous chat messages
            top_k: Number of context entries to retrieve
            
        Yields:
            Chunks of the response as they are generated
        """
        # Retrieve relevant context
        context = self.retrieve_relevant_context(query, knowledge_base, top_k=top_k)
        
        # Yield context information first
        yield {
            'type': 'context',
            'context': context
        }
        
        # Generate streaming response
        if self.openai_client:
            try:
                messages = self._build_messages(query, context, chat_history)
                
                # Generate streaming response using OpenAI
                stream = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=messages,
                    temperature=0.8,
                    max_tokens=800,
                    top_p=0.95,
                    frequency_penalty=0.5,
                    presence_penalty=0.6,
                    stream=True
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield {
                            'type': 'content',
                            'content': chunk.choices[0].delta.content
                        }
                
                yield {
                    'type': 'done'
                }
                
            except Exception as e:
                print(f"❌ OpenAI API streaming error: {e}")
                # Fallback to simple response
                response = self._generate_simple_response(query, context)
                yield {
                    'type': 'content',
                    'content': response
                }
                yield {
                    'type': 'done'
                }
        else:
            # Fallback to simple response
            response = self._generate_simple_response(query, context)
            # Simulate streaming for simple response
            words = response.split(' ')
            for i, word in enumerate(words):
                yield {
                    'type': 'content',
                    'content': word + (' ' if i < len(words) - 1 else '')
                }
            yield {
                'type': 'done'
            }
    
    def _generate_simple_response(self, query: str, context: List[Dict]) -> str:
        """Generate a simple response without LLM (fallback mode)"""
        if not context:
            return (
                "Hey there! I checked my knowledge base but couldn't find specific information about that. "
                "Here's what might help:\n\n"
                "• Try rephrasing your question in a different way\n"
                "• Add the information you're looking for to the knowledge base\n"
                "• Ask about topics that are already in the knowledge base\n\n"
                "I'm here to help with anything else you need! 😊\n\n"
                "💡 Tip: For smarter, more conversational responses, configure an OpenAI API key. "
                "Run 'python setup_openai.py' in the backend directory."
            )
        
        # Build a more helpful template-based response
        response_parts = [
            "Great question! Here's what I found for you:\n\n"
        ]
        
        for i, ctx in enumerate(context, 1):
            response_parts.append(f"📄 **{ctx['title']}**")
            if ctx.get('category'):
                response_parts.append(f" ({ctx['category']})")
            response_parts.append("\n")
            
            # Show more content (first 300 characters)
            content = ctx['content'].strip()
            content_preview = content[:300]
            if len(content) > 300:
                content_preview += "..."
            response_parts.append(f"{content_preview}\n\n")
        
        response_parts.append(
            "Hope this helps! Let me know if you need anything else. 😊\n\n"
            "---\n"
            "💡 For smarter, more conversational responses, configure an OpenAI API key.\n"
            "Run: python setup_openai.py"
        )
        
        return "".join(response_parts)
    
    def generate_chat_response(self, query: str, knowledge_base: List[Dict], 
                              chat_history: List[Dict] = None, 
                              top_k: int = 3) -> Tuple[str, List[Dict]]:
        """
        Complete RAG pipeline: retrieve context and generate response
        
        Args:
            query: User query
            knowledge_base: List of knowledge base entries
            chat_history: Previous chat messages
            top_k: Number of context entries to retrieve
            
        Returns:
            Tuple of (response, context_used)
        """
        # Retrieve relevant context
        context = self.retrieve_relevant_context(query, knowledge_base, top_k=top_k)
        
        # Generate response
        response = self.generate_response_with_context(query, context, chat_history)
        
        return response, context

