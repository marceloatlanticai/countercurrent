import streamlit as st
import time

# Configuração da página - Estética Atlantic
st.set_page_config(page_title="Countercurrent.ai | The Wire Room", page_icon="🌊", layout="wide")

# Estilização CSS para parecer um terminal de inteligência/fita de teletipo
st.markdown("""
    <style>
    .report-text { font-family: 'Courier New', Courier, monospace; background-color: #f0f2f6; padding: 20px; border-left: 5px solid #000; }
    .stButton>button { background-color: #000; color: #fff; border-radius: 0px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: Configurações e Filosofia ---
with st.sidebar:
    st.title("🌊 Countercurrent.ai")
    st.subheader("Foundational Thinking")
    st.info("Current Lens: 'Human Touch & Tactile Premium' (Atlantic Philosophy)")
    st.divider()
    target_topic = st.text_input("Monitor Topic/Client:", value="Automotive Industry")
    st.divider()
    st.write("System Status: **Ready to Scan**")

# --- HEADER ---
st.title("The Wire Room")
st.write(f"Monitoring currents for: **{target_topic}**")

# --- COLUNAS: Input e Data Lake ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Ingestion")
    source = st.multiselect("Select Sources:", ["Reddit", "YouTube", "Tech Blogs", "Past Reports"], default=["Reddit", "Tech Blogs"])
    
    if st.button("RUN SCAN"):
        with st.status("Scanning sources...", expanded=True) as status:
            st.write("Searching r/cars and r/electricvehicles...")
            time.sleep(1)
            st.write("Analyzing sentiment on latest articles...")
            time.sleep(1)
            st.write("Comparing with Atlantic Philosophy...")
            status.update(label="Scan Complete!", state="complete", expanded=False)
            
        st.session_state['scan_done'] = True

# --- ÁREA DE RESULTADOS: O DISPATCH (Item 2 do seu desenho) ---
if st.session_state.get('scan_done'):
    with col2:
        st.subheader("2. Weekly Dispatch (Draft)")
        
        # Simulando o que a IA geraria após ler os dados brutos
        with st.container():
            st.markdown("""
            <div class="report-text">
            <strong>[DISPATCH #001 - AUTOMOTIVE]</strong><br><br>
            <strong>THE CURRENT:</strong> Excessive digitization. Brands are removing physical buttons for "cost-efficiency" disguised as "modernity".<br><br>
            <strong>THE SIGNAL:</strong> Massive backlash on Reddit r/cars regarding the safety of touchscreen-only climate controls.<br><br>
            <strong>THE COUNTERCURRENT PROVOCATION:</strong> 
            What if the next premium is 'The Tactile Luxury'? We should advise our client to reclaim physical 
            precision. In a glass world, a knurled aluminum knob is a revolutionary act.
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        
        # Item 3 do seu desenho: Meta-Analysis / Thinker Partner
        st.subheader("3. Thinker Partner (Meta-Analysis)")
        with st.expander("Ask a strategic question about this dispatch"):
            user_question = st.text_input("E.g.: How does this shift affect Gen Z buyers?")
            if user_question:
                st.write("**Thinker Partner:** Based on our philosophy, Gen Z seeks 'extreme authenticity'. A physical interface offers a grounding experience that glass cannot replicate. This aligns with our 'Tactile Premium' strategy.")
