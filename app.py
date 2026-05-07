import os
import json
import requests
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Countercurrent.ai", layout="wide", initial_sidebar_state="collapsed")

# --- CSS — Estética Wire Room ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    .signal-card {
        background: #111; border: 1px solid #222;
        padding: 12px; border-radius: 6px; margin-bottom: 10px;
    }
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.65rem; text-transform: uppercase; font-weight: bold; }
    .signal-title { font-weight: bold; color: #f0ebe2; font-size: 0.9rem; margin-top: 4px; }
    .insight-box {
        background: #0f100a; border: 1px solid #2a2a1e;
        padding: 20px; border-radius: 8px; margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { font-family: monospace; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO LLM (ROTA VALIDADA PELO SEU TESTE) ---
def call_llm(user_query, system_instruction):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY não encontrada."
    
    # Rota exata para o modelo que apareceu no seu teste
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"SYSTEM INSTRUCTION: {system_instruction}\n\nUSER QUERY: {user_query}"}]
        }],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
    }
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        data = response.json()
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        return f"⚠️ Erro do Google: {data.get('error', {}).get('message', 'Erro desconhecido')}"
    except Exception as e:
        return f"⚠️ Falha: {str(e)}"

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

# --- UI HEADER ---
st.title("⟳ Countercurrent.ai")
st.caption("Wire Room v3.5 — Gemini 2.5 Flash Engine")

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

# --- COLUNA ESQUERDA (FEED + SCROLL) ---
with col_left:
    st.subheader("Global Mixed Feed")
    
    if signals:
        sources = sorted(list({s.get("source", "web") for s in signals}))
        selected_source = st.selectbox("Filter Network", ["All Networks"] + sources)
        
        filtered = [s for s in signals if selected_source == "All Networks" or s.get("source") == selected_source]
        
        # CONTAINER DE SCROLL NATIVO (Altura fixa)
        with st.container(height=650):
            if selected_source == "All Networks":
                by_src = {}
                for s in filtered:
                    src = s.get("source", "web"); by_src.setdefault(src, []).append(s)
                display_list = [i for sub in zip_longest(*by_src.values()) for i in sub if i]
            else:
                display_list = filtered

            for sig in display_list[:60]:
                st.markdown(f"""
                <div class="signal-card">
                    <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'NYL')}</div>
                    <div class="signal-title">{sig.get('title')}</div>
                    <div style="color:#888; font-size:0.8rem; margin-top:5px;">{sig.get('content', '')[:160]}...</div>
                </div>
                """, unsafe_allow_html=True)

# --- COLUNA DIREITA (INTELIGÊNCIA) ---
# ══════════════════════════════════════════════════════════════════════════════
# COLUNA DIREITA: Inteligência Estratégica (v3.6)
# ══════════════════════════════════════════════════════════════════════════════
with col_right:
    st.subheader("Strategic Intelligence")
    
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Decoding cultural shifts..."):
                ctx = "\n".join([f"- {s.get('title')}" for s in signals[:15]])
                # Prompt ajustado para 3+3 como você pediu
                prompt = (
                    "Based on these signals, identify 3 'Cultural Shifts' (the current trend) "
                    "and 3 'Countercurrent Shifts' (the contrarian provocations). "
                    "Style: Hemingway. Be punchy. Use markdown bold for headlines."
                )
                st.session_state.auto_insight = call_llm(ctx, prompt)
        
        # Agora colocamos TODO o conteúdo dentro da caixa cinza
        st.markdown(f"""
        <div class="insight-box">
            <div style="font-family:monospace; color:#e8a838; font-size:0.7rem; margin-bottom:10px; text-transform:uppercase;">
                ⚡ Automated Intelligence Report
            </div>
            {st.session_state.auto_insight}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aguardando sinais para análise.")

    # Tabs Inferiores
    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    # ... (mantenha o código das abas como estava)
        st.markdown("**Meta-Analysis Mode**")
        st.button("Run Historical Cross-Reference")
