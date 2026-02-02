# R.E.X. (Realtime Experience & Execution) V2

**Advanced System Intelligence, Reimagined.**

![R.E.X. V2 Banner](https://via.placeholder.com/1200x400/0a0a0a/00eeff?text=R.E.X.+V2+-+Advanced+System+Intelligence)

> **"A digital extension of your will."**

R.E.X. V2 is a cutting-edge, multimodal AI assistant designed to transcend simple chatbots. It is a full-system agent capable of seeing your screen, hearing your voice, controlling your operating system, managing your smart home, and extending its reach to the physical world via a dedicated mobile companion app. Built on the Gemini 2.0 Multimodal Live API, R.E.X. offers industry-leading low latency, "barge-in" interruptibility, and deep contextual awareness.

---

## 🚀 Key Features

### 🧠 Core Intelligence (Gemini 2.0 Flash)
At the heart of R.E.X. is the Gemini 2.0 model, enabling:
*   **Multimodal Perception:** R.E.X. sees what you see (screen sharing) and hears what you hear (system audio & mic) in real-time.
*   **Zero-Latency Interaction:** Conversational turns are instantaneous. No "processing..." delays.
*   **Barge-In Capable:** Interrupt R.E.X. mid-sentence naturally, just like speaking to a human.

### 🌐 Holographic UI V2
A stunning, sci-fi inspired interface built with **Electron + React**.
*   **Glassmorphism Design:** Translucent, blurred windows that float above your desktop.
*   **Reactive Visualizer:** A central "Orb" that pulses and reacts to voice and system status.
*   **Scanline Aesthetics:** Retro-futuristic visual effects that make the AI feel "alive."

### 📱 R.E.X. Companion App (Flutter)
Extend R.E.X. beyond your desk with the custom Android Companion App.
*   **Two-Way Voice Streaming:** Talk to R.E.X. from anywhere in your house via your phone.
*   **Mobile Vision ("Eye"):** Stream your phone's camera to R.E.X. to show it objects in the real world ("What is this part?").
*   **Remote Control:** Launch desktop apps, control media, and manage system volume from your phone.
*   **File Beam:** Instantly transfer files between your phone and desktop with a gesture.
*   **Contact Sync & Messaging:** Ask R.E.X. to "Text John on WhatsApp" using your phone's native capabilities.

### 🏠 Physical World Agency
R.E.X. isn't stuck in the box.
*   **Smart Home Control:** Native integration with **TP-Link Kasa** devices. Control lights, plugs, and scenes ("Turn the studio lights to blue").
*   **3D Printing Overseer:** Integration with **OctoPrint/Moonraker**. R.E.X. can slice STL files, start prints, and monitor progress ("Check on the print").
*   **Hardware Control:** Manage PC volume, brightness, or even lock the workstation on command.

### 🕵️ Web Intelligence
*   **Autonomous Web Agents:** R.E.X. can navigate websites to perform complex tasks.
*   **Smart Search:** Intelligently queries Google, Reddit, or GitHub based on your intent.
*   **Data Scraping:** Extract structured data (e.g., "Find all manufacturing companies in Chicago") into Excel/CSV.

### 🧬 Self-Evolution
Experimental "Evolution Agent" capability allows R.E.X. to:
*   **Detect Gaps:** Realize when it cannot perform a requested task.
*   **Self-Patch:** Research the necessary Python libraries and write its own tools (`tools.py`) to acquire new skills dynamically.

---

## 🛠️ Installation & Setup

### Prerequisites
*   **OS:** Windows 10/11
*   **Python:** 3.10+
*   **Node.js:** v18+
*   **Android SDK:** (For mobile app build)
*   **Gemini API Key:** [Get here](https://aistudio.google.com/)

### 1. Backend Setup (The "Brain")
```bash
# Clone the repository
git clone https://github.com/RushabhMakim3880/Assistant-Rex-V2.git
cd Assistant-Rex-V2

# Create Virtual Environment
python -m venv venv
.\venv\Scripts\activate

# Install Python Dependencies
pip install -r requirements.txt

# Configure Environment
# Rename .env.example to .env and add your GEMINI_API_KEY
```

### 2. Frontend Setup (The "Face")
```bash
# Install Node Dependencies
npm install

# Start the Application (Backend + Frontend)
npm run dev
```

### 3. Mobile Companion Setup (The "Hand")
```bash
cd rex_companion

# Install Flutter Dependencies
flutter pub get

# Connect Android Device via USB (Ensure USB Debugging is ON)
flutter run --release
```
*Note: Ensure your phone and PC are on the same Wi-Fi network initially for discovery.*

---

## 📖 Usage Scenarios

### Scenario 1: The "Iron Man" Workflow
> **User:** "R.E.X., look at this CAD model on my screen. It looks weak."
>
> **R.E.X. (Viewing Screen):** "I see the stress point on the bracket arm. Shall I run a simulation or suggest a reinforcement rib?"
>
> **User:** "Suggest a rib."
>
> **R.E.X.:** *Generates a new STL file and displays it via the Holographic CAD Viewer.* "Here is a reinforced design. sending it to the printer?"

### Scenario 2: The Remote Assistant
> **User (In Kitchen, via Phone):** "R.E.X., I'm out of milk. Add it to my list."
>
> **R.E.X.:** "Added. By the way, your 3D print just finished successfully."
>
> **User:** "Great. Turn off the studio lights."
>
> **R.E.X.:** *Dims studio lights via Kasa integration.* "Done."

### Scenario 3: Research Automation
> **User:** "Research the top 5 competitors for 'AI Glass' and save it to an Excel sheet."
>
> **R.E.X.:** *Deploys Web Scraper Agent.* "Scanning... compiling data... Done. I've saved `competitors.xlsx` to your desktop and opened it for you."

---

## 🏗️ Architecture

The system follows a modular "Brain-Body-Limb" architecture:

*   **Brain (Backend):** Python/FastAPI server handling Gemini Live API sessions, tool dispatch, and audio processing (`rex_core.py`, `server.py`).
*   **Body (Frontend):** Electron/React application providing the visual interface, system tray presence, and local media handling.
*   **Limb (Mobile):** Flutter application serving as a remote sensory extension and controller (`rex_companion`).

Communication is handled via **Socket.IO** for low-latency, bidirectional event streaming.

---

## 🔮 Roadmap

*   [ ] **Hybrid Local/Cloud:** Fallback to local LLM (Llama 3) when offline.
*   [ ] **Memory V2:** Vector database for long-term recall of user preferences and project history.
*   [ ] **Vision Automation:** "Watch" the screen and auto-trigger macros based on visual events (e.g., finish notification).
*   [ ] **Headless Pi Mode:** Run the backend on a Raspberry Pi for 24/7 availability.

---

**Created by Rushabh Makim.**
*Powered by Google Gemini.*
