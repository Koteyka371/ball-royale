import re
from pathlib import Path

def process_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Add to arena procedural choices
    content = re.sub(
        r'(\["spikes", "lava", "fake_booster", "decoy_item", "link_booster", "stamina_booster", "weather_booster", "poison_cloud", "proximity_trap", "spinning_laser", "healing_spring", "temporal_rift", "bumper", "tornado", "lightning_storm", "hidden_trap", "silence_booster", "switch", "magnet", "quicksand", "magnet_booster", "breakable_wall", "portal_gun_item", "wormhole", "clone_booster", "stealth_zone"\])',
        r'["spikes", "lava", "fake_booster", "decoy_item", "link_booster", "stamina_booster", "weather_booster", "poison_cloud", "proximity_trap", "spinning_laser", "healing_spring", "temporal_rift", "bumper", "tornado", "lightning_storm", "hidden_trap", "silence_booster", "switch", "magnet", "quicksand", "magnet_booster", "breakable_wall", "portal_gun_item", "wormhole", "clone_booster", "stealth_zone", "invert_booster"]',
        content
    )

    content = re.sub(
        r'(elif kind == "stamina_booster" or kind == "weather_booster" or kind == "magnet_booster" or kind == "clone_booster":)',
        r'elif kind == "stamina_booster" or kind == "weather_booster" or kind == "magnet_booster" or kind == "clone_booster" or kind == "invert_booster":',
        content
    )

    with open(file_path, 'w') as f:
        f.write(content)

process_file("src/arena/procedural_arena.py")

with open("src/arena/procedural_arena.gd", "r") as f:
    content = f.read()
content = re.sub(
    r'(elif r < 0.42:\n\s+kind = "clone_booster")',
    r'\1\n        elif r < 0.43:\n            kind = "invert_booster"',
    content
)
content = re.sub(
    r'(elif kind == "stamina_booster" or kind == "weather_booster" or kind == "magnet_booster" or kind == "clone_booster":)',
    r'elif kind == "stamina_booster" or kind == "weather_booster" or kind == "magnet_booster" or kind == "clone_booster" or kind == "invert_booster":',
    content
)
with open("src/arena/procedural_arena.gd", "w") as f:
    f.write(content)

with open("src/arena/test_procedural_arena.py", "r") as f:
    content = f.read()
content = re.sub(
    r'("clone_booster", "stealth_zone"\])',
    r'"clone_booster", "stealth_zone", "invert_booster"]',
    content
)
with open("src/arena/test_procedural_arena.py", "w") as f:
    f.write(content)
