import sys

def patch_python_game_modes():
    filepath = "src/ai/game_modes.py"
    with open(filepath, 'r') as f:
        content = f.read()

    # FIRST OCCURRENCE (line ~614)
    search_str1 = """            elif self.weather == "sandstorm":
                b.cosmetic = "dust_mask"
                if getattr(b, "ball_type", "") == "sand_elemental":
                    b.speed = b.base_speed * 1.2
                    b.damage = b.base_damage
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.3
                    b.speed = b.base_speed * 0.7
                    b.damage = b.base_damage
                    b.dash_range_mult = 0.5
                    b.steering_mult = 0.5
                    if not hasattr(b, "sandstorm_timer"):
                        b.sandstorm_timer = 0.0
                    b.sandstorm_timer += delta
                    if b.sandstorm_timer >= 1.0:
                        b.sandstorm_timer = 0.0
                        if hasattr(b, "hp"):
                            b.hp -= 1.0
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                        if hasattr(b, "hp"):
                            b.hp -= 20.0
                    b.attack_accuracy = 0.5"""

    replace_str1 = """            elif self.weather == "sandstorm":
                b.cosmetic = "dust_mask"
                b_type = getattr(b, "ball_type", "")
                is_earth = b_type in ["tank", "druid", "juggernaut", "sand_elemental"] or (hasattr(b, "traits") and "earth" in getattr(b, "traits", []))

                shelters_or_flares = []
                if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                    for h in world.arena.hazards:
                        if getattr(h, "kind", "") in ["shelter", "flare"]:
                            shelters_or_flares.append(h)

                near_shelter_or_flare = False
                for h in shelters_or_flares:
                    dist_sq = (getattr(h, "x", 0) - getattr(b, "x", 0))**2 + (getattr(h, "y", 0) - getattr(b, "y", 0))**2
                    if dist_sq <= getattr(h, "radius", 0)**2:
                        near_shelter_or_flare = True
                        break

                if getattr(b, "ball_type", "") == "sand_elemental":
                    b.speed = b.base_speed * 1.2
                    b.damage = b.base_damage
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    if near_shelter_or_flare:
                        b.perception_radius = getattr(b, "base_perception_radius", 250.0)
                    else:
                        b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.3
                    b.speed = b.base_speed * 0.7
                    b.damage = b.base_damage
                    b.dash_range_mult = 0.5
                    b.steering_mult = 0.5
                    if not hasattr(b, "sandstorm_timer"):
                        b.sandstorm_timer = 0.0
                    b.sandstorm_timer += delta
                    if b.sandstorm_timer >= 1.0:
                        b.sandstorm_timer = 0.0
                        if hasattr(b, "hp") and not is_earth:
                            b.hp -= 1.0
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta and not is_earth:
                        if hasattr(b, "hp"):
                            b.hp -= 20.0
                    b.attack_accuracy = 0.5"""

    # SECOND OCCURRENCE (line ~1791)
    search_str2 = """            elif self.weather == "sandstorm":
                b.cosmetic = "dust_mask"
                if getattr(b, "ball_type", "") == "sand_elemental":
                    b.speed = b.base_speed * 1.2
                    b.damage = b.base_damage
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.3
                    b.speed = b.base_speed * 0.7 # Hard to move
                    b.damage = b.base_damage
                    b.dash_range_mult = 0.5
                    b.steering_mult = 0.5
                    if getattr(b, "ball_type", "") in ["trickster", "phantom", "mimic"]:
                        if not hasattr(b, "mirage_timer"):
                            b.mirage_timer = getattr(self, "random", __import__("random")).uniform(0.0, 5.0)
                        b.mirage_timer += delta
                        if b.mirage_timer >= 5.0:
                            b.mirage_timer = 0.0
                            if hasattr(world, "balls"):
                                import copy
                                decoy = copy.copy(b)
                                decoy.id = getattr(world, "next_id", getattr(self, "random", __import__("random")).randint(10000, 99999))
                                decoy.hp = getattr(b, "hp", 100)
                                decoy.max_hp = getattr(b, "max_hp", 100)
                                decoy.damage = 0
                                decoy.speed = 0.0
                                decoy.skill_timer = 9999.0
                                decoy.attack_timer = 9999.0
                                decoy.is_decoy = True
                                decoy.decoy_timer = 3.0
                                decoy.decoy_type = "stun_trap" if getattr(self, "random", __import__("random")).random() < 0.5 else "explosive"
                                if hasattr(b, "SKILL") or getattr(b, "active_skill", None) is not None:
                                    decoy.SKILL = None
                                    decoy.active_skill = None
                                world.balls.append(decoy)
                    # dot damage
                    if not hasattr(b, "sandstorm_timer"):
                        b.sandstorm_timer = 0.0
                    b.sandstorm_timer += delta
                    if b.sandstorm_timer >= 1.0:
                        b.sandstorm_timer = 0.0
                        if hasattr(b, "hp"):
                            b.hp -= 1.0 # 1 damage per sec
                    # Random lightning strikes
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                        # Struck by lightning!
                        b.hp = getattr(b, "hp", 100) - 20
                b.attack_accuracy = 0.5"""

    replace_str2 = """            elif self.weather == "sandstorm":
                b.cosmetic = "dust_mask"
                b_type = getattr(b, "ball_type", "")
                is_earth = b_type in ["tank", "druid", "juggernaut", "sand_elemental"] or (hasattr(b, "traits") and "earth" in getattr(b, "traits", []))

                shelters_or_flares = []
                if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                    for h in world.arena.hazards:
                        if getattr(h, "kind", "") in ["shelter", "flare"]:
                            shelters_or_flares.append(h)

                near_shelter_or_flare = False
                for h in shelters_or_flares:
                    dist_sq = (getattr(h, "x", 0) - getattr(b, "x", 0))**2 + (getattr(h, "y", 0) - getattr(b, "y", 0))**2
                    if dist_sq <= getattr(h, "radius", 0)**2:
                        near_shelter_or_flare = True
                        break

                if getattr(b, "ball_type", "") == "sand_elemental":
                    b.speed = b.base_speed * 1.2
                    b.damage = b.base_damage
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    if near_shelter_or_flare:
                        b.perception_radius = getattr(b, "base_perception_radius", 250.0)
                    else:
                        b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.3

                    b.speed = b.base_speed * 0.7 # Hard to move
                    b.damage = b.base_damage
                    b.dash_range_mult = 0.5
                    b.steering_mult = 0.5
                    if getattr(b, "ball_type", "") in ["trickster", "phantom", "mimic"]:
                        if not hasattr(b, "mirage_timer"):
                            b.mirage_timer = getattr(self, "random", __import__("random")).uniform(0.0, 5.0)
                        b.mirage_timer += delta
                        if b.mirage_timer >= 5.0:
                            b.mirage_timer = 0.0
                            if hasattr(world, "balls"):
                                import copy
                                decoy = copy.copy(b)
                                decoy.id = getattr(world, "next_id", getattr(self, "random", __import__("random")).randint(10000, 99999))
                                decoy.hp = getattr(b, "hp", 100)
                                decoy.max_hp = getattr(b, "max_hp", 100)
                                decoy.damage = 0
                                decoy.speed = 0.0
                                decoy.skill_timer = 9999.0
                                decoy.attack_timer = 9999.0
                                decoy.is_decoy = True
                                decoy.decoy_timer = 3.0
                                decoy.decoy_type = "stun_trap" if getattr(self, "random", __import__("random")).random() < 0.5 else "explosive"
                                if hasattr(b, "SKILL") or getattr(b, "active_skill", None) is not None:
                                    decoy.SKILL = None
                                    decoy.active_skill = None
                                world.balls.append(decoy)
                    # dot damage
                    if not hasattr(b, "sandstorm_timer"):
                        b.sandstorm_timer = 0.0
                    b.sandstorm_timer += delta
                    if b.sandstorm_timer >= 1.0:
                        b.sandstorm_timer = 0.0
                        if hasattr(b, "hp") and not is_earth:
                            b.hp -= 1.0 # 1 damage per sec
                    # Random lightning strikes
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta and not is_earth:
                        # Struck by lightning!
                        b.hp = getattr(b, "hp", 100) - 20
                b.attack_accuracy = 0.5"""

    if search_str1 in content and search_str2 in content:
        content = content.replace(search_str1, replace_str1)
        content = content.replace(search_str2, replace_str2)
        with open(filepath, 'w') as f:
            f.write(content)
        print("Updated python game modes successfully.")
    else:
        print("Failed to find search_str in python file.")

patch_python_game_modes()
