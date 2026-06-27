# 📓 NoteVault

A full-stack note-taking web app with JWT authentication and per-user private notes — built with FastAPI, Supabase, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red?logo=streamlit)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase)

---

## ✨ Features

- **User Authentication** — Register and login with email & password
- **JWT Security** — Stateless token-based auth, tokens expire after 24 hours
- **Password Hashing** — bcrypt hashing, passwords never stored in plain text
- **Private Notes** — Each user only sees their own notes
- **Full CRUD** — Create, read, update, and delete notes
- **Live Search** — Filter notes instantly from the sidebar
- **Dark UI** — Clean dark theme built with custom Streamlit CSS
- **REST API** — FastAPI backend with auto-generated Swagger docs

---

## 🏗️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | Streamlit                         |
| Backend    | FastAPI                           |
| Database   | Supabase (PostgreSQL)             |
| Auth       | JWT (python-jose) + bcrypt        |
| Hosting    | Streamlit Cloud + Render          |

---

## 📁 Project Structure

```
note-taking-app/
├── main.py          # FastAPI backend — auth + notes CRUD
├── app.py           # Streamlit frontend
├── schema.sql       # Supabase database setup
├── requirements.txt # Python dependencies
├── .env.example     # Environment variable template
└── README.md
```

---

## 🚀 Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/A-S-Ayon/note-taking-app.git
cd note-taking-app
```

### 2. Create virtual environment

```bash
uv venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Set up Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run the contents of `schema.sql`
3. Go to **Project Settings → API** and copy:
   - **Project URL**
   - **service_role** secret key (not the anon key)

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-secret-key
JWT_SECRET=your-random-secret-string
```

Generate a JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Run the app

**Terminal 1 — FastAPI backend:**
```bash
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Streamlit frontend:**
```bash
streamlit run app.py
```

- Frontend: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## 🌐 API Endpoints

| Method | Endpoint          | Auth | Description         |
|--------|-------------------|------|---------------------|
| POST   | /auth/register    | ❌   | Create account      |
| POST   | /auth/login       | ❌   | Login, get JWT      |
| GET    | /auth/me          | ✅   | Get current user    |
| GET    | /notes            | ✅   | List all notes      |
| POST   | /notes            | ✅   | Create a note       |
| GET    | /notes/{id}       | ✅   | Get one note        |
| PUT    | /notes/{id}       | ✅   | Update a note       |
| DELETE | /notes/{id}       | ✅   | Delete a note       |

---

## ☁️ Deployment

| Service                                        | Purpose          | Cost |
|------------------------------------------------|------------------|------|
| [Render](https://render.com)                   | FastAPI backend  | Free |
| [Streamlit Cloud](https://share.streamlit.io)  | Frontend         | Free |
| [Supabase](https://supabase.com)               | Database         | Free |

### Deploy FastAPI on Render

1. New Web Service → connect GitHub repo
2. Set build and start commands:
```
Build:  pip install -r requirements.txt
Start:  uvicorn main:app --host 0.0.0.0 --port $PORT
```
3. Add environment variables (`SUPABASE_URL`, `SUPABASE_KEY`, `JWT_SECRET`)

### Deploy Frontend on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) → New app
2. Connect GitHub repo, set main file to `app.py`
3. Deploy

> **Note:** Update `API_BASE` in `app.py` to your Render URL before deploying the frontend.

---

## 🔒 Security Notes

- Passwords hashed with **bcrypt** — never stored in plain text
- JWT tokens expire after **24 hours**
- `service_role` key used **server-side only** — never exposed to frontend
- `.env` is gitignored — never commit secrets

---

## 📄 License

MIT License — free to use and modify.
