import re
with open("src/arena/procedural_arena.py", "r") as f:
    code = f.read()

new_code = code.replace(
"""            kind = random.choice(["spikes", "lava", "fake_booster", "decoy_item", "link_booster", "stamina_booster", "weather_booster", "poison_cloud", "proximity_trap", "spinning_laser", "healing_spring", "temporal_rift", "bumper", "tornado", "lightning_storm", "hidden_trap", "hidden_mine", "silence_booster", "freeze_booster", "switch", "magnet", "quicksand", "magnet_booster", "breakable_wall", "portal_gun_item", "wormhole", "clone_booster", "stealth_zone", "invert_booster", "reverse_gravity_booster", "stamina_drain_zone", "tether_trap", "slip_zone", "tall_grass", "vortex"])""",
"""            kind = random.choice(["spikes", "lava", "fake_booster", "decoy_item", "link_booster", "stamina_booster", "weather_booster", "poison_cloud", "proximity_trap", "spinning_laser", "healing_spring", "temporal_rift", "bumper", "tornado", "lightning_storm", "hidden_trap", "hidden_mine", "silence_booster", "freeze_booster", "switch", "magnet", "quicksand", "magnet_booster", "breakable_wall", "portal_gun_item", "wormhole", "clone_booster", "stealth_zone", "invert_booster", "reverse_gravity_booster", "stamina_drain_zone", "tether_trap", "slip_zone", "tall_grass", "vortex", "ice_patch"])""")

with open("src/arena/procedural_arena.py", "w") as f:
    f.write(new_code)
