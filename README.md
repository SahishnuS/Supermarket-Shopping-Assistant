# Supermarket AI Shopping Assistant 

A comprehensive, AI-powered smart shopping assistant designed to enhance the in-store supermarket experience. It features voice and text processing, intelligent product routing, and a store management dashboard.

##  Features

- ** Voice & Text Chat**: Interact with the assistant using voice (powered by OpenAI Whisper) or text to find products naturally.
- ** Local & Cloud AI**: Uses Ollama for local LLM processing (e.g., Phi-2, TinyLlama) or Groq for lightning-fast cloud inference.
- ** Smart Store Routing**: Generates customized visual maps showing the optimal path from the entrance to your desired products.
- ** Fuzzy Search**: Quickly find products even with typos using RapidFuzz.
- ** Admin Dashboard**: A dedicated interface to manage store configuration, products, and aisles.
- ** AMD Hardware Acceleration**: Supports ONNX Runtime with DirectML for accelerated inference on AMD GPUs (Olive optimization ready).

##  Architecture

The project is split into three main components:
1. **Customer UI (`app/customer.py`)**: A Streamlit frontend for shoppers.
2. **Admin UI (`run_admin.py`)**: A Streamlit frontend for store managers.
3. **Backend API (`backend/api.py`)**: A Flask REST API that bridges the UIs, database, and AI models.

##  Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SahishnuS/Supermarket-Shopping-Assistant.git
   cd Supermarket-Shopping-Assistant
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory and add your Groq API key (if using Groq instead of Ollama):
   ```
   GROQ_API_KEY=your_api_key_here
   ```

##  Running the Application

For the full experience, run the following components in separate terminal windows:

**1. Start the Backend API (Flask):**
```bash
python run_api.py
# API runs on http://localhost:5000
```

**2. Start the Customer Interface (Streamlit):**
```bash
python run_customer.py
# UI runs on http://localhost:8502
```

**3. Start the Admin Dashboard (Streamlit):**
```bash
python run_admin.py
# Admin runs on http://localhost:8501
```

##  Model Setup & Configuration

### Whisper (Speech-to-Text)
The app uses OpenAI Whisper (`base` model by default, ~150MB). It automatically downloads on the first voice query.

### LLM (Conversational Assistant)
You have two choices for the conversation AI:
1. **Groq (Cloud)**: Fast inference using the Groq API (requires `.env` setup).
2. **Ollama (Local)**: 
   - Install [Ollama](https://ollama.ai/download)
   - Pull a model: `ollama pull phi` or `ollama pull tinyllama`
   - Adjust `LLM_MODEL` in `backend/ai_pipeline.py`.

*(Note: If no LLM is available, the app falls back to a rule-based response system for product searches).*

## 📊 Database
The application uses SQLite (`data/store.db`). Sample data is automatically seeded upon the first run, providing immediate testing capabilities.

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
