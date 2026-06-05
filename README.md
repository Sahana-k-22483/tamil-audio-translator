# Tamil Audio to English Translator

A web app that transcribes Tamil audio to text and translates it to English using the [Sarvam AI](https://www.sarvam.ai/) API.

## Features

- Upload Tamil audio files (MP3, WAV, WEBM, MP4, etc.)
- Record audio directly in the browser
- Auto-selects REST or Batch STT based on audio duration
- Translates Tamil transcript to English
- Session history (last 5 transcripts)
- Download or copy the English translation

## Usage

1. Get a free API key from [Sarvam AI](https://www.sarvam.ai/)
2. Open the app, enter your API key
3. Upload or record Tamil audio
4. Click **Transcribe and Translate**

## Run Locally

```bash
python3 server.py
```

Then open [http://localhost:8080](http://localhost:8080).

## Deploy on Render

1. Fork this repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your forked repo
4. Render will auto-detect `render.yaml` and deploy

## Tech Stack

- Vanilla HTML/CSS/JS (no frameworks)
- Python stdlib HTTP server (proxy for CORS)
- [Sarvam AI](https://www.sarvam.ai/) STT + Translate APIs
