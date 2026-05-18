import streamlit as st
import datetime
import json

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando)
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

# Função para registrar as ações/edições de cada usuário (Audit Log)
def log_activity(username, action, details=""):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": username,
        "action": action,
        "details": details
    }
    with open("activity_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

# Inicializa os estados da sessão do Streamlit
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# ==========================================
# 2. TELA DE LOGIN (Bloqueia o app se não logado)
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>⟳ Countercurrent.ai</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Strategic Intelligence Platform</p>", unsafe_allow_html=True)
    
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
# 3. BARRA LATERAL (Sidebar) - CONTROLE E PROJETOS
# ==========================================
st.sidebar.title("⟳ Countercurrent.ai")
st.sidebar.write(f"Logged in as: **{st.session_state.username.capitalize()}**")

st.sidebar.markdown("---")

# Seção de Projetos Ativos (Wireframe do Pat: Ongoing Projects)
st.sidebar.subheader("📁 Ongoing Projects")
project_options = ["Master Dashboard", "Haypp", "Likepost", "Pinterest", "Salvie", "Oceano Ozul"]
selected_project = st.sidebar.selectbox("Select Research Desk:", project_options)

# Se houver mudança de projeto, podemos registrar no log
if "current_project" not in st.session_state:
    st.session_state.current_project = "Master Dashboard"

if selected_project != st.session_state.current_project:
    log_activity(st.session_state.username, "switch_project", f"Moved to {selected_project}")
    st.session_state.current_project = selected_project

st.sidebar.markdown("---")

# Módulo de Prompt e Chat (Wireframe do Pat)
st.sidebar.subheader("💬 Prompt & Chat Module")
st.sidebar.info("Allows you to search, sort info by date/keywords, or tweak the master prompt.")
custom_prompt = st.sidebar.text_area("Tweak Master Prompt:", placeholder="Type adjustments to the AI logic here...")
if st.sidebar.button("Update Engine Logic"):
    log_activity(st.session_state.username, "tweak_prompt", f"Updated prompt rules: '{custom_prompt[:30]}...'")
    st.sidebar.success("Engine logic updated for this session!")

st.sidebar.markdown("---")

# Botão de Logout
if st.sidebar.button("Logout", use_container_width=True):
    log_activity(st.session_state.username, "logout", "User logged out")
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()


# ==========================================
# 4. ÁREA PRINCIPAL DO DASHBOARD
# ==========================================
st.title(f"{selected_project}")

# Se estiver no Master Dashboard, mostra o fluxo completo do Pat
if selected_project == "Master Dashboard":
    
    col_left, col_right = st.columns([1, 1])
    
    # --- COLUNA ESQUERDA: MASTER CURRENTS FEED ---
    with col_left:
        st.subheader("🌐 Master Currents Feed")
        st.caption("Live signals from TikTok, Reddit, Pinterest, and BlueSky.")
        
        # Simulação de Sinais categorizados conforme o Wireframe do Pat
        signals = [
            {"category": "Cultural Tension", "title": "The rise of Anti-Athleisure in metropolitan centers", "link": "#"},
            {"category": "Competitor Activity", "title": "Nike launches quiet-luxury capsule collection", "link": "#"},
            {"category": "Consumer Barrier Identified", "title": "Gen-Z rejecting automated customer service in luxury retail", "link": "#"},
            {"category": "Company Update/Earnings", "title": "Key luxury holding groups report 4% drop in traditional retail traffic", "link": "#"}
        ]
        
        for i, sig in enumerate(signals):
            with st.container(border=True):
                st.markdown(f"**[{sig['category']}]**")
                st.write(sig['title'])
                st.markdown(f"[View Live Source]({sig['link']})")
                
                # Botão de Curadoria Humana (Simula o Drag and Drop para o Research Desk)
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    target_project = st.selectbox("Send to project:", ["Haypp", "Pinterest", "Salvie"], key=f"sel_{i}")
                with col_btn2:
                    st.write("") # Espaçador
                    if st.button("📌 Add to Desk", key=f"btn_{i}"):
                        log_activity(
                            st.session_state.username, 
                            "curate_signal", 
                            f"Added '{sig['title'][:25]}...' to {target_project} Desk"
                        )
                        st.toast(f"Saved to {target_project}!")

    # --- COLUNA DIREITA: STRATEGIC INTELLIGENCE & INTERACTIVE MODULES ---
    with col_right:
        st.subheader("🧠 Strategic Intelligence")
        st.caption("Hemingway Logic: 3 Cultural Shifts + 3 Countercurrents")
        
        with st.container(border=True):
            st.markdown("### 3 Cultural Shifts Identified")
            st.write("1. Shift from performance to pure aesthetics in lifestyle wear.")
            st.write("2. Demand for hyper-clandestine brand experiences.")
            st.write("3. Fragmentation of mainstream sports networks.")
            
            st.markdown("### 3 Countercurrent Provocations")
            st.write("1. Building 'Ugly Performance' gear to break the luxury aesthetic mold.")
            st.write("2. Ghost brands: Zero social media presence, maximum impact.")
            st.write("3. The 'Slow Sports' movement: Rewarding loyalty over fast consumption.")

        # ABAS INTERACTIVAS (Dispatch, Thinker Partner, Meta-Analysis)
        st.markdown("---")
        st.subheader("🛠️ Interactive Modules")
        tab1, tab2, tab3 = st.tabs(["⚡ Dispatch", "🤝 Thinker Partner", "📊 Meta-Analysis"])
        
        with tab1:
            st.write("Generate high-level strategic briefings based on active research.")
            dispatch_query = st.text_input("Ask Dispatch for a brief:", placeholder="e.g., WNBA x Luxury Strategy for NY Liberty")
            if st.button("Generate Brief"):
                log_activity(st.session_state.username, "run_dispatch", f"Query: {dispatch_query}")
                st.write("**[Dispatch Output]:** This is a simulated strategic response based on current friction data.")
                
        with tab2:
            st.write("Brainstorm new angles directly with the system lake.")
            st.info("🔄 We are currently fine-tuning this API connection. Full module will be online for the next deep dive.")
            
        with tab3:
            st.write("Cross-reference current signals with historical data to track macro patterns.")
            st.warning("⏳ Future feature: Will build reports from previous search histories over time.")

# Se selecionar um projeto específico (Ex: Haypp)
else:
    st.subheader(f"💼 {selected_project} Research Desk")
    st.write("*Here we detail objectives and outstanding questions we're trying to answer through listening and research.*")
    
    # Espaço para Curadoria Humana (Notas e Rating)
    with st.container(border=True):
        st.markdown("### 📝 Collected Project Data & Notes")
        note_input = st.text_area("Add manual note or observation to this project:")
        rating = st.slider("Delineate importance (Rating):", 1, 5, 3)
        
        if st.button("Save Entry to Project Desk"):
            log_activity(
                st.session_state.username, 
                "add_project_note", 
                f"Project: {selected_project} | Rating: {rating} | Note: {note_input[:30]}..."
            )
            st.success("Data successfully recorded into the project workflow!")

# ==========================================
# 5. HISTÓRICO DE EDIÇÕES / AUDIT LOG (Visível para o time)
# ==========================================
st.markdown("---")
with st.expander("📄 View Team Activity History (Audit Log)"):
    try:
        with open("activity_log.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in reversed(lines):  # Mostra o mais recente no topo
                data = json.loads(line.strip())
                # Formata a linha bonitinha para exibição
                st.text(f"[{data['timestamp']}] {data['user'].upper()} executed '{data['action']}' → {data['details']}")
    except FileNotFoundError:
        st.info("No activity recorded in this session yet.")
