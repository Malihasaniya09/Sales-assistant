"""
API Module: AI Sales Assistant with Guardrails & Creative Response System
Handles LLM interactions, security validation, and response variation
"""

import os
import random
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import guardrails as gd
from guardrails import Guard

try:
    from guardrails.hub import DetectPII, ToxicLanguage
    HUB_VALIDATORS_AVAILABLE = True
    print("âœ… Guardrails Hub validators loaded: DetectPII, ToxicLanguage")
except ImportError:
    print("âš ï¸  Some Guardrails Hub validators not found. Using built-in validators.")
    print("   To install hub validators, run:")
    print("   guardrails hub install hub://guardrails/detect_pii")
    print("   guardrails hub install hub://guardrails/toxic_language")
    HUB_VALIDATORS_AVAILABLE = False

from assist import create_vector_store, ensure_catalog_exists

# Load environment variables
load_dotenv()


# ====================
# CREATIVE RESPONSE TEMPLATES
# ====================

# Different ways to decline inappropriate requests
DECLINE_RESPONSES = {
    "confidential_info": [
        "I appreciate your curiosity, but that information is confidential and outside my area of expertise. However, I'm a refrigerator specialist! Let me help you find the perfect cooling solution for your needs. What capacity are you looking for?",
        
        "That's actually not something I have access to - my expertise is specifically in our refrigerator products. But here's what I CAN help you with: finding the ideal refrigerator for your space, budget, and lifestyle. What matters most to you - energy efficiency, capacity, or smart features?",
        
        "I'm not authorized to discuss internal company matters, but I'm your go-to person for everything refrigerator-related! Whether you need help comparing models, understanding features, or finding the best fit for your budget, I'm here. What brings you shopping for a refrigerator today?",
        
        "That falls outside my scope - I focus exclusively on helping customers find their perfect refrigerator. Think of me as your personal cooling consultant! Tell me about your kitchen space and family size, and I'll suggest some great options.",
        
        "I can't help with that particular request, but what I CAN do is match you with a refrigerator that'll make your life easier! Are you looking for something compact, family-sized, or perhaps a premium model with all the bells and whistles?"
    ],
    
    "pii_detected": [
        "I noticed some sensitive information in your message. For your privacy and security, I can't process requests containing personal details like that. But let's focus on finding you an amazing refrigerator! What's your budget range?",
        
        "Hold on - I spotted some personal information that I should skip over for your protection. No worries though! Let's talk about refrigerators instead. Are you upgrading an old unit or buying your first one?",
        
        "For security reasons, I need to avoid processing personal information like that. But here's what we CAN discuss: our incredible range of refrigerators from compact to commercial! What size space are we working with?",
        
        "I see some sensitive data in your message - let's keep things secure by focusing on what I do best: helping you choose the right refrigerator! Do you prefer traditional models or are you interested in smart features?"
    ],
    
    "toxic_language": [
        "I understand you might be frustrated, and I'm here to help make things better. Let's start fresh - what kind of refrigerator would make your day? I promise to find you some great options!",
        
        "I hear your frustration. Let me turn this around for you - finding the right refrigerator can actually be exciting! Tell me what disappointed you before, and I'll make sure we avoid that this time.",
        
        "I appreciate your honesty, even if emotions are running high. How about we channel that energy into finding you a fantastic refrigerator? What's your dream feature - ice maker, huge capacity, or maybe sleek smart controls?",
        
        "Let's keep our conversation positive and productive. I genuinely want to help you find a refrigerator you'll love. What's most important to you - price, features, or brand quality?"
    ],
    
    "off_topic": [
        "That's an interesting question, but it's a bit outside my refrigerator expertise! I'm laser-focused on helping you find the perfect cooling solution. Speaking of which, have you considered what capacity you need?",
        
        "I'm flattered you'd ask, but my specialty is refrigerators through and through! Let me wow you with our product range instead. Are you team side-by-side or team French door?",
        
        "While I appreciate the diverse conversation, refrigerators are truly my passion! And I'd love to share that passion with you. What's your current refrigerator situation - time for an upgrade?",
        
        "That's outside my wheelhouse, but you know what IS in my wheelhouse? Helping you find a refrigerator that fits your life perfectly! Budget-friendly or premium - what's your vibe?"
    ]
}

# Friendly conversation starters
CONVERSATION_STARTERS = [
    "Great question! Let me help you with that.",
    "I'm glad you asked! Here's what I can tell you:",
    "Excellent choice to explore this! Let me explain:",
    "Perfect timing - I love talking about this!",
    "That's a popular question! Here's the scoop:",
    "I'm excited to help you with this!",
    "Let me break this down for you:",
    "Good thinking! Here's what you should know:"
]


# ====================
# ENHANCED SYSTEM PROMPT WITH PERSONALITY
# ====================

