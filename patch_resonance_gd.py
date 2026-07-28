import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

# simultaneous
search_simultaneous = """            var simultaneous = (decoys.size() >= 2)"""
replace_simultaneous = """            var simultaneous = (decoys.size() >= 2)
            var resonance_chain = (decoys.size() >= 3)

            var center_x = 0.0
            var center_y = 0.0
            if resonance_chain:
                for dec in decoys:
                    center_x += dec.x if "x" in dec else (dec.get_meta("x") if dec.has_method("has_meta") and dec.has_meta("x") else 0.0)
                    center_y += dec.y if "y" in dec else (dec.get_meta("y") if dec.has_method("has_meta") and dec.has_meta("y") else 0.0)
                center_x /= decoys.size()
                center_y /= decoys.size()
            elif "x" in decoys[0]:
                center_x = decoys[0].x
                center_y = decoys[0].y"""

if search_simultaneous in content:
    content = content.replace(search_simultaneous, replace_simultaneous)
else:
    print("Could not find simultaneous in gd.")

search_radius = """                if simultaneous:
                    radius *= 2.0
                    explosion_damage *= 2.0"""
replace_radius = """                if simultaneous:
                    radius *= 2.0
                    explosion_damage *= 2.0
                if resonance_chain:
                    radius = 400.0
                    explosion_damage = 150.0

                    if world != null and "arena" in world and "hazards" in world.arena:
                        var h_id = randi() % 90000 + 10000
                        var scorched = {
                            "id": h_id,
                            "x": center_x,
                            "y": center_y,
                            "radius": 40.0,
                            "kind": "scorched_earth_zone",
                            "duration": 9999.0,
                            "damage": 5.0,
                            "owner_id": owner_id,
                            "active": true
                        }
                        world.arena.hazards.append(scorched)"""

if search_radius in content:
    content = content.replace(search_radius, replace_radius)
else:
    print("Could not find radius in gd.")

search_loop_start = """                                if dist <= radius:
                                    var is_enemy = (other_team != b_team)
                                    var is_ally = (other_team == b_team)
                                    var is_other_decoy = false
                                    if "is_decoy" in other: is_other_decoy = other.is_decoy
                                    elif other.has_method("get_meta") and other.has_meta("is_decoy"): is_other_decoy = other.get_meta("is_decoy")

                                    if is_ally and is_other_decoy:"""
replace_loop_start = """                                if dist <= radius:
                                    var is_enemy = (other_team != b_team)
                                    var is_ally = (other_team == b_team)
                                    var is_other_decoy = false
                                    if "is_decoy" in other: is_other_decoy = other.is_decoy
                                    elif other.has_method("get_meta") and other.has_meta("is_decoy"): is_other_decoy = other.get_meta("is_decoy")

                                    if resonance_chain and is_enemy:
                                        var dx_c = other.x - center_x
                                        var dy_c = other.y - center_y
                                        var dist_c = sqrt(dx_c*dx_c + dy_c*dy_c)
                                        if dist_c > 10.0:
                                            var pull_speed = 300.0
                                            if "vx" in other:
                                                other.vx -= (dx_c / dist_c) * pull_speed
                                            elif other.has_method("set_meta"):
                                                var vvx = other.get_meta("vx") if other.has_meta("vx") else 0.0
                                                other.set_meta("vx", vvx - (dx_c / dist_c) * pull_speed)

                                            if "vy" in other:
                                                other.vy -= (dy_c / dist_c) * pull_speed
                                            elif other.has_method("set_meta"):
                                                var vvy = other.get_meta("vy") if other.has_meta("vy") else 0.0
                                                other.set_meta("vy", vvy - (dy_c / dist_c) * pull_speed)

                                        if "hp" in other:
                                            other.hp -= explosion_damage
                                        elif other.has_method("set_meta"):
                                            var ohp = other.get_meta("hp") if other.has_meta("hp") else 100.0
                                            other.set_meta("hp", ohp - explosion_damage)

                                        if "stutter_timer" in other:
                                            other.stutter_timer += 3.0
                                        elif other.has_method("set_meta"):
                                            var ost = other.get_meta("stutter_timer") if other.has_meta("stutter_timer") else 0.0
                                            other.set_meta("stutter_timer", ost + 3.0)

                                        if world != null and "events" in world:
                                            world.events.append({"type": "visual_effect", "data": {"type": "resonance_chain_hit", "x": other.x, "y": other.y}})
                                        continue

                                    if is_ally and is_other_decoy:"""

if search_loop_start in content:
    content = content.replace(search_loop_start, replace_loop_start)
else:
    print("Could not find loop start in gd.")

with open("src/ai/action.gd", "w") as f:
    f.write(content)
print("Patch applied to action.gd")
