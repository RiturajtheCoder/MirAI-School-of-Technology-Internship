# 🌌 AI Multiverse

AI Multiverse is a Streamlit-based AI chatbot that allows users to chat with different AI personalities powered by **Google Gemini**. The chatbot remembers the conversation using Streamlit's `st.session_state`, creating a seamless and interactive chat experience.

## 🚀 Live Demo

**🌐 Streamlit App:**  
https://aiofmultiverse.streamlit.app/

---

## ✨ Features

- 💬 Stateful conversations with chat memory
- 🤖 Multiple AI personalities
- ⚡ Powered by Google Gemini 2.5 Flash
- 🎭 Personality-based responses using prompt engineering
- 🗨️ Modern chat interface with `st.chat_input()` and `st.chat_message()`
- 🔄 Conversation history persists across Streamlit reruns
- 🔐 Secure API key management using environment variables

---

## 🎭 Available Personalities

- 👨‍💻 An Expert Hacker
- 🏏 Virat Kohli
- 😠 An Angry Ravi Shastri
- ⚽ A Crazy Ronaldo Fan
- 🇺🇸 Donald Trump

Each personality stays in character throughout the conversation, providing a unique and engaging chatting experience.

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- python-dotenv

---

## 📂 Project Structure

```
AI-Multiverse/
│── app.py
│── requirements.txt
│── .gitignore
│── .env.example
│── README.md
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone https://github.com/<your-username>/AI-Multiverse.git
cd AI-Multiverse
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Create a `.env` file

```env
GEMINI_API_KEY=YOUR_API_KEY
```

Get your API key from Google AI Studio.

### Run the application

```bash
streamlit run app.py
```

---

## 🎮 How to Use

1. Open the application.
2. Select an AI personality.
3. Type your message in the chat box.
4. Press **Enter** to send.
5. Continue the conversation naturally—the chatbot remembers previous messages.

---

## 🧠 How It Works

The application uses **Streamlit Session State** to maintain chat history even though Streamlit reruns the script after every interaction.

Conversation history is stored as:

```python
st.session_state.messages
```

Each message is stored as a dictionary:

```python
{
    "role": "user",
    "content": "Hello!"
}
```

or

```python
{
    "role": "assistant",
    "content": "Hi! How can I help you today?"
}
```

The stored messages are rendered on every rerun using `st.chat_message()`.

---

## 📸 Preview

Add a screenshot of your application here.

```markdown
![AI Multiverse Screenshot](assets/screenshot.png)
```

---

## 🔐 Environment Variables

Create a `.env` file containing:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

**Never upload your `.env` file to GitHub.**

---

## 📦 Requirements

- Python 3.10+
- Streamlit
- google-genai
- python-dotenv

Install using:

```bash
pip install -r requirements.txt
```

---

## 🌟 Future Improvements

- 🎙️ Voice input
- 🔊 Text-to-speech responses
- 🧠 Separate chat history for each personality
- 📁 Export conversations
- 🌙 Dark mode enhancements
- 🖼️ AI image generation support
- ⏹️ Streaming responses with Stop Generation functionality

---

## 👨‍💻 Author

**Rituraj Saha**

B.Tech Computer Science & Engineering

---

## 📄 License

This project is created for educational purposes and as part of the **MirAI School of Technology Virtual Summer Internship 2026**.
