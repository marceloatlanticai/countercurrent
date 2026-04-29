import json
import os
from datetime import datetime, timedelta

def populate():
    path = "data/dispatches.jsonl"
    os.makedirs("data", exist_ok=True)
    
    # Mock de dados estratégicos para simular histórico
    history = [
        {
            "topic": "WNBA Fandom & Aesthetics",
            "timestamp": (datetime.now() - timedelta(days=21)).isoformat(),
            "content": "**THE CURRENT:** WNBA is seen primarily as a growth story in sports business. **SIGNALS:** Focus on viewership records and ticket sales. **THE COUNTERCURRENT:** The 'Court-to-Catwalk' pipeline. Fans are more interested in what players wear to the stadium than the final score. **RATIONALE:** High fashion is the new fan engagement."
        },
        {
            "topic": "NY Liberty Fan Rituals",
            "timestamp": (datetime.now() - timedelta(days=14)).isoformat(),
            "content": "**THE CURRENT:** Mascot marketing is for kids. **SIGNALS:** Standard NBA mascot tropes. **THE COUNTERCURRENT:** Ellie the Elephant as a Queer/Fashion Icon. NY Liberty fans treat the mascot as a luxury brand collaborator. **RATIONALE:** Subcultural irony is the bridge between Gen Z and sports."
        },
        {
            "topic": "Pinterest x Sports Search",
            "timestamp": (datetime.now() - timedelta(days=7)).isoformat(),
            "content": "**THE CURRENT:** People use Pinterest for home decor and wedding planning. **SIGNALS:** High volume in 'aesthetic' searches. **THE COUNTERCURRENT:** Pinterest as the 'Visual Stadium'. Fans are building boards for game-day outfits, creating a new category of 'Sports-Visual-Planning'. **RATIONALE:** The stadium is the new runway."
        }
    ]

    with open(path, "a", encoding="utf-8") as f:
        for entry in history:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    print(f"✅ Histórico populado com {len(history)} despachos em {path}")

if __name__ == "__main__":
    populate()
