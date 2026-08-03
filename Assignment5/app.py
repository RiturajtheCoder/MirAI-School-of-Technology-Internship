'''import streamlit as st
import google.generativeai as genai
import json
import requests
from io import BytesIO
from PIL import Image
import os
import tempfile
from gtts import gTTS
import time

# PHASE 1: The Director's Cut (UI & Configuration)

# Configure page
st.set_page_config(
    page_title="AI Visual Novel",
    page_icon="📖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None
if "story_started" not in st.session_state:
    st.session_state.story_started = False
if "current_story" not in st.session_state:
    st.session_state.current_story = None
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "current_audio" not in st.session_state:
    st.session_state.current_audio = None

# Sidebar configuration
with st.sidebar:
    st.title("📚 Story Settings")
    story_genre = st.selectbox(
        "Select Genre",
        ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Adventure"]
    )
    art_style = st.selectbox(
        "Select Art Style",
        ["Anime", "Watercolor", "Oil Painting", "Pixel Art", "Cyberpunk", "Ghibli Style"]
    )
    
    if st.button("🔄 Start New Story"):
        st.session_state.messages = []
        st.session_state.story_started = False
        st.session_state.current_story = None
        st.session_state.current_image = None
        st.session_state.current_audio = None
        st.rerun()

# PHASE 1: Cache Gemini client

@st.cache_resource
def get_gemini_client():
    """Initialize and cache Gemini client"""
    # IMPORTANT: Replace with your actual API key or use st.secrets
    api_key = st.secrets.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

@st.cache_resource
def get_tts_engine():
    """Cache TTS engine - gTTS doesn't need initialization, but keeping for consistency"""
    return "gTTS"

# PHASE 2: Structured JSON Engine

def build_system_prompt(genre, art_style):
    """Build the system prompt with JSON structure requirement"""
    return f"""You are an AI Visual Novel storyteller. Write a {genre} story with {art_style} art style.

CRITICAL: You MUST respond with ONLY a valid JSON object in this exact format:
{{
    "story_text": "Your narrative paragraph here (2-4 sentences, immersive and descriptive)",
    "image_prompt": "A detailed, artistic prompt for generating an image in {art_style} style",
    "options": ["Choice 1", "Choice 2", "Choice 3"]
}}

Rules:
1. story_text: Write immersive, engaging narrative. Set the scene vividly.
2. image_prompt: Create a detailed prompt that captures the key visual elements of the current scene. Include style, mood, lighting, and composition.
3. options: Provide 2-3 distinct, meaningful choices that advance the story. Each option should be a clear action the player can take.
4. The story should be engaging and branch based on user choices.
5. Respond ONLY with the JSON object, no other text.

Start the story with an engaging opening scene based on {genre} genre."""


def parse_gemini_response(response_text):
    """Parse JSON response from Gemini with error handling"""
    try:
        # Clean the response - remove markdown code blocks if present
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # Parse JSON
        data = json.loads(cleaned)
        
        # Validate structure
        required_keys = ["story_text", "image_prompt", "options"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        # Ensure options is a list
        if not isinstance(data["options"], list):
            data["options"] = [str(data["options"])]
        
        # Ensure options are strings
        data["options"] = [str(opt) for opt in data["options"]]
        
        return data
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        return None

# PHASE 4: Multi-Media Rendering

def generate_image(prompt):
    """Generate image using Pollinations API"""
    try:
        # Encode prompt for URL
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=512&nologo=true"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        return image
    except requests.exceptions.RequestException as e:
        st.toast("🎨 Image server is busy, skipping visual...", icon="⚠️")
        return None
    except Exception as e:
        st.toast("🎨 Failed to generate image, continuing story...", icon="⚠️")
        return None

def generate_audio(text):
    """Generate audio using gTTS"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.toast("🔊 Audio generation failed, continuing...", icon="⚠️")
        return None

# Main Story Logic

def start_story():
    """Initialize the story with the first AI response"""
    with st.spinner("🎬 Crafting your story..."):
        model = get_gemini_client()
        system_prompt = build_system_prompt(story_genre, art_style)
        
        # Start chat
        chat = model.start_chat(history=[])
        st.session_state.chat = chat
        
        # Get initial response
        response = chat.send_message(system_prompt + "\n\nStart the story.")
        
        # Parse JSON
        parsed = parse_gemini_response(response.text)
        if parsed:
            st.session_state.current_story = parsed
            st.session_state.messages.append({
                "role": "assistant",
                "story": parsed
            })
            
            # Generate image (with error handling)
            image = generate_image(parsed["image_prompt"])
            if image:
                st.session_state.current_image = image
            
            # Generate audio
            audio_file = generate_audio(parsed["story_text"])
            if audio_file:
                st.session_state.current_audio = audio_file
            
            st.session_state.story_started = True
            st.rerun()

def continue_story(choice_text):
    """Continue the story with user's choice"""
    with st.spinner("📖 Continuing story..."):
        model = get_gemini_client()
        chat = st.session_state.chat
        
        # Send user choice
        response = chat.send_message(f"The player chose: {choice_text}\n\nContinue the story based on this choice.")
        
        # Parse JSON
        parsed = parse_gemini_response(response.text)
        if parsed:
            st.session_state.current_story = parsed
            st.session_state.messages.append({
                "role": "assistant",
                "story": parsed
            })
            
            # Generate image (with error handling)
            image = generate_image(parsed["image_prompt"])
            if image:
                st.session_state.current_image = image
            
            # Generate audio
            audio_file = generate_audio(parsed["story_text"])
            if audio_file:
                st.session_state.current_audio = audio_file
            
            st.rerun()

# UI Rendering

# Title
st.title("📖 AI Visual Novel Engine")
st.caption("A Choose Your Own Adventure experience powered by Gemini AI")

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    # Display story
    if st.session_state.current_story:
        story = st.session_state.current_story
        
        # Display story text
        st.markdown(f"### 📝 Story")
        st.markdown(f"{story['story_text']}")
        
        # Display audio player if available
        if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
            with open(st.session_state.current_audio, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
        
        # ============================================================================
        # PHASE 3: Dynamic UI Generation
        # ============================================================================
        st.markdown("### 🎯 What do you do?")
        
        # Create dynamic buttons for each option
        options = story.get('options', [])
        
        # Use columns for better button layout
        if len(options) == 2:
            cols = st.columns(2)
            for idx, (col, option) in enumerate(zip(cols, options)):
                with col:
                    if st.button(f"➡️ {option}", key=f"opt_{idx}", use_container_width=True):
                        continue_story(option)
        else:
            for idx, option in enumerate(options):
                if st.button(f"➡️ {option}", key=f"opt_{idx}", use_container_width=True):
                    continue_story(option)

with col2:
    # Display image
    if st.session_state.current_image:
        st.markdown("### 🎨 Scene Visualization")
        st.image(st.session_state.current_image, use_container_width=True)
    else:
        st.info("🎨 Image will appear here")

# PHASE 5: Start Story Button

if not st.session_state.story_started:
    # Show a beautiful start screen
    st.markdown("---")
    st.markdown("### 🚀 Ready to begin your adventure?")
    st.markdown("""
    - Select a genre and art style from the sidebar
    - Click the button below to start your story
    - Your choices will shape the narrative!
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎮 Begin Your Adventure", use_container_width=True):
            start_story()

# History display (optional)

with st.expander("📜 Story History"):
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "assistant":
            story = msg["story"]
            st.markdown(f"**Step {idx+1}:** {story['story_text'][:100]}...")
            if idx < len(st.session_state.messages) - 1:
                st.divider()

# Cleanup audio files

# Clean up old audio files
if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
    # Keep only the latest audio file, delete old ones
    for file in os.listdir(tempfile.gettempdir()):
        if file.endswith('.mp3') and file != os.path.basename(st.session_state.current_audio):
            try:
                os.remove(os.path.join(tempfile.gettempdir(), file))
            except:
                pass'''


