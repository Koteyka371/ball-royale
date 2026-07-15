import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

acid_rain_block_search = """            elif self.current_weather == "acid_rain":
                if not has_hazmat:
                    b.damage = b.base_damage * 1.5
                    if hasattr(b, "take_damage"): b.take_damage(10.0 * delta)
                    elif hasattr(b, "hp"): b.hp -= 10.0 * delta"""

acid_rain_block_replace = """            elif self.current_weather == "acid_rain":
                if self.random.random() < 0.2 * delta and hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                    from arena.procedural_arena import Hazard
                    import random
                    h_id = 9500 + len(world.arena.hazards) + random.randint(0, 1000)
                    arena_w = getattr(world.arena, "width", 1000)
                    arena_h = getattr(world.arena, "height", 1000)
                    neutralizing_puddle = Hazard(id=h_id, x=random.uniform(50, arena_w-50), y=random.uniform(50, arena_h-50), radius=40.0, kind="neutralizing_puddle", damage=0.0)
                    neutralizing_puddle.duration = 10.0
                    world.arena.hazards.append(neutralizing_puddle)

                if not has_hazmat:
                    b.damage = b.base_damage * 1.5
                    b_type = getattr(b, "ball_type", "").lower()
                    traits = getattr(b, "traits", [])
                    if "metal" in b_type or "armor" in b_type or "metal" in traits or "armor" in traits:
                        if not hasattr(b, "base_max_hp"):
                            b.base_max_hp = getattr(b, "max_hp", 100.0)
                        b.max_hp = max(1.0, b.max_hp - 5.0 * delta)
                        if b.hp > b.max_hp:
                            b.hp = b.max_hp
                        b.defense_multiplier = getattr(b, "defense_multiplier", 1.0) * 0.9
                    else:
                        if hasattr(b, "take_damage"): b.take_damage(10.0 * delta)
                        elif hasattr(b, "hp"): b.hp -= 10.0 * delta"""

if acid_rain_block_search in content:
    content = content.replace(acid_rain_block_search, acid_rain_block_replace)
    with open("src/ai/game_modes.py", "w") as f:
        f.write(content)
    print("Replaced successfully in src/ai/game_modes.py")
else:
    print("Block not found in src/ai/game_modes.py")
