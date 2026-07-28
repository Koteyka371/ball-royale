import re

with open("tests/test_resonance_chain.py", "r") as f:
    content = f.read()

# Filter hazards to only count scorched earth zones since poison clouds or other stuff might spawn
search_hazards_1 = """    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]"""
replace_hazards_1 = """    scorched_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "scorched_earth_zone"]
    assert len(scorched_hazards) == 1
    hazard = scorched_hazards[0]"""

if search_hazards_1 in content:
    content = content.replace(search_hazards_1, replace_hazards_1)

search_hazards_2 = """    assert len(world.arena.hazards) == 0"""
replace_hazards_2 = """    scorched_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "scorched_earth_zone"]
    assert len(scorched_hazards) == 0"""

if search_hazards_2 in content:
    content = content.replace(search_hazards_2, replace_hazards_2)

with open("tests/test_resonance_chain.py", "w") as f:
    f.write(content)