import streamlit as st
import google.generativeai as genai
import json
import requests
from io import BytesIO
from PIL import Image
import os
import tempfile
from gtts import gTTS
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PHASE 1: The Director's Cut (UI & Configuration)
# ============================================================================

# Configure page
st.set_page_config(
    page_title="AI Visual Novel",
    page_label="📖",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None
if "story_started" not in st.session_state:
    st.session_state.story_started = False
if "current_story" not in st.session_state:
    st.session_state.current_story = None
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "current_audio" not in st.session_state:
    st.session_state.current_audio = None

# Sidebar configuration
with st.sidebar:
    st.title("📚 Story Settings")
    story_genre = st.selectbox(
        "Select Genre",
        ["Fantasy", "Sci-Fi", "Mystery", "Romance", "Horror", "Adventure"]
    )
    art_style = st.selectbox(
        "Select Art Style",
        ["Anime", "Watercolor", "Oil Painting", "Pixel Art", "Cyberpunk", "Ghibli Style"]
    )
    
    if st.button("🔄 Start New Story"):
        st.session_state.messages = []
        st.session_state.story_started = False
        st.session_state.current_story = None
        st.session_state.current_image = None
        st.session_state.current_audio = None
        st.rerun()

# ============================================================================
# PHASE 1: Cache Gemini client
# ============================================================================

@st.cache_resource
def get_gemini_client():
    """Initialize and cache Gemini client"""
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found in .env file! Please add your API key.")
        st.stop()
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

@st.cache_resource
def get_tts_engine():
    """Cache TTS engine - gTTS doesn't need initialization, but keeping for consistency"""
    return "gTTS"

# ============================================================================
# PHASE 2: Structured JSON Engine
# ============================================================================

def build_system_prompt(genre, art_style):
    """Build the system prompt with JSON structure requirement"""
    return f"""You are an AI Visual Novel storyteller. Write a {genre} story with {art_style} art style.

CRITICAL: You MUST respond with ONLY a valid JSON object in this exact format:
{{
    "story_text": "Your narrative paragraph here (2-4 sentences, immersive and descriptive)",
    "image_prompt": "A detailed, artistic prompt for generating an image in {art_style} style",
    "options": ["Choice 1", "Choice 2", "Choice 3"]
}}

Rules:
1. story_text: Write immersive, engaging narrative. Set the scene vividly.
2. image_prompt: Create a detailed prompt that captures the key visual elements of the current scene. Include style, mood, lighting, and composition.
3. options: Provide 2-3 distinct, meaningful choices that advance the story. Each option should be a clear action the player can take.
4. The story should be engaging and branch based on user choices.
5. Respond ONLY with the JSON object, no other text.

Start the story with an engaging opening scene based on {genre} genre."""
}

