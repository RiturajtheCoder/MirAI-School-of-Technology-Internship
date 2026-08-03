import streamlit as st
from google import genai
import json
import requests
from io import BytesIO
from PIL import Image
import os
import tempfile
from gtts import gTTS
import time
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# PHASE 1: The Director's Cut (UI & Configuration)
# ============================================================================

st.set_page_config(
    page_title="AI Visual Novel",
    page_icon="📖",
    layout="wide"
)

# Initialize ALL session state variables
def init_session_state():
    defaults = {
        "messages": [],
        "chat": None,
        "story_started": False,
        "current_story": None,
        "current_image": None,
        "current_audio": None,
        "audio_files": []  # Track audio files for cleanup
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default

init_session_state()

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
        # Clean up old audio files
        for audio_file in st.session_state.audio_files:
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except:
                pass
        
        # Reset session state
        st.session_state.messages = []
        st.session_state.chat = None
        st.session_state.story_started = False
        st.session_state.current_story = None
        st.session_state.current_image = None
        st.session_state.current_audio = None
        st.session_state.audio_files = []
        st.rerun()

# ============================================================================
# PHASE 1: Cache Gemini client - CORRECTED VERSION
# ============================================================================

@st.cache_resource
def get_gemini_client():
    """Initialize and cache Gemini client"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found! Please add your API key to .env file.")
        st.stop()
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        # Return the model directly
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {str(e)}")
        st.stop()

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

def parse_gemini_response(response_text):
    """Parse JSON response from Gemini with enhanced error handling"""
    try:
        # Clean the response - remove markdown code blocks
        cleaned = response_text.strip()
        
        # Handle various markdown formats
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Try to find JSON if there's extra text
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            cleaned = cleaned[start_idx:end_idx]
        
        # Parse JSON
        data = json.loads(cleaned)
        
        # Validate structure
        required_keys = ["story_text", "image_prompt", "options"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        # Ensure options is a list and contains strings
        if not isinstance(data["options"], list):
            data["options"] = [str(data["options"])]
        
        data["options"] = [str(opt).strip() for opt in data["options"] if str(opt).strip()]
        
        # Ensure we have at least 2 options
        if len(data["options"]) < 2:
            data["options"].extend(["Continue", "Explore"])[:2]
        
        return data
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response. Please try again.")
        st.error(f"Raw response: {response_text[:200]}...")
        return None
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        return None

# ============================================================================
# PHASE 4: Multi-Media Rendering
# ============================================================================

def generate_image(prompt):
    """Generate image using Pollinations API with graceful failure"""
    try:
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
    """Generate audio using gTTS with graceful failure"""
    try:
        # Truncate text if too long for TTS
        if len(text) > 500:
            text = text[:497] + "..."
        
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(temp_file.name)
        
        # Track audio file for cleanup
        st.session_state.audio_files.append(temp_file.name)
        
        return temp_file.name
        
    except Exception as e:
        st.toast("🔊 Audio generation failed, continuing...", icon="⚠️")
        return None

# ============================================================================
# Main Story Logic - CORRECTED VERSION
# ============================================================================

def start_story():
    """Initialize the story with the first AI response"""
    with st.spinner("🎬 Crafting your story..."):
        try:
            # Get the model (which is a GenerativeModel instance)
            model = get_gemini_client()
            system_prompt = build_system_prompt(story_genre, art_style)
            
            # Start chat with history
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
                
        except Exception as e:
            st.error(f"Failed to start story: {str(e)}")
            st.error("Please check your API key and try again.")

def continue_story(choice_text):
    """Continue the story with user's choice"""
    with st.spinner("📖 Continuing story..."):
        try:
            chat = st.session_state.chat
            
            # Send user choice with context
            response = chat.send_message(
                f"The player chose: {choice_text}\n\n"
                f"Continue the story based on this choice. "
                f"Remember to respond with a valid JSON object."
            )
            
            # Parse JSON
            parsed = parse_gemini_response(response.text)
            if parsed:
                st.session_state.current_story = parsed
                st.session_state.messages.append({
                    "role": "assistant",
                    "story": parsed
                })
                
                # Generate new image
                image = generate_image(parsed["image_prompt"])
                if image:
                    st.session_state.current_image = image
                
                # Generate new audio
                audio_file = generate_audio(parsed["story_text"])
                if audio_file:
                    st.session_state.current_audio = audio_file
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Failed to continue story: {str(e)}")

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
            try:
                with open(st.session_state.current_audio, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format='audio/mp3')
            except Exception as e:
                st.toast("🔊 Audio playback failed", icon="⚠️")
        
        # ============================================================================
        # PHASE 3: Dynamic UI Generation
        # ============================================================================
        st.markdown("### 🎯 What do you do?")
        
        # Create dynamic buttons for each option
        options = story.get('options', [])
        
        # Ensure we have valid options
        if options:
            # Use columns for better button layout
            if len(options) == 2:
                cols = st.columns(2)
                for idx, (col, option) in enumerate(zip(cols, options)):
                    with col:
                        button_key = f"opt_{idx}_{hash(option)}"
                        if st.button(f"➡️ {option}", key=button_key, use_container_width=True):
                            continue_story(option)
            else:
                for idx, option in enumerate(options):
                    button_key = f"opt_{idx}_{hash(option)}"
                    if st.button(f"➡️ {option}", key=button_key, use_container_width=True):
                        continue_story(option)
        else:
            st.warning("No options available. Please restart the story.")

with col2:
    # Display image
    if st.session_state.current_image:
        st.markdown("### 🎨 Scene Visualization")
        try:
            st.image(st.session_state.current_image, use_container_width=True)
        except Exception as e:
            st.info("🎨 Image display error, but story continues...")
    else:
        st.info("🎨 Image will appear here")

# ============================================================================
# PHASE 5: Start Story Button
# ============================================================================

if not st.session_state.story_started:
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
# History display
# ============================================================================

with st.expander("📜 Story History"):
    if st.session_state.messages:
        for idx, msg in enumerate(st.session_state.messages):
            if msg["role"] == "assistant":
                story = msg["story"]
                st.markdown(f"**Step {idx+1}:** {story['story_text'][:100]}...")
                if idx < len(st.session_state.messages) - 1:
                    st.divider()
    else:
        st.info("No story history yet. Start your adventure!")

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")
st.caption("Built with ❤️ for MirAI School of Technology Virtual Summer Internship 2026")
