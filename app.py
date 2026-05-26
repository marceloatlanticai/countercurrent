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

# Estilização CSS para as Tags Coloridas (Rounded Rectangles)
st.markdown("""
<style>
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        margin-right: 8px;
    }
    .tag-tension { background-color: #ef4444; } /* Vermelho */
    .tag-competitor { background-color: #f59e0b; color: #1e293b; } /* Amarelo */
    .tag-barrier { background-color: #3b82f6; } /* Azul */
    .tag-custom { background-color: #a855f7; } /* Roxo */
    .tag-general { background-color: #64748b; } /* Cinza */
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
    vault_data = {"Haypp": [], "Likepost": [], "Sallve": [], "Oceano Azul": [], "Pinterest": []}
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
        "Haypp": "Search for answers regarding nicotine pouch market disruption and alternative cultural patterns.",
        "Likepost": "Analyze micro-influencer exhaustion and the friction against traditional aesthetic feeds.",
        "Sallve": "Understand the shift toward chaotic curations, skin-intellectual trends, and clean beauty barriers.",
        "Oceano Azul": "Explore counter-cultural environmental movements and alternative sustainability narratives.",
        "Pinterest": "Understand the shift toward chaotic curations, 'Anti-Athleisure' trends, and private digital mood boards as a brand ecosystem strategy."
    }

# MOTOR DE CATEGORIZAÇÃO INTELIGENTE
def get_ai_category(title, content):
    text = (title + " " + content).lower()
    rules = st.session_state.custom_prompt_rules.lower()
    if rules and any(word in text for word in rules.split()): return "Custom Strategic Alert"
    if "fashion" in text or "aesthetic" in text or "shift" in text or "core" in text or "beauty" in text: return "Cultural Tension"
    elif "competitor" in text or "nike" in text or "brand" in text or "market" in text or "cosméticos" in text: return "Competitor Activity"
    elif "barrier" in text or "fatigue" in text or "rejecting" in text or "drop" in text or "pouches" in text: return "Consumer Barrier Identified"
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
# 2. TELA DE LOGIN
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>⟳ Countercurrent.ai</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username_input = st.text_input("Username").strip().lower()
            password_input = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if username_input in USER_CREDENTIALS and USER_CREDENTIALS[username_input] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    log_activity(username_input, "login", "User logged in")
                    st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

# ==========================================
# 3. BARRA LATERAL
# ==========================================
st.sidebar.title("⟳ Countercurrent.ai")
st.sidebar.write(f"Logged in as: **{st.session_state.username.capitalize()}**")
st.sidebar.markdown("---")

st.sidebar.subheader("📁 Ongoing Projects")
project_options = ["Master Dashboard", "Haypp", "Likepost", "Sallve", "Oceano Azul", "Pinterest"]
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
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()

# ==========================================
# 4. ÁREA PRINCIPAL
# ==========================================
st.title(f"{selected_project}")

project_vault = load_from_vault()

if selected_project == "Master Dashboard":
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("🌐 Master Currents Feed")
        
        # FILTROS LADO A LADO
        col_f1, col_f2 = st.columns([1, 1])
        with col_f1:
            source_filter = st.multiselect("Filter Source:", options=["All Networks", "TikTok", "Reddit", "Pinterest", "BlueSky", "Twitter/X"], default=["All Networks"])
        with col_f2:
            client_filter = st.multiselect("Filter Target Client:", options=["All Clients", "Ny_liberty", "Haypp", "Likepost", "Sallve", "Oceano_azul", "Pinterest"], default=["All Clients"])

        # 🛠️ NOVA EVOLUÇÃO: Terceiro filtro dedicado para as Categorias da IA (Fica logo abaixo dos dois primeiros)
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
            # Funil de Filtro 1: Redes
            if "All Networks" in source_filter or not source_filter: stage_1 = all_signals
            else: stage_1 = [s for s in all_signals if s.get("source") in source_filter]
            
            # Funil de Filtro 2: Clientes
            if "All Clients" in client_filter or not client_filter: stage_2 = stage_1
            else:
                client_filter_clean = [c.lower() for c in client_filter]
                stage_2 = [s for s in stage_1 if s.get("client_tag", "").lower() in client_filter_clean]
                
            # Funil de Filtro 3: Categorias da IA (Adicionado dinamicamente à listagem)
            if "All Categories" in category_filter or not category_filter:
                filtered_signals = stage_2
            else:
                filtered_signals = []
                for sig in stage_2:
                    # Calcula a categoria em tempo real para bater com o filtro selecionado
                    real_cat = get_ai_category(sig.get("title", ""), sig.get("content", ""))
                    if real_cat in category_filter:
                        filtered_signals.append(sig)

        st.caption(f"Showing {len(filtered_signals)} deep signals from database based on combined parameters.")

        with st.container(height=550):
            for i, sig in enumerate(filtered_signals):
                ai_category = get_ai_category(sig.get("title", ""), sig.get("content", ""))
                client_display = sig.get("client_tag", "General").replace("_", " ").capitalize()
                
                with st.container(border=True):
                    # Ingestão de metadados limpos
                    st.markdown(f"📱 **{sig.get('source')}** | 🏢 *Client: {client_display}*")
                    
                    # 🛠️ NOVA EVOLUÇÃO: Renderização do Rounded Rectangle Colorido baseado na Categoria
                    tag_html = get_tag_html(ai_category)
                    st.markdown(tag_html, unsafe_allow_html=True)
                    st.write("") # Pequeno espaçamento estético
                    
                    st.markdown(f"**{sig.get('title')}**")
                    st.write(sig.get('content'))
                    
                    source_url = sig.get("url", "#")
                    st.markdown(f"[View Live Source]({source_url})")
                    
                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                        target_project = st.selectbox("Send to project:", ["Haypp", "Likepost", "Sallve", "Oceano Azul", "Pinterest"], key=f"sel_{i}")
                    with col_btn2:
                        st.write("")
                        if st.button("📌 Add to Desk", key=f"btn_{i}"):
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
                st.write("**[Dispatch Output]:** Simulated strategic brief for: " + dispatch_query)

# PÁGINAS DOS PROJETOS
else:
    with st.container(border=True):
        st.markdown("### 📋 The Brief")
        current_brief = st.text_area("Project Objectives:", value=st.session_state.project_briefs[selected_project], key="brief_area")
        if st.button("Update Project Brief"):
            st.session_state.project_briefs[selected_project] = current_brief
            st.toast("Brief updated!")

    st.markdown("---")
    col_proj_left, col_proj_right = st.columns([1, 1])
    
    with col_proj_left:
        st.markdown("### 🗂️ Research Desk (Collected Data)")
        saved_items = project_vault[selected_project]
        
        if len(saved_items) == 0: st.info("No data collected yet.")
        else:
            for item in saved_items:
                with st.container(border=True):
                    st.markdown(f"**[{item['category']}]** — *Curated by {item['saved_by'].capitalize()}*")
                    st.write(item['title'])
                    st.markdown(f"[🔗 View Original Live Source]({item['link']})")

    with col_proj_right:
        st.markdown("### 🎯 Currents Summary & Whitespaces")
        if st.button(f"🔮 Run AI Synthesis for {selected_project}", use_container_width=True):
            if len(saved_items) == 0: st.warning("Research Desk is empty.")
            else:
                with st.spinner("Analyzing team curation..."):
                    st.markdown("#### 🔍 Identified Whitespace")
                    st.info(f"Based on the {len(saved_items)} permanent signals saved for {selected_project}, there is an unexploited gap in subverting traditional category codes.")

# AUDIT LOG
st.markdown("---")
with st.expander("📄 View Team Activity History (Audit Log)"):
    try:
        with open("activity_log.jsonl", "r", encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                data = json.loads(line.strip())
                st.text(f"[{data['timestamp']}] {data['user'].upper()} executed '{data['action']}' → {data['details']}")
    except: st.info("No activity recorded yet.")
