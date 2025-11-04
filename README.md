# 🎵 Kokoro TTS Bulk Generator

A simple GUI app to convert multiple text files to speech using Kokoro-FastAPI.

## ✨ Features

- 🖥️ Clean tkinter GUI
- 🎤 Voice fetching and selection
- 🔄 Voice combination support
- 📁 Bulk folder processing
- 📊 Real-time progress logging
- 🎵 MP3 output format

## 📋 Requirements

- Python 3.6+
- `requests` library
- Running Kokoro-FastAPI server

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install requests
   ```

2. **Run the app**:
   ```bash
   python kokoro_tts_gui.py
   ```

3. **Configure**:
   - Enter API URL (default: `http://localhost:8880/v1`)
   - Fetch voices
   - Select input/output folders
   - Choose voice and generate!

## 🎭 Voice Combination

Combine voices by entering: `voice1+voice2` (e.g., `af_bella+af_sky`)

## 🔧 API Endpoints

- `GET /v1/audio/voices` - List voices
- `POST /v1/audio/speech` - Generate audio

## 💡 Tips

- Ensure Kokoro-FastAPI server is running
- Input folder should contain `.txt` files
- Output defaults to input folder if not specified
- Progress shown in GUI log area
