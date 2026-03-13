# AvianQuest: Pocket Vet AI 🦜

AvianQuest is a cross-platform Proof of Concept (PoC) application designed to provide pre-ownership education for exotic bird care. This repository contains "Phase 1" of the project: an AI-powered conversational assistant built with Python and the Flet UI framework.

## Features
* **Modern UI:** A responsive, dark-theme interface built with Flet, utilizing custom navigation and markdown rendering.
* **Domain-Specific AI:** Powered by the Google Gemini 2.5 Flash model, strictly constrained to avian veterinary health.
* **Local Privacy:** All chat histories and session titles are stored locally using an SQLite database.
* **Real-Time Streaming:** Utilizes asynchronous processing to stream AI responses directly into the UI without freezing the app.

## Installation & Setup
To run this application on your own machine, you will need to provide your own free Google Gemini API key.

### 1. Clone the repository
`git clone https://github.com/YourUsername/AvianQuest.git`
`cd AvianQuest`

### 2. Install Dependencies
Ensure you have Python installed, then run:
`pip install -r requirements.txt`

### 3. Set up your API Key
* Get a free API key from Google AI Studio.
* In the root folder of this project, create a new file named exactly `.env`
* Add your API key to the file exactly like this (no quotes or spaces around the equals sign):
`GEMINI_API_KEY=your_api_key_here`

### 4. Run the application
`python main.py`