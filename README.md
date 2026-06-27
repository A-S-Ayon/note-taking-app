# 📓 NoteVault — FastAPI + Supabase + Streamlit

A full-stack note-taking web app with JWT authentication and per-user private notes.

---

## Stack

| Layer    | Tech                         |
|----------|------------------------------|
| Backend  | FastAPI + python-jose (JWT)  |
| Database | Supabase (PostgreSQL)        |
| Frontend | Streamlit                    |
| Auth     | bcrypt passwords + JWT       |

---

## Project Structure

```
notetaking-app/
├── main.py          # FastAPI backend (auth + notes CRUD)
├── app.py           # Streamlit frontend
├── schema.sql       # Supabase tables setup
├── requirements.txt
└── .env.example     # Copy to .env and fill in your values
```

---

## Setup (step by step)

### 1. Create a Supabase project
1. Go to [supabase.com](https://supabase.com) → New Project
2. Open **SQL Editor** → paste the contents of `schema.sql` → Run
3. Go to **Project Settings → API** and copy:
   - **Project URL** → `SUPABASE_URL`
   - **service_role** secret key → `SUPABASE_KEY` ⚠️ (NOT the anon key)

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your Supabase URL, service_role key, and a random JWT secret
```

Generate a JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI backend
```bash
uvicorn main:app --reload --port 8000
```
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000

### 5. Run the Streamlit frontend
In a **separate terminal**:
```bash
streamlit run app.py
```
- App: http://localhost:8501

---

## API Endpoints

| Method | Path                | Auth | Description          |
|--------|---------------------|------|----------------------|
| POST   | /auth/register      | ❌   | Create account       |
| POST   | /auth/login         | ❌   | Login, get JWT       |
| GET    | /auth/me            | ✅   | Get current user     |
| GET    | /notes              | ✅   | List all your notes  |
| POST   | /notes              | ✅   | Create a note        |
| GET    | /notes/{id}         | ✅   | Get one note         |
| PUT    | /notes/{id}         | ✅   | Update a note        |
| DELETE | /notes/{id}         | ✅   | Delete a note        |

---

## Notes on Security
- Passwords are hashed with **bcrypt** (never stored plain)
- JWTs expire after **24 hours**
- The `service_role` key is only used server-side in FastAPI — never expose it to the frontend
- Keep `.env` in `.gitignore`

---

## Deployment Tips

| Service | What to deploy |
|---------|---------------|
| [Render](https://render.com) | FastAPI backend (free tier) |
| [Streamlit Cloud](https://streamlit.io/cloud) | Streamlit frontend (free) |
| [Railway](https://railway.app) | FastAPI alternative |

For Streamlit Cloud, set `API_BASE` in `app.py` to your deployed FastAPI URL, and add your env vars as secrets.
