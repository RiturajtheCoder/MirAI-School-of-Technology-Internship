# 🧠 Life-OS: AI Wellbeing Dashboard

> **MirAI School of Technology – Virtual Summer Internship 2026**
> **AI Builder Track Final Capstone Project**

---

## 🌟 Overview

**Life-OS** is an AI-powered digital wellbeing dashboard built with **Streamlit**, **Pandas**, and **Google Gemini AI**.

The application helps users visualize their daily screen time habits and receive personalized, actionable lifestyle coaching from Gemini. Rather than simply displaying statistics, Life-OS analyzes screen time behavior and recommends healthier real-world alternatives to improve productivity and wellbeing.

---

## 🚀 Live Demo

**Deployed Application:**

**👉 https://lifeosai.streamlit.app**

---

## 💻 GitHub Repository

**Repository:**

**👉 https://github.com/RiturajtheCoder/MirAI-School-of-Technology-Internship/tree/main/Assignment7**

---

# ✨ Features

## 📊 Screen Time Dashboard

* View daily screen time
* Filter by any day
* Professional SaaS-style dashboard
* Responsive Streamlit interface

---

## 📈 Data Visualizations

* Daily screen time trend
* Category-wise usage chart
* Interactive graphs
* 14-day synthetic dataset

---

## 📌 KPI Cards

Displays:

* 📱 Total screen time
* 🔥 Most used application
* 🎯 Difference from daily goal

---

## 🤖 Gemini AI Lifestyle Coach

Powered by **Google Gemini API**.

The AI:

* Analyzes screen time patterns
* Detects unhealthy habits
* Rewards productive behavior
* Suggests practical offline alternatives
* Gives a daily wellbeing score
* Provides a personalized challenge for the next day

---

## 🎭 Hidden Gem — AI Accountability Avatar

The dashboard dynamically generates an AI image based on your daily digital habits.

Examples:

* 🧟 Heavy phone usage → Lazy Zombie
* 😐 Average usage → Distracted Office Worker
* ⚔️ Healthy usage → Focused Warrior

Generated using the **Pollinations AI Image API**.

---

## 🔗 Shareable Accountability Link

The dashboard stores the day's screen time in the URL using Streamlit Query Parameters, making it easy to share daily progress with an accountability partner.

---

# 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* Google Gemini API (`google-genai`)
* Pollinations AI
* python-dotenv

---

# 📂 Project Structure

```text
Life-OS/
│
├── app.py
├── screentime.csv
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
```

---

# 📦 Installation

Clone the repository:

```bash
https://github.com/RiturajtheCoder/MirAI-School-of-Technology-Internship.git
```

Move into the project folder:

```bash
cd Assignment7
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Or, if deploying to Streamlit Community Cloud, add the key under **Secrets**.

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

---

# 📊 Dataset

The project uses a synthetic dataset containing:

* 14 days of screen time
* Multiple applications
* Usage categories
* Minutes spent per application

Columns:

| Column       | Description      |
| ------------ | ---------------- |
| Date         | Date of usage    |
| App_Name     | Application name |
| Category     | Usage category   |
| Minutes_Used | Minutes spent    |

---

# 📸 Screenshots

Add screenshots here after deployment.

Example:

```
screenshots/
├── dashboard.png
├── charts.png
├── ai_analysis.png
├── avatar.png
```

---

# 🎯 Learning Outcomes

This project demonstrates:

* Data visualization
* Streamlit UI development
* Prompt engineering
* AI API integration
* Dashboard design
* CSV data processing
* User experience design
* AI-assisted productivity analysis

---

# 📌 Future Improvements

* Voice journal using speech-to-text
* Weekly productivity reports
* Google Calendar integration
* Apple Screen Time API integration
* Android Digital Wellbeing integration
* User authentication
* Cloud database
* Historical AI reports
* Dark/Light mode
* Mobile optimization

---

# 👨‍💻 Author

**Rituraj Saha**
---

# 📄 License

This project was developed as part of the **MirAI School of Technology Virtual Summer Internship 2026** for educational and portfolio purposes.

---

## ⭐ If you found this project interesting, consider giving it a star on GitHub!
