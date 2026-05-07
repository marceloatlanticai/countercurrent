import os
import json
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

# Tenta importar a biblioteca do Google, se falhar, avisa o usuário
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

load_dotenv()

st.set_page_config(page_title="Countercurrent.ai", layout="wide")

# --- CSS Simplificado e Funcional ---
st.markdown("""
<style>
    /* Estilização dos Cards */
    .signal-card {
        background: #111;
        border: 1px solid #222;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.7rem; text-transform: uppercase; }
    .signal-title { font-weight: bold; color: #eee; margin-top: 5px; }
    .signal-content { color: #888; font-size: 0.8rem; margin-top: 5px; }
    
    /* Forçar altura e scroll nas colunas do Streamlit */
    [data-testid="stVerticalBlock"] > div > div > [data-testid="stVerticalBlock"] {
        max-height: 80vh;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- Funções de Apoio ---
def call_llm(messages, system):
    if not HAS_GENAI:
        return "⚠️ Erro: Biblioteca 'google-generativeai' não instalada."
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY faltando no ambiente."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system) # Voltando para a 2.0 que é a estável atual
        chat = model.start_chat(history=[])
        response = chat.send_message(messages[-1]["content"])
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

def load_signals():
    if not os.path.exists("data/signals.jsonl"): return []
    signals = []
    with open("data/signals.jsonl", "r") as f:
        for line in f:
            try: signals.append(json.loads(line))
            except: pass
    return sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)

# --- UI ---
st.title("⟳ Countercurrent.ai")
st.caption("Intelligence Wire Room v2.6")

signals = load_signals()

col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    st.subheader("Mixed Feed")
    if not signals:
        st.warning("Aguardando sinais... Execute o ingestion.")
    else:
        # Lógica de Intercalação (Mixed)
        by_source = {}
        for s in signals:
            src = s.get("source", "web")
            by_source.setdefault(src, []).append(s)
        
        mixed_list = [item for sublist in zip_longest(*by_source.values()) for item in sublist if item]
        
        for sig in mixed_list[:30]:
            st.markdown(f"""
            <div class="signal-card">
                <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', '')}</div>
                <div class="signal-title">{sig.get('title')}</div>
                <div class="signal-content">{sig.get('content', '')[:150]}...</div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("Strategic Insights")
    
    # Área de Correntes e Provocações
    with st.container(border=True):
        if signals:
            if "auto_insight" not in st.session_state:
                with st.spinner("Analyzing signals..."):
                    context = "\n".join([s.get('title','') for s in signals[:10]])
                    prompt = f"Identify 2 dominant currents and 3 short countercurrent provocations for NY Liberty: {context}"
                    st.session_state.auto_insight = call_llm([{"role": "user", "content": prompt}], "You are a trend analyst.")
            
            st.markdown(f"### {st.session_state.auto_insight}")
        else:
            st.write("Sem dados para analisar.")

    # Tabs inferiores
    tab1, tab2 = st.tabs(["Dispatch", "Thinker Partner"])
    with tab1:
        topic = st.text_input("Briefing Topic", "NY Liberty vs Fandom Trends")
        if st.button("Generate Strategy"):
            res = call_llm([{"role": "user", "content": topic}], "Style: Hemingway. Focus on Countercurrents.")
            st.write(res)
