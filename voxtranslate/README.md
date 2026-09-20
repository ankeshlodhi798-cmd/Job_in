# VoxTranslate AI

Deployment-ready MVP for AI transcription + translation + text-to-speech.

## Stack
- Frontend: responsive HTML/CSS/JavaScript
- Backend: Netlify Functions
- AI: OpenAI transcription, Responses API translation, speech generation
- Database: Supabase/Postgres
- Hosting: Netlify

## Deploy
1. Connect this repository to Netlify.
2. Set the site base directory to the repository root.
3. Build command: leave empty.
4. Publish directory: `voxtranslate`.
5. Functions directory: `voxtranslate/netlify/functions`.
6. Add the environment variables from `.env.example`.
7. In Supabase, run `supabase/schema.sql`.
8. Never put OPENAI_API_KEY or SUPABASE_SERVICE_ROLE_KEY in frontend JavaScript.

The app is an MVP foundation. For production scale, add authentication, rate limiting, upload-size limits, usage quotas, SRT/VTT export and a queue for long files.