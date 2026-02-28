# Supermarket AI Shopping Assistant - Model Setup

## Whisper (Speech-to-Text)
The app uses OpenAI Whisper for voice transcription. It will auto-download the model on first use.

### Install:
```bash
pip install openai-whisper
```

The `base` model (~150MB) is used by default. It will download automatically on first voice query.

## LLM (Conversational AI)
The app uses Ollama to run a local LLM for conversational responses.

### Install Ollama:
1. Download from: https://ollama.ai/download
2. Install and run the Ollama service

### Pull the model:
```bash
ollama pull phi
```

This downloads the Phi-2 model (~1.6GB, Q4 quantized).

### Alternative smaller model:
```bash
ollama pull tinyllama
```

Then update `LLM_MODEL` in `backend/ai_pipeline.py`.

## Fallback Mode
If Ollama is not running, the app will automatically fall back to a rule-based response system.
The app remains fully functional for product search and navigation without the LLM.

## AMD Olive Optimization (Optional)
For production deployment with AMD hardware:
1. Install AMD Olive on a Linux machine with ROCm
2. Export Whisper to ONNX format using Olive
3. Replace the Whisper model loading in `ai_pipeline.py` with ONNX Runtime inference