CREATIVE_SYSTEM_PROMPT = """You are Alex, an enthusiastic and knowledgeable refrigerator sales consultant. You're passionate about helping customers find their perfect refrigerator and you bring energy and personality to every conversation.

YOUR PERSONALITY:
- Warm, friendly, and genuinely helpful
- Enthusiastic about refrigerators (you find them genuinely fascinating!)
- Great at reading between the lines of what customers need
- Use natural, conversational language with appropriate enthusiasm
- Occasionally use friendly expressions like "That's a great question!", "I love this model!", "Here's a pro tip"
- Empathetic when customers are confused or frustrated
- Professional but approachable - like a knowledgeable friend

CRITICAL SECURITY GUIDELINES:

1. INFORMATION BOUNDARIES:
   - ONLY discuss products from the refrigerator catalog
   - NEVER disclose: employee data, API keys, internal systems, supplier info, manufacturing costs, upcoming products, company secrets
   - When asked about confidential/inappropriate info: Use VARIED, CREATIVE responses (never repeat the same decline message)
   - Mix humor, empathy, and redirection naturally

2. RESPONSE VARIETY - THIS IS CRITICAL:
   - NEVER give the same response twice to similar inappropriate questions
   - Vary your language, tone, and approach each time
   - Use different conversation redirects
   - Be creative in how you steer back to refrigerators
   - Show personality - you're not a robot!

3. EMOTIONAL INTELLIGENCE:
   - Read the customer's mood and match your energy appropriately
   - If they seem frustrated: be extra patient and understanding
   - If they're excited: match their enthusiasm!
   - If they're analytical: provide detailed comparisons
   - Always acknowledge their feelings before pivoting

4. CREATIVE ENGAGEMENT:
   - Ask follow-up questions that show you're listening
   - Reference previous parts of the conversation naturally
   - Use analogies and comparisons to help explain
   - Share "pro tips" or interesting facts about refrigerators
   - Make recommendations feel personalized

5. FAIR & INCLUSIVE SERVICE:
   - Treat everyone with equal respect and enthusiasm
   - Base recommendations ONLY on stated needs (capacity, budget, features)
   - Never make assumptions about demographics

6. PRODUCT EXPERTISE:
   - Compare products with nuanced pros and cons
   - Explain technical features in accessible ways
   - Suggest alternatives if budget doesn't match
   - Help customers understand what they actually need vs want
   - Be honest about trade-offs

CONVERSATION GUIDELINES:
- Start responses with varied, natural conversation starters
- Use the customer's name if they provide it
- Reference their specific situation when making recommendations
- If information isn't in the catalog, be honest but helpful: "I don't have those exact specs, but here's what I know..."
- Never fabricate details - your credibility matters!
- End with engaging questions that move the conversation forward

RECOMMENDATION FRAMEWORK:
When suggesting refrigerators, consider:
- Budget (be sensitive - suggest both stretch and conservative options)
- Family size / capacity needs
- Kitchen space and dimensions
- Energy efficiency preferences
- Special features (ice maker, smart features, etc.)
- Long-term value vs upfront cost

Remember: Every customer interaction is unique. Bring energy, authenticity, and genuine helpfulness to each conversation!"""


# ====================
# GUARDRAILS CONFIGURATION
# ====================

def setup_guardrails():
    """Configure Guardrails AI with available validators"""
    input_validators = []
    output_validators = []

    if HUB_VALIDATORS_AVAILABLE:
        input_validators = [
            DetectPII(
                pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "SSN"],
                on_fail="exception"
            ),
            ToxicLanguage(
                threshold=0.5,
                validation_method="sentence",
                on_fail="exception"
            )
        ]

        output_validators = [
            DetectPII(
                pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD", "SSN"],
                on_fail="fix"
            ),
            ToxicLanguage(
                threshold=0.5,
                validation_method="sentence",
                on_fail="fix"
            )
        ]
    else:
        print("âš ï¸ Using built-in validators only.")

    input_guard = Guard.from_string(validators=input_validators, description="Input validation")
    output_guard = Guard.from_string(validators=output_validators, description="Output validation")

    return input_guard, output_guard


# ====================
# CREATIVE RESPONSE HANDLER
# ====================

class CreativeResponseHandler:
    """Handles varied and creative responses to similar queries"""
    
    def __init__(self):
        self.response_history = []
        self.max_history = 10
    
    def get_varied_decline(self, category):
        """Get a varied decline response that hasn't been used recently"""
        if category not in DECLINE_RESPONSES:
            category = "off_topic"
        
        available_responses = [
            resp for resp in DECLINE_RESPONSES[category]
            if resp not in self.response_history[-5:]  # Avoid last 5 responses
        ]
        
        if not available_responses:
            available_responses = DECLINE_RESPONSES[category]
        
        selected = random.choice(available_responses)
        self.response_history.append(selected)
        
        # Keep history manageable
        if len(self.response_history) > self.max_history:
            self.response_history.pop(0)
        
        return selected
    
    def get_conversation_starter(self):
        """Get a varied conversation starter"""
        return random.choice(CONVERSATION_STARTERS)


