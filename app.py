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

# --- CSS PARA SCROLL E LAYOUT ---
st.markdown("""
<style>
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
    
    /* FORÇAR ROLAGEM INDEPENDENTE */
    [data-testid="stVerticalBlock"] > div > div > [data-testid="stVerticalBlock"] {
        max-height: 75vh !important;
        overflow-y: auto !important;
        padding-right: 10px;
        display: block !important;
    }

    ::-webkit-scrollbar { width: 4px; }
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

# --- FUNÇÃO LLM CORRIGIDA ---
def call_llm(user_query, system_instruction):
    if not HAS_GENAI:
        return "⚠️ Erro: Execute 'pip install google-generativeai'"
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY faltando no arquivo .env"
    
    try:
        genai.configure(api_key=api_key)
        # Usando o sufixo -latest para garantir que ele ache o modelo estável
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_instruction
        )
        response = model.generate_content(user_query)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

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
st.caption("Wire Room v2.8 — Intelligence Hub")

signals = load_signals()

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Global Mixed Feed")
    # Div dummy para forçar o início do container de scroll do Streamlit
    st.write("") 
    
    if not signals:
        st.info("Aguardando sinais... Execute o script de ingestão.")
    else:
        by_source = {}
        for s in signals:
            src = s.get("source", "web")
            by_source.setdefault(src, []).append(s)
        
        mixed_list = [item for sublist in zip_longest(*by_source.values()) for item in sublist if item]
        
        for sig in mixed_list[:40]:
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'CORE')}</div>
                <div class="signal-title">{sig.get('title')}</div>
                <div class="signal-content">{sig.get('content', '')[:160]}...</div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("Strategic Insights")
    
    # Insights Automáticos
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Analyzing..."):
                context = "\n".join([f"- {s.get('title')}" for s in signals[:15]])
                instruction = "You are a trend spotter. Style: Hemingway. Give 2 currents and 3 counter-provocations."
                query = f"Analyze these recent signals for NY Liberty: {context}"
                st.session_state.auto_insight = call_llm(query, instruction)
        
        st.markdown(st.session_state.auto_insight)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    
    with tab1:
        topic = st.text_input("Topic", "NY Liberty vs Stadium Style")
        if st.button("Run Dispatch"):
            with st.spinner("Writing..."):
                res = call_llm(topic, "Style: Hemingway. Countercurrent strategy.")
                st.markdown(res)
    
    with tab2:
        st.text_input("Ask the Lake", key="lake_q")
        st.button("Inquire")

    with tab3:
        st.markdown("**Meta-Analysis Enabled**")
        st.button("Analyze Patterns")
