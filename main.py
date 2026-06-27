from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
SUPABASE_URL     = os.getenv("SUPABASE_URL")
SUPABASE_KEY     = os.getenv("SUPABASE_KEY")       # service_role key (server-side only)
JWT_SECRET       = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM    = "HS256"
ACCESS_TOKEN_EXP = 60 * 24  # minutes → 1 day

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
bearer            = HTTPBearer()

app = FastAPI(title="NoteVault API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ──────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

# ── Helpers ──────────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXP)
    return jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    try:
        payload  = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ── Auth Routes ───────────────────────────────────────────────────────────────
@app.post("/auth/register", status_code=201)
def register(body: RegisterRequest):
    # Check duplicate email
    existing = supabase.table("users").select("id").eq("email", body.email).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = hash_password(body.password)
    result = supabase.table("users").insert({
        "email":     body.email,
        "password":  hashed,
        "full_name": body.full_name,
    }).execute()

    user = result.data[0]
    token = create_access_token(user["id"])
    return {"message": "Account created", "access_token": token, "token_type": "bearer"}


@app.post("/auth/login")
def login(body: LoginRequest):
    result = supabase.table("users").select("*").eq("email", body.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = result.data[0]
    if not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user["id"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user["id"], "email": user["email"], "full_name": user["full_name"]},
    }


@app.get("/auth/me")
def me(user_id: str = Depends(get_current_user)):
    result = supabase.table("users").select("id, email, full_name, created_at").eq("id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data[0]


# ── Notes Routes ──────────────────────────────────────────────────────────────
@app.get("/notes")
def list_notes(user_id: str = Depends(get_current_user)):
    result = supabase.table("notes") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("updated_at", desc=True) \
        .execute()
    return result.data


@app.post("/notes", status_code=201)
def create_note(body: NoteCreate, user_id: str = Depends(get_current_user)):
    result = supabase.table("notes").insert({
        "user_id": user_id,
        "title":   body.title,
        "content": body.content,
    }).execute()
    return result.data[0]


@app.get("/notes/{note_id}")
def get_note(note_id: str, user_id: str = Depends(get_current_user)):
    result = supabase.table("notes").select("*").eq("id", note_id).eq("user_id", user_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Note not found")
    return result.data[0]


@app.put("/notes/{note_id}")
def update_note(note_id: str, body: NoteUpdate, user_id: str = Depends(get_current_user)):
    # Verify ownership
    existing = supabase.table("notes").select("id").eq("id", note_id).eq("user_id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Note not found")

    updates = {k: v for k, v in body.dict().items() if v is not None}
    updates["updated_at"] = datetime.utcnow().isoformat()

    result = supabase.table("notes").update(updates).eq("id", note_id).execute()
    return result.data[0]


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str, user_id: str = Depends(get_current_user)):
    existing = supabase.table("notes").select("id").eq("id", note_id).eq("user_id", user_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Note not found")

    supabase.table("notes").delete().eq("id", note_id).execute()
    return


@app.get("/")
def root():
    return {"message": "NoteVault API is running 🚀"}
