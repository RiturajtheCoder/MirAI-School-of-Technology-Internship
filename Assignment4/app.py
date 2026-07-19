import streamlit as st
import requests
import random
import urllib.parse

st.set_page_config(page_title="The AI Image Studio", page_icon="🎨")
st.title("🎨 The AI Image Studio")

#User Input
user_prompt = st.text_input("🖌️ Describe your masterpiece")

#Sidebar Settings
st.sidebar.title("⚙️ Settings")
art_style = st.sidebar.selectbox(
    "Select Art Style",
    [
        "Photorealistic",
        "Anime",
        "Vintage Victorian",
        "Sketch",
        "3D Render",
        "Ghibli"
    ]
)

image_width = st.sidebar.slider(
    "Image Width",
    min_value=256,
    max_value=2048,
    value=1024,
    step=64
)

image_height = st.sidebar.slider(
    "Image Height",
    min_value=256,
    max_value=2048,
    value=1024,
    step=64
)

magic_enhance = st.sidebar.checkbox("✨ Enable Magic Enhance")

#Surprise Prompts
surprise_prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A dragon drinking coffee in a library",
    "A floating castle above the ocean during sunset",
    "A futuristic underwater city with glowing whales"
]

#Image Generation Function
def generate_image(prompt):
    full_prompt = f"{prompt}, art style: {art_style}"
    if magic_enhance:
        full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width={image_width}&height={image_height}"
    )
    with st.spinner("🎨 Rendering your masterpiece..."):
        response = requests.get(url)
    if response.status_code == 200:
        st.success("✅ Image Generated Successfully!")
        st.image(
            response.content,
            caption=full_prompt,
            use_container_width=True
        )
        st.download_button(
            label="⬇️ Download Image",
            data=response.content,
            file_name=f"{art_style.lower().replace(' ','_')}_image.png",
            mime="image/png"
        )
    else:
        st.error("❌ Failed to generate image. Please try again.")

#Generate Button
if st.button("🎨 Generate Image"):
    if user_prompt.strip():
        generate_image(user_prompt)
    else:
        st.warning("Please enter an image description.")


#Surprise Me Button
if st.button("🎲 Surprise Me!"):

    random_prompt = random.choice(surprise_prompts)

    st.info(f"**Prompt:** {random_prompt}")

    generate_image(random_prompt)
