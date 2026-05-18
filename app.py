import streamlit as st
import datetime
import json

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

# 🧠 BANCO DE DADOS TEMPORÁRIO (Memória dos Projetos)
if "project_data" not in st.session_state:
    st.session_state.project_data = {
        "Haypp": [],
        "Likepost": [],
        "Pinterest": [],
        "Salvie": [],
        "Oceano Ozul": []
    }

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
    
    with col_left:
        st.subheader("🌐 Master Currents Feed")
        st.caption("Live signals from TikTok, Reddit, Pinterest, and BlueSky.")
        
        # Sinais simulados (adicionei links reais do Google/TikTok/Trends como exemplo)
        signals = [
            {"category": "Cultural Tension", "title": "The rise of Anti-Athleisure in metropolitan centers. Consumers are trading stretch yoga pants for structural denim and tailoring as a subtle rejection of constant corporate-casual casualness.", "link": "https://trends.google.com"},
            {"category": "Competitor Activity", "title": "Nike launches quiet-luxury capsule collection with zero logos. The industry giant pivots away from loud performance emblems to secure high-fashion real estate.", "link": "https://www.tiktok.com"},
            {"category": "Consumer Barrier Identified", "title": "Gen-Z rejecting automated customer service in luxury retail. Social proof shows a massive drop in satisfaction when high-ticket purchases are handled by bots instead of experts.", "link": "https://www.reddit.com"},
            {"category": "Company Update/Earnings", "title": "Key luxury holding groups report a 4% drop in traditional brick-and-mortar retail traffic, while underground digital private networks double their active membership.", "link": "https://www.pinterest.com"}
        ]
        
        for i, sig in enumerate(signals):
            with st.container(border=True):
                st.markdown(f"**[{sig['category']}]**")
                st.write(sig['title']) # Exibe o texto completo sem cortes
                st.markdown(f"[View Live Source]({sig['link']})")
                
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    target_project = st.selectbox("Send to project:", ["Haypp", "Likepost", "Pinterest", "Salvie", "Oceano Ozul"], key=f"sel_{i}")
                with col_btn2:
                    st.write("") 
                    if st.button("📌 Add to Desk", key=f"btn_{i}"):
                        # 💾 AGORA SALVA O LINK JUNTO COM O DADO COMPLETO
                        st.session_state.project_data[target_project].append({
                            "category": sig["category"],
                            "title": sig["title"],
                            "link": sig["link"], # Salvando o link real
                            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                            "saved_by": st.session_state.username
                        })
                        
                        log_activity(
                            st.session_state.username, 
                            "curate_signal", 
                            f"Added '{sig['title'][:25]}...' to {target_project} Desk"
                        )
                        st.toast(f"Saved to {target_project}!")

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
# 5. PÁGINAS DOS PROJETOS ESPECÍFICOS (Ex: Pinterest)
# ==========================================
else:
    st.subheader(f"💼 {selected_project} Research Desk")
    st.write("*Here we detail objectives and outstanding questions we're trying to answer through listening and research.*")
    
    st.markdown("### 🗂️ Collected Data from Master Feed")
    saved_items = st.session_state.project_data[selected_project]
    
    if len(saved_items) == 0:
        st.info("No data collected from Master Feed yet. Go to Master Dashboard to curate some signals!")
    else:
        for item in saved_items:
            with st.container(border=True):
                st.markdown(f"**[{item['category']}]** — *Saved at {item['timestamp']} by {item['saved_by'].capitalize()}*")
                
                # 🛠️ AJUSTE AQUI: Texto completo exibido de forma limpa
                st.write(item['title'])
                
                # 🛠️ AJUSTE AQUI: O link original agora aparece e funciona dentro do projeto!
                st.markdown(f"[🔗 View Original Live Source]({item['link']})")
    
    st.markdown("---")
    
    # Espaço para Notas Manuais
    with st.container(border=True):
        st.markdown("### 📝 Project Notes & Rating")
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
