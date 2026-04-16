import streamlit as st
import praw
import time

# --- CONFIGURAÇÃO DAS CHAVES (Coloque as suas aqui ou no .env) ---
# Dica: Em produção, nunca deixe as chaves expostas no código.
REDDIT_CLIENT_ID = "SEU_CLIENT_ID_AQUI"
REDDIT_CLIENT_SECRET = "SEU_CLIENT_SECRET_AQUI"
REDDIT_USER_AGENT = "countercurrent_v1_by_marcelo"

# --- FUNÇÃO DE BUSCA REAL NO REDDIT ---
def fetch_real_reddit_data(query):
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        # Busca nos subreddits de carros os posts "Quentes" (Hot)
        subreddit = reddit.subreddit("cars+electricvehicles+automotive")
        search_results = subreddit.search(query, limit=5)
        
        posts = []
        for post in search_results:
            posts.append({
                "title": post.title,
                "text": post.selftext[:300] + "...", # Pega os primeiros 300 caracteres
                "url": post.url
            })
        return posts
    except Exception as e:
        return f"Error: {e}"

# --- INTERFACE STREAMLIT (Atualizada) ---
st.set_page_config(page_title="Countercurrent.ai", page_icon="🌊", layout="wide")

st.title("The Wire Room | Live Feed")

topic = st.sidebar.text_input("Monitor Topic:", "Physical buttons in cars")

if st.sidebar.button("RUN LIVE SCAN"):
    with st.spinner("Accessing Reddit API..."):
        results = fetch_real_reddit_data(topic)
        
        if isinstance(results, list):
            st.subheader(f"Latest Signals for: {topic}")
            
            for i, post in enumerate(results):
                with st.expander(f"SIGNAL #{i+1}: {post['title']}"):
                    st.write(post['text'])
                    st.caption(f"Source: {post['url']}")
                    
                    # Simulação do "Cérebro" da Atlantic analisando o post real
                    st.markdown("---")
                    st.markdown("**Atlantic Brain Analysis:**")
                    st.info("Identifying countercurrent opportunity... (Requires OpenAI Key for full analysis)")
        else:
            st.error(results)
