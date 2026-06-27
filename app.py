import streamlit as st
import requests
from datetime import datetime
import threading

def wake_backend():
    try:
        requests.get(f"{API_BASE}/", timeout=10)
    except Exception:
        pass

# Ping backend in background so it wakes up
threading.Thread(target=wake_backend, daemon=True).start()


API_BASE = "https://note-taking-app-ks18.onrender.com/"

st.set_page_config(
    page_title="NoteVault",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ---- Global ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Fraunces:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Background */
    .stApp {
        background-color: #0f1117;
        color: #e2e8f0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161b27 !important;
        border-right: 1px solid #2d3748;
    }

    /* Headings */
    h1, h2, h3 {
        font-family: 'Fraunces', serif !important;
        color: #f7fafc !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.25rem !important;
        transition: opacity 0.2s ease !important;
    }
    .stButton > button:hover {
        opacity: 0.88 !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1e2535 !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.25) !important;
    }

    /* Note cards */
    .note-card {
        background: #1a2033;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s;
        cursor: pointer;
    }
    .note-card:hover {
        border-color: #6366f1;
    }
    .note-card h4 {
        font-family: 'Fraunces', serif;
        font-size: 1rem;
        margin: 0 0 0.3rem 0;
        color: #f7fafc;
    }
    .note-card p {
        font-size: 0.82rem;
        color: #94a3b8;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .note-card .meta {
        font-size: 0.72rem;
        color: #4b5563;
        margin-top: 0.5rem;
    }

    /* Auth card */
    .auth-container {
        max-width: 420px;
        margin: 3rem auto;
        background: #161b27;
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 2.5rem;
    }

    /* Tag pill */
    .tag-pill {
        display: inline-block;
        background: rgba(99,102,241,0.15);
        color: #818cf8;
        border-radius: 999px;
        font-size: 0.72rem;
        padding: 2px 10px;
        margin-right: 4px;
    }

    /* Success / error */
    .stAlert { border-radius: 8px !important; }

    /* Divider */
    hr { border-color: #2d3748 !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "token":        None,
        "user":         None,
        "notes":        [],
        "active_note":  None,
        "editing":      False,
        "auth_tab":     "login",   # "login" | "register"
        "search_query": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── API Helpers ───────────────────────────────────────────────────────────────
def api(method: str, path: str, *, json=None, auth=True):
    headers = {"Content-Type": "application/json"}
    if auth and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        r = requests.request(method, f"{API_BASE}{path}", json=json, headers=headers, timeout=30)
        return r
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot reach the API. Backend may be sleeping, try again in 30 seconds.")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Backend is waking up, please try again.")
        return None

def fetch_notes():
    r = api("GET", "/notes")
    if r and r.status_code == 200:
        st.session_state.notes = r.json()

def fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y · %H:%M")
    except Exception:
        return iso or ""


# ── Auth Page ─────────────────────────────────────────────────────────────────
def auth_page():
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("<h1 style='text-align:center;font-size:2.2rem;margin-bottom:0.2rem'>📓 NoteVault</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#94a3b8;margin-bottom:1.8rem'>Your private space to think and write.</p>", unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["Sign In", "Create Account"])

        # ── Login ──
        with tab_login:
            with st.form("login_form"):
                email    = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit   = st.form_submit_button("Sign In", use_container_width=True)

            if submit:
                if not email or not password:
                    st.warning("Please fill in all fields.")
                else:
                    r = api("POST", "/auth/login", json={"email": email, "password": password}, auth=False)
                    if r is None:
                        pass
                    elif r.status_code == 200:
                        try:
                            data = r.json()
                        except Exception:
                            st.error(f"Backend returned invalid response (HTTP {r.status_code}). It may be waking up — wait 30 seconds and try again.")
                            st.stop()
                        st.session_state.token = data["access_token"]
                        
                        st.session_state.user  = data["user"]
                        fetch_notes()
                        st.rerun()
                    else:
                        try:
                            msg = r.json().get("detail", "Login failed")
                        except Exception:
                            msg = f"Login failed (HTTP {r.status_code})"
                        st.error(msg)

        # ── Register ──
        with tab_reg:
            with st.form("reg_form"):
                full_name = st.text_input("Full Name", placeholder="Arafat Hossain")
                email_r   = st.text_input("Email", placeholder="you@example.com", key="reg_email")
                pass_r    = st.text_input("Password", type="password", placeholder="min 8 characters", key="reg_pass")
                submit_r  = st.form_submit_button("Create Account", use_container_width=True)

            if submit_r:
                if not email_r or not pass_r or not full_name:
                    st.warning("Please fill in all fields.")
                elif len(pass_r) < 8:
                    st.warning("Password must be at least 8 characters.")
                else:
                    r = api("POST", "/auth/register", json={
                        "email":     email_r,
                        "password":  pass_r,
                        "full_name": full_name,
                    }, auth=False)
                    if r is None:
                        pass
                    elif r.status_code == 201:
                        data = r.json()
                        st.session_state.token = data["access_token"]
                        # Fetch user profile
                        me = api("GET", "/auth/me")
                        if me and me.status_code == 200:
                            st.session_state.user = me.json()
                        fetch_notes()
                        st.success("Account created! Welcome 🎉")
                        st.rerun()
                    else:
                        try:
                            msg = r.json().get("detail", "Registration failed")
                        except Exception:
                            msg = f"Registration failed (HTTP {r.status_code})"
                        st.error(msg)


