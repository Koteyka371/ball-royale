import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Let's insert the resonance chain check
search_simultaneous = """                            simultaneous = (len(decoy_sibs) >= 2)"""
replace_simultaneous = """                            simultaneous = (len(decoy_sibs) >= 2)
                            resonance_chain = (len(decoy_sibs) >= 3)

                            center_x = sum([sib.x for sib in decoy_sibs]) / len(decoy_sibs) if resonance_chain else b.x
                            center_y = sum([sib.y for sib in decoy_sibs]) / len(decoy_sibs) if resonance_chain else b.y
"""
if search_simultaneous in content:
    content = content.replace(search_simultaneous, replace_simultaneous)
else:
    print("Could not find simultaneous definition.")

search_radius = """                            if simultaneous:
                                radius *= 2.0
                                explosion_damage *= 2.0"""
replace_radius = """                            if simultaneous:
                                radius *= 2.0
                                explosion_damage *= 2.0
                            if resonance_chain:
                                radius = 400.0
                                explosion_damage = 150.0

                                # Spawn scorched earth zone
                                if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                                    from arena.arena_types import Hazard
                                    import random
                                    h_id = getattr(self.world, "next_id", random.randint(10000, 99999))
                                    if hasattr(self.world, "next_id"):
                                        self.world.next_id += 1

                                    scorched = Hazard(h_id, center_x, center_y, 40.0, "scorched_earth_zone", 5.0)
                                    scorched.duration = 9999.0
                                    scorched.owner_id = owner_id
                                    self.world.arena.hazards.append(scorched)
"""
if search_radius in content:
    content = content.replace(search_radius, replace_radius)
else:
    print("Could not find radius *= 2.0.")

search_loop_start = """                                    if dist <= radius:
                                        if is_ally and getattr(other, "is_decoy", False):"""
replace_loop_start = """                                    if dist <= radius:
                                        if resonance_chain and is_enemy:
                                            # Pull enemies toward the center
                                            dx_c = other.x - center_x
                                            dy_c = other.y - center_y
                                            dist_c = math.sqrt(dx_c*dx_c + dy_c*dy_c)
                                            if dist_c > 10.0:
                                                pull_speed = 300.0
                                                other.vx -= (dx_c / dist_c) * pull_speed
                                                other.vy -= (dy_c / dist_c) * pull_speed

                                            # True damage ignores armor (direct HP subtraction)
                                            other.hp -= explosion_damage
                                            other.stutter_timer = getattr(other, "stutter_timer", 0.0) + 3.0

                                            if hasattr(self.world, "events"):
                                                self.world.events.append({"type": "visual_effect", "data": {"type": "resonance_chain_hit", "x": other.x, "y": other.y}})

                                            continue  # Skip normal explosion effects for enemies

                                        if is_ally and getattr(other, "is_decoy", False):"""
if search_loop_start in content:
    content = content.replace(search_loop_start, replace_loop_start)
else:
    print("Could not find loop start.")

with open("src/ai/action.py", "w") as f:
    f.write(content)
print("Patch applied to action.py")
