import json
import random
import time
import os
from datetime import datetime

def generate_mock_signals():
    # Canais atualizados incluindo BlueSky
    sources = ["TikTok", "Reddit", "Pinterest", "BlueSky", "Twitter/X"]
    
    # Contexto focado em NY Liberty e Tendências
    topics = [
        "NY Liberty pre-game outfits", "WNBA lifestyle shifts", 
        "Stadium tunnel walk fashion", "Digital fandom communities",
        "Luxury brands entering women sports", "Courtside culture",
        "Athletic-chic aesthetic", "Equity in sports marketing"
    ]
    
    verbs = ["exploding", "shifting", "declining", "merging with", "redefining"]
    
    signals = []
    
    for _ in range(15):
        source = random.choice(sources)
        topic = random.choice(topics)
        verb = random.choice(verbs)
        
        # Gerador de títulos simulando cada rede
        if source == "BlueSky":
            title = f"Post: Why {topic} is {verb} the way we think about WNBA."
        elif source == "TikTok":
            title = f"Trend Alert: {topic} is {verb} right now. #wnba #fashion"
        elif source == "Pinterest":
            title = f"Board: {topic} inspiration and {verb} styles."
        else:
            title = f"{topic} is {verb} the current strategy."

        signal = {
            "source": source,
            "client_tag": "NY_LIBERTY",
            "title": title,
            "content": f"Detailed analysis of how {topic} is {verb} through social signals and engagement patterns in {source}.",
            "timestamp": datetime.now().isoformat()
        }
        signals.append(signal)
    
    return signals

def run_ingestion():
    print(f"[{datetime.now()}] Starting ingestion...")
    
    # Garante que a pasta data existe
    if not os.path.exists('data'):
        os.makedirs('data')
        
    new_signals = generate_mock_signals()
    
    # Salva no formato JSONL
    with open("data/signals.jsonl", "a", encoding="utf-8") as f:
        for s in new_signals:
            f.write(json.dumps(s) + "\n")
            
    print(f"✅ Success: {len(new_signals)} new signals ingested (including BlueSky).")

if __name__ == "__main__":
    run_ingestion()
