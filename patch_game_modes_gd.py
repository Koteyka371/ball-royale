import re

with open("src/ai/game_modes.gd", "r") as f:
    content = f.read()

# 1. Add final_boss_spawned
content = content.replace(
    'var sudden_death_black_hole_spawned: bool = false',
    'var sudden_death_black_hole_spawned: bool = false\n    var final_boss_spawned: bool = false'
)

# 2. Add boss logic right after the decoy spawner logic
boss_logic = """
        # Final Zone Boss logic
        if self.get("zone_radius") <= 250.0 and not self.get("final_boss_spawned"):
            self.set("final_boss_spawned", true)

            var boss_type = "juggernaut"
            if weather in ["snow", "blizzard"]:
                boss_type = "yeti"
            elif weather == "sandstorm":
                boss_type = "sandworm"

            var new_boss = {}
            var boss_id = 90000 + (randi() % 9999)
            new_boss["id"] = boss_id
            new_boss["x"] = self.get("zone_x")
            new_boss["y"] = self.get("zone_y")
            new_boss["vx"] = 0.0
            new_boss["vy"] = 0.0
            new_boss["radius"] = 40.0
            new_boss["hp"] = 3000.0
            new_boss["max_hp"] = 3000.0
            new_boss["alive"] = true
            new_boss["ball_type"] = boss_type
            new_boss["team"] = "Boss"
            new_boss["speed"] = 120.0
            new_boss["base_speed"] = 120.0
            new_boss["damage"] = 40.0
            new_boss["base_damage"] = 40.0
            new_boss["perception_radius"] = 500.0
            new_boss["base_perception_radius"] = 500.0
            new_boss["is_final_boss"] = true
            new_boss["reward_given"] = false
            new_boss["has_method"] = Callable(func(method_name): return false)

            if world != null and "balls" in world:
                world.balls.append(new_boss)

            if world != null and world.has_method("add_event"):
                world.add_event("final_boss_spawn", {"message": "A massive " + boss_type.capitalize() + " has emerged in the center of the safe zone!"})

        # Check boss death
        for b in balls:
            var is_final = false
            if typeof(b) == TYPE_DICTIONARY and b.has("is_final_boss"): is_final = b["is_final_boss"]
            elif "is_final_boss" in b: is_final = b.is_final_boss
            elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("is_final_boss"): is_final = b.get_meta("is_final_boss")

            if is_final:
                var b_alive = true
                if typeof(b) == TYPE_DICTIONARY and b.has("alive"): b_alive = b["alive"]
                elif "alive" in b: b_alive = b.alive

                var r_given = false
                if typeof(b) == TYPE_DICTIONARY and b.has("reward_given"): r_given = b["reward_given"]
                elif "reward_given" in b: r_given = b.reward_given
                elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("reward_given"): r_given = b.get_meta("reward_given")

                if not b_alive and not r_given:
                    if typeof(b) == TYPE_DICTIONARY: b["reward_given"] = true
                    elif "reward_given" in b: b.reward_given = true
                    elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"): b.set_meta("reward_given", true)

                    var killer_id = null
                    if typeof(b) == TYPE_DICTIONARY and b.has("killer_id"): killer_id = b["killer_id"]
                    elif "killer_id" in b: killer_id = b.killer_id
                    elif typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("killer_id"): killer_id = b.get_meta("killer_id")

                    if world != null and world.has_method("add_event"):
                        world.add_event("boss_defeated", {"killer_id": killer_id, "points": 5000, "message": "The final boss was defeated!"})
"""

content = content.replace(
    '# Handle decoy movement mimicking',
    boss_logic + '\n        # Handle decoy movement mimicking'
)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(content)
