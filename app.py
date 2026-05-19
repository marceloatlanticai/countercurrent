import streamlit as st
import datetime
import json
import os

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Countercurrent.ai — Dashboard",
    page_icon="⟳",
    layout="wide"
)

# ==========================================
# 1. SISTEMA DE USUÁRIOS E CREDENCIAIS
# ==========================================
USER_CREDENTIALS = {
    "marcelo": "senha123",
    "pat": "design2026",
    "marco": "strategy3",
    "joao": "trends4"
}

def log_activity(username, action, details=""):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": username,
        "action": action,
        "details": details
    }
    with open("activity_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

# Inicializa os estados da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# BANCO DE DADOS TEMPORÁRIO (Memória dos Projetos)
if "project_data" not in st.session_state:
    st.session_state.project_data = {
        "Haypp": [],
        "Likepost": [],
        "Pinterest": [],
        "Salvie": [],
        "Oceano Ozul": []
    }

if "project_briefs" not in st.session_state:
    st.session_state.project_briefs = {
        "Haypp": "Search for answers regarding nicotine pouch market disruption and alternative cultural patterns.",
        "Likepost": "Analyze micro-influencer exhaustion and the friction against traditional aesthetic feeds.",
        "Pinterest": "Understand the shift toward chaotic curations, 'Anti-Athleisure' trends, and private digital mood boards.",
        "Salvie": "Investigate underground wellness movements and non-corporate lifestyle signals.",
        "Oceano Ozul": "Explore counter-cultural environmental movements and alternative sustainability narratives."
    }

# 🛠️ FUNÇÃO PARA CARREGAR OS DADOS REAIS DA INGESTÃO
def load_ingested_signals():
    path = "data/signals.jsonl"
    if not os.path.exists(path):
        return []
    
    signals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                signals.append(json.loads(line.strip()))
    return list(reversed(signals)) # Traz os mais recentes primeiro

# ==========================================
# 2. TELA DE LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>⟳ Countercurrent.ai</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            if submit_button:
                if username_input in USER_CREDENTIALS and USER_CREDENTIALS[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    log_activity(username_input, "login", "User successfully logged in")
                    st.success(f"Welcome back, {username_input.capitalize()}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    st.stop()

# ==========================================
# 3. BARRA LATERAL (Sidebar)
# ==========================================
st.sidebar.title("⟳ Countercurrent.ai")
st.sidebar.write(f"Logged in as: **{st.session_state.username.capitalize()}**")
st.sidebar.markdown("---")

st.sidebar.subheader("📁 Ongoing Projects")
project_options = ["Master Dashboard", "Haypp", "Likepost", "Pinterest", "Salvie", "Oceano Ozul"]
selected_project = st.sidebar.selectbox("Select Research Desk:", project_options)

if "current_project" not in st.session_state:
    st.session_state.current_project = "Master Dashboard"

if selected_project != st.session_state.current_project:
    log_activity(st.session_state.username, "switch_project", f"Moved to {selected_project}")
    st.session_state.current_project = selected_project

st.sidebar.markdown("---")
st.sidebar.subheader("💬 Prompt & Chat Module")
custom_prompt = st.sidebar.text_area("Tweak Master Prompt:", placeholder="Type adjustments to the AI logic here...")
if st.sidebar.button("Update Engine Logic"):
    log_activity(st.session_state.username, "tweak_prompt", f"Updated prompt rules: '{custom_prompt[:30]}...'")
    st.sidebar.success("Engine logic updated!")

st.sidebar.markdown("---")
if st.sidebar.button("Logout", use_container_width=True):
    log_activity(st.session_state.username, "logout", "User logged out")
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

# ==========================================
# 4. ÁREA PRINCIPAL DO DASHBOARD
# ==========================================
st.title(f"{selected_project}")

if selected_project == "Master Dashboard":
    col_left, col_right = st.columns([1, 1])
    
    # --- COLUNA ESQUERDA: MASTER CURRENTS FEED (REAL) ---
    with col_left:
        st.subheader("🌐 Master Currents Feed")
        
        source_filter = st.multiselect(
            "Filter by Platform Source:",
            options=["All Networks", "TikTok", "Reddit", "Pinterest", "BlueSky", "Twitter/X"],
            default=["All Networks"]
        )

        # 🛠️ MUDANÇA AQUI: Carrega os dados reais coletados do arquivo JSONL
        all_signals = load_ingested_signals()

        if not all_signals:
            st.warning("⚠️ No data found in 'data/signals.jsonl'. Please run 'python3 ingestion.py' in your terminal first!")
            filtered_signals = []
        else:
            if "All Networks" in source_filter or not source_filter:
                filtered_signals = all_signals
            else:
                filtered_signals = [s for s in all_signals if s.get("source") in source_filter]

        st.caption(f"Showing {len(filtered_signals)} real live signals from database.")

        # FEED COM BARRA DE ROLAGEM INDEPENDENTE
        with st.container(height=550):
            for i, sig in enumerate(filtered_signals):
                with st.container(border=True):
                    # Identifica a rede
                    st.markdown(f"📱 **{sig.get('source', 'Unknown')}** | *Client: {sig.get('client_tag', 'General')}*")
                    st.markdown(f"**{sig.get('title', 'No Title')}**")
                    st.write(sig.get('content', ''))
                    
                    # 🛠️ MUDANÇA AQUI: Usa a chave "url" vinda do ingestion.py (que tem os links de busca exatos)
                    source_url = sig.get("url", sig.get("link", "#"))
                    st.markdown(f"[View Live Source]({source_url})")
                    
                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                        target_project = st.selectbox("Send to project:", ["Haypp", "Likepost", "Pinterest", "Salvie", "Oceano Ozul"], key=f"sel_{i}")
                    with col_btn2:
                        st.write("") 
                        if st.button("📌 Add to Desk", key=f"btn_{i}"):
                            st.session_state.project_data[target_project].append({
                                "category": f"{sig.get('source')} - Signal",
                                "title": f"{sig.get('title')} \n\n {sig.get('content')}",
                                "link": source_url, # Passa a URL real e profunda adiante
                                "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                                "saved_by": st.session_state.username
                            })
                            log_activity(st.session_state.username, "curate_signal", f"[{sig.get('source')}] Added to {target_project} Desk")
                            st.toast(f"Saved to {target_project}!")

    # --- COLUNA DIREITA: STRATEGIC INTELLIGENCE ---
    with col_right:
        st.subheader("🧠 Strategic Intelligence")
        with st.container(border=True):
            st.markdown("### 3 Cultural Shifts Identified")
            st.write("1. Shift from performance to pure aesthetics in lifestyle wear.")
            st.write("2. Demand for hyper-clandestine brand experiences.")
            st.write("3. Fragmentation of mainstream sports networks.")
            st.markdown("### 3 Countercurrent Provocations")
            st.write("1. Building 'Ugly Performance' gear to break the luxury aesthetic mold.")
            st.write("2. Ghost brands: Zero social media presence, maximum impact.")
            st.write("3. The 'Slow Sports' movement: Rewarding loyalty over fast consumption.")

        st.markdown("---")
        st.subheader("🛠️ Interactive Modules")
        tab1, tab2, tab3 = st.tabs(["⚡ Dispatch", "🤝 Thinker Partner", "📊 Meta-Analysis"])
        with tab1:
            dispatch_query = st.text_input("Ask Dispatch for a brief:", placeholder="e.g., WNBA x Luxury Strategy for NY Liberty")
            if st.button("Generate Brief"):
                log_activity(st.session_state.username, "run_dispatch", f"Query: {dispatch_query}")
                st.write("**[Dispatch Output]:** Simulated strategic brief for: " + dispatch_query)
        with tab2:
            st.info("🔄 Fine-tuning API connection...")
        with tab3:
            st.warning("⏳ Future feature: Database connection.")

# ==========================================
# 5. PÁGINAS DOS PROJETOS ESPECÍFICOS
# ==========================================
else:
    with st.container(border=True):
        st.markdown("### 📋 The Brief")
        st.caption("Objectives and outstanding questions we're trying to answer through listening and research.")
        current_brief = st.text_area("Project Objectives:", value=st.session_state.project_briefs[selected_project], key="brief_area")
        if st.button("Update Project Brief"):
            st.session_state.project_briefs[selected_project] = current_brief
            log_activity(st.session_state.username, "update_brief", f"Updated brief for {selected_project}")
            st.toast("Brief updated successfully!")

    st.markdown("---")
    col_proj_left, col_proj_right = st.columns([1, 1])
    
    with col_proj_left:
        st.markdown("### 🗂️ Research Desk (Collected Data)")
        saved_items = st.session_state.project_data[selected_project]
        
        if len(saved_items) == 0:
            st.info("No data collected from Master Feed yet. Go to Master Dashboard to curate some signals!")
        else:
            for item in saved_items:
                with st.container(border=True):
                    st.markdown(f"**[{item['category']}]** — *Curated by {item['saved_by'].capitalize()}*")
                    st.write(item['title'])
                    st.markdown(f"[🔗 View Original Live Source]({item['link']})")
        
        st.markdown("---")
        with st.container(border=True):
            st.markdown("### ✍️ Add Manual Insight & Rating")
            note_input = st.text_area("Add custom observation to this desk:")
            rating = st.slider("Delineate data importance (Rating):", 1, 5, 3)
            if st.button("Save Entry to Project Desk"):
                log_activity(st.session_state.username, "add_project_note", f"Project: {selected_project} | Rating: {rating}")
                st.success("Insight added to the research workflow!")

    with col_proj_right:
        st.markdown("### 🎯 Currents Summary & Whitespaces")
        if st.button(f"🔮 Run AI Synthesis for {selected_project}", use_container_width=True):
            if len(saved_items) == 0:
                st.warning("Cannot synthesize. The Research Desk is empty.")
            else:
                log_activity(st.session_state.username, "run_project_synthesis", f"Generated strategic summary for {selected_project}")
                with st.spinner("Analyzing team curation..."):
                    st.markdown("#### 🔍 Identified Whitespace")
                    st.info(f"Based on the {len(saved_items)} signals saved by your team, there is an unexploited gap in subverting traditional category codes.")
                    with st.container(border=True):
                        st.markdown("#### 💡 Countercurrent Suggestion")
                        st.write(f"**Strategy Proposal for {selected_project}:** Launch a hyper-limited 'Ghost Drop' to capitalize on the user tensions mapped on your desk.")

# ==========================================
# 6. HISTÓRICO DE EDIÇÕES / AUDIT LOG
# ==========================================
st.markdown("---")
with st.expander("📄 View Team Activity History (Audit Log)"):
    try:
        with open("activity_log.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):
                data = json.loads(line.strip())
                st.text(f"[{data['timestamp']}] {data['user'].upper()} executed '{data['action']}' → {data['details']}")
    except FileNotFoundError:
        st.info("No activity recorded yet.")
