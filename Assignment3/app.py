import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.title("🌌 AI Multiverse")

personality = st.selectbox(
    "Who do you want to talk to?",
    [
        "Select a personality",
        "An expert hacker",
        "Virat Kohli",
        "An angry Ravi Shastri",
        "A crazy Ronaldo fan",
        "Donald Trump"
    ]
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_message := st.chat_input("Say something..."):

    with st.chat_message("user"):
        st.markdown(user_message)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    if personality == "Select a personality":
        ai_response = "Please select a personality first."

    else:
        prompt = f"""
You are acting like {personality}.

Reply exactly as this personality would.

Stay completely in character.

User: {user_message}
"""

        with st.spinner("Connecting to the multiverse..."):

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            ai_response = response.text

    with st.chat_message("assistant"):
        st.markdown(ai_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )
