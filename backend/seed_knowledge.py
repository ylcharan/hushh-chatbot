"""
Seed script to populate the knowledge base with sample data
Run this after starting the backend for the first time
"""

from database import Database
from rag_service import RAGService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def seed_knowledge_base():
    """Add sample knowledge entries to the database"""
    
    print("Initializing database and RAG service...")
    db = Database()
    rag = RAGService()
    
    sample_knowledge = [
        {
            "title": "Company Overview",
            "content": """Our company is a leading provider of AI-powered solutions. 
            We specialize in natural language processing, machine learning, and chatbot development. 
            Founded in 2020, we serve clients across various industries including healthcare, 
            finance, and e-commerce. Our mission is to make AI accessible and practical for businesses 
            of all sizes.""",
            "category": "general"
        },
        {
            "title": "Business Hours",
            "content": """We are open Monday through Friday, 9:00 AM to 6:00 PM EST. 
            Our customer support team is available during these hours via phone, email, or chat. 
            For urgent matters outside business hours, please use our emergency contact form, 
            and we will respond within 24 hours.""",
            "category": "general"
        },
        {
            "title": "Product Features",
            "content": """Our main product includes the following features:
            1. Natural Language Understanding - Process and understand user queries in multiple languages
            2. Knowledge Base Management - Easy-to-use interface for managing information
            3. Semantic Search - Find relevant information using AI-powered search
            4. Chat History - Track and analyze all conversations
            5. Custom Integrations - API access for integration with existing systems
            6. Analytics Dashboard - Insights into user interactions and common queries""",
            "category": "technical"
        },
        {
            "title": "Pricing Plans",
            "content": """We offer three pricing tiers:
            
            Starter Plan ($49/month):
            - Up to 1,000 messages per month
            - 100 knowledge base entries
            - Email support
            - Basic analytics
            
            Professional Plan ($149/month):
            - Up to 10,000 messages per month
            - Unlimited knowledge base entries
            - Priority email and chat support
            - Advanced analytics
            - API access
            
            Enterprise Plan (Custom pricing):
            - Unlimited messages
            - Unlimited knowledge base entries
            - 24/7 dedicated support
            - Custom integrations
            - On-premise deployment option
            - SLA guarantee""",
            "category": "pricing"
        },
        {
            "title": "Getting Started Guide",
            "content": """To get started with our platform:
            
            Step 1: Create an account on our website
            Step 2: Choose your pricing plan
            Step 3: Add your first knowledge base entries through the dashboard
            Step 4: Customize your chatbot's appearance and behavior
            Step 5: Integrate the chatbot into your website using our embed code
            Step 6: Monitor performance through the analytics dashboard
            
            Most users can complete setup in under 30 minutes. Our onboarding team is available 
            to assist with setup and answer any questions.""",
            "category": "faq"
        },
        {
            "title": "API Documentation",
            "content": """Our REST API provides programmatic access to all features:
            
            Base URL: https://api.example.com/v1
            
            Authentication: Use Bearer token in Authorization header
            
            Main Endpoints:
            - POST /chat - Send a message to the chatbot
            - GET /knowledge - Retrieve knowledge base entries
            - POST /knowledge - Add new knowledge entry
            - GET /analytics - Retrieve usage analytics
            
            Rate Limits:
            - Starter: 100 requests/hour
            - Professional: 1,000 requests/hour
            - Enterprise: Custom limits
            
            All responses are in JSON format. Detailed documentation available at docs.example.com""",
            "category": "technical"
        },
        {
            "title": "Data Security and Privacy",
            "content": """We take data security seriously:
            
            - All data is encrypted in transit (TLS 1.3) and at rest (AES-256)
            - We are SOC 2 Type II certified
            - GDPR and CCPA compliant
            - Regular security audits by third-party firms
            - Data backup every 6 hours with 30-day retention
            - Option for data residency in US, EU, or Asia regions
            - No data sharing with third parties
            - Customer data is isolated and never used for model training
            
            For enterprise clients, we offer additional security features including SSO, 
            IP whitelisting, and custom data retention policies.""",
            "category": "security"
        },
        {
            "title": "Supported Languages",
            "content": """Our platform supports the following languages:
            
            Fully Supported (99%+ accuracy):
            - English
            - Spanish
            - French
            - German
            - Italian
            - Portuguese
            
            Beta Support (90%+ accuracy):
            - Chinese (Simplified & Traditional)
            - Japanese
            - Korean
            - Arabic
            - Russian
            - Hindi
            
            We continuously add support for more languages. Contact us if you need 
            support for a specific language not listed here.""",
            "category": "technical"
        },
        {
            "title": "Integration Options",
            "content": """We offer multiple integration methods:
            
            1. JavaScript Widget - Simple embed code for websites
            2. REST API - Full programmatic access
            3. Webhooks - Real-time event notifications
            4. Pre-built Integrations:
               - Slack
               - Microsoft Teams
               - WhatsApp Business
               - Facebook Messenger
               - WordPress plugin
               - Shopify app
            
            Custom integrations available for enterprise clients. Our integration team 
            can help with setup and provide sample code in multiple programming languages.""",
            "category": "technical"
        },
        {
            "title": "Common Troubleshooting",
            "content": """Solutions to common issues:
            
            Problem: Chatbot not responding
            Solution: Check your API key is valid and you haven't exceeded rate limits
            
            Problem: Irrelevant answers
            Solution: Add more detailed knowledge base entries and use clear, specific language
            
            Problem: Slow response times
            Solution: Optimize knowledge base size, check your internet connection, 
            or upgrade to a higher tier for better performance
            
            Problem: Integration not working
            Solution: Verify your embed code is placed before closing </body> tag, 
            check browser console for errors
            
            For additional help, contact support@example.com or use the live chat on our website.""",
            "category": "faq"
        }
    ]
    
    print(f"\nAdding {len(sample_knowledge)} knowledge entries...")
    
    for idx, knowledge in enumerate(sample_knowledge, 1):
        print(f"  [{idx}/{len(sample_knowledge)}] Adding: {knowledge['title']}")
        
        # Generate embedding
        embedding = rag.generate_embedding(knowledge['content'])
        
        # Add to database
        knowledge_id = db.add_knowledge(
            title=knowledge['title'],
            content=knowledge['content'],
            embedding=embedding,
            category=knowledge['category']
        )
        
        print(f"      ✓ Added with ID: {knowledge_id}")
    
    print(f"\n✅ Successfully added {len(sample_knowledge)} knowledge entries!")
    print("\nYou can now start chatting with the bot. Try asking:")
    print("  - What are your business hours?")
    print("  - Tell me about your pricing plans")
    print("  - What languages do you support?")
    print("  - How do I get started?")

if __name__ == "__main__":
    print("=" * 60)
    print("Knowledge Base Seeder")
    print("=" * 60)
    seed_knowledge_base()
    print("\n" + "=" * 60)

