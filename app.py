import os
import json
import requests
import streamlit as st
from datetime import datetime
from itertools import zip_longest
from dotenv import load_dotenv

load_dotenv()

# ── Configuração da Página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Countercurrent.ai",
    page_icon="⟳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS — Estética Wire Room & Links ───────────────────────────────────────
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
    
    /* Ajuste de Títulos e Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { font-family: monospace; font-size: 0.7rem; }
</style>
""", unsafe_allow_html=True)

# ── Função LLM (Potencializada para não cortar o texto) ──────────────────────
def call_llm(user_query, system_instruction):
    api_key = os.environ.get("GOOGLE_API_KEY")
    # Rota validada pelo seu teste de terminal
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": f"SYSTEM INSTRUCTION: {system_instruction}\n\nUSER QUERY: {user_query}"}]
        }],
        "generationConfig": {
            "temperature": 0.4,     # Mais focado
            "maxOutputTokens": 2000 # Espaço de sobra para os 6 pontos
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        return "⚠️ Erro: O modelo não retornou uma resposta válida."
    except Exception as e:
        return f"⚠️ Falha na conexão: {str(e)}"

# ── Carregamento de Dados ────────────────────────────────────────────────────
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

# ── UI Header ────────────────────────────────────────────────────────────────
st.title("⟳ Countercurrent.ai")
st.caption("Wire Room v3.12 — Full Intelligence Engine")

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# COLUNA ESQUERDA: Mixed Feed (Com Links Clicáveis)
# ══════════════════════════════════════════════════════════════════════════════
with col_left:
    st.subheader("Mixed Feed")
    
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
            else:
                display_list = filtered

            for sig in display_list[:60]:
                target_url = sig.get('url', '#')
                st.markdown(f"""
                <a href="{target_url}" target="_blank" class="signal-link">
                    <div class="signal-card">
                        <div class="signal-source">{sig.get('source')} | {sig.get('client_tag', 'NYL')}</div>
                        <div class="signal-title">{sig.get('title')}</div>
                        <div style="color:#888; font-size:0.8rem; margin-top:5px;">{sig.get('content', '')[:140]}...</div>
                    </div>
                </a>
                """, unsafe_allow_html=True)
    else:
        st.info("Aguardando ingestão de sinais...")

# ══════════════════════════════════════════════════════════════════════════════
# COLUNA DIREITA: Strategic Intelligence (Fixo 3+3)
# ══════════════════════════════════════════════════════════════════════════════
with col_right:
    # Cabeçalho com Botão de Refresh
    col_t, col_r = st.columns([3, 1])
    with col_t:
        st.subheader("Strategic Intelligence")
    with col_r:
        if st.button("🔄 Refresh"):
            if "auto_insight" in st.session_state:
                del st.session_state.auto_insight
            st.rerun()
    
    if signals:
        if "auto_insight" not in st.session_state:
            with st.spinner("Analyzing cultural signals..."):
                ctx = "\n".join([f"- {s.get('title')}" for s in signals[:25]])
                
                # Instrução rigorosa de formatação
                instruction = (
                    "Act as a professional trend analyst. Strictly provide 3 'CULTURAL SHIFTS' and 3 'COUNTERCURRENT SHIFTS'. "
                    "Format each item as: **Title**: Brief Hemingway-style description. "
                    "Do not write conversational text, just the list. Use bold for titles."
                )
                st.session_state.auto_insight = call_llm(ctx, instruction)
        
        # Header Visual
        st.markdown(f"""
        <div style="background:#0f100a; border:1px solid #2a2a1e; border-bottom:none; padding:15px; border-radius:8px 8px 0 0; margin-bottom:-20px;">
            <div style="font-family:monospace; color:#e8a838; font-size:0.7rem; text-transform:uppercase; border-bottom:1px solid #2a2a1e; padding-bottom:5px;">
                ⚡ Automated Intelligence Report
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Caixa de Texto com borda fixa
        with st.container(border=True):
            st.markdown(st.session_state.auto_insight)
            
    # Abas Inferiores
    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    with tab1:
        topic = st.text_input("Dispatch Topic", "WNBA x Luxury Strategy")
        if st.button("Generate Strategy"):
            with st.spinner("Writing..."):
                res = call_llm(topic, "Style: Hemingway. Strategic Countercurrent vs Trend.")
                st.info(res)
    
    with tab2:
        st.text_input("Ask the Data Lake", key="lake_chat")
        st.button("Inquire")

    with tab3:
        st.markdown("**Meta-Analysis Mode**")
        st.caption("Cross-referencing historical signals.")
