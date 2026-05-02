# 🗳️ Hadron Core: Your Smart Election Assistant

Welcome to **Hadron Core**! This is a very smart computer program (AI) made to help you understand elections easily. It is like having a personal expert who knows everything about voting, candidates, and election rules, specifically for **India** and the whole world!

---

## 🌟 What is Hadron Core?

Hadron Core is not just a simple chatbot. It is a "Sovereign Intelligence Hub." That sounds fancy, but it just means:
*   **It is very smart**: It uses the latest Gemini AI models from Google.
*   **It is always up-to-date**: It can search the real internet (Google Search) to find news from *today*.
*   **It is easy to use**: No complex buttons. Just type your question and get an answer.
*   **It looks beautiful**: We made a custom "Minimalist" design that is clean and professional.

---

## 🚀 Amazing Features

1.  **Real-Time News**: Ask "Who is winning the election today?" and it will search the web to tell you the latest news.
2.  **India-First**: While it knows the whole world, it is specially trained to help people in India with registration, parties, and voting dates.
3.  **Elite AI Conduits**: It automatically switches between different AI models if one is busy. This means it almost never stops working!
4.  **Verified Sources**: Every time it gives you a big answer, it checks multiple sources to make sure the information is correct.
5.  **Quick Actions**: Don't want to type? Just click on "Registration" or "Candidates" to get instant info.

---

## 🛠️ What is under the hood? (Tech Stack)

We used simple but powerful tools to build this:
*   **Backend**: Python with FastAPI (This is the brain that talks to the AI).
*   **Frontend**: Clean HTML, CSS, and Javascript (This is what you see and click on).
*   **AI Engine**: Google Gemini (The newest versions like 2.5 and 3.1).
*   **Database**: None! It's all real-time, so it doesn't store your private data.

---

## 📥 How to Install and Start (Step-by-Step)

Follow these easy steps to get Hadron Core running on your own computer.

### **Step 1: Things you need first**
Make sure you have these two things on your computer:
1.  **Python**: [Download it here](https://www.python.org/downloads/). (Version 3.10 or higher is best).
2.  **A Text Editor**: Like [VS Code](https://code.visualstudio.com/).

### **Step 2: Get your Google AI Key**
To talk to the AI, you need a secret key. 
1.  Go to the [Google AI Studio](https://aistudio.google.com/).
2.  Click on "Get API Key".
3.  Copy that key. Keep it safe!

### **Step 3: Download the Project**
1.  Download this project as a ZIP file and extract it.
2.  OR, if you know Git, run this:
    ```bash
    git clone https://github.com/darshit-lagdhir/election-process-assistant.git
    ```

### **Step 4: Setting up the "Environment"**
Computers need to know your API key. 
1.  Look for a file named `.env.example` in the main folder.
2.  Rename it to just `.env`.
3.  Open the `.env` file and paste your key like this:
    ```env
    GOOGLE_API_KEY=your_key_here
    ```

### **Step 5: Install the Requirements**
Open your terminal (Command Prompt or PowerShell) in the project folder and type:
```bash
pip install -r requirements.txt
```
This tells your computer to download all the extra tools needed to run the AI.

### **Step 6: Start the Magic!**
Now, type this in your terminal:
```bash
python backend/main.py
```
You will see a message saying "Uvicorn running on http://0.0.0.0:8000".

### **Step 7: Open your Browser**
Go to your internet browser (Chrome, Edge, or Brave) and type this in the address bar:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🐳 Running with Docker (Advanced)

If you have **Docker** installed, you can start everything with just one command!
```bash
docker-compose up --build
```
This is great if you don't want to install Python manually.

---

## 📂 Project Structure

Here is what the folders do:
*   `backend/`: This is where the Python code lives.
*   `frontend/`: This is where the website files (HTML/CSS) are.
*   `data/`: (Wait, we deleted this! The AI is now so smart it doesn't need old data files anymore).
*   `logs/`: If something goes wrong, look here to see the errors.

---

## ❓ Common Problems (Troubleshooting)

**1. "ModuleNotFoundError"**
*   **Fix**: You forgot Step 5! Run `pip install -r requirements.txt` again.

**2. "429 Rate Limit" Error**
*   **Fix**: This means the AI is tired. Wait for 1 minute and try again. The AI will automatically try to switch to a different model for you.

**3. "API Key Not Found"**
*   **Fix**: Check your `.env` file. Make sure it is named exactly `.env` and not `.env.txt`.

---

## 🛡️ Privacy & Security

We care about your privacy. Hadron Core:
*   Does **not** save your chat history in a database.
*   Does **not** sell your data.
*   Uses a "Sovereign Architecture," meaning the AI reasoning is filtered and safe.

---

## 📈 Future Roadmap

*   [ ] Add voice support so you can talk to the AI.
*   [ ] Add support for more Indian regional languages (Hindi, Gujarati, etc.).
*   [ ] Create a mobile app version.

---

## 🤝 How to Help
If you like this project, give it a ⭐️ on GitHub! If you find a bug, please tell us.

---

## 📜 License
This project is made for the community. You can use it, change it, and share it!

---
**Created with ❤️ by Hadron Core Team**
**Version 7.0.0-SOVEREIGN**
