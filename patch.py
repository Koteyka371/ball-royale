with open("src/arena/procedural_arena.py", "r") as f:
    content = f.read()

# We need to add "shrinking_zone" to the hazard generation in procedural_arena.py
import re

old = """            kind = random.choice(["spikes", "lava", "fake_booster", "decoy_item", "link_booster", "stamina_booster", "weather_booster", "poison_cloud", "proximity_trap", "spinning_laser", "healing_spring", "temporal_rift", "bumper", "tornado", "lightning_storm", "hidden_trap", "silence_booster", "switch", "magnet", "quicksand", "magnet_booster", "breakable_wall", "portal_gun_item", "wormhole", "clone_booster", "stealth_zone", "invert_booster"])"""
new = """            kind = random.choice(["spikes", "lava", "fake_booster", "decoy_item", "link_booster", "stamina_booster", "weather_booster", "poison_cloud", "proximity_trap", "spinning_laser", "healing_spring", "temporal_rift", "bumper", "tornado", "lightning_storm", "hidden_trap", "silence_booster", "switch", "magnet", "quicksand", "magnet_booster", "breakable_wall", "portal_gun_item", "wormhole", "clone_booster", "stealth_zone", "invert_booster", "shrinking_zone"])"""
content = content.replace(old, new)

old = """            elif kind == "stealth_zone":
                radius = random.uniform(40.0, 80.0)
                damage = 0.0"""
new = """            elif kind == "stealth_zone":
                radius = random.uniform(40.0, 80.0)
                damage = 0.0
            elif kind == "shrinking_zone":
                radius = random.uniform(100.0, 200.0)
                damage = 15.0"""
content = content.replace(old, new)

old = """            if kind == "temporal_rift":
                new_hazard.time_scale = random.choice([0.5, 1.5, 2.0])
            elif kind == "magnet":
                setattr(new_hazard, "polarity", random.choice([1, -1]))
            self.hazards.append(new_hazard)"""
new = """            if kind == "temporal_rift":
                new_hazard.time_scale = random.choice([0.5, 1.5, 2.0])
            elif kind == "magnet":
                setattr(new_hazard, "polarity", random.choice([1, -1]))
            elif kind == "shrinking_zone":
                setattr(new_hazard, "shrink_rate", random.uniform(2.0, 10.0))
                setattr(new_hazard, "min_radius", random.uniform(20.0, 50.0))
            self.hazards.append(new_hazard)"""
content = content.replace(old, new)

old = """                elif getattr(h, "kind", "") == "fire_ring" or getattr(h, "kind", "") == "poison_nova":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                        else:
                            shrink_rate = getattr(h, "shrink_rate", 50.0)
                            h.radius = max(0.0, h.radius - shrink_rate * delta)"""
new = """                elif getattr(h, "kind", "") == "fire_ring" or getattr(h, "kind", "") == "poison_nova":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                        else:
                            shrink_rate = getattr(h, "shrink_rate", 50.0)
                            h.radius = max(0.0, h.radius - shrink_rate * delta)
                elif getattr(h, "kind", "") == "shrinking_zone":
                    shrink_rate = getattr(h, "shrink_rate", 5.0)
                    min_radius = getattr(h, "min_radius", 20.0)
                    if h.radius > min_radius:
                        h.radius -= shrink_rate * delta
                        if h.radius < min_radius:
                            h.radius = min_radius"""
content = content.replace(old, new)

with open("src/arena/procedural_arena.py", "w") as f:
    f.write(content)
