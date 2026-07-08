# 🛰️ The Identity Echo Interface

A simple Streamlit web application developed as part of the **MirAI School of Technology – Virtual Summer Internship 2026 (AI Builder Track)**.

This project demonstrates the fundamentals of building an interactive web interface using Streamlit, including user input collection, conditional logic, and dynamic output generation.

---

## 📌 Features

- Interactive Streamlit interface
- User Name input field
- Message input field
- "Transmit" button to process user input
- Input validation with:
  - ❌ Error for empty name
  - ⚠️ Warning for empty message
- Personalized success message using Python f-strings
- AI Token Cost Estimator (Advanced Challenge)

---

## 🛠️ Technologies Used

- Python 3
- Streamlit

---

## 📂 Project Structure

```
Assignment 1/
│── app.py
│── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/MSOT-Assignment-1.git
```

### 2. Navigate to the project directory

```bash
cd MSOT-Assignment-1
```

### 3. Install Streamlit

```bash
pip install streamlit
```

### 4. Run the application

```bash
streamlit run app.py
```

---

## 📸 Application Workflow

1. Enter your **Name**.
2. Enter your **Message**.
3. Click the **Transmit** button.
4. The application validates the input.
5. If both fields are valid:
   - Displays a personalized success message.
   - Estimates the number of AI tokens required based on the message length.
   - Displays the estimated token consumption.

---

## 🧠 Token Cost Estimator

The application estimates token usage using the common heuristic:

```
1 Token ≈ 4 Characters
```

Estimated Tokens:

```
Total Characters / 4
```

The estimated token count is displayed using Streamlit's `st.info()` component.

---

## 🎯 Assignment Objectives

This project fulfills the following requirements:

- ✅ Streamlit UI Shell
- ✅ Multi-Data Collection
- ✅ Action Gate using Button
- ✅ Conditional Routing
- ✅ Formatted Output using f-strings
- ✅ Advanced Challenge – Token Cost Estimator

---

## 👨‍💻 Author

**Rituraj Saha**

B.Tech Computer Science & Engineering

MirAI School of Technology – Virtual Summer Internship 2026

---

## 📄 License

This project is created for educational purposes as part of the MirAI School of Technology Virtual Summer Internship 2026.