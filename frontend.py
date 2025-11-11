"""
Streamlit Frontend for Secure Refrigerator Sales Assistant
Run with: streamlit run frontend.py
"""

import streamlit as st
from api import initialize_chatbot, get_api_key_from_env, get_security_features
from assist import get_catalog_stats

# ====================
# PAGE CONFIGURATION
# ====================

st.set_page_config(
    page_title="AI Refrigerator Sales Assistant",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================
# CUSTOM CSS
# ====================

st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(120deg, #2193b0, #6dd5ed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .security-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
        margin: 0.25rem;
        font-size: 0.85rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 0.5rem 0;
        border: 2px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem 0;
    }
    .security-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    .price-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .personality-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
        margin: 0.25rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================
# SIDEBAR
# ====================

def render_sidebar():
    """Render sidebar with configuration and info"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # API Key status
        st.markdown('<div class="success-box">✅ <b>API Key:</b> Loaded from .env</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Alex's Personality Badge
        st.markdown("### 🎭 Your Sales Consultant")
        st.markdown('<div class="personality-badge">👤 Alex - Your Fridge Expert</div>', unsafe_allow_html=True)
        st.markdown("""
        **Personality Traits:**
        - 🎯 Enthusiastic & Knowledgeable
        - 💬 Natural conversational style
        - 🎨 Creative responses
        - 💡 Helpful problem-solver
        """)
        
        st.divider()
        
        # Guardrails AI Security Status
        st.markdown("### 🛡️ Security Status")
        st.markdown('<div class="security-badge">🔒 Guardrails AI Active</div>', unsafe_allow_html=True)
        st.markdown('<div class="security-badge">✔ Input Validated</div>', unsafe_allow_html=True)
        st.markdown('<div class="security-badge">✔ Output Protected</div>', unsafe_allow_html=True)
        st.markdown('<div class="security-badge">🎨 Creative Responses</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Session Statistics
        if "messages" in st.session_state and len(st.session_state.messages) > 0:
            st.markdown("### 💬 Session Statistics")
            
            total_msgs = len(st.session_state.messages)
            user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
            bot_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Your Questions", user_msgs)
            with col2:
                st.metric("Alex's Responses", bot_msgs)
            
            st.metric("Total Messages", total_msgs)
        
        st.divider()
        
        # Security Features Expandable
        with st.expander("🔍 Security Features", expanded=False):
            security_features = get_security_features()
            for category, features in security_features.items():
                st.markdown(f"**{category}:**")
                for feature in features:
                    st.markdown(f"• {feature}")
                st.markdown("")
        
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat & Start Fresh", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            if "bot" in st.session_state:
                st.session_state.bot.clear_memory()
            st.success("Chat cleared! Alex is ready for a fresh conversation.")
            st.rerun()

# ====================
# QUICK ACTION BUTTONS
# ====================

def render_quick_actions():
    """Render quick action buttons for common queries"""
    st.subheader("💡 Quick Questions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    quick_questions = [
        ("💰 Budget Options", "Show me refrigerators under $500"),
        ("👨‍👩‍👧‍👦 Family Size", "I need a refrigerator for a family of 4"),
        ("⭐ Premium Models", "What are your best premium refrigerators?"),
        ("⚡ Energy Efficient", "Show me the most energy-efficient models")
    ]
    
    cols = [col1, col2, col3, col4]
    
    for idx, (label, question) in enumerate(quick_questions):
        with cols[idx]:
            if st.button(label, use_container_width=True, key=f"quick_{idx}"):
                return question
    
    # Second row of quick actions
    col5, col6, col7, col8 = st.columns(4)
    
    quick_questions_2 = [
        ("📏 Compact Size", "I need a compact refrigerator for a small space"),
        ("🏢 Commercial", "Looking for commercial refrigerators"),
        ("📱 Smart Features", "Show me smart refrigerators with IoT features"),
        ("🆚 Compare Models", "Compare side-by-side vs French door models")
    ]
    
    cols_2 = [col5, col6, col7, col8]
    
    for idx, (label, question) in enumerate(quick_questions_2):
        with cols_2[idx]:
            if st.button(label, use_container_width=True, key=f"quick2_{idx}"):
                return question
    
    return None

# ====================
# CHAT INTERFACE
# ====================

def render_chat_interface():
    """Render main chat interface"""
    
    # Display chat messages
    for message in st.session_state.messages:
        avatar = "🧑" if message["role"] == "user" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    # Chat input
    prompt = st.chat_input("Ask Alex about refrigerators... (e.g., 'I need a 400L refrigerator under $1000')")
    
    return prompt

# ====================
# ERROR MESSAGE
# ====================

def show_error_message(error_msg):
    """Show error message when API key is not found"""
    st.markdown('<div class="main-header">❄️ AI Refrigerator Sales Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Meet Alex - Your Creative AI Sales Consultant</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="error-box">❌ <b>Configuration Error:</b><br>{error_msg}</div>', unsafe_allow_html=True)
    
    # How to setup .env file
    with st.expander("📖 How to setup .env file", expanded=True):
        st.markdown("""
        ### Steps to setup your environment:
        
        1. Create a file named `.env` in the same directory as your Python files
        2. Add your Groq API key in the following format:
        
        ```
        GROQ_API_KEY=your_api_key_here
        ```
        
        3. Get your API key from [Groq Console](https://console.groq.com/keys)
        4. Replace `your_api_key_here` with your actual API key
        5. Save the file and restart the application
        
        **Example .env file:**
        ```
        GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        ```
        
        **Note:** The `.env` file should be added to `.gitignore` to keep your API key secure.
        """)
    
    # Feature showcase
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🎨 Creative Responses</h3>
            <p>Alex never repeats the same answer - each response is unique and natural!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🛡️ Secure by Design</h3>
            <p>Enterprise-grade security with PII detection and content filtering.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Smart Matching</h3>
            <p>AI-powered recommendations based on your unique needs.</p>
        </div>
        """, unsafe_allow_html=True)

# ====================
# PRODUCT HIGHLIGHTS
# ====================

def show_product_highlights():
    """Show product range highlights"""
    st.divider()
    st.subheader("❄️ Our Refrigerator Range")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>💰 Budget-Friendly</h4>
            <div class="price-badge">$199 - $399</div>
            <p style="margin-top: 1rem;">Perfect for students, small apartments, and basic cooling needs.</p>
            <small>3 models available</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🏠 Family-Sized</h4>
            <div class="price-badge">$649 - $999</div>
            <p style="margin-top: 1rem;">Ideal for medium to large families with advanced features.</p>
            <small>4 models available</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>⭐ Premium Luxury</h4>
            <div class="price-badge">$1,299 - $1,899</div>
            <p style="margin-top: 1rem;">Luxury models with smart features and maximum capacity.</p>
            <small>3 models available</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h4>🏢 Commercial</h4>
            <div class="price-badge">$2,299+</div>
            <p style="margin-top: 1rem;">Heavy-duty solutions for restaurants and businesses.</p>
            <small>Custom orders</small>
        </div>
        """, unsafe_allow_html=True)

# ====================
# MAIN APPLICATION
# ====================

def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "test_query" not in st.session_state:
        st.session_state.test_query = None
    
    # Check for API key in environment
    try:
        api_key = get_api_key_from_env()
    except ValueError as e:
        show_error_message(str(e))
        return
    
    # Render sidebar
    render_sidebar()
    
    # Header
    st.markdown('<div class="main-header">❄️ AI Refrigerator Sales Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Meet Alex - Your Creative & Secure AI Consultant 🎭</div>', unsafe_allow_html=True)
    
    # Initialize chatbot
    if "bot" not in st.session_state:
        try:
            with st.spinner("🔧 Initializing Alex with Guardrails AI security & creative personality... This may take a moment."):
                st.session_state.bot = initialize_chatbot()
            st.markdown(
                '<div class="success-box">✅ <b>Success!</b> Alex is ready to help! All conversations are '
                'protected by Guardrails AI with creative, varied responses.</div>',
                unsafe_allow_html=True
            )
        except Exception as e:
            st.markdown(
                f'<div class="error-box">❌ <b>Error:</b> {str(e)}<br><br>'
                'Please check your .env file and API key.</div>',
                unsafe_allow_html=True
            )
            return
    
    # Render chat interface
    user_prompt = render_chat_interface()
    
    # Check for quick action button click
    quick_question = render_quick_actions()
    
    # Check for test query from sidebar
    test_query = st.session_state.test_query
    if test_query:
        st.session_state.test_query = None
        prompt_to_process = test_query
    else:
        prompt_to_process = user_prompt or quick_question
    
    # Process input
    if prompt_to_process:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})
        
        # Display user message immediately
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt_to_process)
        
        # Get bot response
        with st.chat_message("assistant", avatar="👤"):
            with st.spinner("🤔 Alex is thinking... (Validating with Guardrails AI)"):
                response = st.session_state.bot.chat(prompt_to_process)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Rerun to update UI
        if quick_question or test_query:
            st.rerun()
    
    # Show product highlights only if chat is empty
    if len(st.session_state.messages) == 0:
        show_product_highlights()

# ====================
# RUN APPLICATION
# ====================

if __name__ == "__main__":
    main()