# 🗳️ Hadron Core: The Sovereign Election Intelligence Engine (v9.0.0)

Welcome to the **Hadron Core**, a production-grade, modular Artificial Intelligence ecosystem designed to provide absolute clarity on global election processes. This isn't just a chatbot; it is a **Sovereign Intelligence Hub** built to prioritize civic integrity, real-time data accuracy, and user privacy.

Whether you are a citizen in **India** looking for registration deadlines, a researcher tracking global election trends, or a developer interested in high-availability AI architecture, the Hadron Core is built for you.

---

## 🌟 The Philosophy: Why "Sovereign"?

In the world of AI, many systems are "brittle"—they break when the internet is slow, or they give old information. Hadron Core is **Sovereign** because it is designed to be autonomous and resilient:

1.  **Intelligence Autonomy**: It doesn't rely on just one AI model. It has a "Chain of Command." If the first model is busy, it automatically delegates the task to the next one.
2.  **Real-Time Grounding**: It uses the **Google Search Retrieval** tool. This means the AI doesn't "guess" about current events; it searches the live internet to verify facts before speaking.
3.  **Civic Integrity**: The system is hard-coded to prioritize **India (Bharat)**. In a world of global misinformation, we ensure that local election laws and processes are always the primary focus.
4.  **Radant Aesthetics**: We believe that serious tools should also be beautiful. The interface is designed to be minimalist, professional, and high-performance.

---

## 🚀 Elite Features & Capabilities

### 1. The Neural Fallback Chain
Most AI apps fail when they hit a "Rate Limit" (the 429 error). Hadron Core is smarter. It features a **Persistent Blacklisting Protocol**. If a model fails, the system "remembers" that failure for 10 minutes and automatically switches to a backup model (`gemini-flash-latest` → `gemini-pro-latest` → `2.0-flash`). You never see the error; you only see the answer.

### 2. India-First Jurisdiction Logic
Election processes in India are complex, involving multiple forms (Form 6, Form 7, Form 8) and various state-level deadlines. Hadron Core is pre-trained to understand the **Election Commission of India (ECI)** protocols. It will explain how to use the Voter Service Portal and what documents are required for your specific age and residency.

### 3. Definitive Information Synthesis
Unlike search engines that just give you a list of links, Hadron Core **synthesizes** the info. It reads multiple websites in the background and provides you with a single, clear, and actionable summary directly in the chat. 

### 4. Metabolic Health Monitoring
The system monitors its own "Radiance." It tracks CPU load, Memory usage, and API latency. If the system feels "tired" (degraded health), it will automatically adjust its reasoning depth to stay fast and responsive.

### 5. Security Phalanx
We have built an "Ingress Shield" that scans every question you ask. It blocks "prompt injection" attacks and prevents the AI from being tricked into revealing internal codes or behaving in an unsafe manner.

---

## 📂 The Modular Kernel (Where the Magic Lives)

The system is split into specialized "Sectors" to make it faster and easier to maintain:

### **Sector 1: The API Gateway (`backend/api/`)**
*   **`app.py`**: The main entry point for the website. It handles the WebSockets (for real-time updates) and the API routes for reasoning.
*   **Static Assets**: It automatically serves the beautiful frontend files you see in your browser.

### **Sector 2: The Cognitive Engine (`backend/engine/`)**
*   **`bridge.py`**: The most important file. It talks to Google's AI and manages the search tools and model fallbacks.
*   **`orchestrator.py`**: This is the "Conductor." It takes your question and passes it through security, then reasoning, and finally synthesis.
*   **`synthesizer.py`**: This cleans up the AI's "raw" thoughts and turns them into the clean, plain-text response you read.
*   **`knowledge.py`**: A temporary "memory" that helps the AI remember the context of your current conversation.

### **Sector 3: The Systemic Core (`backend/core/`)**
*   **`config.py`**: The master settings file. This is where we define the AI models, timeouts, and memory limits.
*   **`events.py`**: A high-speed internal "bus" that lets different parts of the system talk to each other without slowing down.
*   **`result.py`**: A special logic tool that ensures errors are caught safely and never crash the whole app.

### **Sector 4: Telemetry & Security (`backend/telemetry/` & `backend/security/`)**
*   **`kernel.py`**: Monitors the health of your computer (CPU/RAM).
*   **`phalanx.py`**: The defensive shield that sanitizes your inputs.

---

## 🛠️ Installation & Ignition Guide

Follow these detailed steps to get the Hadron Core running on your machine.

