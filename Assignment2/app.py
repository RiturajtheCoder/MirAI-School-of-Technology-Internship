import streamlit as st
st.title("Multiverse of Chatbots")
personality=st.selectbox("Who do you want to talk to?",
["Select a personality","An expert hacker","Virat Kohli","An angry Ravi Shastri","A crazy Ronaldo fan","Donald Trump"]                )


import os
from dotenv import load_dotenv
from google import genai
load_dotenv(override=True)
client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
message=st.text_input("Say Something: ")
if st.button("SEND"):
    if message:
        ai_instructions=f"You're acting like {personality}. Respond to the message sent by the user staying completely in the character: {message}"
        with st.spinner("Connecting to the multiverse!....."):
            response=client.models.generate_content(
                model="gemini-2.5-flash",
                contents=ai_instructions
            )
            st.success("Message received!")
            st.write(response.text)
    else:
        st.warning("Please type a message first!")
