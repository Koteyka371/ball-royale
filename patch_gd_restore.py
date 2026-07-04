import sys

def patch_gd():
    filepath = "src/ai/game_modes.gd"
    with open(filepath, 'r') as f:
        content = f.read()

    # Search pattern 1
    s1 = """                    if not near_shelter_or_flare:
                        if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
                        elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
                        else: b.perception_radius = 250.0 * 0.3"""
    r1 = """                    if near_shelter_or_flare:
                        if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius")
                        elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius
                        else: b.perception_radius = 250.0
                    else:
                        if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
                        elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
                        else: b.perception_radius = 250.0 * 0.3"""

    # Search pattern 2
    s2 = """					else:
						if not near_shelter_or_flare:
							if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
							elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
							else: b.perception_radius = 250.0 * 0.3"""
    r2 = """					else:
						if near_shelter_or_flare:
							if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius")
							elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius
							else: b.perception_radius = 250.0
						else:
							if b.has_method("get_meta") and b.has_meta("base_perception_radius"): b.perception_radius = b.get_meta("base_perception_radius") * 0.3
							elif "base_perception_radius" in b: b.perception_radius = b.base_perception_radius * 0.3
							else: b.perception_radius = 250.0 * 0.3"""

    if s1 in content and s2 in content:
        content = content.replace(s1, r1)
        content = content.replace(s2, r2)
        with open(filepath, 'w') as f:
            f.write(content)
        print("Updated GDScript successfully")
    else:
        print("Failed to find replacement strings")

patch_gd()
