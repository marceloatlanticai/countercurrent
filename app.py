"""
Countercurrent.ai — Layer 3 (v2.2): The Wire Room 
Updated: Gemini 2.5 Flash + Mixed Feed + Dual Intelligence Layer
"""

import os
import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Optional
from itertools import zip_longest

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Streamlit Cloud: Secrets injection
try:
    for key, value in st.secrets.items():
        if key not in os.environ:
            os.environ[key] = str(value)
except Exception:
    pass 

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Countercurrent.ai",
    page_icon="⟳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS — Wire Room aesthetic ─────────────────────────────────────────────────

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
.badge-tiktok   { background: #0f1a12; color: #25d366; border: 1px solid #1a2a1e; }
.badge-web      { background: #1a1a0f; color: #e8c438; border: 1px solid #2a2a1a; }
.badge-pdf      { background: #1a0f1a; color: #c44aff; border: 1px solid #2a1a2a; }
.badge-youtube   { background: #1a0a0a; color: #ff4444; border: 1px solid #2a1a1a; }
.badge-rss       { background: #1a1200; color: #ffaa00; border: 1px solid #2a2000; }
.badge-discord   { background: #0f1a2a; color: #5865f2; border: 1px solid #1a2a3a; }

/* AUTO CURRENT BOX (Right Side Top) */
.auto-current-box {
    background: linear-gradient(145deg, #151510, #0a0a0a);
    border: 1px solid #e8a83830;
    border-radius: 4px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
}
.auto-current-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #e8a838;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 0.8rem;
}
.current-pill {
    display: inline-block;
    background: #1a1a1a;
    border: 1px solid #333;
    padding: 0.4rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    color: #d4cfc7;
    font-family: 'IBM Plex Mono', monospace;
}

.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers & AI ──────────────────────────────────────────────────────────────

BADGE_MAP = {
    "reddit": "badge-reddit", "tiktok": "badge-tiktok", "web": "badge-web",
    "pdf": "badge-pdf", "youtube": "badge-youtube", "rss": "badge-rss",
    "discord": "badge-discord"
}

def call_llm(messages: list[dict], system: str, temperature: float = 0.7) -> str:
    import google.generativeai as genai
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ GOOGLE_API_KEY Missing"
    genai.configure(api_key=api_key)
    
    # CORREÇÃO AQUI: gemini-2.5-flash
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system
    )
    
    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    
    chat = model.start_chat(history=history)
    try:
        response = chat.send_message(messages[-1]["content"])
        return response.text
    except Exception as e:
        return f"⚠️ API Error: {e}"

def load_signals(path: str = "data/signals.jsonl", limit: int = 300) -> list[dict]:
    if not os.path.exists(path): return []
    signals = []
    with open(path) as f:
        for line in f:
            try: signals.append(json.loads(line))
            except: pass
    signals.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return signals[:limit]

def build_simple_context(signals: list[dict], limit: int = 15) -> str:
    return "\n".join([f"- {s.get('title','')}: {s.get('content','')[:200]}" for s in signals[:limit]])

# ── PROMPTS ───────────────────────────────────────────────────────────────────

COUNTERCURRENT_SYSTEM_PROMPT = """You are Countercurrent AI. 
1. Identify THE CURRENT (mainstream narrative). 
2. Propose THE COUNTERCURRENT (unexpected provocation).
Structure: **THE CURRENT:**, **SIGNALS:**, **THE COUNTERCURRENT:**, **RATIONALE:**."""

THINKER_SYSTEM_PROMPT = "You are a strategic creative director. Sharp, incisive, and curiosity-driven."

# ── Session State ─────────────────────────────────────────────────────────────

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "dispatch_cache" not in st.session_state: st.session_state.dispatch_cache = {}

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""<div class="wire-header"><h1>Countercurrent.ai</h1><span class="tagline">Intelligence Wire Room · v2.2</span></div>""", unsafe_allow_html=True)

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN — Mixed Feed
# ══════════════════════════════════════════════════════════════════════════════

with col_left:
    st.markdown('<div class="col-label">Global Mixed Feed (WNBA x NY Liberty)</div>', unsafe_allow_html=True)
    
    if not signals:
        st.info("No signals. Run ingestion.py first.")
    else:
        # MIXED FEED LOGIC: Interleave by source
        by_source = {}
        for s in signals:
            src = s.get("source", "web")
            if src not in by_source: by_source[src] = []
            by_source[src].append(s)
        
        mixed = [item for sublist in zip_longest(*by_source.values()) for item in sublist if item is not None]
        
        for sig in mixed[:40]:
            src = sig.get("source", "web")
            badge = BADGE_MAP.get(src, "badge-web")
            ts = sig.get("timestamp", "")[:16].replace("T", " ")
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source"><span class="badge {badge}">{src}</span> {sig.get('client_tag','')}</div>
                <div class="signal-title">{sig.get('title','')}</div>
                <div class="signal-snippet">{sig.get('content','')[:250]}...</div>
                <div class="signal-ts">{ts}</div>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — Auto-Currents + Intelligence Tabs
# ══════════════════════════════════════════════════════════════════════════════

with col_right:
    # --- TOP: AUTO-DETECTED CURRENTS ---
    st.markdown('<div class="auto-current-box"><div class="auto-current-title">⚡ Emerging Cultural Currents (Real-time)</div>', unsafe_allow_html=True)
    
    if signals:
        auto_ctx = build_simple_context(signals, limit=12)
        auto_prompt = f"Extract 3 very short emerging themes (max 4 words each) from these signals about NY Liberty/WNBA: {auto_ctx}"
        
        if "auto_themes" not in st.session_state:
            with st.spinner("Decoding currents..."):
                res = call_llm([{"role": "user", "content": auto_prompt}], "Return only a comma-separated list.")
                st.session_state.auto_themes = res.split(",")
        
        pills = "".join([f'<span class="current-pill">● {t.strip()}</span>' for t in st.session_state.auto_themes])
        st.markdown(f'<div style="margin-top:-0.5rem">{pills}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown("</div>", unsafe_allow_html=True)

    # --- BOTTOM: STRATEGIC TOOLS TABS ---
    tab_dispatch, tab_thinker, tab_meta = st.tabs(["Strategic Dispatch", "Thinker Partner", "Meta-Analysis"])

    with tab_dispatch:
        topic = st.text_input("Brief / Focus Topic", value="WNBA fan culture and high-fashion intersection")
        if st.button("Generate Countercurrent Analysis"):
            with st.spinner("Thinking..."):
                ctx = build_simple_context(signals, limit=20)
                res = call_llm([{"role": "user", "content": f"Context: {ctx}\nTopic: {topic}"}], COUNTERCURRENT_SYSTEM_PROMPT)
                st.session_state.dispatch_cache["last"] = res
        
        if "last" in st.session_state.dispatch_cache:
            st.markdown(st.session_state.dispatch_cache["last"])

    with tab_thinker:
        st.markdown('<div class="col-label">Interrogate the Data Lake</div>', unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            role = "USER" if m["role"] == "user" else "AI"
            st.markdown(f"**{role}:** {m['content']}")
        
        query = st.text_input("Type your question...", key="chat_in")
        if st.button("Ask Partner"):
            st.session_state.chat_history.append({"role": "user", "content": query})
            ctx = build_simple_context(signals, limit=25)
            ans = call_llm(st.session_state.chat_history, f"Context: {ctx}\n{THINKER_SYSTEM_PROMPT}")
            st.session_state.chat_history.append({"role": "assistant", "content": ans})
            st.rerun()

    with tab_meta:
        st.markdown('<p style="color:#666;font-size:0.8rem">Meta-Analysis cross-references patterns across all stored signals and dispatches.</p>', unsafe_allow_html=True)
        if st.button("Run Meta-Analysis"):
             st.info("Analysis history building... Requires persistent dispatch data.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""<div style="border-top:1px solid #1a1a1a;margin-top:3rem;padding-top:1rem;font-family:monospace;font-size:0.6rem;color:#333;display:flex;justify-content:space-between"><span>COUNTERCURRENT.AI v2.2</span><span>SIGNALS → VECTORS → INSIGHTS</span></div>""", unsafe_allow_html=True)
