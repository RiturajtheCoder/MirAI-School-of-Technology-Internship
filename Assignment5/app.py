import base64
import json
import os
import re
import tempfile
from io import BytesIO
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
from google import genai


st.set_page_config(page_title="Visual Novel Engine", page_icon="🎭", layout="wide")

load_dotenv()

GENRES = [
    "Fantasy",
    "Sci-Fi",
    "Mystery",
    "Horror",
    "Romance",
    "Adventure",
    "Cyberpunk",
    "Thriller",
]

ART_STYLES = [
    "Anime",
    "Cinematic",
    "Watercolor",
    "Digital Painting",
    "Studio Ghibli-inspired aesthetic",
    "Dark Fantasy",
    "Cyberpunk",
    "Comic Book",
]


def get_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            key = ""
    return key or ""


@st.cache_resource
def get_gemini_client():
    api_key = get_api_key()
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def initialize_session_state():
    defaults = {
        "story_history": [],
        "gemini_chat": None,
        "current_story_scene": None,
        "current_options": [],
        "current_image": None,
        "current_audio": None,
        "selected_genre": GENRES[0],
        "selected_art_style": ART_STYLES[0],
        "story_started": False,
        "pending_choice": None,
        "scene_counter": 0,
        "last_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sanitize_markdown_fences(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def parse_story_response(response_text):
    cleaned = sanitize_markdown_fences(response_text or "")
    if not cleaned:
        raise ValueError("Empty response from Gemini.")
    data = json.loads(cleaned)
    story_text = data.get("story_text")
    image_prompt = data.get("image_prompt")
    options = data.get("options")
    if not story_text or not image_prompt or not isinstance(options, list):
        raise ValueError("Missing required JSON fields.")
    options = [str(option).strip() for option in options if str(option).strip()]
    if not (2 <= len(options) <= 3):
        raise ValueError("options must contain 2 to 3 choices.")
    return {
        "story_text": str(story_text).strip(),
        "image_prompt": str(image_prompt).strip(),
        "options": options,
    }


def build_previous_context():
    if not st.session_state.story_history:
        return "No previous story yet."
    lines = []
    for idx, scene in enumerate(st.session_state.story_history, start=1):
        choice = scene.get("selected_choice", "Story start")
        text = scene.get("story_text", "")
        lines.append(f"Scene {idx}: Choice={choice}. Story={text}")
    return "\n".join(lines[-8:])


def create_system_prompt():
    return f"""
You are a professional interactive fiction writer and visual-novel director.
Maintain continuity and remember prior events.
Never contradict established facts.
Make choices meaningful and distinct.
Keep characters consistent.
Create suspense and progression.
Avoid ending the story immediately.
Avoid repetitive choices.
Make each scene visually distinct.

Selected genre: {st.session_state.selected_genre}
Selected art style: {st.session_state.selected_art_style}

Previous story context:
{build_previous_context()}

Return ONLY valid JSON. Do not wrap the JSON in Markdown code fences. Do not add explanations before or after the JSON.

The JSON object must contain exactly these keys:
{{
  "story_text": "A narrative paragraph of about 100-180 words advancing the story.",
  "image_prompt": "A detailed prompt for Pollinations including subject, character appearance, pose, environment, time of day, lighting, atmosphere, camera angle, composition, color mood, and the selected art style. No text or subtitles.",
  "options": ["Choice 1", "Choice 2", "Choice 3"]
}}

The options list must contain 2 to 3 distinct choices that meaningfully change the next scene.
""".strip()


def get_story_client():
    client = get_gemini_client()
    if client is None:
        return None
    if st.session_state.gemini_chat is None:
        st.session_state.gemini_chat = client.chats.create(model="gemini-2.0-flash")
    return st.session_state.gemini_chat


def call_gemini_for_scene(choice_text=None):
    chat = get_story_client()
    if chat is None:
        raise RuntimeError("Missing Gemini API key.")

    prompt = create_system_prompt()
    if choice_text is None:
        user_message = (
            "Begin the story with a cinematic opening scene based on the selected genre "
            "and art style. Establish the setting, conflict, and 2-3 meaningful choices."
        )
    else:
        user_message = (
            f"The player chose: {choice_text}\n"
            "Continue the story from the current scene with strong continuity and new choices."
        )

    response = chat.send_message(f"{prompt}\n\nUser instruction:\n{user_message}")
    text = getattr(response, "text", "") or ""
    return parse_story_response(text)


def pollinations_image_url(prompt):
    return "https://image.pollinations.ai/prompt/" + requests.utils.quote(prompt, safe="")


def generate_image(image_prompt):
    try:
        url = pollinations_image_url(image_prompt)
        resp = requests.get(url, timeout=45)
        resp.raise_for_status()
        return resp.content
    except Exception:
        st.toast("Image server is busy, skipping visual...")
        return None


def generate_narration(text):
    try:
        tts = gTTS(text=text, lang="en")
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes.getvalue()
    except Exception:
        st.toast("Narration is temporarily unavailable.")
        return None


def make_scene(selected_choice=None):
    try:
        story = call_gemini_for_scene(selected_choice)
    except Exception as exc:
        st.session_state.last_error = str(exc)
        st.error("The story engine could not generate the next scene right now.")
        return None

    image_bytes = generate_image(story["image_prompt"])
    audio_bytes = generate_narration(story["story_text"])

    scene_number = len(st.session_state.story_history) + 1
    scene = {
        "scene_number": scene_number,
        "selected_choice": selected_choice or "Story start",
        "story_text": story["story_text"],
        "image_prompt": story["image_prompt"],
        "options": story["options"],
        "image": image_bytes,
        "audio": audio_bytes,
    }
    st.session_state.current_story_scene = scene
    st.session_state.current_options = story["options"]
    st.session_state.current_image = image_bytes
    st.session_state.current_audio = audio_bytes
    st.session_state.scene_counter = scene_number
    st.session_state.story_started = True
    st.session_state.story_history.append(scene)
    return scene


def start_story():
    if not get_api_key():
        st.warning("Add GEMINI_API_KEY to your environment or Streamlit secrets to start the story.")
        return
    if not st.session_state.story_started:
        make_scene(None)


def continue_story(choice_text):
    st.session_state.pending_choice = choice_text
    make_scene(choice_text)


def reset_story():
    st.session_state.story_history = []
    st.session_state.gemini_chat = None
    st.session_state.current_story_scene = None
    st.session_state.current_options = []
    st.session_state.current_image = None
    st.session_state.current_audio = None
    st.session_state.story_started = False
    st.session_state.pending_choice = None
    st.session_state.scene_counter = 0
    st.session_state.last_error = None
    st.rerun()


def render_css():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top, rgba(255,255,255,0.08), transparent 30%),
                linear-gradient(180deg, #0b0f1a 0%, #111827 50%, #05070d 100%);
            color: #f5f7fb;
        }
        .hero {
            padding: 2.2rem;
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(17,24,39,0.9), rgba(6,10,18,0.75));
            box-shadow: 0 25px 80px rgba(0,0,0,0.35);
        }
        .chapter-card {
            padding: 1.2rem 1.3rem;
            border-radius: 20px;
            background: rgba(15, 23, 42, 0.88);
            border: 1px solid rgba(148, 163, 184, 0.18);
            margin-bottom: 1rem;
        }
        .scene-label {
            letter-spacing: 0.22em;
            color: #93c5fd;
            font-size: 0.78rem;
            text-transform: uppercase;
        }
        .choice-box {
            padding: 1rem;
            border-radius: 16px;
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid rgba(96, 165, 250, 0.22);
        }
        .stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 0.8rem 1rem;
            border: 1px solid rgba(96, 165, 250, 0.25);
            background: linear-gradient(135deg, #1d4ed8, #7c3aed);
            color: white;
            font-weight: 700;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 35px rgba(59, 130, 246, 0.22);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_scene(scene):
    st.markdown(f"<div class='chapter-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='scene-label'>SCENE {scene['scene_number']:02d}</div>", unsafe_allow_html=True)
    st.subheader(f"Chapter {scene['scene_number']:02d}")

    col1, col2 = st.columns([1.15, 1])
    with col1:
        if scene.get("image"):
            st.image(scene["image"], use_container_width=True)
        else:
            st.info("🎨 Scene artwork temporarily unavailable.")
    with col2:
        st.markdown("### 📖 Story")
        st.write(scene["story_text"])
        st.markdown("### 🔊 Narration")
        if scene.get("audio"):
            st.audio(scene["audio"], format="audio/mp3")
        else:
            st.info("Narration not available for this scene.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_choice_buttons(options):
    st.markdown("### ⚔️ Your choices")
    st.markdown("<div class='choice-box'>", unsafe_allow_html=True)
    choice_cols = st.columns(min(len(options), 3))
    for i, option in enumerate(options):
        with choice_cols[i % len(choice_cols)]:
            if st.button(option, key=f"choice_{st.session_state.scene_counter}_{i}"):
                continue_story(option)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_welcome():
    st.markdown(
        """
        <div class="hero">
            <div class="scene-label">MULTI-MODAL VISUAL NOVEL</div>
            <h1>🎭 Visual Novel Engine</h1>
            <p style="font-size: 1.1rem; color: #dbeafe; max-width: 820px;">
                Your choices shape the story. Gemini writes the scene, Pollinations paints it, and gTTS gives it a voice.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    st.info(f"Genre: {st.session_state.selected_genre} | Art Style: {st.session_state.selected_art_style}")
    if st.button("✨ Begin Adventure", type="primary"):
        start_story()
        st.rerun()


def sidebar_controls():
    with st.sidebar:
        st.title("🎬 Story Settings")
        st.session_state.selected_genre = st.selectbox(
            "Story Genre", GENRES, index=GENRES.index(st.session_state.selected_genre)
        )
        st.session_state.selected_art_style = st.selectbox(
            "Art Style", ART_STYLES, index=ART_STYLES.index(st.session_state.selected_art_style)
        )
        if st.button("🔄 Restart Story"):
            reset_story()
        if not get_api_key():
            st.warning("GEMINI_API_KEY is missing.")


def main():
    initialize_session_state()
    render_css()
    sidebar_controls()

    st.markdown("## 🎭 Visual Novel Engine")
    st.caption("A stateful, multimodal choose-your-own-adventure built with Gemini, Pollinations, and gTTS.")

    if not st.session_state.story_started:
        render_welcome()
        return

    if st.session_state.story_history:
        for scene in st.session_state.story_history:
            render_scene(scene)
            if scene.get("options") and scene is st.session_state.story_history[-1]:
                render_choice_buttons(scene["options"])
    else:
        render_welcome()


if __name__ == "__main__":
    main()
