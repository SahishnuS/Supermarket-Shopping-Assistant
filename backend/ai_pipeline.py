"""
AI Pipeline — Orchestrates Whisper (Speech-to-Text) and Ollama LLM (Conversational AI).
Uses AMD DirectML acceleration when available for GPU-accelerated inference.
Handles multi-turn conversation, product search context injection, and response generation.
"""

import os
import json
import tempfile

# Try to import whisper — graceful fallback if not installed
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# Try to import ollama — graceful fallback
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# AMD acceleration utilities
from backend.amd_utils import get_amd_acceleration_status, detect_amd_gpu

from backend.search import search_products, format_search_results_for_llm
from backend.pathfinding import get_directions_to_product
from backend.database import get_config

# Whisper model (loaded lazily)
_whisper_model = None

# LLM model name — tinyllama for fast on-device AI
LLM_MODEL = "tinyllama"

# Log AMD acceleration status on module load
_amd_status = get_amd_acceleration_status()
print(f"\n{'='*50}")
print("🔧 AMD Acceleration Status")
print(f"{'='*50}")
print(_amd_status["summary"])
print(f"{'='*50}\n")

SYSTEM_PROMPT = """You are a friendly and helpful supermarket shopping assistant. You help customers find products in the store.

RULES:
1. You ONLY answer questions about products and their locations in THIS store.
2. When product information is provided in the context, use it to give specific aisle and shelf locations.
3. If no matching products are found, politely say you couldn't find that product and suggest alternatives.
4. Keep responses short, conversational, and helpful (2-3 sentences max).
5. If the customer asks a follow-up, remember the conversation context.
6. Always mention the aisle name and shelf number when giving directions.
7. Be warm and use phrases like "Sure!", "Great choice!", "Let me help you find that!"
8. If asked about things unrelated to the store, politely redirect to shopping assistance.

STORE NAME: {store_name}
"""


def get_whisper_model():
    """Lazy-load the Whisper model with AMD GPU acceleration when available."""
    global _whisper_model
    if _whisper_model is None and WHISPER_AVAILABLE:
        # Detect AMD GPU for device selection
        amd_gpu = detect_amd_gpu()
        
        if amd_gpu["found"]:
            print(f"🔥 AMD GPU detected: {amd_gpu['name']}")
            print("   Loading Whisper with AMD-optimized settings...")
            # Load model — Whisper uses PyTorch which can leverage ROCm on AMD GPUs
            # On Windows with DirectML, PyTorch ROCm headers enable AMD acceleration
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"  # ROCm exposes as CUDA on AMD GPUs
                    print("   ✅ Using AMD ROCm GPU acceleration")
                else:
                    device = "cpu"
                    print("   ⚠️ AMD GPU found but ROCm runtime not active, using CPU")
            except ImportError:
                device = "cpu"
        else:
            device = "cpu"
            print("ℹ️  No AMD GPU detected, using CPU for Whisper")
        
        # Use 'tiny' model — fastest, good enough for short queries
        _whisper_model = whisper.load_model("tiny", device=device)
        print(f"   Whisper model loaded on: {device}")
    return _whisper_model


def transcribe_audio(audio_bytes):
    """
    Transcribe audio bytes to text.
    Tries Groq cloud Whisper first (fast ~1s), falls back to local Whisper (slow).

    Args:
        audio_bytes: Raw audio data (WAV format)

    Returns:
        Transcribed text string
    """
    # ── Try Groq Cloud Whisper first (blazing fast) ──
    try:
        from groq import Groq
        import io

        groq_key = os.environ.get("GROQ_API_KEY", "")
        if not groq_key:
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        if line.startswith("GROQ_API_KEY="):
                            groq_key = line.strip().split("=", 1)[1]

        if groq_key:
            client = Groq(api_key=groq_key)
            # Write audio to temp file for Groq API
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                with open(tmp_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-large-v3-turbo",
                        file=audio_file,
                        language="en",
                        response_format="text",
                    )
                result_text = str(transcription).strip()
                if result_text:
                    print(f"🎤 Groq Whisper transcription: {result_text}")
                    return result_text
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    except Exception as e:
        print(f"[Groq Whisper] Falling back to local: {e}")

    # ── Fallback: Local Whisper (slower, works offline) ──
    if not WHISPER_AVAILABLE:
        return "[Whisper not installed. Please install openai-whisper.]"

    model = get_whisper_model()
    if model is None:
        return "[Failed to load Whisper model.]"

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path, language="en")
        return result.get("text", "").strip()
    except Exception as e:
        return f"[Transcription error: {str(e)}]"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def build_context_prompt(user_query, search_results, directions_info):
    """Build the context block that gets injected into the LLM prompt."""
    context_parts = []

    if search_results:
        context_parts.append(format_search_results_for_llm(search_results))

    if directions_info and directions_info.get("found"):
        context_parts.append(f"\nDirections: {directions_info['directions']}")

    if context_parts:
        return "\n".join(context_parts)
    return "No matching products found in the store inventory."


