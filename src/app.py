"""
Streamlit Web App for Fertilizer Recommendation System
"""
import streamlit as st
import sys
sys.path.insert(0, 'src')
from chatbot import FertilizerChatbot
from database import FertilizerDatabase

# Page config
st.set_page_config(
    page_title="Fertilizer AI Assistant",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: #000000;
    }
    .user-message {
        background-color: #2196F3;
        color: #FFFFFF;
        margin-left: 20%;
    }
    .bot-message {
        background-color: #4CAF50;
        color: #FFFFFF;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = FertilizerChatbot()
        st.session_state.messages = []
        st.session_state.initialized = True
    except Exception as e:
        st.session_state.initialized = False
        st.session_state.error = str(e)

# Header
st.markdown('<p class="main-header">🌾 AI Fertilizer Recommendation System</p>', unsafe_allow_html=True)
st.markdown("### Your Smart Agricultural Assistant for Kenya")

# Check if initialized
if not st.session_state.get("initialized", False):
    st.error(f"❌ Failed to initialize chatbot: {st.session_state.get('error', 'Unknown error')}")
    st.info("Make sure your GOOGLE_API_KEY is set in the .env file")
    st.stop()

# Sidebar - Quick Info
with st.sidebar:
    st.header("📊 System Info")
    
    db = FertilizerDatabase()
    stats = db.get_database_stats()
    
    st.metric("Available Crops", stats["crops_count"])
    st.metric("Soil Types", stats["soils_count"])
    st.metric("Fertilizers", stats["fertilizers_count"])
    
    st.markdown("---")
    st.header("🌱 Available Crops")
    crops = [c["crop_name"] for c in db.get_all_crops()]
    for crop in crops:
        st.write(f"• {crop}")
    
    st.markdown("---")
    st.header("🏞️ Soil Types")
    soils = [s["soil_type"] for s in db.get_all_soils()]
    for soil in soils:
        st.write(f"• {soil}")
    
    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        st.session_state.chatbot.reset()
        st.session_state.messages = []
        st.rerun()

# Main chat area
st.markdown("### 💬 Chat with AI Assistant")

# Display chat history
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message">👨‍🌾 <b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot-message">🤖 <b>Assistant:</b> {message["content"]}</div>', unsafe_allow_html=True)

# Quick start buttons
if len(st.session_state.messages) == 0:
    st.info("👋 Welcome! I can help you find the best fertilizer for your farm. Click a button below or type your question:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌽 I want to plant Maize"):
            user_input = "I want to plant maize"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("🫘 I want to plant Beans"):
            user_input = "I want to plant beans"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("🥔 I want to plant Potatoes"):
            user_input = "I want to plant potatoes"
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = st.session_state.chatbot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get bot response
    with st.spinner("Thinking..."):
        response = st.session_state.chatbot.chat(user_input)
    
    # Add bot response
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to update UI
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🌾 Fertilizer AI System | Powered by Google Gemini | Made for Kenyan Farmers</p>
    <p><small>Fourth Year Engineering Project - SPM3400</small></p>
</div>
""", unsafe_allow_html=True)
