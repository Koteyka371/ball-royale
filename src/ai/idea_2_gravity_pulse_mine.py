from ai.game_modes import GameMode
import random
import math

class GravityPulseMineMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Gravity Pulse Mine Mode"
        self.description = "A rare drop hazard that periodically pulsates, pushing away enemies in a large radius but pulling in allies."
        self.spawn_timer = 0.0
        self.spawn_interval = 15.0

    def tick(self, world, balls, delta=0.016):
        self.spawn_timer += delta

        # occasionally spawn one
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                x = random.uniform(100, getattr(world.arena, "width", 1000) - 100)
                y = random.uniform(100, getattr(world.arena, "height", 1000) - 100)

                # Pick a random owner team from existing balls
                owner_team = "blue"
                valid_balls = [b for b in balls if getattr(b, "alive", True) and getattr(b, "team", None) is not None]
                if valid_balls:
                    owner_team = getattr(random.choice(valid_balls), "team", "blue")

                class GravityPulseMineHazard:
                    def __init__(self, x, y, team):
                        self.id = random.randint(100000, 999999)
                        self.x = x
                        self.y = y
                        self.radius = 20.0
                        self.kind = "idea_2_gravity_pulse_mine"
                        self.duration = 20.0
                        self.damage = 0.0
                        self.active = True
                        self.team = team
                        self.pulse_timer = 0.0
                        self.pulse_interval = 2.0
                        self.pulse_radius = 250.0

                world.arena.hazards.append(GravityPulseMineHazard(x, y, owner_team))

        if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
            hazards_to_remove = []
            for h in world.arena.hazards:
                if getattr(h, "kind", "") == "idea_2_gravity_pulse_mine" and getattr(h, "active", True):
                    h.duration -= delta
                    if h.duration <= 0:
                        h.active = False
                        hazards_to_remove.append(h)
                        continue

                    h.pulse_timer = getattr(h, "pulse_timer", 0.0) + delta
                    if h.pulse_timer >= getattr(h, "pulse_interval", 2.0):
                        h.pulse_timer -= getattr(h, "pulse_interval", 2.0)

                        # Apply pulse effect
                        pulse_radius = getattr(h, "pulse_radius", 250.0)
                        mine_team = getattr(h, "team", None)

                        for b in balls:
                            if not getattr(b, "alive", True):
                                continue

                            dx = b.x - h.x
                            dy = b.y - h.y
                            dist_sq = dx * dx + dy * dy

                            if dist_sq > 0 and dist_sq <= pulse_radius * pulse_radius:
                                dist = math.sqrt(dist_sq)
                                nx = dx / dist
                                ny = dy / dist

                                b_team = getattr(b, "team", None)

                                # Pulls allies, pushes enemies
                                strength = 200.0 # impulse

                                if b_team == mine_team:
                                    # Pull in ally
                                    b.vx = getattr(b, "vx", 0.0) - nx * strength
                                    b.vy = getattr(b, "vy", 0.0) - ny * strength
                                else:
                                    # Push away enemy
                                    b.vx = getattr(b, "vx", 0.0) + nx * strength
                                    b.vy = getattr(b, "vy", 0.0) + ny * strength

            for h in hazards_to_remove:
                if h in world.arena.hazards:
                    world.arena.hazards.remove(h)
