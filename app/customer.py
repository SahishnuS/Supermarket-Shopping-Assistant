"""
Customer Chat Interface — Streamlit chatbot for shoppers to find products.
Supports text and voice input, product cards, and store map.
Run: streamlit run app/customer.py --server.port 8502
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import get_all_aisles, get_all_config, init_db, seed_sample_data
from backend.ai_pipeline import chat, voice_chat, WHISPER_AVAILABLE, OLLAMA_AVAILABLE
from app.components.chat_ui import (
    apply_chat_styles, render_product_card, render_directions, render_header
)
from app.components.store_map import render_store_map

# Voice recording widget
try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# Initialize
init_db()
seed_sample_data()


# ── Page Config ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="Supermarket Assistant",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

apply_chat_styles()


# ── Session State ─────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "last_map_data" not in st.session_state:
    st.session_state.last_map_data = None


# ── Helper Functions ──────────────────────────────────────────────────

def process_query(query):
    """Process a text query and update the conversation."""
    if not query.strip():
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.conversation_history.append({"role": "user", "content": query})

    # Get AI response
    result = chat(query, st.session_state.conversation_history)

    # Build inline map data for this message
    map_data = None
    if result.get("products") and result.get("directions"):
        map_data = {
            "target_aisle": result["products"][0].get("aisle_name"),
            "path": result["directions"].get("path"),
            "entrance": result["directions"].get("entrance", (0, 0)),
        }

    # Add assistant response (with map data embedded)
    response_text = result.get("response", "I'm sorry, I couldn't understand that.")
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "products": result.get("products", []),
        "directions": result.get("directions"),
        "map_data": map_data,
    })
    st.session_state.conversation_history.append({"role": "assistant", "content": response_text})


# ── Main UI ───────────────────────────────────────────────────────────

def main():
    config = get_all_config()
    store_name = config.get("store_name", "My Supermarket")
    render_header(store_name)

    # Status row
    status_html = '<div style="text-align:center; margin-bottom:10px;">'
    if OLLAMA_AVAILABLE:
        status_html += '<span class="status-pill status-online">🟢 AI Online</span> '
    else:
        status_html += '<span class="status-pill status-warn">🟡 AI Fallback</span> '
    if WHISPER_AVAILABLE:
        status_html += '<span class="status-pill status-online">🟢 Voice Ready</span> '
    else:
        status_html += '<span class="status-pill status-offline">🔴 Voice Off</span> '
    status_html += '</div>'
    st.markdown(status_html, unsafe_allow_html=True)

    # ── Search Bar at TOP ─────────────────────────────────────────────
    with st.form(key="search_form", clear_on_submit=True, border=False):
        search_col, btn_col = st.columns([7, 1])
        with search_col:
            user_input = st.text_input(
                "Search",
                placeholder="🔍 Ask me anything... (e.g., 'Where is sugar?' or 'I need shampoo')",
                label_visibility="collapsed"
            )
        with btn_col:
            submitted = st.form_submit_button("🔍", use_container_width=True)

    # Process text input
    if submitted and user_input:
        process_query(user_input)
        st.rerun()

    # ── Voice Input ───────────────────────────────────────────────────
    if WHISPER_AVAILABLE and AUDIO_RECORDER_AVAILABLE:
        st.markdown('<div style="text-align:center; margin: -5px 0 10px 0;">', unsafe_allow_html=True)
        audio_bytes = audio_recorder(
            text="",
            recording_color="#b89d00",
            neutral_color="#6b7280",
            icon_size="2x",
            pause_threshold=2.0,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if audio_bytes:
            # Prevent reprocessing the same audio
            import hashlib
            audio_hash = hashlib.md5(audio_bytes).hexdigest()
            if audio_hash != st.session_state.get("last_audio_hash"):
                st.session_state.last_audio_hash = audio_hash
                with st.spinner("🎤 Listening... (Whisper STT)"):
                    result = voice_chat(audio_bytes, st.session_state.conversation_history)
                    transcription = result.get("transcription", "")
                    if transcription and not transcription.startswith("["):
                        # Add user message with transcription
                        st.session_state.messages.append({"role": "user", "content": f"🎤 {transcription}"})
                        st.session_state.conversation_history.append({"role": "user", "content": transcription})

                        # Build map data
                        map_data = None
                        if result.get("products") and result.get("directions"):
                            map_data = {
                                "target_aisle": result["products"][0].get("aisle_name"),
                                "path": result["directions"].get("path"),
                                "entrance": result["directions"].get("entrance", (0, 0)),
                            }

                        response_text = result.get("response", "I couldn't understand that.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text,
                            "products": result.get("products", []),
                            "directions": result.get("directions"),
                            "map_data": map_data,
                        })
                        st.session_state.conversation_history.append({"role": "assistant", "content": response_text})
                        st.rerun()

    # ── Chat Conversation (newest interactions first) ─────────────────
    if st.session_state.messages:
        # Group messages into "interactions" (User + Assistant pairs)
        interactions = []
        current_interaction = []
        
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                if current_interaction:
                    interactions.append(current_interaction)
                current_interaction = [msg]
            elif msg["role"] == "assistant":
                current_interaction.append(msg)
                interactions.append(current_interaction)
                current_interaction = []
        
        if current_interaction:
            interactions.append(current_interaction)

        # Reverse: show most recent INTERACTION at top
        for interaction in reversed(interactions):
            for msg in interaction:
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(msg["content"])
                else:
                    with st.chat_message("assistant", avatar="🛒"):
                        st.markdown(msg["content"])
                        
                        # Render product cards in 3-column grid
                        products = msg.get("products", [])
                        if products:
                            cols = st.columns(3)
                            for idx, product in enumerate(products[:6]):
                                with cols[idx % 3]:
                                    render_product_card(product)
    
                        # Render directions
                        directions = msg.get("directions")
                        if directions:
                            render_directions(directions)

                        # Render store map inline (per query)
                        msg_map = msg.get("map_data")
                        if msg_map:
                            with st.expander("🗺️ View Store Map", expanded=False):
                                aisles = get_all_aisles()
                                grid_rows = int(config.get("grid_rows", 6))
                                grid_cols = int(config.get("grid_cols", 5))
                                fig = render_store_map(
                                    aisles=aisles,
                                    target_aisle=msg_map.get("target_aisle"),
                                    path=msg_map.get("path"),
                                    entrance=msg_map.get("entrance", (0, 0)),
                                    grid_rows=grid_rows,
                                    grid_cols=grid_cols
                                )
                                st.pyplot(fig)


if __name__ == "__main__":
    main()

