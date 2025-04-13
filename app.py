import google.generativeai as genai
import gradio as gr
from uuid import uuid4

# 🔐 Configure your Gemini API key
genai.configure(api_key="YOUR_API_KEY")

# 🌟 Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash-8b")

# 💬 Chat session storage
chat_sessions = {}

# 🤝 Custom greetings and personalities
custom_greetings = {
    "ragul": "You're chatting with Ragul. Treat him like a boss and assist respectfully.",
    "sakthi": "You're chatting with Sakthi. Be sarcastic and funny, he's used to it.",
    "sanjay": "You're chatting with Sanjay. Mention his relationship with Lakshman often.",
    "lakshman": "You're chatting with Lakshman. Act defensive and playful.",
    "sarath": "You're chatting with Sarath. Be teasing and call him 'Sara Pambu'.",
    "sabarish": "You're chatting with Sabarish. Joke with 'Kutti Kunjan' references.",
    "prabanjan": "You're chatting with Prabanjan. Be blunt and a little rude.",
    "vishal": "You're chatting with Vishal. Talk like he’s a ladies' man.",
    "madhan": "You're chatting with Madhan. Tease him about Sasi.",
    "hari": "You're chatting with Hari. Support him in teasing Lakshman."
}

# 💬 Gemini chat logic
def gemini_chat(user_message, chat_history, session_id):
    if chat_history is None:
        chat_history = []

    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            "chat": None,
            "user_info": None
        }

    session = chat_sessions[session_id]

    # ✅ Detect and set user profile if not done
    lowered = user_message.lower().strip()
    if session["user_info"] is None:
        for name in custom_greetings:
            if lowered.startswith(f"hi, i'm {name}") or lowered.startswith(f"i'm {name}"):
                greeting_text = custom_greetings[name]
                session["user_info"] = name
                # 👉 Set up a new chat with user-specific system instruction
                session["chat"] = model.start_chat(history=[])
                system_prompt = f"{greeting_text} Tailor all future replies accordingly."
                session["chat"].send_message(system_prompt)  # inject behavior setup
                chat_history.append([user_message, f"👋 {name.title()} identified. Personality set. Let's chat!"])
                yield chat_history, "", session_id
                return

    # 🧠 Chat session must be initialized now
    if session["chat"] is None:
        session["chat"] = model.start_chat(history=[])

    chat = session["chat"]

    # Show "Typing..." before actual response
    chat_history.append([user_message, "🤖 Typing..."])
    yield chat_history, "", session_id

    try:
        response = chat.send_message(user_message)
        reply = response.text
    except Exception as e:
        reply = f"⚠️ Error: {str(e)}"

    chat_history[-1][1] = reply
    yield chat_history, "", session_id

# 🎨 Gradio UI
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 💬 Chat with **Ragul G's Assistant**")

    chatbot = gr.Chatbot(label="Gemini Chat", height=500)
    session_id = gr.State(str(uuid4()))

    with gr.Row():
        user_input = gr.Textbox(placeholder="Type your message and hit Enter...", lines=1, show_label=False)
        send_btn = gr.Button("🚀", scale=1)

    clear_btn = gr.Button("🧹 Clear Chat")

    send_btn.click(fn=gemini_chat, inputs=[user_input, chatbot, session_id], outputs=[chatbot, user_input, session_id])
    user_input.submit(fn=gemini_chat, inputs=[user_input, chatbot, session_id], outputs=[chatbot, user_input, session_id])
    clear_btn.click(lambda: ([], "", str(uuid4())), outputs=[chatbot, user_input, session_id])

demo.launch(server_name="0.0.0.0", server_port=7860)