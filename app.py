"""
Countercurrent.ai — Wire Room v2.5
- Fixed heights with independent scrolling
- 3 Instant Provocations (Countercurrents)
- Large text for Emerging Currents
- Hemingway Style + Gemini 2.5 Flash
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

# ── CSS — Layout e Estética ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    background-color: #0a0a0a !important;
    color: #d4cfc7 !important;
    font-family: 'DM Sans', sans-serif;
    overflow: hidden; /* Evita scroll na página inteira */
}

/* Containers com Scroll Fixo */
.feed-container, .intel-container {
    height: 82vh;
    overflow-y: auto;
    padding-right: 15px;
}
.feed-container::-webkit-scrollbar, .intel-container::-webkit-scrollbar { width: 4px; }
.feed-container::-webkit-scrollbar-thumb, .intel-container::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }

.wire-header {
    display: flex; align-items: baseline; gap: 1.2rem;
    border-bottom: 1px solid #2a2a2a; padding-bottom: 0.5rem; margin-bottom: 1rem;
}
.wire-header h1 {
    font-family: 'DM Serif Display', serif; font-size: 1.8rem;
    color: #f0ebe2; letter-spacing: -0.02em; margin: 0;
}
.wire-header .tagline {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    color: #e8a838; letter-spacing: 0.12em; text-transform: uppercase;
}

.col-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.18em; text-transform: uppercase; color: #666;
    border-bottom: 1px solid #1e1e1e; padding-bottom: 0.5rem; margin-bottom: 1rem;
}

/* Signal Cards */
.signal-card {
    background: #111111; border: 1px solid #1e1e1e;
    border-left: 3px solid #2a2a2a; border-radius: 3px;
    padding: 0.8rem 1rem; margin-bottom: 0.8rem;
}
.signal-source { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; color: #e8a838; text-transform: uppercase; }
.signal-title { font-size: 0.85rem; color: #e0dbd3; font-weight: 500; margin-top: 0.3rem; }
.signal-snippet { font-size: 0.75rem; color: #777; line-height: 1.5; margin-top: 0.3rem; }

.badge {
    display: inline-block; padding: 0.1rem 0.4rem; border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.55rem;
    text-transform: uppercase; margin-right: 0.3rem;
}
.badge-reddit   { background: #1a0f0f; color: #ff4500; border: 1px solid #331a1a; }
.badge-tiktok   { background: #0f1a12; color: #25d366; border: 1px solid #1a3324; }

/* Inteligência Direita */
.auto-current-box {
    background: #0f0f0a; border: 1px solid #2a2a1e;
    border-radius: 4px; padding: 1.2rem; margin-bottom: 1.5rem;
}
.current-large-text {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem; color: #f0ebe2; line-height: 1.3; margin-bottom: 1rem;
}
.provocation-box {
    background: #1a0f1a; border-left: 3px solid #c44aff;
    padding: 0.8rem; margin-top: 1rem; font-style: italic; font-size: 0.9rem; color: #c8b8e8;
}

.stTabs [data-baseweb="tab-list"] { gap: 10px; }
.stTabs [data-baseweb="tab"] { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ── Helpers e LLM ──────────────────────────────────────────────────────────────

def call_llm(messages, system, temperature=0.7):
    import google.generativeai as genai
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY Missing"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system)
    
    history = []
    for msg in messages[:-1]:
        history.append({"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]})
    
    chat = model.start_chat(history=history)
    try:
        response = chat.send_message(messages[-1]["content"])
        return response.text
    except Exception as e: return f"⚠️ Error: {e}"

def load_signals():
    path = "data/signals.jsonl"
    if not os.path.exists(path): return []
    data = []
    with open(path) as f:
        for line in f:
            try: data.append(json.loads(line))
            except: pass
    data.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return data

def build_context(signals, limit=15):
    return "\n".join([f"- {s.get('title','')}: {s.get('content','')[:150]}" for s in signals[:limit]])

# ── Prompts — Hemingway Style ──────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Countercurrent. Write in a style like Hemingway: short, punchy, plainspoken.
Identify 'The Current' (mainstream) and 'The Countercurrent' (provocation). 
Always use direct quotes and citations if available."""

# ── Layout Principal ───────────────────────────────────────────────────────────

st.markdown('<div class="wire-header"><h1>Countercurrent.ai</h1><span class="tagline">Intelligence Wire Room v2.5</span></div>', unsafe_allow_html=True)

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# COLUNA ESQUERDA: Mixed Feed com Scroll
# ══════════════════════════════════════════════════════════════════════════════
with col_left:
    st.markdown('<div class="col-label">Global Mixed Feed</div>', unsafe_allow_html=True)
    
    # Filtros simples
    sources = sorted(list({s.get("source", "web") for s in signals}))
    sel_source = st.selectbox("Filter Source", ["All Sources"] + sources)
    
    filtered = signals
    if sel_source != "All Sources":
        filtered = [s for s in filtered if s.get("source") == sel_source]

    # Container com Scroll
    st.markdown('<div class="feed-container">', unsafe_allow_html=True)
    if not filtered:
        st.info("No signals found.")
    else:
        # Lógica de interclação
        by_source = {}
        for s in filtered:
            src = s.get("source", "web"); by_source.setdefault(src, []).append(s)
        mixed = [i for s in zip_longest(*by_source.values()) for i in s if i]

        for sig in mixed[:50]:
            src = sig.get("source", "web")
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source">{src} · {sig.get('client_tag','')}</div>
                <div class="signal-title">{sig.get('title','')}</div>
                <div class="signal-snippet">{sig.get('content','')[:180]}...</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COLUNA DIREITA: Inteligência + 3 Provocações
# ══════════════════════════════════════════════════════════════════════════════
with col_right:
    st.markdown('<div class="intel-container">', unsafe_allow_html=True)
    
    # PARTE SUPERIOR: AUTO-CURRENTS
    st.markdown('<div class="auto-current-box"><div class="col-label" style="color:#e8a838">⚡ Emerging Currents</div>', unsafe_allow_html=True)
    
    if signals:
        ctx = build_context(signals, limit=12)
        if "auto_data" not in st.session_state:
            with st.spinner("Decoding signals..."):
                curr_prompt = f"Identify 2 main currents and 3 short countercurrent provocations from: {ctx}"
                res = call_llm([{"role": "user", "content": curr_prompt}], "Respond in clean markdown.")
                st.session_state.auto_data = res
        
        st.markdown(f'<div class="current-large-text">{st.session_state.auto_data}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # PARTE INFERIOR: ABAS DE TRABALHO
    t1, t2, t3 = st.tabs(["Strategic Dispatch", "Thinker Partner", "Meta-Analysis"])
    
    with t1:
        topic = st.text_input("Focus Topic", value="WNBA x High Fashion")
        if st.button("Generate Dispatch"):
            with st.spinner("Analyzing..."):
                res = call_llm([{"role": "user", "content": f"Topic: {topic}\nContext: {build_context(signals)}"}], SYSTEM_PROMPT)
                st.session_state.last_dispatch = res
        if "last_dispatch" in st.session_state:
            st.markdown(st.session_state.last_dispatch)

    with t2:
        st.markdown('<div class="col-label">Chat with Data Lake</div>', unsafe_allow_html=True)
        # Lógica simples de chat aqui...
        st.text_input("Ask anything...", key="chat_input")

    st.markdown('</div>', unsafe_allow_html=True)
