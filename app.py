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

# ── CSS — Estética Wire Room & Scroll ───────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #d4cfc7; }
    
    /* Estilização dos Cards do Feed */
    .signal-card {
        background: #111; border: 1px solid #222;
        padding: 12px; border-radius: 6px; margin-bottom: 10px;
    }
    .signal-source { color: #e8a838; font-family: monospace; font-size: 0.65rem; text-transform: uppercase; font-weight: bold; }
    .signal-title { font-weight: bold; color: #f0ebe2; font-size: 0.9rem; margin-top: 4px; }
    
    /* Caixa de Inteligência (Coluna Direita) */
    .insight-box {
        background: #0f100a; 
        border: 1px solid #2a2a1e;
        padding: 20px; 
        border-radius: 8px; 
        margin-bottom: 20px;
        color: #f0ebe2;
        line-height: 1.6;
    }
    
    /* Ajuste de Títulos e Tabs */
    h1, h2, h3 { font-family: serif; letter-spacing: -0.02em; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #222; }
    .stTabs [data-baseweb="tab"] { font-family: monospace; font-size: 0.7rem; color: #666; }
    .stTabs [aria-selected="true"] { color: #e8a838 !important; }
</style>
""", unsafe_allow_html=True)

# ── Função LLM (Gemini 2.5 Flash) ───────────────────────────────────────────
def call_llm(user_query, system_instruction):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key: return "⚠️ API_KEY não configurada no .env"
    
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
        return f"⚠️ Erro API: {data.get('error', {}).get('message', 'Erro desconhecido')}"
    except Exception as e:
        return f"⚠️ Falha de Conexão: {str(e)}"

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

# ── UI Layout Principal ──────────────────────────────────────────────────────
st.title("⟳ Countercurrent.ai")
st.caption("Wire Room v3.6 — Intelligence Hub")

signals = load_signals()
col_left, col_right = st.columns([1, 1], gap="large")

# ══════════════════════════════════════════════════════════════════════════════
# COLUNA ESQUERDA: Mixed Feed
# ══════════════════════════════════════════════════════════════════════════════
with col_left:
    st.subheader("Mixed Feed")
    
    if signals:
        sources = sorted(list({s.get("source", "web") for s in signals}))
        selected_source = st.selectbox("Filter Network", ["All Networks"] + sources)
        
        filtered = [s for s in signals if selected_source == "All Networks" or s.get("source") == selected_source]
        
        # Container nativo com scroll (height fixo)
        with st.container(height=650):
            if selected_source == "All Networks":
                by_src = {}
                for s in filtered:
                    src = s.get("source", "web")
                    by_src.setdefault(src, []).append(s)
                
                # Intercala os sinais das fontes (Mixed)
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
    else:
        st.info("Execute o script de ingestão para visualizar os sinais.")

# ══════════════════════════════════════════════════════════════════════════════
# COLUNA DIREITA: Strategic Intelligence (3+3 Hemingway)
# ══════════════════════════════════════════════════════════════════════════════
with col_right:
    st.subheader("Strategic Intelligence")
    
    if signals:
        # Gera o insight automático apenas uma vez por sessão
        if "auto_insight" not in st.session_state:
            with st.spinner("Decoding signals..."):
                ctx = "\n".join([f"- {s.get('title')}" for s in signals[:15]])
                instruction = (
                    "You are a strategic trend spotter. Write in Hemingway style: short, punchy, plainspoken. "
                    "Identify exactly 3 'Cultural Shifts' and 3 'Countercurrent Shifts' (contrarian provocations). "
                    "Use markdown bold for headlines."
                )
                st.session_state.auto_insight = call_llm(ctx, instruction)
        
        # Conteúdo envelopado na caixa cinza
        st.markdown(f"""
        <div class="insight-box">
            <div style="font-family:monospace; color:#e8a838; font-size:0.7rem; margin-bottom:15px; text-transform:uppercase; border-bottom:1px solid #2a2a1e; padding-bottom:5px;">
                ⚡ Automated Intelligence Report
            </div>
            {st.session_state.auto_insight}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write("Aguardando dados para análise estratégica...")

    # Abas de Ação
    tab1, tab2, tab3 = st.tabs(["Dispatch", "Thinker Partner", "Meta-Analysis"])
    
    with tab1:
        topic = st.text_input("Topic for Dispatch", "WNBA x Fashion Strategy")
        if st.button("Run Strategic Dispatch"):
            with st.spinner("Writing..."):
                res = call_llm(topic, "Style: Hemingway. Provide a current trend vs a contrarian countercurrent.")
                st.markdown(f'<div class="insight-box">{res}</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div style="font-size:0.8rem; color:#666; margin-bottom:10px;">Chat with the collective data lake.</div>', unsafe_allow_html=True)
        st.text_input("Interrogate Lake", key="lake_chat")
        st.button("Inquire")

    with tab3:
        st.markdown("**Meta-Analysis Mode**")
        st.caption("Cross-referencing historical signals to detect long-term shifts.")
        if st.button("Generate Historical Patterns"):
            st.write("Análise de padrões habilitada.")
