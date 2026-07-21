with open("src/ai/action.py", "r") as f:
    content = f.read()

search_b = """                                        radius_mult = 1.5 if is_ts and getattr(hazard, "kind", "") == "tornado" else 1.0
                                        bpull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, bdist)) * 50.0 * delta * lifetime_mult
                                        b.x += bnx * bpull_strength"""
replace_b = """                                        radius_mult = 1.5 if is_ts and getattr(hazard, "kind", "") == "tornado" else 1.0
                                        bpull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, bdist)) * 50.0 * delta * lifetime_mult
                                        if getattr(b, "gravity_multiplier_timer", 0.0) > 0 and hazard.kind in ("black_hole", "clone_black_hole", "massive_black_hole", "mini_black_hole", "gravity_well"):
                                            bpull_strength *= 10.0
                                        b.x += bnx * bpull_strength"""
content = content.replace(search_b, replace_b)

with open("src/ai/action.py", "w") as f:
    f.write(content)