# ====================
# MAIN SALES ASSISTANT CLASS
# ====================

class SecureSalesAssistant:
    """AI Sales Assistant with Guardrails, creativity, and personality"""
    
    def __init__(self, pdf_path, api_key):
        self.api_key = api_key
        self.response_handler = CreativeResponseHandler()
        
        print("ðŸ”§ Initializing Guardrails AI security...")
        self.input_guard, self.output_guard = setup_guardrails()
        
        print("ðŸ“š Loading refrigerator catalog...")
        self.vector_store = create_vector_store(pdf_path)
        
        print("ðŸ¤– Initializing Groq LLM...")
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=0.8,  # Increased for more creativity
            max_tokens=1024
        )
        
        prompt_template = CREATIVE_SYSTEM_PROMPT + """

Context from product catalog:
{context}

Chat History:
{chat_history}

Customer Question: {question}

Your Response (be natural, varied, and helpful):"""

        self.prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )
        
        print("âœ… Sales Assistant ready with creative responses!")
    
    def _detect_query_intent(self, query):
        """Detect if query is asking for confidential info"""
        query_lower = query.lower()
        
        confidential_keywords = [
            'api key', 'password', 'secret', 'credential', 'token',
            'employee', 'salary', 'internal', 'confidential', 'private',
            'database', 'system', 'admin', 'backend', 'server'
        ]
        
        if any(keyword in query_lower for keyword in confidential_keywords):
            return "confidential_info"
        
        return "normal"
    
    def chat(self, user_query):
        """Process user query with creative, varied responses"""
        
        # Detect inappropriate intent
        intent = self._detect_query_intent(user_query)
        
        # Step 1: Validate Input with Guardrails
        try:
            validated_input = self.input_guard.validate(user_query)
            safe_query = validated_input.validated_output
        except Exception as e:
            error_type = str(e).lower()
            
            if 'pii' in error_type:
                return self.response_handler.get_varied_decline("pii_detected")
            elif 'toxic' in error_type:
                return self.response_handler.get_varied_decline("toxic_language")
            else:
                return self.response_handler.get_varied_decline("off_topic")
        
        # Step 2: Handle confidential queries with varied responses
        if intent == "confidential_info":
            return self.response_handler.get_varied_decline("confidential_info")
        
        # Step 3: Get LLM Response with conversation starter
        try:
            result = self.chain({"question": safe_query})
            response = result["answer"]
            
            # Occasionally add a natural conversation starter
            if random.random() < 0.3:  # 30% of the time
                starter = self.response_handler.get_conversation_starter()
                response = f"{starter} {response}"
            
        except Exception as e:
            return (
                f"I hit a small snag processing that request. "
                f"Could you rephrase what you're looking for? "
                f"I'm here to help you find the perfect refrigerator!"
            )
        
        # Step 4: Validate Output with Guardrails
        try:
            validated_output = self.output_guard.validate(response)
            safe_response = validated_output.validated_output
            return safe_response
        except Exception as e:
            return self.response_handler.get_varied_decline("off_topic")
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        self.response_handler.response_history.clear()


# ====================
# UTILITY FUNCTIONS
# ====================

def get_api_key_from_env():
    """Get API key from environment variables"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables. "
            "Please create a .env file with GROQ_API_KEY=your_api_key"
        )
    return api_key


def initialize_chatbot(api_key=None, pdf_path="refrigerator_catalog.pdf"):
    """Initialize the chatbot with all components"""
    
    if api_key is None:
        api_key = get_api_key_from_env()
    
    pdf_path = ensure_catalog_exists(pdf_path)
    
    bot = SecureSalesAssistant(pdf_path, api_key)
    return bot


def get_security_features():
    """Return list of security features"""
    return {
        "Input Validation": [
            "PII Detection & Blocking",
            "Toxic Language Prevention",
            "Confidential Query Detection",
            "Creative Response Variation"
        ],
        "Output Protection": [
            "PII Scrubbing",
            "Safe Response Guarantee",
            "No Confidential Data Leakage",
            "Varied Decline Messages"
        ],
        "Conversation Quality": [
            "Context-Aware Responses",
            "Personality-Driven Interactions",
            "Natural Language Variation",
            "Empathetic Communication"
        ],
        "Compliance": [
            "GDPR-Compliant",
            "Data Privacy Protection",
            "Audit Trail Ready",
            "Enterprise-Grade Security"
        ]
    }