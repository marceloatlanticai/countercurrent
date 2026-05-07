import os
import json
import requests
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Countercurrent.ai", layout="wide", initial_sidebar_state="collapsed")

# --- CSS DEFINITIVO PARA LAYOUT E SCROLL ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    
    /* Container para forçar o Scroll Independente */
    .scroll-container {
        max-height: 72vh;
        overflow-y: auto;
        padding-right: 15px;
        display: block;
    }
    
    .signal-card {
        background: #111; border: 1px solid #222;
        padding: 12px; border-radius: 6px; margin-bottom: 10px;
    }
    
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.65rem; text-transform: uppercase; }
    .signal-title { font-weight: bold; color: #f0ebe2; font-size: 0.9rem; margin-top: 4px; }
    
    .insight-box {
        background: #0f100a; border: 1px solid #2a2a1e;
        padding: 20px; border-radius: 8px; margin-bottom: 15px;
    }

    /* Estilo da Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO LLM COM TRATAMENTO DE ERRO MELHORADO ---
def call_llm(user_query, system_instruction):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY faltando."
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": f"Instruction: {system_instruction}\n\nUser Query: {user_query}"}]}],
        "safetySettings": [ # Desativa filtros para evitar erro 'candidates' por bloqueio de segurança bobo
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"⚠️ Erro do Google: {data.get('error', {}).get('message', 'Resposta vazia')}"
    except Exception as e:
        return f"⚠️ Erro de Conexão: {str(e)}"

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

# --- UI PRINCIPAL ---
st.title("⟳ Countercurrent.ai")
st.caption("Wire Room v3.0 — High Performance Edition")

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

# --- COLUNA ESQUERDA (FEED + FILTRO) ---
with col_left:
    st.subheader("Global Mixed Feed")
    
    # 1. Filtro por Canal (RESTAURADO)
    if signals:
        sources = sorted(list({s.get("source", "web") for s in signals}))
        selected_source = st.selectbox("Select Network", ["All Networks"] + sources)
        
        filtered = signals
        if selected_source != "All Networks":
            filtered = [s for s in signals if s.get("source") == selected_source]
        
        # 2. Feed com Barra de Rolagem (RESTAURADA)
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        
        # Lógica de Intercalação se for "All"
        if selected_source == "All Networks":
            by_src = {}
            for s in filtered:
                src = s.get("source", "web"); by_src.setdefault(src, []).append(s)
            display_list = [i for sub in zip_longest(*by_src.values()) for i in sub if i]
        else:
            display_list = filtered

        for sig in display_list[:50]:
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'NYL')}</div>
                <div class="signal-title">{sig.get('title')}</div>
                <div style="color:#888; font-size:0.8rem; margin-top:5px;">{sig.get('content', '')[:160]}...</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- COLUNA DIREITA (INSIGHTS) ---
with col_right:
    st.subheader("Strategic Intelligence")
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Decoding currents..."):
                context = "\n".join([f"- {s.get('title')}" for s in signals[:12]])
                st.session_state.auto_insight = call_llm(
                    f"Analyze for NY Liberty: {context}", 
                    "Style: Hemingway. Give 2 currents and 3 counter-provocations."
                )
        st.markdown(st.session_state.auto_insight)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabs Inferiores (RESTURADAS)
    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    with tab1:
        topic = st.text_input("Topic", "WNBA x Fashion Intersection")
        if st.button("Run Strategic Dispatch"):
            st.markdown(call_llm(topic, "Style: Hemingway. Provide current vs countercurrent."))
    
    with tab2:
        st.text_input("Interrogate Data Lake", key="lake_chat")
        st.button("Inquire")

    with tab3:
        st.markdown("**Meta-Analysis Mode**")
        st.button("Analyze History")
