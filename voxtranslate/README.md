# VoxTranslate AI — GitHub + FastAPI

AI transcription, translation and natural voice generation in one FastAPI application.

## Stack
- Frontend: HTML/CSS/JavaScript
- Backend: Python + FastAPI
- AI: OpenAI API
- Source control: GitHub
- Deployment option: Render (no Netlify required)

## Run locally

```bash
cd voxtranslate
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and add your OpenAI API key.

Start the server:

```bash
uvicorn main:app --reload --port 8000
```

Open `http://127.0.0.1:8000`.

## Production

GitHub stores the code; GitHub Pages cannot run the Python/FastAPI backend. Deploy this same repository/folder to a Python host such as Render and add `OPENAI_API_KEY` as a server-side environment variable.

Never put the OpenAI API key in `app.js` or any browser-visible file.

## API
- GET `/api/health`
- POST `/api/transcribe`
- POST `/api/translate`
- POST `/api/speak`

The default translation model is `gpt-5.6-luna`; change it with `OPENAI_TRANSLATE_MODEL` if needed.
