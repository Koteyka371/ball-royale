import re

file_path = "src/arena/procedural_arena.py"
with open(file_path, "r") as f:
    content = f.read()

# Add deployable_proximity_mud_puddle to the items choice
content = content.replace(
    'item_kind = random.choice(["healing_spring"',
    'item_kind = random.choice(["deployable_proximity_mud_puddle", "deployable_mud_puddle", "deployable_acid_puddle", "healing_spring"'
)

# And to the hazards choice just in case items are also spawned there
content = content.replace(
    'kind = random.choice(["spikes",',
    'kind = random.choice(["deployable_proximity_mud_puddle", "deployable_mud_puddle", "deployable_acid_puddle", "spikes",'
)

with open(file_path, "w") as f:
    f.write(content)
