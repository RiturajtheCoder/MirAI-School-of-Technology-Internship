import streamlit as st
st.title("The Void")
st.write("Welcome to the application! Enter your Username and Message below")
user_name=st.text_input("Provide your Name")
user_message=st.text_input("Provide your Message")
if st.button("Transmit"):
    if(user_name.strip()==""):
        st.error("Please provide your name")
    elif(user_message.strip()==""):
        st.warning("Please type a message to transmit")
    else:
        st.success(f"Transmission successful! Greetings, {user_name}.\nWe received your message: {user_message}")
        total_characters=len(user_message)
        token_count=total_characters/4
        st.info(f"System Check: Your message will consume approximately {token_count:.2f} tokens from our context window")