"""
Countercurrent.ai — Layer 3 (v2): The Wire Room
Now includes:
  - Document upload (PDFs, trend reports, past work)
  - Semantic search via Pinecone (RAG-powered Thinker)
  - Weekly email dispatch via SendGrid
  - Meta-analysis of dispatches against briefs

Run with:
    streamlit run app.py
"""

import os
import json
import hashlib
import time
from datetime import datetime
from typing import Optional

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Streamlit Cloud: injeta os Secrets como variáveis de ambiente
try:
    for key, value in st.secrets.items():
        if key not in os.environ:
            os.environ[key] = str(value)
except Exception:
    pass  # Rodando localmente sem secrets

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Countercurrent.ai",
    page_icon="⟳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS — Wire Room aesthetic (consistent with v1) ────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    background-color: #0a0a0a !important;
    color: #d4cfc7 !important;
    font-family: 'DM Sans', sans-serif;
}
.wire-header {
    display: flex; align-items: baseline; gap: 1.2rem;
    border-bottom: 1px solid #2a2a2a; padding-bottom: 1rem; margin-bottom: 2rem;
}
.wire-header h1 {
    font-family: 'DM Serif Display', serif; font-size: 2.2rem;
    color: #f0ebe2; letter-spacing: -0.02em; margin: 0;
}
.wire-header .tagline {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
    color: #e8a838; letter-spacing: 0.12em; text-transform: uppercase;
}
.col-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.18em; text-transform: uppercase; color: #666;
    border-bottom: 1px solid #1e1e1e; padding-bottom: 0.5rem; margin-bottom: 1.2rem;
}
.signal-card {
    background: #111111; border: 1px solid #1e1e1e;
    border-left: 3px solid #2a2a2a; border-radius: 3px;
    padding: 1rem 1.1rem; margin-bottom: 0.8rem; transition: border-left-color 0.15s;
}
.signal-card:hover { border-left-color: #e8a838; }
.signal-card .signal-source {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem;
    color: #666; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.3rem;
}
.signal-card .signal-title { font-size: 0.9rem; color: #e0dbd3; font-weight: 500; line-height: 1.4; margin-bottom: 0.4rem; }
.signal-card .signal-snippet {
    font-size: 0.8rem; color: #888; line-height: 1.6;
    display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.signal-card .signal-ts { font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem; color: #444; margin-top: 0.5rem; }
.badge {
    display: inline-block; padding: 0.1rem 0.45rem; border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem;
    text-transform: uppercase; letter-spacing: 0.1em; margin-right: 0.3rem;
}
.badge-reddit   { background: #1a0f0f; color: #d44800; border: 1px solid #2a1a1a; }
.badge-twitter  { background: #0a0f1a; color: #4a9eff; border: 1px solid #1a2030; }
.badge-tiktok   { background: #0f1a12; color: #25d366; border: 1px solid #1a2a1e; }
.badge-web      { background: #1a1a0f; color: #e8c438; border: 1px solid #2a2a1a; }
.badge-pdf      { background: #1a0f1a; color: #c44aff; border: 1px solid #2a1a2a; }
.badge-doc       { background: #0f1a1a; color: #4ae8d4; border: 1px solid #1a2a2a; }
.badge-youtube   { background: #1a0a0a; color: #ff4444; border: 1px solid #2a1a1a; }
.badge-instagram { background: #1a0f1a; color: #f77737; border: 1px solid #2a1a2a; }
.badge-rss       { background: #1a1200; color: #ffaa00; border: 1px solid #2a2000; }

/* Upload zone */
.upload-zone {
    border: 1px dashed #2a2a2a; border-radius: 4px;
    padding: 1.5rem; text-align: center;
    background: #0d0d0d; margin-bottom: 1rem;
    transition: border-color 0.15s;
}
.upload-zone:hover { border-color: #c44aff; }
.upload-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    color: #555; text-transform: uppercase; letter-spacing: 0.12em;
}

/* Doc card */
.doc-card {
    background: #0f0a1a; border: 1px solid #2a1a3a;
    border-left: 3px solid #c44aff; border-radius: 3px;
    padding: 0.8rem 1rem; margin-bottom: 0.6rem;
}
.doc-card .doc-name { font-size: 0.85rem; color: #d8ccf0; font-weight: 500; }
.doc-card .doc-meta { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; color: #666; margin-top: 0.3rem; }

/* Dispatch card */
.dispatch-card {
    background: #0f0f0a; border: 1px solid #2a2a1e;
    border-radius: 3px; padding: 1.4rem; margin-bottom: 1rem;
}
.dispatch-current {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    color: #e8a838; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.4rem;
}
.dispatch-heading {
    font-family: 'DM Serif Display', serif; font-size: 1.25rem;
    color: #f0ebe2; margin-bottom: 0.6rem; line-height: 1.3;
}
.dispatch-body { font-size: 0.85rem; color: #999; line-height: 1.7; }
.countercurrent-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem;
    color: #c44aff; text-transform: uppercase; letter-spacing: 0.14em;
    margin-top: 1rem; margin-bottom: 0.3rem;
}
.countercurrent-text {
    font-family: 'DM Serif Display', serif; font-style: italic;
    font-size: 1rem; color: #c8b8e8; line-height: 1.5;
}

/* RAG result */
.rag-result {
    background: #0a110f; border: 1px solid #1e2a26;
    border-left: 3px solid #25d366; border-radius: 3px;
    padding: 0.8rem 1rem; margin-bottom: 0.6rem;
}
.rag-score {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem;
    color: #25d366; margin-bottom: 0.3rem;
}
.rag-text { font-size: 0.82rem; color: #aaa; line-height: 1.6; }
.rag-meta { font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem; color: #444; margin-top: 0.4rem; }

/* Chat */
.chat-msg-user { text-align: right; margin-bottom: 0.8rem; }
.chat-msg-user span {
    display: inline-block; background: #1a1a2e; color: #c8d8ff;
    border-radius: 12px 12px 2px 12px; padding: 0.5rem 0.9rem;
    font-size: 0.85rem; max-width: 80%;
}
.chat-msg-ai { text-align: left; margin-bottom: 0.8rem; }
.chat-msg-ai span {
    display: inline-block; background: #111; border: 1px solid #2a2a2a; color: #d4cfc7;
    border-radius: 2px 12px 12px 12px; padding: 0.5rem 0.9rem;
    font-size: 0.85rem; max-width: 85%; line-height: 1.6;
}

/* Email preview */
.email-preview {
    background: #f8f6f2; border-radius: 4px; padding: 2rem;
    color: #1a1a1a; font-family: 'DM Sans', sans-serif;
}
.email-preview h2 { font-family: 'DM Serif Display', serif; font-size: 1.6rem; color: #1a1a1a; }
.email-preview .email-label { font-size: 0.7rem; color: #e8a838; text-transform: uppercase; letter-spacing: 0.12em; }

/* Inputs & buttons */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #111 !important; color: #d4cfc7 !important;
    border: 1px solid #2a2a2a !important; border-radius: 3px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #e8a838 !important; box-shadow: 0 0 0 1px #e8a83830 !important;
}
.stButton > button {
    background: transparent !important; border: 1px solid #333 !important;
    color: #d4cfc7 !important; font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important; border-radius: 2px !important;
    padding: 0.4rem 1rem !important; transition: all 0.15s !important;
}
.stButton > button:hover { border-color: #e8a838 !important; color: #e8a838 !important; }
.stSelectbox > div > div { background: #111 !important; border: 1px solid #2a2a2a !important; color: #d4cfc7 !important; }
.metric-pill {
    display: inline-block; background: #111; border: 1px solid #1e1e1e;
    border-radius: 2px; padding: 0.4rem 0.8rem;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: #888; margin-right: 0.5rem;
}
.metric-pill b { color: #e0dbd3; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px; }
.stTabs [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid #1e1e1e; }
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.65rem !important;
    letter-spacing: 0.14em !important; text-transform: uppercase !important;
    color: #555 !important; background: transparent !important;
    border: none !important; padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] { color: #e8a838 !important; border-bottom: 1px solid #e8a838 !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

BADGE_MAP = {
    "reddit":    "badge-reddit",
    "twitter":   "badge-twitter",
    "tiktok":    "badge-tiktok",
    "web":       "badge-web",
    "pdf":       "badge-pdf",
    "doc":       "badge-doc",
    "youtube":   "badge-youtube",
    "instagram": "badge-instagram",
    "rss":       "badge-rss",
}

COUNTERCURRENT_SYSTEM_PROMPT = """
You are Countercurrent — the strategic intelligence engine inside an agency "Wire Room."

Your job:
1. IDENTIFY THE CURRENT — the dominant, obvious cultural trend in the signals.
2. PROPOSE THE COUNTERCURRENT — a bold, contrarian strategic provocation for a brand.

Always structure output as:
---
**THE CURRENT:** [one sharp sentence]

**SIGNALS DRIVING IT:** [2–3 bullet points]

**THE COUNTERCURRENT:** [1–2 sentences — the provocation]

**STRATEGIC RATIONALE:** [2–3 sentences]
---

Be specific. Be bold. Write like a senior strategist, not a trend report.
"""

THINKER_SYSTEM_PROMPT = """
You are the Thinker Partner — a conversational strategic advisor with access to a
cultural signals and proprietary documents knowledge base.

When given retrieved context + a brief, you:
- Identify the most relevant cultural tensions
- Suggest unexpected brand angles rooted in those tensions
- Challenge assumptions and push for more interesting ideas
- Reference specific signals or documents when relevant
- Speak like a brilliant creative director: sharp, incisive, curious

Keep answers focused and conversational.
"""

META_ANALYSIS_SYSTEM_PROMPT = """
You are conducting a meta-analysis of multiple Countercurrent strategic dispatches.

Your role: find the patterns ACROSS dispatches — the macro themes, recurring tensions,
and strategic opportunities that only become visible when looking at many weeks of data together.

Structure your response as:
---
**MACRO THEMES:** [2–3 dominant patterns across all dispatches]

**RECURRING TENSIONS:** [cultural contradictions appearing repeatedly]

**EMERGING COUNTERCURRENT:** [the big strategic idea hiding in the aggregate]

**BRIEF APPLICATION:** [how these macro themes apply to the specific brief provided]
---
"""

# ── Data helpers ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=60)
def load_signals(path: str = "data/signals.jsonl", limit: int = 200) -> list[dict]:
    if not os.path.exists(path):
        return []
    signals = []
    with open(path) as f:
        for line in f:
            try:
                signals.append(json.loads(line))
            except Exception:
                pass
    signals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return signals[:limit]


def load_dispatches(path: str = "data/dispatches.jsonl") -> list[dict]:
    if not os.path.exists(path):
        return []
    dispatches = []
    with open(path) as f:
        for line in f:
            try:
                dispatches.append(json.loads(line))
            except Exception:
                pass
    return dispatches


def save_dispatch(content: str, topic: str):
    os.makedirs("data", exist_ok=True)
    with open("data/dispatches.jsonl", "a") as f:
        f.write(json.dumps({
            "content": content,
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
        }) + "\n")


def load_uploaded_docs(path: str = "data/uploaded_docs.json") -> list[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def save_uploaded_doc_meta(meta: dict):
    os.makedirs("data", exist_ok=True)
    docs = load_uploaded_docs()
    docs.append(meta)
    with open("data/uploaded_docs.json", "w") as f:
        json.dump(docs, f, indent=2)


# ── AI helpers ────────────────────────────────────────────────────────────────

def call_llm(messages: list[dict], system: str, temperature: float = 0.75) -> str:
    import google.generativeai as genai

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "⚠️ GOOGLE_API_KEY não configurada no .env"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system,
    )

    # Converte histórico para formato Gemini
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=history)

    try:
        response = chat.send_message(messages[-1]["content"])
        return response.text
    except Exception as e:
        return f"⚠️ Erro na API Gemini: {e}"


def semantic_search(query: str, top_k: int = 6, client_filter: Optional[str] = None) -> list[dict]:
    """Query Pinecone for semantically relevant chunks."""
    try:
        from vectorizer import query_knowledge_base
        filter_meta = {"client_tag": client_filter} if client_filter else None
        return query_knowledge_base(query, top_k=top_k, filter_metadata=filter_meta)
    except ImportError:
        return []
    except Exception as e:
        st.warning(f"Semantic search unavailable: {e}")
        return []


def build_rag_context(results: list[dict]) -> str:
    parts = []
    for i, r in enumerate(results):
        source_label = f"[{r.get('source','?').upper()}]"
        if r.get("doc_type") == "pdf":
            source_label = f"[PDF: {r.get('title','?')}]"
        parts.append(
            f"SOURCE {i+1} {source_label} (relevance: {r['score']:.2f})\n{r['text']}"
        )
    return "\n\n---\n\n".join(parts)


def build_simple_context(signals: list[dict], limit: int = 12) -> str:
    parts = []
    for i, sig in enumerate(signals[:limit]):
        parts.append(
            f"SIGNAL {i+1} [{sig.get('source','?').upper()}]\n"
            f"Title: {sig.get('title','')}\n"
            f"Content: {sig.get('content','')[:400]}"
        )
    return "\n---\n".join(parts)


def send_email_sendgrid(to_email: str, subject: str, html_body: str) -> bool:
    """Send dispatch email via SendGrid."""
    import urllib.request
    import urllib.error

    api_key = os.environ.get("SENDGRID_API_KEY")
    from_email = os.environ.get("SENDGRID_FROM_EMAIL", "dispatch@countercurrent.ai")

    if not api_key:
        return False

    payload = json.dumps({
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_body}],
    }).encode()

    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status == 202
    except urllib.error.HTTPError:
        return False


def markdown_to_email_html(content: str, week_label: str) -> str:
    """Convert dispatch markdown to a clean HTML email."""
    import re

    body = content.replace("**THE CURRENT:**", '<p class="label">▲ THE CURRENT</p><p class="current">')
    body = re.sub(r'\*\*SIGNALS DRIVING IT:\*\*', '</p><p class="label">SIGNALS DRIVING IT</p><p class="body">', body)
    body = re.sub(r'\*\*THE COUNTERCURRENT:\*\*', '</p><p class="label cc-label">⟳ THE COUNTERCURRENT</p><p class="cc">', body)
    body = re.sub(r'\*\*STRATEGIC RATIONALE:\*\*', '</p><p class="label">STRATEGIC RATIONALE</p><p class="body">', body)
    body = body.replace("---", "").strip() + "</p>"

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Georgia, serif; background: #f8f6f2; margin: 0; padding: 40px 20px; }}
  .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 48px; border-top: 4px solid #e8a838; }}
  .masthead {{ font-family: monospace; font-size: 11px; color: #999; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 8px; }}
  h1 {{ font-family: Georgia, serif; font-size: 28px; color: #1a1a1a; margin: 0 0 32px 0; font-weight: normal; }}
  .label {{ font-family: monospace; font-size: 10px; color: #e8a838; text-transform: uppercase; letter-spacing: 0.15em; margin: 24px 0 4px 0; }}
  .cc-label {{ color: #9b5de5; }}
  .current {{ font-size: 18px; color: #1a1a1a; font-weight: bold; line-height: 1.4; margin: 0; }}
  .cc {{ font-size: 17px; color: #5a3a7a; font-style: italic; line-height: 1.5; margin: 0; }}
  .body {{ font-size: 14px; color: #555; line-height: 1.8; margin: 0; }}
  .footer {{ font-family: monospace; font-size: 10px; color: #bbb; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
</style>
</head>
<body>
<div class="container">
  <div class="masthead">Countercurrent.ai · {week_label}</div>
  <h1>Weekly Cultural Dispatch</h1>
  {body}
  <div class="footer">COUNTERCURRENT.AI — ATLANTIC INTELLIGENCE LAYER · Human-in-the-loop · Culture-first</div>
</div>
</body>
</html>
"""


# ── Vectorize uploaded file ───────────────────────────────────────────────────

def vectorize_uploaded_file(file_bytes: bytes, filename: str, doc_type: str, client_tag: str) -> bool:
    """Try to vectorize a file. Returns True if successful."""
    try:
        from vectorizer import VectorizationPipeline
        pipeline = VectorizationPipeline()
        metadata = {
            "doc_type": doc_type,
            "client_tag": client_tag,
            "title": filename,
        }
        if filename.lower().endswith(".pdf"):
            pipeline.process_pdf(file_bytes, filename, metadata)
        else:
            text = file_bytes.decode("utf-8", errors="ignore")
            doc_id = hashlib.sha256(file_bytes[:500]).hexdigest()[:16]
            pipeline.process_text(text, doc_id, {**metadata, "source": "doc"})
        return True
    except Exception as e:
        st.warning(f"Vectorization skipped (Pinecone not configured): {e}")
        return False


# ── Session state ─────────────────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "dispatch_cache" not in st.session_state:
    st.session_state.dispatch_cache = {}
if "rag_results" not in st.session_state:
    st.session_state.rag_results = []


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="wire-header">
  <h1>Countercurrent.ai</h1>
  <span class="tagline">Cultural Intelligence Wire Room · v2</span>
</div>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────

signals      = load_signals()
dispatches   = load_dispatches()
uploaded_docs = load_uploaded_docs()

sources  = list({s.get("source", "?") for s in signals})
clients  = sorted({s.get("client_tag") for s in signals if s.get("client_tag")})

# Metrics bar
cols = st.columns([1, 1, 1, 1, 1, 4])
for col, label, value in zip(cols, ["signals", "sources", "clients", "dispatches", "docs"],
                              [len(signals), len(sources), len(clients), len(dispatches), len(uploaded_docs)]):
    with col:
        st.markdown(f'<div class="metric-pill"><b>{value}</b> {label}</div>', unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Main layout ───────────────────────────────────────────────────────────────

col_left, col_right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — Signal Feed + Document Library
# ══════════════════════════════════════════════════════════════════════════════

with col_left:
    left_tab1, left_tab2 = st.tabs(["Signal Feed", "Document Library"])

    # ── SIGNAL FEED ──────────────────────────────────────────────────────────
    with left_tab1:
        st.markdown('<div class="col-label">Live Signal Feed</div>', unsafe_allow_html=True)

        fc1, fc2 = st.columns(2)
        with fc1:
            source_filter = st.selectbox("Source", ["All"] + sorted(sources),
                                          key="source_filter", label_visibility="collapsed")
        with fc2:
            client_filter = st.selectbox("Client", ["All clients"] + clients,
                                          key="client_filter", label_visibility="collapsed")

        filtered = signals
        if source_filter != "All":
            filtered = [s for s in filtered if s.get("source") == source_filter]
        if client_filter != "All clients":
            filtered = [s for s in filtered if s.get("client_tag") == client_filter]

        if not filtered:
            st.markdown('<p style="color:#444;font-family:\'IBM Plex Mono\',monospace;font-size:0.8rem">No signals yet. Run ingestion.py first.</p>', unsafe_allow_html=True)
        else:
            for sig in filtered[:40]:
                source = sig.get("source", "web")
                badge_cls = BADGE_MAP.get(source, "badge-web")
                title = sig.get("title", "(no title)")[:120]
                content = sig.get("content", "")[:300]
                ts_raw = sig.get("timestamp", "")
                try:
                    ts = datetime.fromisoformat(ts_raw).strftime("%d %b %Y · %H:%M")
                except Exception:
                    ts = ts_raw[:16]
                url = sig.get("url", "#")
                client_tag = sig.get("client_tag") or ""

                st.markdown(f"""
<div class="signal-card">
  <div class="signal-source">
    <span class="badge {badge_cls}">{source}</span>
    {'<span class="badge" style="background:#1a1a1a;color:#555;border:1px solid #2a2a2a">' + client_tag + '</span>' if client_tag else ''}
  </div>
  <div class="signal-title"><a href="{url}" target="_blank" style="color:inherit;text-decoration:none">{title}</a></div>
  <div class="signal-snippet">{content}</div>
  <div class="signal-ts">{ts}</div>
</div>""", unsafe_allow_html=True)

    # ── DOCUMENT LIBRARY ─────────────────────────────────────────────────────
    with left_tab2:
        st.markdown('<div class="col-label">Knowledge Base — Upload Documents</div>', unsafe_allow_html=True)

        # Upload form
        with st.expander("+ Upload new document", expanded=not bool(uploaded_docs)):
            uploaded_file = st.file_uploader(
                "Drop file here",
                type=["pdf", "txt", "md"],
                label_visibility="collapsed",
            )
            uc1, uc2 = st.columns(2)
            with uc1:
                doc_type = st.selectbox("Type", [
                    "trend_report", "past_work", "foundational", "research", "brief", "other"
                ], key="doc_type")
            with uc2:
                doc_client = st.text_input("Client tag", placeholder="BrandX or leave blank", key="doc_client")

            if st.button("Upload & Vectorize") and uploaded_file:
                with st.spinner("Processing and embedding document…"):
                    file_bytes = uploaded_file.read()
                    vectorized = vectorize_uploaded_file(
                        file_bytes,
                        uploaded_file.name,
                        doc_type,
                        doc_client or "General",
                    )
                    meta = {
                        "filename": uploaded_file.name,
                        "doc_type": doc_type,
                        "client_tag": doc_client or "General",
                        "size_kb": round(len(file_bytes) / 1024, 1),
                        "vectorized": vectorized,
                        "uploaded_at": datetime.utcnow().isoformat(),
                    }
                    save_uploaded_doc_meta(meta)
                    st.success(f"✓ '{uploaded_file.name}' added to knowledge base")
                    st.rerun()

        # Document list
        if not uploaded_docs:
            st.markdown('<p style="color:#444;font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem">No documents uploaded yet.</p>', unsafe_allow_html=True)
        else:
            for doc in reversed(uploaded_docs):
                vec_badge = "✓ vectorized" if doc.get("vectorized") else "· not vectorized"
                vec_color = "#25d366" if doc.get("vectorized") else "#555"
                st.markdown(f"""
<div class="doc-card">
  <div class="doc-name">{doc['filename']}</div>
  <div class="doc-meta">
    <span class="badge badge-pdf">{doc['doc_type']}</span>
    {doc.get('client_tag','')} · {doc.get('size_kb','?')} KB ·
    <span style="color:{vec_color}">{vec_badge}</span>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — Dispatch / Thinker / Email / Meta-Analysis
# ══════════════════════════════════════════════════════════════════════════════

with col_right:
    tab_dispatch, tab_thinker, tab_email, tab_meta = st.tabs([
        "Strategic Dispatch", "Thinker Partner", "Email Dispatch", "Meta-Analysis"
    ])

    # ── DISPATCH ─────────────────────────────────────────────────────────────
    with tab_dispatch:
        st.markdown('<div class="col-label">Countercurrent Analysis</div>', unsafe_allow_html=True)

        topic = st.text_input("Focus topic", placeholder="e.g. Gen Z brand trust, creator economy…", key="dispatch_topic")

        d1, d2, d3 = st.columns([1, 1, 2])
        with d1:
            run_dispatch = st.button("⟳  Generate")
        with d2:
            if st.button("Clear") and st.session_state.dispatch_cache:
                st.session_state.dispatch_cache = {}

        if run_dispatch:
            if not signals:
                st.warning("No signals found. Run ingestion.py first.")
            else:
                with st.spinner("Reading the currents…"):
                    # Try RAG first, fall back to simple context
                    rag_results = semantic_search(topic or "cultural trends brand strategy", top_k=10)
                    if rag_results:
                        context = build_rag_context(rag_results)
                        context_note = f"_(using semantic search — {len(rag_results)} relevant chunks retrieved)_"
                    else:
                        context = build_simple_context(signals, limit=20)
                        context_note = "_(using latest signals — connect Pinecone for semantic search)_"

                    user_msg = f"""
Here are the most relevant signals from the knowledge base:

{context}

{'Focus on: ' + topic if topic else 'Identify the dominant cultural current.'}

Generate the Countercurrent dispatch.
"""
                    result = call_llm([{"role": "user", "content": user_msg}], COUNTERCURRENT_SYSTEM_PROMPT)
                    st.session_state.dispatch_cache["last"] = result
                    st.session_state.dispatch_cache["topic"] = topic
                    save_dispatch(result, topic or "general")

        if st.session_state.dispatch_cache.get("last"):
            import re
            raw = st.session_state.dispatch_cache["last"]

            def extract(label, text):
                m = re.search(rf"\*\*{label}:\*\*\s*(.*?)(?=\*\*[A-Z]|\Z)", text, re.DOTALL)
                return m.group(1).strip() if m else ""

            current_text   = extract("THE CURRENT", raw)
            signals_text   = extract("SIGNALS DRIVING IT", raw)
            counter_text   = extract("THE COUNTERCURRENT", raw)
            rationale_text = extract("STRATEGIC RATIONALE", raw)

            if current_text:
                st.markdown(f"""
<div class="dispatch-card">
  <div class="dispatch-current">▲ The Current</div>
  <div class="dispatch-heading">{current_text}</div>
  <div class="dispatch-body">{signals_text.replace(chr(10), '<br>')}</div>
  <div class="countercurrent-label">⟳ The Countercurrent</div>
  <div class="countercurrent-text">{counter_text}</div>
  <div class="dispatch-body" style="margin-top:0.8rem">{rationale_text}</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(raw)

            st.download_button("↓ Export Markdown", data=raw,
                file_name=f"dispatch_{datetime.utcnow().strftime('%Y%m%d')}.md", mime="text/markdown")

    # ── THINKER PARTNER ───────────────────────────────────────────────────────
    with tab_thinker:
        st.markdown('<div class="col-label">Chat with the Knowledge Base</div>', unsafe_allow_html=True)

        brief = st.text_area("Active brief", placeholder="Brief: Launch a challenger brand in…", height=72, key="brief_context")

        use_semantic = st.checkbox("Use semantic search (requires Pinecone)", value=True, key="use_semantic")

        for msg in st.session_state.chat_history:
            cls = "chat-msg-user" if msg["role"] == "user" else "chat-msg-ai"
            st.markdown(f'<div class="{cls}"><span>{msg["content"]}</span></div>', unsafe_allow_html=True)

        prompt = st.text_input("Ask the data lake…", placeholder="What tensions exist in the wellness space?", key="thinker_input", label_visibility="collapsed")

        t1, t2 = st.columns([1, 1])
        with t1:
            send = st.button("Send  →")
        with t2:
            if st.button("Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

        if send and prompt:
            with st.spinner("Searching knowledge base…"):
                if use_semantic:
                    rag_results = semantic_search(prompt, top_k=8,
                        client_filter=client_filter if client_filter != "All clients" else None)
                    st.session_state.rag_results = rag_results
                    context = build_rag_context(rag_results) if rag_results else build_simple_context(signals)
                else:
                    context = build_simple_context(signals)
                    st.session_state.rag_results = []

                enriched = f"""
BRIEF: {brief or 'None provided.'}

KNOWLEDGE BASE CONTEXT:
{context}

QUESTION: {prompt}
"""
                history_for_api = [
                    *st.session_state.chat_history[:-1],
                    {"role": "user", "content": enriched}
                ]

                st.session_state.chat_history.append({"role": "user", "content": prompt})
                reply = call_llm(history_for_api, THINKER_SYSTEM_PROMPT, temperature=0.8)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.rerun()

        # Show retrieved sources
        if st.session_state.rag_results:
            with st.expander(f"📎 {len(st.session_state.rag_results)} sources retrieved"):
                for r in st.session_state.rag_results:
                    st.markdown(f"""
<div class="rag-result">
  <div class="rag-score">relevance {r['score']:.2f} · {r.get('source','?').upper()}</div>
  <div class="rag-text">{r['text'][:280]}…</div>
  <div class="rag-meta">{r.get('title','')[:80]} · {r.get('client_tag','')}</div>
</div>""", unsafe_allow_html=True)

    # ── EMAIL DISPATCH ────────────────────────────────────────────────────────
    with tab_email:
        st.markdown('<div class="col-label">Weekly Email Dispatch</div>', unsafe_allow_html=True)

        if not st.session_state.dispatch_cache.get("last"):
            st.markdown('<p style="color:#555;font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem">Generate a dispatch first in the Strategic Dispatch tab.</p>', unsafe_allow_html=True)
        else:
            raw_dispatch = st.session_state.dispatch_cache["last"]
            week_label = datetime.utcnow().strftime("Week of %d %b %Y")
            html_email = markdown_to_email_html(raw_dispatch, week_label)

            # Preview
            with st.expander("Preview email", expanded=True):
                st.components.v1.html(html_email, height=500, scrolling=True)

            # Send form
            st.markdown("---")
            email_to = st.text_input("Send to", placeholder="strategist@agency.com", key="email_to")
            email_subject = st.text_input("Subject", value=f"Countercurrent Dispatch · {week_label}", key="email_subject")

            sg_configured = bool(os.environ.get("SENDGRID_API_KEY"))
            if not sg_configured:
                st.info("💡 Add SENDGRID_API_KEY to your .env to enable sending. Download the HTML to send manually in the meantime.")

            e1, e2 = st.columns([1, 1])
            with e1:
                if st.button("Send via SendGrid") and email_to:
                    if not sg_configured:
                        st.error("SENDGRID_API_KEY not configured.")
                    else:
                        with st.spinner("Sending…"):
                            ok = send_email_sendgrid(email_to, email_subject, html_email)
                        if ok:
                            st.success(f"✓ Dispatch sent to {email_to}")
                        else:
                            st.error("Send failed. Check your SendGrid key and FROM email.")
            with e2:
                st.download_button("↓ Download HTML", data=html_email,
                    file_name=f"dispatch_{datetime.utcnow().strftime('%Y%m%d')}.html", mime="text/html")

    # ── META-ANALYSIS ─────────────────────────────────────────────────────────
    with tab_meta:
        st.markdown('<div class="col-label">Meta-Analysis — Dispatches Over Time</div>', unsafe_allow_html=True)

        if len(dispatches) < 2:
            st.markdown(f'<p style="color:#555;font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem">Need at least 2 dispatches for meta-analysis. You have {len(dispatches)} so far.</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color:#666;font-size:0.8rem">{len(dispatches)} dispatches available for analysis.</p>', unsafe_allow_html=True)

            meta_brief = st.text_area("Brief to analyse against", placeholder="What should we recommend to a challenger brand in the food space?", height=80, key="meta_brief")

            if st.button("⟳  Run Meta-Analysis"):
                with st.spinner("Analysing patterns across all dispatches…"):
                    # Build a compressed summary of all dispatches
                    all_dispatch_text = ""
                    for i, d in enumerate(dispatches[-20:]):  # last 20 dispatches
                        ts = d.get("timestamp", "")[:10]
                        topic_label = d.get("topic") or "general"
                        all_dispatch_text += f"\n\n--- DISPATCH {i+1} ({ts} · {topic_label}) ---\n{d['content'][:600]}"

                    user_msg = f"""
Here are {len(dispatches)} Countercurrent dispatches from recent weeks:

{all_dispatch_text}

{'Brief to analyse against: ' + meta_brief if meta_brief else 'Identify macro patterns without a specific brief.'}

Conduct the meta-analysis.
"""
                    result = call_llm([{"role": "user", "content": user_msg}], META_ANALYSIS_SYSTEM_PROMPT, temperature=0.7)
                    st.session_state["meta_result"] = result

            if st.session_state.get("meta_result"):
                st.markdown("---")
                st.markdown(st.session_state["meta_result"])
                st.download_button("↓ Export Meta-Analysis", data=st.session_state["meta_result"],
                    file_name=f"meta_analysis_{datetime.utcnow().strftime('%Y%m%d')}.md", mime="text/markdown")

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="border-top:1px solid #1a1a1a;margin-top:3rem;padding-top:1rem;
     font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#333;
     display:flex;justify-content:space-between">
  <span>COUNTERCURRENT.AI v2 — ATLANTIC INTELLIGENCE LAYER</span>
  <span>SIGNAL → VECTOR → DISPATCH → INSIGHT</span>
</div>
""", unsafe_allow_html=True)
