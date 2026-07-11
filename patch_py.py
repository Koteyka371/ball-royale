import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

new_mode = """
class ColorControlMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Color Control"
        self.description = "Leave a trail of your team's color. Stepping on your own color gives a speed and regen buff, while stepping on enemy colors causes slowdown and damage. Teams win by controlling the most territory."
        self.trail_timer = 0.0

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)

        self.trail_timer += delta
        should_spawn_trail = False
        if self.trail_timer >= 0.1:
            self.trail_timer = 0.0
            should_spawn_trail = True

        import math
        from arena.procedural_arena import Hazard

        arena_hazards = getattr(world.arena, "hazards", []) if hasattr(world, "arena") else []

        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            b_team = getattr(b, "team", getattr(b, "ball_type", ""))
            if not b_team:
                continue

            if should_spawn_trail:
                # Add trail hazard
                import random
                trail_id = len(arena_hazards) + random.randint(10000, 99999)
                trail = Hazard(trail_id, b.x, b.y, 15.0, "color_trail", 0.0)
                setattr(trail, "team", b_team)
                setattr(trail, "duration", 10.0) # Lasts 10 seconds
                arena_hazards.append(trail)

            # Check collisions with color trails
            for h in arena_hazards:
                if getattr(h, "kind", "") == "color_trail":
                    h_team = getattr(h, "team", "")
                    dx = b.x - h.x
                    dy = b.y - h.y
                    dist_sq = dx*dx + dy*dy

                    b_rad = getattr(b, "radius", 20.0)
                    h_rad = getattr(h, "radius", 15.0)

                    if dist_sq < (b_rad + h_rad) ** 2:
                        # Inside a trail
                        if h_team == b_team:
                            # Own team: speed + regen
                            base_speed = getattr(b, "base_speed", getattr(b, "speed", 100.0))
                            b.speed = max(b.speed, base_speed * 1.5)
                            b.hp = min(getattr(b, "max_hp", 100.0), b.hp + 5.0 * delta)
                        else:
                            # Enemy team: slowdown + damage
                            base_speed = getattr(b, "base_speed", getattr(b, "speed", 100.0))
                            b.speed = min(b.speed, base_speed * 0.5)

                            if hasattr(b, "take_damage"):
                                b.take_damage(10.0 * delta, "Color Trail")
                            else:
                                b.hp -= 10.0 * delta

    def check_winner(self, world, balls):
        # 1. If only one team alive or time is up
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)

        # If time is up, territory control determines winner
        arena_hazards = getattr(world.arena, "hazards", []) if hasattr(world, "arena") else []
        territory = {}
        for h in arena_hazards:
            if getattr(h, "kind", "") == "color_trail":
                h_team = getattr(h, "team", "")
                if h_team:
                    territory[h_team] = territory.get(h_team, 0) + 1

        is_time_up = getattr(self, "timer", 1) <= 0  # Assuming timer is set if there's a timeout

        if len(teams_alive) <= 1 or is_time_up:
            if territory:
                # Win by territory
                winner = max(territory, key=territory.get)
                return winner
            elif len(teams_alive) == 1:
                return list(teams_alive)[0]
            else:
                return "Draw"

        return None

"""

# Insert the class before GAME_MODES dictionary
insert_pos = content.find("GAME_MODES = {")
if insert_pos == -1:
    print("Could not find GAME_MODES = {")
else:
    new_content = content[:insert_pos] + new_mode + "\n" + content[insert_pos:]

    # Add to GAME_MODES dictionary
    dict_insert = '    GAME_MODES["color_control"] = ColorControlMode()\n'
    # Find a good place to insert inside GAME_MODES dictionary
    # Assuming GAME_MODES is at the end, just add it right after GAME_MODES['interactive_training']...

    lines = new_content.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith('GAME_MODES["interactive_training"]'):
            lines.insert(i + 1, '    GAME_MODES["color_control"] = ColorControlMode()')
            break

    with open("src/ai/game_modes.py", "w") as f:
        f.write("\n".join(lines) + "\n")
    print("Python game mode added.")
