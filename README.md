# 🗳️ Hadron Core: The Sovereign Election Assistant (v9.0.0)

Welcome to the **Hadron Core**! This is a state-of-the-art, super-smart Artificial Intelligence (AI) designed to be your personal expert on everything related to elections. Whether you want to know how to register in **India**, who the candidates are in the **USA**, or what happened in past elections, Hadron Core has the answer.

We have built this system to be **Fast**, **Beautiful**, and **Extremely Smart**.

---

## 🌟 What makes Hadron Core special?

Hadron Core is not just a chatbot. It is a "Sovereign Intelligence Engine." Here is what that means in simple words:

1.  **It Thinks for Itself**: It uses the most advanced Google Gemini models (`flash-latest` and `pro-latest`) to understand your questions.
2.  **It Searches the Real World**: Unlike other AI that only knows old data, Hadron Core can search the actual internet using **Google Search** to find news from *right now*.
3.  **It Never Gives Up**: If one AI model is busy or hits a limit (like the "429 error"), it automatically switches to another model in a split second. You won't even notice!
4.  **India-First Focus**: We have specially tuned the brain of this assistant to prioritize **Indian elections** (Bharat). It knows about the Voters Service Portal, Form 6, and local deadlines.
5.  **Plain Talk**: It doesn't use confusing "AI code" or formatting. It talks to you like a normal, helpful human being.

---

## 🚀 Key Features you will love

*   **Real-Time Extraction**: Ask "Who is the current Chief Minister of Gujarat?" or "What are the latest election dates in 2026?" and it will find the answer instantly.
*   **No Markdown Mess**: We have removed all the confusing bolding and symbols. You get clean, easy-to-read text.
*   **One-Command Start**: You don't need to be a coder to run this. One command starts the whole system.
*   **Privacy First**: Your chats are processed in real-time and are not saved in any database. Your secrets are safe.
*   **Beautiful UI**: A "Minimalist Dark Mode" interface that feels premium and is easy on the eyes.

---

## 📂 Understanding the Folders (The Modular Kernel)

We have organized the code into small "modules" so it runs better:

*   **`backend/api/`**: The "Gatekeeper." This handles the connection between the website and the AI.
*   **`backend/engine/`**: The "Brain." This is where the AI reasoning and Google Search tools live.
*   **`backend/core/`**: The "Skeleton." This handles the settings, errors, and system events.
*   **`backend/security/`**: The "Shield." This protects the system from bad inputs or hackers.
*   **`frontend/`**: The "Face." This contains the HTML, CSS, and Javascript that you see in your browser.
*   **`start.py`**: The "Key." This is the only file you need to run to start the engine.

---

## 📥 How to Install and Start (The Easy Way)

Follow these steps to get your own Hadron Core running in minutes!

### **Step 1: Get the Tools**
You need two simple things on your computer:
1.  **Python 3.12**: [Download it here](https://www.python.org/downloads/). (Make sure to check the box that says "Add to PATH").
2.  **A Text Editor**: Like [VS Code](https://code.visualstudio.com/).

### **Step 2: Get your AI Key**
To talk to the Google AI, you need a free API Key:
1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Click "Get API Key" and copy it.

### **Step 3: Setup your Secret File**
1.  In the project folder, look for `.env.example`.
2.  Rename it to exactly `.env`.
3.  Open it and paste your key like this:
    ```env
    GOOGLE_API_KEY=your_actual_key_here
    ```

### **Step 4: Install Dependencies**
Open your terminal (PowerShell or Command Prompt) in the project folder and type:
```bash
pip install -r requirements.txt
```

### **Step 5: The Master Ignition!**
To start the engine, just type:
```bash
python start.py
```
Wait for the message: **"INFO: Uvicorn running on http://0.0.0.0:8000"**.

### **Step 6: Open the Assistant**
Go to your browser (Chrome or Edge) and type:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🐳 Running with Docker (For Pros)

If you have Docker installed, you can skip all the steps above and just run:
```bash
docker-compose up --build
```
The system is already configured to work perfectly inside a container.

---

## ☁️ Deploying to the Cloud (Render.com)

Hadron Core is fully compatible with **Render.com**. 
1.  Connect your GitHub repo to Render.
2.  Select "Web Service."
3.  Render will automatically use the `render.yaml` blueprint I have created for you.
4.  Add your `GOOGLE_API_KEY` in the Render environment settings.

---

## ❓ Troubleshooting (If things go wrong)

*   **"No module named backend.api"**: Make sure you are running `python start.py` from the main project folder, not from inside the `backend` folder.
*   **"429 Resource Exhausted"**: This means you have used your free AI limit for this minute. **Just wait 60 seconds.** The system will automatically try to use a "Pure Cognitive" mode (no search) to save your quota.
*   **"Port 8000 already in use"**: The `start.py` script usually fixes this for you automatically! If not, just close your other terminal windows.

---

## 📈 Future Goals

*   [ ] **Voice Support**: Speak to the assistant like Siri or Alexa.
*   [ ] **Regional Languages**: Hindi, Gujarati, Tamil, and more.
*   [ ] **Mobile App**: A dedicated app for Android and iOS.

---

## 🤝 Support the Project
If you find this helpful, please give the repository a ⭐️ on GitHub. It helps more people find this civic tool!

---
**Created with ❤️ by the Hadron Core Team**
**Version 9.0.0-AGNOSTIC / RADIANT / SOVEREIGN**