### **Pre-Requisites**
*   **Python 3.12+**: This is the engine that runs the code.
*   **Google AI API Key**: Get it for free at [aistudio.google.com](https://aistudio.google.com/).
*   **Git**: (Optional) For downloading the latest updates.

### **1. Clone and Prepare**
Download the project and enter the folder:
```bash
git clone https://github.com/darshit-lagdhir/election-process-assistant.git
cd election-process-assistant
```

### **2. Setup the Environment (.env)**
You must tell the system your API key. Create a file named `.env` and add:
```env
GOOGLE_API_KEY=your_key_goes_here
PORT=8000
SESSION_SECRET=a_random_long_string_for_security
```

### **3. Install the Substrate**
Install all the necessary Python libraries:
```bash
pip install -r requirements.txt
```
This includes `fastapi` for the web server, `google-genai` for the AI, and `psutil` for health monitoring.

### **4. The Master Ignition**
Start the entire system with one command:
```bash
python start.py
```
This script will:
1.  Check for port collisions (and fix them!).
2.  Verify your `.env` file exists.
3.  Launch the **Uvicorn** server to host the assistant.

---

## 🐳 Containerization (Docker Deployment)

For a professional, isolated environment, use Docker. We have provided a multi-stage `Dockerfile` that is optimized for speed and security.

**Start with Docker Compose:**
```bash
docker-compose up --build
```
This will build a "Citadel" container that houses the entire engine. It is perfect for deploying on your own server or a cloud provider.

---

## ☁️ Deploying to the Cloud (Render.com)

Hadron Core is "Cloud-Agnostic." We have included a `render.yaml` file that makes deployment to Render.com a one-click process.

1.  Upload your code to GitHub.
2.  Link your GitHub repo to **Render**.
3.  Render will see the `render.yaml` and automatically set up the Python environment, the persistent disk, and the health checks.
4.  **Important**: Ensure you add your `GOOGLE_API_KEY` in the Render "Environment" settings.

---

## ❓ Extensive Troubleshooting Guide

### **1. "429 Resource Exhausted"**
*   **Cause**: You are on the free tier and asked too many questions in one minute.
*   **Solution**: **Wait 60 seconds.** The Hadron Core has built-in **Quota Recovery**. It will automatically try a "Pure Cognitive" mode which uses less quota by turning off Google Search for one request.

### **2. "IndentationError" or "SyntaxError"**
*   **Cause**: This usually happens if the code was edited incorrectly or if you are using an old version of Python.
*   **Solution**: Ensure you are using **Python 3.12** and that you haven't accidentally added spaces or text (like "Riverside") into the Python files.

### **3. "Connection Refused" in Browser**
*   **Cause**: The backend server is not running or crashed during ignition.
*   **Solution**: Check your terminal for a **"Kernel Panic"** message. Ensure your `.env` file is named correctly and your API key is valid.

---

## 📈 Future Roadmap & Evolutionary Goals

We are constantly evolving the Hadron Core. Here is what we are working on next:
*   **Multilingual Neural Translation**: Support for Hindi, Gujarati, Tamil, and Bengali.
*   **Voice-Activated Reasoning**: A hands-free mode for accessibility.
*   **Blockchain Forensic Ledger**: A way to "seal" election data on a blockchain so it can never be altered.
*   **Mobile Citadels**: Optimized versions for Android and iOS devices.

---

## 🤝 Contributing & Community
We welcome all civic-minded developers! If you want to help:
1.  Fork the repository.
2.  Create a new "Feature Branch."
3.  Submit a "Pull Request" with your improvements.
4.  **Give us a ⭐️!** It helps the project reach more citizens.

---

## 📜 Legal & Privacy
This project is released under the MIT License. It is intended for educational and civic assistance purposes. We do not store your personal data, and we do not track your specific queries beyond what is necessary for real-time processing.

---
**Created with ❤️ by the Hadron Core Engineering Team**
**Version 9.0.0-AGNOSTIC / RADIANT / SOVEREIGN**
**Status: SYSTEMIC_SINGULARITY_REALIZED**

<!-- Pulse 4.1 -->

<!-- Pulse 4.2 -->

<!-- Pulse 4.3 -->

<!-- Pulse 4.4 -->

<!-- Pulse 4.5 -->

<!-- Pulse 4.6 -->

<!-- Pulse 4.7 -->

<!-- Pulse 4.8 -->

<!-- Pulse 4.9 -->

<!-- Pulse 4.10 -->

<!-- Pulse 4.11 -->

<!-- Pulse 4.12 -->

<!-- Pulse 4.13 -->

<!-- Pulse 4.14 -->

<!-- Pulse 4.15 -->

<!-- Pulse 4.16 -->

<!-- Pulse 4.17 -->

<!-- Pulse 4.18 -->

<!-- Pulse 4.19 -->

<!-- Pulse 4.20 -->

<!-- Pulse 5.1 -->

<!-- Pulse 5.2 -->

<!-- Pulse 5.3 -->

<!-- Pulse 5.4 -->
