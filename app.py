import streamlit as st
import datetime
import json
import os
import google.generativeai as genai

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (Premium Theme)
# ==========================================
st.set_page_config(
    page_title="Countercurrent.ai — Dashboard",
    page_icon="⟳",
    layout="wide"
)

# 🎨 CAMADA DE DESIGN: Google AI Studio UI Inspired Style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Customização dos Cards do Feed (Efeito Neumórfico Escuro) */
    div[data-testid="stCard"], .st-emotion-cache-1r6slb0, .st-emotion-cache-6q9sum {
        background-color: #1e2025 !important;
        border: 1px solid #2d3139 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 16px !important;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    div[data-testid="stCard"]:hover {
        border-color: #4f46e5 !important;
        transform: translateY(-2px);
    }

    /* Estilização dos Rounded Rectangles (Tags de Categoria) */
    .tag {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: #ffffff;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
    }
    .tag-tension { background: linear-gradient(135deg, #ef4444, #b91c1c); }
    .tag-competitor { background: linear-gradient(135deg, #f59e0b, #d97706); color: #0f172a; }
    .tag-barrier { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .tag-custom { background: linear-gradient(135deg, #a855f7, #6b21a8); }
    .tag-general { background: linear-gradient(135deg, #64748b, #475569); }

    /* Botões Premium Customizados */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5, #3730a3) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(79, 70, 229, 0.2) !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
        box-shadow: 0 6px 12px rgba(79, 70, 229, 0.4) !important;
        transform: translateY(-1px);
    }
    
    /* Inputs, Selectboxes e Text Areas elegantes */
    .stTextArea textarea, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #121417 !important;
        border: 1px solid #2d3139 !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    
    /* Scrollbars mais finas e elegantes */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f1115; }
    ::-webkit-scrollbar-thumb { background: #2d3139; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #4f46e5; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SISTEMA DE USUÁRIOS E CREDENCIAIS
# ==========================================
USER_CREDENTIALS = { "marcelo": "senha123", "pat": "pat2026", "marco": "marco2026", "joao": "joao2026" }

def log_activity(username, action, details=""):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": username, "action": action, "details": details
    }
    with open("activity_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = None
if "custom_prompt_rules" not in st.session_state: st.session_state.custom_prompt_rules = ""

# 📁 FUNÇÕES PARA MEMÓRIA PERMANENTE DOS PROJETOS (Cofre de Dados)
VAULT_PATH = "data/project_vault.jsonl"

def save_to_vault(project, item):
    if not os.path.exists("data"): os.makedirs("data")
    entry = {"project": project, "data": item}
    with open(VAULT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def load_from_vault():
    vault_data = {"Heinz Soup": [], "Haypp": [], "Likepost": [], "Sallve": [], "Oceano Azul": [], "Pinterest": []}
    if os.path.exists(VAULT_PATH):
        with open(VAULT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line.strip())
                    proj = entry.get("project")
                    if proj in vault_data:
                        vault_data[proj].append(entry.get("data"))
    return vault_data

if "project_briefs" not in st.session_state:
    st.session_state.project_briefs = {
        "Heinz Soup": "Analyze modern convenience vs. heritage comfort food. Track shifts in quick meal culture, winter comfort trends, and pantry aesthetics.",
        "Haypp": "Search for answers regarding nicotine pouch market disruption and alternative cultural patterns.",
        "Likepost": "Analyze micro-influencer exhaustion and the friction against traditional aesthetic feeds.",
        "Sallve": "Understand the shift toward chaotic curations, skin-intellectual trends, and clean beauty barriers.",
        "Oceano Azul": "Explore counter-cultural environmental movements and alternative sustainability narratives.",
        "Pinterest": "Understand the shift toward chaotic curations, 'Anti-Athleisure' trends, and private digital mood boards as a brand ecosystem strategy."
    }

# MOTOR DE CATEGORIZAÇÃO INTELIGENTE (Simulado para o Feed de Entrada)
def get_ai_category(title, content):
    text = (title + " " + content).lower()
    rules = st.session_state.custom_prompt_rules.lower()
    if rules and any(word in text for word in rules.split()): return "Custom Strategic Alert"
    if "fashion" in text or "aesthetic" in text or "shift" in text or "core" in text or "beauty" in text or "comfort" in text: return "Cultural Tension"
    elif "competitor" in text or "nike" in text or "brand" in text or "market" in text or "campbell" in text or "soup" in text: return "Competitor Activity"
    elif "barrier" in text or "fatigue" in text or "rejecting" in text or "drop" in text or "sodium" in text or "processed" in text: return "Consumer Barrier Identified"
    else: return "Company Update/Earnings"

# Mapeamento de Classes CSS para as Tags
def get_tag_html(category):
    if category == "Cultural Tension": return f'<span class="tag tag-tension">{category}</span>'
    elif category == "Competitor Activity": return f'<span class="tag tag-competitor">{category}</span>'
    elif category == "Consumer Barrier Identified": return f'<span class="tag tag-barrier">{category}</span>'
    elif category == "Custom Strategic Alert": return f'<span class="tag tag-custom">{category}</span>'
    else: return f'<span class="tag tag-general">{category}</span>'

def load_ingested_signals():
    path = "data/signals.jsonl"
    if not os.path.exists(path): return []
    signals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip(): signals.append(json.loads(line.strip()))
    return list(reversed(signals))

# ==========================================
# 2. TELA DE LOGIN (Premium Card Style)
# ==========================================
if not st.session_state.logged_in:
    st.write("")
    st.write("")
    st.markdown("<h1 style='text-align: center; font-weight:700; color:#f8fafc;'>⟳ Countercurrent.ai</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#94a3b8;'>Intelligence engine for brand strategy</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            st.write("")
            if st.button("Access Workstation", use_container_width=True):
                if username_input in USER_CREDENTIALS and USER_CREDENTIALS[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    log_activity(username_input, "login", "User logged in")
                    st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

# ==========================================
# 3. BARRA LATERAL (Clean Sidebar Look)
# ==========================================
st.sidebar.markdown("<h2 style='font-weight:700; margin-bottom:0px;'>⟳ Countercurrent</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"Active user: <span style='color:#6366f1; font-weight:600;'>{st.session_state.username.capitalize()}</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("📁 Ongoing Projects")
project_options = ["Master Dashboard", "Heinz Soup", "Haypp", "Likepost", "Sallve", "Oceano Azul", "Pinterest"]
selected_project = st.sidebar.selectbox("Select Research Desk:", project_options)

if "current_project" not in st.session_state: st.session_state.current_project = "Master Dashboard"
if selected_project != st.session_state.current_project:
    log_activity(st.session_state.username, "switch_project", f"Moved to {selected_project}")
    st.session_state.current_project = selected_project

st.sidebar.markdown("---")
st.sidebar.subheader("💬 Prompt & Chat Module")
custom_prompt_input = st.sidebar.text_area("Tweak Master Prompt:", value=st.session_state.custom_prompt_rules, placeholder="Type target keywords or custom AI rules here...")
if st.sidebar.button("Update Engine Logic", use_container_width=True):
    st.session_state.custom_prompt_rules = custom_prompt_input
    log_activity(st.session_state.username, "tweak_prompt", f"Updated prompt rules")
    st.sidebar.success("Engine logic updated!")
    st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("Logout Station", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ==========================================
# 4. ÁREA PRINCIPAL
# ==========================================
st.markdown(f"<h1 style='font-weight:700; letter-spacing:-1px;'>{selected_project}</h1>", unsafe_allow_html=True)

project_vault = load_from_vault()

if selected_project == "Master Dashboard":
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.markdown("<h3 style='font-weight:600; font-size:18px; color:#f1f5f9;'>🌐 Master Currents Feed</h3>", unsafe_allow_html=True)
        
        # FILTROS LADO A LADO
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            source_filter = st.multiselect("Filter Source:", options=["All Networks", "TikTok", "Reddit", "Pinterest", "BlueSky", "Twitter/X"], default=["All Networks"])
        with col_f2:
            client_filter = st.multiselect("Filter Target Client:", options=["All Clients", "Heinz_soup", "Ny_liberty", "Haypp", "Likepost", "Sallve", "Oceano_azul", "Pinterest"], default=["All Clients"])

        category_filter = st.multiselect(
            "Filter AI Strategic Category:",
            options=["All Categories", "Cultural Tension", "Competitor Activity", "Consumer Barrier Identified", "Custom Strategic Alert", "Company Update/Earnings"],
            default=["All Categories"]
        )

        all_signals = load_ingested_signals()

        if not all_signals:
            st.warning("⚠️ No data found. Run 'python3 ingestion.py' first!")
            filtered_signals = []
        else:
            if "All Networks" in source_filter or not source_filter: stage_1 = all_signals
            else: stage_1 = [s for s in all_signals if s.get("source") in source_filter]
            
            if "All Clients" in client_filter or not client_filter: stage_2 = stage_1
            else:
                client_filter_clean = [c.lower() for c in client_filter]
                stage_2 = [s for s in stage_1 if s.get("client_tag", "").lower() in client_filter_clean]
                
            if "All Categories" in category_filter or not category_filter:
                filtered_signals = stage_2
            else:
                filtered_signals = []
                for sig in stage_2:
                    real_cat = get_ai_category(sig.get("title", ""), sig.get("content", ""))
                    if real_cat in category_filter:
                        filtered_signals.append(sig)

        st.caption(f"Showing {len(filtered_signals)} deep signals from database based on combined parameters.")

        with st.container(height=580):
            for i, sig in enumerate(filtered_signals):
                ai_category = get_ai_category(sig.get("title", ""), sig.get("content", ""))
                client_display = sig.get("client_tag", "General").replace("_", " ").capitalize()
                
                with st.container(border=True):
                    st.markdown(f"<span style='color:#94a3b8; font-size:12px;'>📱 <b>{sig.get('source')}</b> | 🏢 Client: <i>{client_display}</i></span>", unsafe_allow_html=True)
                    
                    tag_html = get_tag_html(ai_category)
                    st.markdown(tag_html, unsafe_allow_html=True)
                    
                    st.markdown(f"<h4 style='margin-top:0px; font-weight:600; font-size:16px; color:#f8fafc;'>{sig.get('title')}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#cbd5e1; font-size:14px; line-height:1.5;'>{sig.get('content')}</p>", unsafe_allow_html=True)
                    
                    source_url = sig.get("url", "#")
                    st.markdown(f"<a href='{source_url}' target='_blank' style='color:#818cf8; font-size:13px; font-weight:500; text-decoration:none;'>→ Open Source Link</a>", unsafe_allow_html=True)
                    st.write("")
                    
                    col_btn1, col_btn2 = st.columns([1.2, 0.8])
                    with col_btn1:
                        target_project = st.selectbox("Assign Project Desk:", ["Heinz Soup", "Haypp", "Likepost", "Sallve", "Oceano Azul", "Pinterest"], key=f"sel_{i}", label_visibility="collapsed")
                    with col_btn2:
                        if st.button("📌 Add to Desk", key=f"btn_{i}", use_container_width=True):
                            new_item = {
                                "category": f"{sig.get('source')} - {ai_category}",
                                "title": f"{sig.get('title')} \n\n {sig.get('content')}",
                                "link": source_url,
                                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "saved_by": st.session_state.username
                            }
                            save_to_vault(target_project, new_item)
                            log_activity(st.session_state.username, "curate_signal", f"Permanent capture for {target_project}")
                            st.toast(f"Saved permanently to {target_project}!")

    with col_right:
        st.markdown("<h3 style='font-weight:600; font-size:18px; color:#f1f5f9;'>🧠 Strategic Intelligence Matrix</h3>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<h5 style='color:#818cf8; font-weight:600;'>⚡ 3 Cultural Shifts Identified</h5>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:14px; color:#e2e8f0;'>1. Shift from performance to pure aesthetics in lifestyle wear.<br>2. Demand for hyper-clandestine brand experiences.<br>3. Fragmentation of mainstream sports networks.</p>", unsafe_allow_html=True)
            st.write("")
            st.markdown("<h5 style='color:#f43f5e; font-weight:600;'>🎯 3 Countercurrent Provocations</h5>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:14px; color:#e2e8f0;'>1. Building 'Ugly Performance' gear to break the luxury aesthetic mold.<br>2. Ghost brands: Zero social media presence, maximum impact.<br>3. The 'Slow Sports' movement: Rewarding loyalty over fast consumption.</p>", unsafe_allow_html=True)

        st.write("")
        st.markdown("<h3 style='font-weight:600; font-size:18px; color:#f1f5f9;'>🛠️ Real-time Processing Labs</h3>", unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["⚡ AI Dispatch", "🤝 Thinker Partner", "📊 Meta-Analysis"])
        with tab1:
            dispatch_query = st.text_input("Ask Dispatch for an instant brief:", placeholder="e.g., WNBA x Luxury Strategy for NY Liberty")
            if st.button("Generate Strategic Framework"):
                st.info("**[Dispatch Output]:** Simulated strategic brief for: " + dispatch_query)

# PÁGINAS DOS PROJETOS
else:
    with st.container(border=True):
        st.markdown("<h4 style='font-weight:600; color:#f1f5f9;'>📋 Project Workspace Brief</h4>", unsafe_allow_html=True)
        current_brief = st.text_area("Project Objectives:", value=st.session_state.project_briefs[selected_project], key="brief_area", label_visibility="collapsed")
        if st.button("Lock Strategic Brief"):
            st.session_state.project_briefs[selected_project] = current_brief
            st.toast("Brief updated!")

    st.markdown("---")
    col_proj_left, col_proj_right = st.columns([1, 1])
    
    with col_proj_left:
        st.markdown("<h4 style='font-weight:600; color:#f1f5f9;'>🗂️ Research Desk (Curation Vault)</h4>", unsafe_allow_html=True)
        saved_items = project_vault[selected_project]
        
        if len(saved_items) == 0: st.info("This desk is currently clean. Add signals from the Master Feed.")
        else:
            for item in saved_items:
                with st.container(border=True):
                    st.markdown(f"<span style='color:#818cf8; font-size:12px;'><b>[{item['category']}]</b> — Curated by {item['saved_by'].capitalize()}</span>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color:#e2e8f0; font-size:14px; margin-top:8px;'>{item['title']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<a href='{item['link']}' target='_blank' style='color:#94a3b8; font-size:13px; text-decoration:none;'>🔗 View Source</a>", unsafe_allow_html=True)

    with col_proj_right:
        st.markdown("<h4 style='font-weight:600; color:#f1f5f9;'>🔮 AI Synthesis Lab (Gemini Live Engine)</h4>", unsafe_allow_html=True)
        
        if st.button(f"Execute Engine Intelligence for {selected_project}", use_container_width=True):
            if len(saved_items) == 0: 
                st.warning("Add elements to the desk first to perform analytical cross-referencing.")
            else:
                # 🛠️ CAPTURA IMEDIATA DA CHAVE SEM ENTRAVES DE ESCOPO GLOBAL
                live_key = ""
                if "GEMINI_API_KEY" in st.secrets:
                    live_key = st.secrets["GEMINI_API_KEY"]
                elif os.environ.get("GEMINI_API_KEY"):
                    live_key = os.environ.get("GEMINI_API_KEY")

                # Se falhar nos dois métodos padrão, tentamos a leitura direta do dicionário interno do Streamlit
                if not live_key:
                    try:
                        live_key = st.secrets.get("GEMINI_API_KEY", "")
                    except:
                        pass

                if not live_key:
                    st.error("🚨 GEMINI_API_KEY not detected by Streamlit core. Please re-check your Cloud Secrets panel.")
                else:
                    with st.spinner("Gemini Pro is compiling workspace nodes and engineering creative counter-brief..."):
                        try:
                            # 🧠 Força a configuração da API direto no escopo de execução da ação
                            genai.configure(api_key=live_key)
                            
                            # Compila todos os posts salvos em texto puro para a IA ler
                            compiled_posts = ""
                            for idx, item in enumerate(saved_items):
                                compiled_posts += f"\n--- CURATED POST {idx+1} ---\n{item['title']}\n"

                            # Prompt Avançado de Estratégia Contracorrente
                            master_prompt = f"""
                            You are the strategic brain behind Countercurrent.ai, a vanguard advertising agency intelligence tool.
                            Your job is to cross-reference a client's brief with real social internet signals curated by the team, and find an unpredictable market opportunity.
                            
                            CLIENT: {selected_project}
                            STRATEGIC BRIEF OBJECTIVE: {current_brief}
                            
                            HERE ARE THE REAL SOCIAL MEDIA INSIGHTS CURATED BY THE TEAM FOR THIS CLIENT:
                            {compiled_posts}
                            
                            Based on these specific posts and the brief, write a high-level strategic response in English. You must provide:
                            1. UNEXPLOITED WHITE SPACE (A market opportunity or cultural gap born directly from these posts that competitors are ignoring).
                            2. COUNTERCURRENT BRAND PROVOCATION (A bold, practical recommendation on what the brand should do or say to subvert expectations).
                            
                            Keep the tone sharp, executive, and highly strategic. Use clean bullet points or short text paragraphs.
                            """
                            
                            # Inicialização direta do modelo de produção
                            model = genai.GenerativeModel("gemini-1.5-pro")
                            response = model.generate_content(master_prompt)
                            
                            log_activity(st.session_state.username, "execute_ai_synthesis", f"Generated live Gemini Pro report for {selected_project}")
                            
                            # Exibição do relatório estratégico gerado ao vivo
                            st.markdown("<h5 style='color:#34d399; font-weight:600;'>⚡ Live Strategic Output (Gemini 1.5 Pro)</h5>", unsafe_allow_html=True)
                            st.write(response.text)
                            
                        except Exception as e:
                            st.error(f"Error executing Gemini runtime generation: {str(e)}")

# AUDIT LOG
st.markdown("---")
with st.expander("📄 System Governance & Audit Log"):
    try:
        with open("activity_log.jsonl", "r", encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                data = json.loads(line.strip())
                st.text(f"[{data['timestamp']}] {data['user'].upper()} executed '{data['action']}' → {data['details']}")
    except: st.info("No activity recorded yet.")
