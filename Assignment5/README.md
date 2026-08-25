# Visual Novel Engine

Multi-Modal Visual Novel Engine is a Streamlit-based interactive fiction project that combines Gemini for stateful story generation, Pollinations for scene artwork, and gTTS for browser-playable narration.

## Features

- Cinematic Streamlit UI with a dark visual-novel theme
- Sidebar story settings for genre and art style
- Stateful Gemini chat preserved in `st.session_state`
- Structured JSON responses with `story_text`, `image_prompt`, and `options`
- Dynamic choice buttons generated from AI output
- Pollinations image generation from AI-engineered prompts
- gTTS narration rendered with `st.audio()`
- Persistent story history across reruns
- Graceful failure handling for API and parsing errors

## Architecture

The app follows a simple multi-modal pipeline:

1. Gemini generates the next scene as JSON.
2. Python parses the JSON with `json.loads()`.
3. The UI renders the scene text, artwork, and narration.
4. The choice list becomes dynamic Streamlit buttons.
5. The selected choice is sent back into Gemini chat history.

## Gemini Integration

The app uses the modern Google GenAI SDK:

```python
from google import genai
```

The client is created with `@st.cache_resource` and reads `GEMINI_API_KEY` from environment variables or Streamlit secrets.

## Structured JSON Generation

Gemini is instructed to return only valid JSON with three keys:

- `story_text`
- `image_prompt`
- `options`

This keeps the model output machine-readable and makes the UI truly interactive.

## JSON Parsing

The app strips accidental Markdown code fences and parses the response with Python’s built-in `json` module. If the JSON is invalid or missing required fields, the app shows a friendly error instead of a traceback.

## Dynamic UI Generation

Choice buttons are rendered from the `options` array using a loop. If Gemini returns two options, the app renders two buttons. If it returns three, the app renders three. The clicked option becomes the next user move.

## Pollinations Image Generation

The `image_prompt` is sent to the Pollinations image endpoint, then the generated image is downloaded with `requests` and displayed with `st.image()`. If image generation fails, the app shows a toast and continues the story.

## TTS Narration

The `gTTS` library converts each scene’s story text into MP3 narration. The result is played directly in the browser using `st.audio()`. Narration is generated once per scene and stored in session state.

## Session State

The app uses `st.session_state` to persist:

- story history
- Gemini chat object
- current scene
- current options
- current image
- current audio
- selected genre
- selected art style
- story start status

This is what keeps the novel visible and coherent across Streamlit reruns.

## Error Handling

The app handles:

- missing API keys
- Gemini API failures
- invalid JSON
- Pollinations failures
- image download failures
- gTTS failures
- empty responses
- network issues

It avoids exposing raw tracebacks to the user.

## Installation

```bash
pip install -r requirements.txt
```

## API Configuration

Create a local `.env` file from `.env.example`:

```bash
GEMINI_API_KEY=your_real_key_here
```

Or set `GEMINI_API_KEY` in Streamlit Cloud secrets.

## Running Locally

```bash
streamlit run app.py
```

## Example User Flow

1. Open the app and review the genre and art style.
2. Click `Begin Adventure`.
3. Gemini returns a JSON scene.
4. The app shows the image, narration, and dynamic choices.
5. Click a choice to continue the story.
6. The previous scenes remain visible in chronological order.

## Future Improvements

- Scene bookmarking
- Saving and loading story saves
- Character sheets
- Branch map visualization
- Voice selection for narration
- Better image caching for repeated scene views
