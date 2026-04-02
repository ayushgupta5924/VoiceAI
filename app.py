import os
import gradio as gr
from assistant import run_pipeline

def handle(audio_path, user_id):
    if not audio_path:
        return "Please record or upload an audio query.", None
    user_id = user_id.strip() or "U1"
    text, audio_out = run_pipeline(audio_path, user_id)
    return text, audio_out

with gr.Blocks(title="E-Commerce Voice Assistant") as demo:
    gr.Markdown("## 🛒 E-Commerce Voice Support Assistant")
    gr.Markdown("Ask about your orders, returns, or refund policy using your voice.")

    with gr.Row():
        audio_in = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Your Query")
        user_id = gr.Textbox(value="U1", label="User ID", placeholder="e.g. U1 or U2")

    btn = gr.Button("Submit", variant="primary")

    subtitle = gr.Textbox(label="Response (Subtitles)", interactive=False, lines=4)
    audio_out = gr.Audio(label="Response Audio", type="filepath")

    btn.click(fn=handle, inputs=[audio_in, user_id], outputs=[subtitle, audio_out])

if __name__ == "__main__":
    demo.launch()
