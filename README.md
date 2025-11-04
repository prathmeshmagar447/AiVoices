# 🎵 Kokoro TTS Bulk Generator

A powerful GUI application for bulk text-to-speech conversion using Kokoro-FastAPI with advanced features for professional audio production.

## ✨ Features

### 🎨 Modern Interface
- **CustomTkinter UI**: Beautiful dark/light themes with modern styling
- **macOS-Optimized**: Responsive sizing, centered windows, native transparency
- **Scrollable Interface**: Smooth mouse wheel and touchpad scrolling
- **Organized Sections**: Clean layout with grouped functionality and emojis

### 🎤 Advanced Voice Management
- **Multi-Voice Selection**: Interactive checkboxes for voice selection
- **Voice Combination**: Combine multiple voices (e.g., `af_bella+af_sky`)
- **Voice Preview**: 🔊 Listen to voice combinations before processing
- **Dynamic Voice List**: Auto-fetch voices from API server

### ⚡ High-Performance Processing
- **Concurrent Processing**: Configurable parallel requests (1-5 workers)
- **Real-time Progress**: Live progress bar with ETA calculation
- **Multiple Formats**: MP3, WAV, and FLAC output support
- **Smart Batching**: Efficient API call management

### 🛡️ Reliability & Error Handling
- **Retry Logic**: Exponential backoff for failed requests
- **Cancellation Support**: Stop processing mid-operation
- **Settings Persistence**: Remembers your preferences between sessions
- **Comprehensive Logging**: Both GUI and file logging with timestamps

### 📁 Professional Workflow
- **Folder Management**: Easy input/output folder selection
- **Batch Processing**: Handle hundreds of files efficiently
- **Status Tracking**: Detailed success/failure reporting
- **Non-blocking UI**: Responsive interface during processing

## 📋 Requirements

- Python 3.6+
- `requests` library
- `customtkinter` library
- Running Kokoro-FastAPI server
- System audio player (built-in on macOS/Linux/Windows)

## 🚀 Installation & Setup

1. **Install dependencies**:
   ```bash
   pip install requests customtkinter
   ```

2. **Run the app**:
   ```bash
   python kokoro_tts_gui.py
   ```

## 🎯 Usage Guide

### Initial Setup
1. **API Configuration**: Enter your Kokoro-FastAPI server URL
2. **Fetch Voices**: Click "Fetch Voices" to load available voice options
3. **Voice Selection**: Check boxes to select and combine voices
4. **Preview**: Click 🔊 Preview to test voice combinations

### Batch Processing
1. **Select Folders**: Choose input folder with `.txt` files and output destination
2. **Configure Options**: Set audio format and concurrent processing limit
3. **Start Generation**: Click "Start Generation" and monitor progress
4. **Cancel if Needed**: Use "Cancel" button to stop processing

### Advanced Features
- **Concurrent Control**: Adjust max concurrent requests based on server capacity
- **Format Selection**: Choose MP3 for web, WAV for editing, FLAC for archival
- **Progress Monitoring**: Watch real-time progress with estimated completion time

## 🎭 Voice Features

### Voice Combination
Select multiple voices using checkboxes. Combined voices use `+` syntax:
- Single voice: `af_bella`
- Combined voices: `af_bella+af_sky+am_adam`

### Voice Preview
Test voice combinations instantly with the preview feature:
- Generates sample audio: "Hello, this is a voice preview test."
- Plays automatically using system audio
- Helps verify voice quality before bulk processing

## 🔧 Technical Details

### API Integration
- **Endpoints Used**:
  - `GET /v1/audio/voices` - Fetch available voices
  - `POST /v1/audio/speech` - Generate speech audio
- **Error Handling**: Automatic retry with exponential backoff
- **Timeout Management**: 30-second timeouts with graceful failure

### Performance Optimization
- **Thread Pool**: Configurable concurrent processing
- **Memory Efficient**: Streaming downloads prevent memory issues
- **Smart Scheduling**: As-completed processing for optimal throughput

### Data Persistence
- **Settings File**: `~/.kokoro_tts_gui.json` stores user preferences
- **Log Files**: Timestamped logs in `~/kokoro_tts_logs/`
- **Session Recovery**: Remembers last used folders and settings

## 💡 Tips & Best Practices

- **Server Capacity**: Start with 2-3 concurrent requests, increase based on server performance
- **File Organization**: Use descriptive filenames for easy output identification
- **Voice Testing**: Always preview voice combinations before large batches
- **Resource Monitoring**: Watch server load during high-concurrency processing
- **Log Review**: Check logs for detailed processing statistics and error details

## 🐛 Troubleshooting

### Common Issues
- **No Voices Loaded**: Ensure Kokoro-FastAPI server is running and accessible
- **Preview Not Working**: Check system audio setup (afplay on macOS, aplay on Linux)
- **Slow Processing**: Reduce concurrent requests or check server performance
- **Memory Issues**: Process in smaller batches or increase system RAM

### Log Locations
- **Settings**: `~/.kokoro_tts_gui.json`
- **Logs**: `~/kokoro_tts_logs/` (timestamped files)
- **Temp Files**: Automatic cleanup of preview audio files

## 🔄 Version History

- **v1.0**: Basic tkinter interface with single voice support
- **v2.0**: Complete UI overhaul with CustomTkinter, multi-voice selection, concurrent processing, retry logic, settings persistence, and voice preview

---

**Ready to convert your text files to professional audio? Start the Kokoro TTS Bulk Generator today!** 🎵
