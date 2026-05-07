import os
import json
import requests
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Countercurrent.ai", layout="wide", initial_sidebar_state="collapsed")

# --- CSS DEFINITIVO PARA LAYOUT E ROLAGEM ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    
    /* ESTE BLOCO FORÇA A ROLAGEM NA COLUNA DA ESQUERDA */
    [data-testid="stVerticalBlock"] > div:nth-child(1) > [data-testid="stVerticalBlock"] {
        max-height: 80vh !important;
        overflow-y: auto !important;
        padding-right: 10px;
    }
    
    .signal-card {
        background: #111; border: 1px solid #222;
        padding: 12px; border-radius: 6px; margin-bottom: 10px;
    }
    
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.65rem; text-transform: uppercase; }
    .signal-title { font-weight: bold; color: #f0ebe2; font-size: 0.9rem; }
    
    .insight-box {
        background: #0f100a; border: 1px solid #2a2a1e;
        padding: 20px; border-radius: 8px; margin-bottom: 15px;
    }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: #444; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO LLM (ROTA ULTRA-ESTÁVEL) ---
def call_llm(user_query, system_instruction):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY faltando."
    
    # Mudamos para a rota v1 (estável) e o modelo gemini-pro que é universal
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"System: {system_instruction}\n\nUser: {user_query}"}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        data = response.json()
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            # Caso o Pro falhe, tentamos a última cartada com o nome genérico do Flash
            url_alt = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            response = requests.post(url_alt, json=payload, timeout=20)
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"⚠️ Erro de conexão ou API Key inválida: {str(e)}"

def load_signals():
    path = "data/signals.jsonl"
    if not os.path.exists(path): return []
    signals = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try: signals.append(json.loads(line))
                except: pass
    except: return []
    return sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)

# --- UI ---
st.title("⟳ Countercurrent.ai")
st.caption("Wire Room v3.1 — Stable Engine")

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Mixed Feed")
    
    if signals:
        sources = sorted(list({s.get("source", "web") for s in signals}))
        selected_source = st.selectbox("Filter Network", ["All Networks"] + sources)
        
        filtered = signals
        if selected_source != "All Networks":
            filtered = [s for s in signals if s.get("source") == selected_source]
        
        # Lógica Mixed
        if selected_source == "All Networks":
            by_src = {}
            for s in filtered:
                src = s.get("source", "web"); by_src.setdefault(src, []).append(s)
            display_list = [i for sub in zip_longest(*by_source.values()) for i in sub if i] # Corrigido aqui
        else:
            display_list = filtered

        # Listagem (A rolagem agora é automática pelo CSS do VerticalBlock)
        for sig in display_list[:50]:
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'NYL')}</div>
                <div class="signal-title">{sig.get('title')}</div>
                <div style="color:#888; font-size:0.8rem; margin-top:5px;">{sig.get('content', '')[:160]}...</div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("Strategic Intelligence")
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Analyzing..."):
                context = "\n".join([f"- {s.get('title')}" for s in signals[:15]])
                st.session_state.auto_insight = call_llm(
                    f"Analyze for NY Liberty: {context}", 
                    "You are a trend spotter. Style: Hemingway. Give 2 currents and 3 counter-provocations."
                )
        st.markdown(st.session_state.auto_insight)
    st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    with tab1:
        topic = st.text_input("Topic", "WNBA x Pinterest Trends")
        if st.button("Run Dispatch"):
            st.markdown(call_llm(topic, "Style: Hemingway. Strategic Countercurrent."))
    
    with tab2:
        st.text_input("Interrogate Lake", key="lake_chat")
        st.button("Search")

    with tab3:
        st.markdown("**Meta-Analysis Mode**")
        st.button("Cross-Reference Patterns")