# ── Sidebar ────────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        user = st.session_state.user or {}
        st.markdown(f"### 👤 {user.get('full_name', 'User')}")
        st.caption(user.get("email", ""))
        st.markdown("---")

        # New note button
        if st.button("＋ New Note", use_container_width=True):
            st.session_state.active_note = None
            st.session_state.editing     = True
            st.rerun()

        st.markdown("---")

        # Search
        search = st.text_input("🔍 Search notes", placeholder="Type to filter…", label_visibility="collapsed")
        st.session_state.search_query = search

        st.markdown("---")

        # Note list
        notes = st.session_state.notes
        if search:
            notes = [n for n in notes if search.lower() in n["title"].lower() or search.lower() in n["content"].lower()]

        if not notes:
            st.caption("No notes yet. Create your first one!")
        else:
            st.caption(f"{len(notes)} note{'s' if len(notes) != 1 else ''}")
            for note in notes:
                preview = note["content"][:80].replace("\n", " ")
                card_html = f"""
                <div class="note-card">
                    <h4>{note['title'] or 'Untitled'}</h4>
                    <p>{preview}{'…' if len(note['content']) > 80 else ''}</p>
                    <div class="meta">{fmt_date(note.get('updated_at',''))}</div>
                </div>"""
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button("Open", key=f"open_{note['id']}", use_container_width=True):
                    st.session_state.active_note = note
                    st.session_state.editing     = False
                    st.rerun()

        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            for k in ["token", "user", "notes", "active_note", "editing"]:
                st.session_state[k] = None if k != "notes" else []
            st.session_state.editing = False
            st.rerun()


# ── Main Notes Area ────────────────────────────────────────────────────────────
def notes_area():
    note    = st.session_state.active_note
    editing = st.session_state.editing

    # ── Empty state ──
    if not editing and note is None:
        st.markdown("""
        <div style='text-align:center;padding:5rem 0;'>
            <div style='font-size:4rem;margin-bottom:1rem'>📓</div>
            <h2 style='font-family:Fraunces,serif;color:#f7fafc'>Welcome to NoteVault</h2>
            <p style='color:#94a3b8;max-width:380px;margin:0 auto'>
                Select a note from the sidebar, or hit <b>＋ New Note</b> to start writing.
            </p>
        </div>""", unsafe_allow_html=True)
        return

    # ── Editor (new or edit) ──
    if editing:
        st.markdown("## ✏️ " + ("New Note" if note is None else "Edit Note"))
        default_title   = note["title"]   if note else ""
        default_content = note["content"] if note else ""

        title   = st.text_input("Title", value=default_title, placeholder="Give your note a title…")
        content = st.text_area("Content", value=default_content, placeholder="Start writing…", height=380)

        col_save, col_cancel = st.columns([1, 1])

        with col_save:
            if st.button("💾 Save Note", use_container_width=True):
                if not title.strip():
                    st.warning("Please add a title.")
                else:
                    if note is None:
                        # Create
                        r = api("POST", "/notes", json={"title": title, "content": content})
                        if r is None:
                            st.error("No response from API — is FastAPI running?")
                        elif r.status_code == 201:
                            st.session_state.active_note = r.json()
                            st.session_state.editing     = False
                            fetch_notes()
                            st.success("Note created!")
                            st.rerun()
                        else:
                            try:
                                detail = r.json()
                            except Exception:
                                detail = r.text or "empty response"
                            st.error(f"HTTP {r.status_code} — {detail}")

        with col_cancel:
            if st.button("✕ Cancel", use_container_width=True):
                st.session_state.editing = False
                if note is None:
                    st.session_state.active_note = None
                st.rerun()

        return

    # ── View mode ──
    if note:
        col_head, col_btns = st.columns([3, 1])
        with col_head:
            st.markdown(f"<h1 style='font-family:Fraunces,serif;font-size:2rem'>{note['title']}</h1>", unsafe_allow_html=True)
            st.caption(f"Last updated: {fmt_date(note.get('updated_at', ''))}")
        with col_btns:
            edit_col, del_col = st.columns(2)
            with edit_col:
                if st.button("✏️ Edit", use_container_width=True):
                    st.session_state.editing = True
                    st.rerun()
            with del_col:
                if st.button("🗑️ Delete", use_container_width=True):
                    st.session_state["confirm_delete"] = True

        # Confirm delete
        if st.session_state.get("confirm_delete"):
            st.warning("Are you sure you want to delete this note? This cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Yes, delete", use_container_width=True):
                    r = api("DELETE", f"/notes/{note['id']}")
                    if r and r.status_code == 204:
                        st.session_state.active_note   = None
                        st.session_state["confirm_delete"] = False
                        fetch_notes()
                        st.rerun()
            with c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state["confirm_delete"] = False
                    st.rerun()

        st.markdown("---")
        st.markdown(note["content"])


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.token:
        auth_page()
    else:
        sidebar()
        notes_area()

main()
