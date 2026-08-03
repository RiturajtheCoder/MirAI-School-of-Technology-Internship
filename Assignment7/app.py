import os
import json
import urllib.parse
from datetime import datetime

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Life-OS Dashboard",
    page_icon="🧠",
    layout="wide",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main{
    background:#0E1117;
}

.metric-card{
    padding:15px;
    border-radius:15px;
    background:#1C1F26;
}

.block-container{
    padding-top:1rem;
}

h1,h2,h3{
    color:white;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================

DATA_FILE = "Assignment7/screentime.csv"

df = pd.read_csv(DATA_FILE)

df["Date"] = pd.to_datetime(df["Date"])

dates = sorted(df["Date"].dt.date.unique())

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Controls")

selected_day = st.sidebar.selectbox(
    "Select Day",
    dates[::-1]
)

daily_goal = st.sidebar.slider(
    "Daily Screen Time Goal (Minutes)",
    60,
    720,
    240,
    30
)

# ============================================================
# FILTER DATA
# ============================================================

today_df = df[df["Date"].dt.date == selected_day]

# ============================================================
# KPIs
# ============================================================

total_today = int(today_df["Minutes_Used"].sum())

top_app = (
    today_df.groupby("App_Name")["Minutes_Used"]
    .sum()
    .idxmax()
)

delta = total_today - daily_goal

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "📱 Total Screen Time",
        f"{total_today} min"
    )

with col2:
    st.metric(
        "🔥 Most Used App",
        top_app
    )

with col3:
    st.metric(
        "🎯 Goal Difference",
        f"{delta:+} min",
        delta=f"{delta:+} min",
        delta_color="inverse"
    )

st.divider()

# ============================================================
# CHARTS
# ============================================================

left, right = st.columns(2)

with left:

    st.subheader("Daily Screen Time")

    daily_usage = (
        df.groupby("Date")["Minutes_Used"]
        .sum()
    )

    st.line_chart(daily_usage)

with right:

    st.subheader("Today's Category Usage")

    category_usage = (
        today_df.groupby("Category")["Minutes_Used"]
        .sum()
    )

    st.bar_chart(category_usage)

st.divider()

# ============================================================
# APP TABLE
# ============================================================

st.subheader("Today's App Usage")

st.dataframe(
    today_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ============================================================
# DATA BRIDGE FOR GEMINI
# ============================================================

def summarize_data(dataframe):

    summary = (
        dataframe.groupby("Category")["Minutes_Used"]
        .sum()
        .sort_values(ascending=False)
    )

    return summary.to_string()


summary_string = summarize_data(today_df)

# ============================================================
# GEMINI
# ============================================================

st.header("🧠 AI Lifestyle Coach")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:

    st.warning(
        "GEMINI_API_KEY not found.\n\n"
        "Create a .env file or add it in Streamlit Secrets."
    )

else:

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are Life-OS.

You are NOT a motivational speaker.

You are an honest,
brutally fair,
yet caring productivity coach.

The user's screen-time summary is:

{summary_string}

Today's total screen time:
{total_today} minutes

Daily goal:
{daily_goal} minutes

Instructions:

1. Analyze every category.

2. Identify unhealthy behaviour.

3. Explain WHY it is harmful.

4. Suggest REAL physical replacements.

Examples:

Instead of doomscrolling:
- Go outside for a walk
- Meal prep
- Read 30 pages
- Stretch
- Gym
- Call family
- Meditate

If coding time is high,
praise it.

If education time is high,
encourage it.

If entertainment is excessive,
recommend limits.

If social media exceeds 2 hours,
be strict.

Return markdown.

Structure:

# Daily Score

Score /100

## What's Good

...

## Biggest Problems

...

## Your Mission Tomorrow

...

## One Challenge

...

End with one memorable quote.
"""

    if st.button("Generate AI Analysis"):

        with st.spinner("Analyzing your habits..."):

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

                advice = response.text

                if total_today <= daily_goal:

                    st.success(advice)

                elif total_today <= daily_goal + 90:

                    st.info(advice)

                else:

                    st.warning(advice)

            except Exception as e:

                st.error(e)

st.divider()

# ============================================================
# HIDDEN GEM
# GUILT-TRIP AVATAR
# ============================================================

st.header("🎭 Today's Avatar")

if total_today > daily_goal + 120:

    avatar_prompt = (
        "a lazy zombie staring at a glowing smartphone, "
        "dark room, exhausted eyes, cinematic, digital art"
    )

elif total_today > daily_goal:

    avatar_prompt = (
        "a distracted office worker surrounded by phone notifications, "
        "semi realistic digital art"
    )

else:

    avatar_prompt = (
        "a focused warrior studying peacefully, sunlight, books, "
        "healthy lifestyle, inspirational digital art"
    )

image_url = (
    "https://image.pollinations.ai/prompt/"
    + urllib.parse.quote(avatar_prompt)
)

st.image(
    image_url,
    use_container_width=True,
    caption="AI Generated Accountability Avatar"
)

st.divider()

# ============================================================
# SHAREABLE ACCOUNTABILITY LINK
# ============================================================

st.header("🔗 Accountability Link")

st.query_params["screen_time"] = str(total_today)

share_url = (
    f"?screen_time={total_today}"
)

st.code(share_url)

st.caption(
    "Send this link to your accountability partner."
)

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
"""
### Life-OS Dashboard

Built with ❤️ using

- Streamlit
- Pandas
- Google Gemini
- AI Productivity Coaching
"""
)
