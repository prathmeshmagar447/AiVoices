# Kokoro TTS Bulk Generator

A Python GUI application for bulk text-to-speech generation using Kokoro-FastAPI. This tool allows you to convert multiple text files (.txt) to audio files (MP3) using the Kokoro TTS model through a FastAPI server.

## Features

- **GUI Interface**: User-friendly tkinter-based interface
- **Voice Management**: Fetch and select from available voices via API
- **Voice Combination**: Support for combining multiple voices (e.g., "af_bella+af_sky")
- **Bulk Processing**: Process entire folders of text files
- **Progress Logging**: Real-time progress updates in the GUI
- **Flexible Output**: Choose custom output directories

## Requirements

- Python 3.6+
- `tkinter` (usually included with Python)
- `requests` library
- Kokoro-FastAPI server running and accessible

## Installation

1. Clone or download this repository
2. Install required Python packages:
   ```bash
   pip install requests
   ```
3. Ensure Kokoro-FastAPI server is running (see server documentation for setup)

## Usage

1. **Start the Application**:
   ```bash
   python kokoro_tts_gui.py
   ```

2. **Configure API**:
   - Enter the API base URL (default: `http://localhost:8880/v1`)
   - Click "Fetch Voices" to load available voices

3. **Select Voice**:
   - Choose a voice from the dropdown
   - For voice combination, manually enter combined voices (e.g., `af_bella+af_sky`)

4. **Choose Folders**:
   - Select input folder containing `.txt` files
   - Choose output folder (optional - defaults to input folder)

5. **Generate Audio**:
   - Click "Start Generation"
   - Monitor progress in the log area
   - Audio files will be saved as MP3 with the same name as input files

## API Endpoints Used

- `GET /v1/audio/voices` - Fetch available voices
- `POST /v1/audio/speech` - Generate speech from text

## Voice Combination

To combine voices, enter multiple voice names separated by `+` in the voice selection field. For example:
- `af_bella+af_sky`
- `am_adam+af_heart`

## Notes

- The application processes files in the background using threading to keep the UI responsive
- Empty text files are automatically skipped
- Error handling includes network issues and invalid API responses
- Output files are saved in MP3 format

## Troubleshooting

- Ensure Kokoro-FastAPI server is running and accessible
- Check API base URL is correct
- Verify input folder contains valid `.txt` files
- Check network connectivity for API calls

## License

This project is open source. Please refer to Kokoro-FastAPI documentation for server licensing.
