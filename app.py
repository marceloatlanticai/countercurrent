import os
import json
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

# Tenta importar a biblioteca do Google
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

load_dotenv()

st.set_page_config(page_title="Countercurrent.ai", layout="wide", initial_sidebar_state="collapsed")

# --- CSS DEFINITIVO PARA SCROLL E LAYOUT ---
st.markdown("""
<style>
    /* Estilização dos Cards */
    .signal-card {
        background: #111;
        border: 1px solid #222;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.65rem; text-transform: uppercase; font-weight: bold; }
    .signal-title { font-weight: bold; color: #f0ebe2; margin-top: 4px; font-size: 0.9rem; }
    .signal-content { color: #888; font-size: 0.8rem; margin-top: 4px; line-height: 1.4; }
    
    /* FORÇAR ROLAGEM INDEPENDENTE NAS COLUNAS */
    [data-testid="stVerticalBlock"] > div > div > [data-testid="stVerticalBlock"] {
        max-height: 78vh !important;
        overflow-y: auto !important;
        padding-right: 10px;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
    
    .insight-box {
        background: #0f0f0a;
        border: 1px solid #2a2a1e;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÃO LLM ATUALIZADA (VERSÃO 1.5 FLASH) ---
def call_llm(messages, system):
    if not HAS_GENAI:
        return "⚠️ Erro: Execute 'pip install google-generativeai'"
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY faltando."
    
    try:
        genai.configure(api_key=api_key)
        # ATUALIZADO PARA gemini-1.5-flash (Versão estável atual)
        model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system)
        response = model.generate_content(messages[-1]["content"])
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

def load_signals():
    path = "data/signals.jsonl"
    if not os.path.exists(path): return []
    signals = []
    with open(path, "r") as f:
        for line in f:
            try: signals.append(json.loads(line))
            except: pass
    return sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)

# --- UI HEADER ---
st.title("⟳ Countercurrent.ai")
st.caption("Intelligence Wire Room v2.7 — Hemingway Engine")

signals = load_signals()

col_left, col_right = st.columns([1, 1], gap="large")

# --- COLUNA ESQUERDA (FEED) ---
with col_left:
    st.markdown("### Mixed Feed")
    if not signals:
        st.warning("Sem dados. Execute o script de ingestão.")
    else:
        by_source = {}
        for s in signals:
            src = s.get("source", "web")
            by_source.setdefault(src, []).append(s)
        
        mixed_list = [item for sublist in zip_longest(*by_source.values()) for item in sublist if item]
        
        # O scroll agora é controlado pelo CSS acima injetado no stVerticalBlock
        for sig in mixed_list[:40]:
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'NY_LIBERTY')}</div>
                <div class="signal-title">{sig.get('title')}</div>
                <div class="signal-content">{sig.get('content', '')[:160]}...</div>
            </div>
            """, unsafe_allow_html=True)

# --- COLUNA DIREITA (INTELIGÊNCIA) ---
with col_right:
    st.markdown("### Strategic Intelligence")
    
    # 1. Top Section: Currents & Provocations
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Analyzing signals..."):
                context = "\n".join([f"- {s.get('title')}" for s in signals[:12]])
                prompt = f"Identify 2 dominant currents and 3 short countercurrent provocations for NY Liberty based on: {context}"
                st.session_state.auto_insight = call_llm([{"role": "user", "content": prompt}], "Style: Hemingway. Direct and punchy.")
        
        st.markdown(st.session_state.auto_insight)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Tabs Inferiores (Restauradas as 3 abas)
    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    
    with tab1:
        topic = st.text_input("Briefing Topic", "WNBA Fandom vs Luxury Fashion")
        if st.button("Generate Strategy"):
            with st.spinner("Processing..."):
                res = call_llm([{"role": "user", "content": topic}], "Style: Hemingway. Provide current vs countercurrent.")
                st.markdown(res)

    with tab2:
        st.text_input("Ask the Data Lake...", key="ask_lake")
        st.button("Inquire")

    with tab3:
        st.markdown("**Meta-Analysis Mode**")
        st.info("Aqui o sistema cruza dados históricos para identificar mudanças de longo prazo.")
        if st.button("Run Historical Analysis"):
            st.write("Analisando padrões dos últimos 30 dias...")