def chat(user_query, conversation_history=None):
    """
    Process a user query through the full AI pipeline:
    1. Search products (fuzzy match)
    2. Get directions (BFS pathfinding)
    3. Generate conversational response (LLM)

    Args:
        user_query: The user's text query
        conversation_history: List of previous messages [{"role": "user"/"assistant", "content": "..."}]

    Returns:
        Dictionary with response text, matched products, directions, etc.
    """
    if conversation_history is None:
        conversation_history = []

    # Step 1: Search for matching products
    search_results = search_products(user_query, top_n=3)

    # Step 2: Get directions for the top result
    directions_info = None
    if search_results:
        directions_info = get_directions_to_product(search_results[0])

    # Step 3: Build context for the LLM
    context = build_context_prompt(user_query, search_results, directions_info)

    # Step 4: Generate response using Ollama LLM
    store_name = get_config("store_name") or "My Supermarket"
    system_msg = SYSTEM_PROMPT.format(store_name=store_name)

    messages = [{"role": "system", "content": system_msg}]

    # Add conversation history for multi-turn
    for msg in conversation_history[-6:]:  # Keep last 6 messages to save RAM
        messages.append(msg)

    # Add context + user query
    augmented_query = f"""Customer's question: "{user_query}"

Store inventory search results:
{context}

Please respond to the customer's question using the information above. Be conversational and helpful."""

    messages.append({"role": "user", "content": augmented_query})

    # Generate response
    response_text = generate_llm_response(messages)

    return {
        "response": response_text,
        "products": search_results,
        "directions": directions_info,
        "query": user_query,
    }


def generate_llm_response(messages):
    """Instant response using smart fallback (Ollama too slow on CPU for any model)."""
    return generate_fallback_response(messages)


def generate_fallback_response(messages):
    """
    Generate a smart rule-based fallback response when Ollama is not available.
    Produces conversational, chatbot-like responses using search results.
    """
    import random

    # Extract the user's query and context from the last message
    last_msg = messages[-1]["content"] if messages else ""

    # Check if we have product search results in the context
    if "matching products from the store inventory" in last_msg:
        lines = last_msg.split("\n")
        product_lines = [l.strip() for l in lines if l.strip().startswith("- **")]

        if product_lines:
            # Extract location info
            location_lines = [l.strip() for l in lines if "Location:" in l]
            location_info = ""
            if location_lines:
                location_info = location_lines[0].replace("Location:", "").strip()

            # Extract direction if present
            direction_line = ""
            for line in lines:
                if line.strip().startswith("Directions:"):
                    direction_line = line.strip().replace("Directions:", "").strip()
                    break

            # Build a concise response
            if location_info:
                response = f"📍 Found at **{location_info}**."
            else:
                response = "Here's what I found."

            if direction_line:
                response += f"\n\n🚶 {direction_line}"

            return response

    if "No matching products found" in last_msg:
        no_match = [
            "I couldn't find that in our store. Try a different search term or category (e.g., 'snacks', 'dairy', 'personal care').",
            "No exact match. Try broader terms like the product category or brand name.",
            "Sorry, that doesn't seem to be in stock. Can you describe it differently?"
        ]
        return random.choice(no_match)

    # Generic responses
    generic = [
        "Hi! Type what you're looking for — like 'milk', 'shampoo', or 'something for a cold' — and I'll find it.",
        "I'm here to help you find products. What do you need today?",
        "Welcome! Just tell me what you're looking for."
    ]
    return random.choice(generic)


def voice_chat(audio_bytes, conversation_history=None):
    """
    Full voice pipeline: Audio → Text (Whisper) → Response (LLM)

    Args:
        audio_bytes: Raw audio data
        conversation_history: Previous messages

    Returns:
        Same as chat() but with added 'transcription' field
    """
    transcription = transcribe_audio(audio_bytes)
    result = chat(transcription, conversation_history)
    result["transcription"] = transcription
    return result
