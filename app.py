import os
import json
import requests
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Countercurrent.ai", layout="wide", initial_sidebar_state="collapsed")

# --- CSS — Ajustado para Links e Containers ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #d4cfc7; }
    
    /* Card do Feed com Link */
    .signal-card {
        background: #111; border: 1px solid #222;
        padding: 12px; border-radius: 6px; margin-bottom: 10px;
        transition: 0.3s;
    }
    .signal-card:hover { border-color: #e8a838; background: #151515; }
    .signal-link { text-decoration: none; color: inherit; }
    
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.65rem; text-transform: uppercase; font-weight: bold; }
    .signal-title { font-weight: bold; color: #f0ebe2; font-size: 0.9rem; margin-top: 4px; }
    
    /* Caixa de Inteligência */
    .insight-box {
        background: #0f100a; border: 1px solid #2a2a1e;
        padding: 20px; border-radius: 8px; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

def call_llm(user_query, system_instruction):
    api_key = os.environ.get("GOOGLE_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": f"Instruction: {system_instruction}\n\nQuery: {user_query}"}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except: return "⚠️ Falha ao gerar insights."

def load_signals():
    path = "data/signals.jsonl"
    if not os.path.exists(path): return []
    signals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try: signals.append(json.loads(line))
            except: pass
    return sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)

st.title("⟳ Countercurrent.ai")
st.caption("Wire Room v3.9 — Strategic Link Enabled")

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

# --- COLUNA ESQUERDA (FEED COM LINKS REATIVADOS) ---
with col_left:
    st.subheader("Global Mixed Feed")
    if signals:
        sources = sorted(list({s.get("source", "web") for s in signals}))
        selected_source = st.selectbox("Filter Network", ["All Networks"] + sources)
        filtered = [s for s in signals if selected_source == "All Networks" or s.get("source") == selected_source]
        
        with st.container(height=650):
            if selected_source == "All Networks":
                by_src = {}
                for s in filtered:
                    src = s.get("source", "web"); by_src.setdefault(src, []).append(s)
                display_list = [i for sub in zip_longest(*by_src.values()) for i in sub if i]
            else: display_list = filtered

            for sig in display_list[:60]:
                target_url = sig.get('url', '#')
                st.markdown(f"""
                <a href="{target_url}" target="_blank" class="signal-link">
                    <div class="signal-card">
                        <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'NYL')}</div>
                        <div class="signal-title">{sig.get('title')}</div>
                        <div style="color:#888; font-size:0.8rem; margin-top:5px;">{sig.get('content', '')[:150]}...</div>
                    </div>
                </a>
                """, unsafe_allow_html=True)

# --- COLUNA DIREITA (INTELIGÊNCIA COM FIX DE DIAGRAMAÇÃO) ---
with col_right:
    st.subheader("Strategic Intelligence")
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Analyzing..."):
                ctx = "\n".join([f"- {s.get('title')}" for s in signals[:15]])
                prompt = "Identify 3 Cultural Shifts and 3 Countercurrent Shifts. Style: Hemingway. Use markdown bold for headlines."
                st.session_state.auto_insight = call_llm(ctx, prompt)
        
        # O segredo para não quebrar: Header e Conteúdo em blocos HTML separados, mas visualmente unidos
        st.markdown(f"""
        <div style="background:#0f100a; border:1px solid #2a2a1e; border-bottom:none; padding:20px 20px 0px 20px; border-radius:8px 8px 0 0;">
            <div style="font-family:monospace; color:#e8a838; font-size:0.7rem; text-transform:uppercase; border-bottom:1px solid #2a2a1e; padding-bottom:5px;">
                ⚡ Automated Intelligence Report
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True): # Usando o container nativo para envolver o texto da IA
            st.markdown(st.session_state.auto_insight)
    
    # Abas
    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    with tab1:
        topic = st.text_input("Topic", "WNBA Trends")
        if st.button("Run Dispatch"):
            res = call_llm(topic, "Style: Hemingway. Strategic Countercurrent.")
            st.info(res)