def parse_gemini_response(response_text):
    """Parse JSON response from Gemini with error handling"""
    try:
        # Clean the response - remove markdown code blocks if present
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        # Parse JSON
        data = json.loads(cleaned)
        
        # Validate structure
        required_keys = ["story_text", "image_prompt", "options"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        # Ensure options is a list
        if not isinstance(data["options"], list):
            data["options"] = [str(data["options"])]
        
        # Ensure options are strings
        data["options"] = [str(opt) for opt in data["options"]]
        
        return data
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        return None

# ============================================================================
# PHASE 4: Multi-Media Rendering
# ============================================================================

def generate_image(prompt):
    """Generate image using Pollinations API"""
    try:
        # Encode prompt for URL
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=512&nologo=true"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        return image
    except requests.exceptions.RequestException as e:
        st.toast("🎨 Image server is busy, skipping visual...", icon="⚠️")
        return None
    except Exception as e:
        st.toast("🎨 Failed to generate image, continuing story...", icon="⚠️")
        return None

def generate_audio(text):
    """Generate audio using gTTS"""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.toast("🔊 Audio generation failed, continuing...", icon="⚠️")
        return None

# ============================================================================
# Main Story Logic
# ============================================================================

def start_story():
    """Initialize the story with the first AI response"""
    with st.spinner("🎬 Crafting your story..."):
        model = get_gemini_client()
        system_prompt = build_system_prompt(story_genre, art_style)
        
        # Start chat
        chat = model.start_chat(history=[])
        st.session_state.chat = chat
        
        # Get initial response
        response = chat.send_message(system_prompt + "\n\nStart the story.")
        
        # Parse JSON
        parsed = parse_gemini_response(response.text)
        if parsed:
            st.session_state.current_story = parsed
            st.session_state.messages.append({
                "role": "assistant",
                "story": parsed
            })
            
            # Generate image (with error handling)
            image = generate_image(parsed["image_prompt"])
            if image:
                st.session_state.current_image = image
            
            # Generate audio
            audio_file = generate_audio(parsed["story_text"])
            if audio_file:
                st.session_state.current_audio = audio_file
            
            st.session_state.story_started = True
            st.rerun()

def continue_story(choice_text):
    """Continue the story with user's choice"""
    with st.spinner("📖 Continuing story..."):
        model = get_gemini_client()
        chat = st.session_state.chat
        
        # Send user choice
        response = chat.send_message(f"The player chose: {choice_text}\n\nContinue the story based on this choice.")
        
        # Parse JSON
        parsed = parse_gemini_response(response.text)
        if parsed:
            st.session_state.current_story = parsed
            st.session_state.messages.append({
                "role": "assistant",
                "story": parsed
            })
            
            # Generate image (with error handling)
            image = generate_image(parsed["image_prompt"])
            if image:
                st.session_state.current_image = image
            
            # Generate audio
            audio_file = generate_audio(parsed["story_text"])
            if audio_file:
                st.session_state.current_audio = audio_file
            
            st.rerun()

# ============================================================================
# UI Rendering
# ============================================================================

# Title
st.title("📖 AI Visual Novel Engine")
st.caption("A Choose Your Own Adventure experience powered by Gemini AI")

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    # Display story
    if st.session_state.current_story:
        story = st.session_state.current_story
        
        # Display story text
        st.markdown(f"### 📝 Story")
        st.markdown(f"{story['story_text']}")
        
        # Display audio player if available
        if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
            with open(st.session_state.current_audio, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
        
        # ============================================================================
        # PHASE 3: Dynamic UI Generation
        # ============================================================================
        st.markdown("### 🎯 What do you do?")
        
        # Create dynamic buttons for each option
        options = story.get('options', [])
        
        # Use columns for better button layout
        if len(options) == 2:
            cols = st.columns(2)
            for idx, (col, option) in enumerate(zip(cols, options)):
                with col:
                    if st.button(f"➡️ {option}", key=f"opt_{idx}", use_container_width=True):
                        continue_story(option)
        else:
            for idx, option in enumerate(options):
                if st.button(f"➡️ {option}", key=f"opt_{idx}", use_container_width=True):
                    continue_story(option)

with col2:
    # Display image
    if st.session_state.current_image:
        st.markdown("### 🎨 Scene Visualization")
        st.image(st.session_state.current_image, use_container_width=True)
    else:
        st.info("🎨 Image will appear here")

# ============================================================================
# PHASE 5: Start Story Button
# ============================================================================

if not st.session_state.story_started:
    # Show a beautiful start screen
    st.markdown("---")
    st.markdown("### 🚀 Ready to begin your adventure?")
    st.markdown("""
    - Select a genre and art style from the sidebar
    - Click the button below to start your story
    - Your choices will shape the narrative!
    """)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎮 Begin Your Adventure", use_container_width=True):
            start_story()

# ============================================================================
# History display (optional)
# ============================================================================

with st.expander("📜 Story History"):
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "assistant":
            story = msg["story"]
            st.markdown(f"**Step {idx+1}:** {story['story_text'][:100]}...")
            if idx < len(st.session_state.messages) - 1:
                st.divider()

# ============================================================================
# Cleanup audio files
# ============================================================================

# Clean up old audio files
if st.session_state.current_audio and os.path.exists(st.session_state.current_audio):
    # Keep only the latest audio file, delete old ones
    for file in os.listdir(tempfile.gettempdir()):
        if file.endswith('.mp3') and file != os.path.basename(st.session_state.current_audio):
            try:
                os.remove(os.path.join(tempfile.gettempdir(), file))
            except:
                pass

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.caption("Built with ❤️ for MirAI School of Technology Virtual Summer Internship 2026")
