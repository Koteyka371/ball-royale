import re

with open('src/ai/game_modes.py', 'r') as f:
    text = f.read()

# First block of mud_pit (BattleRoyaleMode)
search_mud1 = """                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn mud pit
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    mud_pit = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=60.0, kind="quicksand", damage=0.0)
                    setattr(mud_pit, 'duration', 15.0)
                    world.arena.hazards.append(mud_pit)"""

replace_mud1 = """                arena_name = getattr(world.arena, "__class__", type(world.arena)).__name__.lower()
                is_dirt_sand = "sand" in arena_name or "dirt" in arena_name or "summer" in arena_name or getattr(world.arena, "is_sandstorming", False)
                if is_dirt_sand and getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn mud pit
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    mud_pit = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=60.0, kind="quicksand", damage=0.0)
                    setattr(mud_pit, 'duration', 15.0)
                    world.arena.hazards.append(mud_pit)"""

if search_mud1 in text:
    text = text.replace(search_mud1, replace_mud1)
    print("Replaced mud_pit spawns")
else:
    print("Could not find mud_pit block 1")

# Now the rain speed block
search_rain_speed1 = """            elif self.weather == "rain":
                b.cosmetic = "umbrella"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.5
                b.speed = b.base_speed * 0.8
                b.damage = b.base_damage"""

replace_rain_speed1 = """            elif self.weather == "rain":
                b.cosmetic = "umbrella"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.5

                # Check for swamp/water traits
                b_type = str(getattr(b, "ball_type", "")).lower()
                traits = getattr(b, "traits", [])
                has_water_trait = "water" in b_type or "swamp" in b_type or any("water" in str(t).lower() or "swamp" in str(t).lower() for t in traits)

                if not has_water_trait:
                    b.speed = b.base_speed * 0.8
                else:
                    b.speed = getattr(b, "base_speed", 100.0)
                b.damage = b.base_damage"""

if search_rain_speed1 in text:
    text = text.replace(search_rain_speed1, replace_rain_speed1)
    print("Replaced rain speed blocks")
else:
    print("Could not find rain speed block")

with open('src/ai/game_modes.py', 'w') as f:
    f.write(text)
