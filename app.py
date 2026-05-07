import os
import json
import requests
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Countercurrent.ai", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PARA SCROLL (HACK MAIS FORTE) ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    .signal-card {
        background: #111; border: 1px solid #222;
        padding: 12px; border-radius: 6px; margin-bottom: 10px;
    }
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.65rem; text-transform: uppercase; }
    .signal-title { font-weight: bold; color: #f0ebe2; font-size: 0.9rem; }
    
    /* ROLAGEM INDEPENDENTE */
    [data-testid="stVerticalBlock"] > div > div > [data-testid="stVerticalBlock"] {
        max-height: 75vh !important;
        overflow-y: auto !important;
        padding-right: 15px;
    }
    .insight-box {
        background: #0f0f0a; border: 1px solid #2a2a1e;
        padding: 20px; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO LLM VIA API DIRETA (SEM DEPENDER DE BIBLIOTECA) ---
def call_llm(user_query, system_instruction):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY faltando."
    
    # URL da API estável
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"Instruction: {system_instruction}\n\nUser Query: {user_query}"}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        response_data = response.json()
        return response_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"⚠️ Erro na API: {str(e)}"

def load_signals():
    path = "data/signals.jsonl"
    if not os.path.exists(path): return []
    signals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try: signals.append(json.loads(line))
            except: pass
    return sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)

# --- UI ---
st.title("⟳ Countercurrent.ai")
st.caption("Wire Room v2.9 — REST API Edition")

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Mixed Feed")
    st.write("") # Anchor
    if signals:
        by_source = {}
        for s in signals:
            src = s.get("source", "web"); by_source.setdefault(src, []).append(s)
        mixed = [i for sub in zip_longest(*by_source.values()) for i in sub if i]
        for sig in mixed[:40]:
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'NYL')}</div>
                <div class="signal-title">{sig.get('title')}</div>
                <div class="signal-content" style="color:#888; font-size:0.8rem;">{sig.get('content', '')[:150]}...</div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("Strategic Insights")
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Analyzing..."):
                context = "\n".join([f"- {s.get('title')}" for s in signals[:12]])
                st.session_state.auto_insight = call_llm(
                    f"Analyze these signals for NY Liberty: {context}", 
                    "You are a trend spotter. Style: Hemingway. Give 2 currents and 3 counter-provocations."
                )
        st.markdown(st.session_state.auto_insight)
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    with tab1:
        topic = st.text_input("Topic", "WNBA x Fashion")
        if st.button("Run Dispatch"):
            st.markdown(call_llm(topic, "Style: Hemingway. Countercurrent strategy."))
