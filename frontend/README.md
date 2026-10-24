# ASDL frontend

React with JavaScript, powered by Vite.

## Local setup

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Vite serves the app at `http://localhost:5173`. Set `VITE_API_BASE_URL` in `.env` to point at the FastAPI API base (default: `http://localhost:8000/api/v1`).

Build a production bundle with `npm run build`; preview it with `npm run preview`.
