import json
import uuid
import os

def create_idea(title, description):
    filename = f"src/ideas/idea_{uuid.uuid4().hex[:8]}.json"
    with open(filename, 'w') as f:
        json.dump({"title": title, "description": description}, f, indent=2)
    print(f"Created {filename}")

if not os.path.exists("src/ideas"):
    os.makedirs("src/ideas")

create_idea("Weather Totems", "Totems scattered across the map that players can destroy to change the current arena weather, gaining a tactical advantage.")
create_idea("Shadow Clones", "A new booster that spawns 3 AI-controlled clones of the player that mimic their movements but deal reduced damage and vanish after taking a hit.")
