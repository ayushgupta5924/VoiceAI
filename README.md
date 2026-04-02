# Voice-Enabled E-Commerce Support Assistant

A voice-in, voice-out support assistant for an e-commerce platform. The user speaks a query (e.g. "Where is my order?"), and the system responds with both synthesized speech and a text subtitle — entirely free and running locally.

---

## Demo

| Step | What happens |
|------|-------------|
| 1 | User records or uploads an audio query |
| 2 | Whisper transcribes speech to text |
| 3 | LLaMA 3.2 generates a response grounded in order/policy data |
| 4 | Edge TTS synthesizes the response to audio |
| 5 | Gradio UI displays text subtitle + plays audio response |

---

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed on your machine

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/voice-support-assistant.git
cd voice-support-assistant
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Pull the LLM model

Open a terminal and run:

```bash
ollama pull llama3.2:1b
```

### 4. Start Ollama server

```bash
ollama serve
```

Keep this terminal open and open a new terminal for the next step.

### 5. Run the app

```bash
python app.py
```

Open `http://127.0.0.1:7860` in your browser.

---

## Project Structure

```
├── assistant.py       # Core pipeline: STT → LLM → TTS
├── app.py             # Gradio UI
├── orders.json        # Order dataset
├── policies.json      # Policy dataset
├── requirements.txt
└── .env.example
```

---

## Assumptions

- **User identity**: The user enters their User ID (e.g. `U1`, `U2`) manually in the UI. There is no authentication layer — this is a demo system.
- **Return eligibility**: Computed dynamically at runtime as `delivery_date + return_window_days >= today`. If the window has passed, the assistant informs the user accordingly.
- **Single-turn conversations**: Each query is independent. There is no multi-turn memory or session state.
- **Dataset as source of truth**: The LLM is instructed via system prompt to answer strictly from the provided `orders.json` and `policies.json` data, not from its general training knowledge.
- **Audio format**: Whisper accepts any common audio format (WAV, MP3, WebM) — whatever the browser microphone or file upload provides.
- **Internet for TTS**: `edge-tts` uses Microsoft's neural voice API and requires an internet connection. All other components (Whisper, LLaMA) run fully offline.

---

## Design Decisions & Tradeoffs

### STT — `faster-whisper` (tiny model)
- Runs fully locally on CPU with no API key required.
- The `tiny` model is fast (~2–3s) but less accurate than larger variants. Chosen for speed on low-resource machines.
- Tradeoff: accuracy vs. latency. The `base` or `small` model can be swapped in `assistant.py` for better transcription at the cost of speed.

### LLM — `llama3.2:1b` via Ollama
- Free, local, no API key needed.
- The 1B parameter model is lightweight and runs on CPU.
- Tradeoff: response quality is lower than GPT-4 class models. The system prompt and structured context injection compensate by constraining the model to only use provided data.
- A larger model (e.g. `llama3.2`, `mistral`) can be used by changing one line in `assistant.py`.

### TTS — `edge-tts` (Microsoft Jenny Neural)
- Produces natural-sounding speech using Microsoft's neural voices.
- Free with no API key — uses the same backend as Windows Narrator.
- Tradeoff: requires internet. `pyttsx3` was considered as a fully offline alternative but produced unreliable audio output on Windows.

### UI — Gradio
- Minimal setup, runs in the browser, supports mic recording and file upload out of the box.
- Tradeoff: not production-grade. A FastAPI backend with a proper frontend would be more appropriate for real deployment.

### Context injection over RAG
- Given the small dataset size (3 orders, 1 policy file), the entire dataset is serialized as a string and injected into the LLM prompt directly.
- Tradeoff: this approach does not scale beyond ~20–30 orders. For larger datasets, a vector database with semantic search (RAG) would be needed.

---

## Potential Improvements

- **Multi-turn memory**: Maintain conversation history per session so the user can ask follow-up questions naturally.
- **User authentication**: Replace the manual User ID input with a proper login or session token.
- **RAG for large datasets**: Use a vector store (e.g. FAISS, ChromaDB) to retrieve relevant orders/policies semantically instead of injecting the full dataset.
- **Streaming responses**: Stream LLM tokens to the UI in real time instead of waiting for the full response, reducing perceived latency.
- **Better STT model**: Swap `tiny` for `base` or `small` Whisper model for improved transcription accuracy, especially for accented speech.
- **Offline TTS**: Replace `edge-tts` with a fully offline neural TTS like `Coqui TTS` for zero internet dependency.
- **REST API**: Expose the pipeline as a FastAPI endpoint so it can be integrated into any frontend or mobile app.
