# YouTube Demucs Separation Service

This Flask app runs on an AWS GPU instance. It accepts a YouTube video ID, downloads the video, separates it into original, karaoke (instrumental), and vocals using Demucs at 32kHz, and returns MP3 files for each.

## Endpoints

- `POST /separate` with JSON `{ "video_id": "<id>" }` returns download links or files for original, karaoke, and vocals.

## Requirements
- Python 3.8+
- GPU-enabled AWS instance (CUDA)
- See requirements.txt for dependencies

## Quickstart

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Run the app:
   ```
   python app.py
   ```
3. POST to `http://<host>:5000/separate` with a YouTube video ID.

## Notes
- Demucs will use GPU if available.
- Output files are 32kHz MP3s.
- For production, use a WSGI server (e.g., gunicorn).
