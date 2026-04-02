import json
import tempfile
from datetime import date, datetime
from pathlib import Path

import asyncio
from faster_whisper import WhisperModel
import ollama
import edge_tts

# ── Load dataset ──────────────────────────────────────────────────────────────
_BASE = Path(__file__).parent
with open(_BASE / "orders.json") as f:
    ORDERS: list[dict] = json.load(f)
with open(_BASE / "policies.json") as f:
    POLICIES: dict = json.load(f)

# Load Whisper model once at startup (tiny = fast, runs on CPU)
_whisper = WhisperModel("tiny", device="cpu", compute_type="int8")


def _build_context(user_id: str) -> str:
    today = date.today().isoformat()
    user_orders = [o for o in ORDERS if o["user_id"] == user_id]
    for o in user_orders:
        if o.get("delivery_date") and o.get("return_window_days"):
            delivered = datetime.strptime(o["delivery_date"], "%Y-%m-%d").date()
            o["return_eligible"] = date.today().toordinal() <= delivered.toordinal() + o["return_window_days"]
    return (
        f"Today: {today}\n"
        f"User orders: {json.dumps(user_orders)}\n"
        f"Store policies: {json.dumps(POLICIES)}"
    )


SYSTEM_PROMPT = (
    "You are a helpful e-commerce support assistant. "
    "Answer using ONLY the provided order and policy data. "
    "Be concise (2-4 sentences). If information is missing, say so politely."
)


def transcribe(audio_path: str) -> str:
    segments, _ = _whisper.transcribe(audio_path)
    return " ".join(s.text for s in segments).strip()


def generate_response(query: str, user_id: str = "U1") -> str:
    context = _build_context(user_id)
    resp = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return resp["message"]["content"].strip()


def synthesize(text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    async def _synth():
        tts = edge_tts.Communicate(text, voice="en-US-JennyNeural")
        await tts.save(tmp.name)
    asyncio.run(_synth())
    return tmp.name


def run_pipeline(audio_path: str, user_id: str = "U1") -> tuple[str, str]:
    query = transcribe(audio_path)
    response_text = generate_response(query, user_id)
    audio_out = synthesize(response_text)
    return response_text, audio_out
