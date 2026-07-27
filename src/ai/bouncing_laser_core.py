from ai.game_modes import GameMode
import random
import math

class BouncingLaserCoreMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Bouncing Laser Core"
        self.description = "A single indestructible laser core spawns in the center of the map. It fires two continuous solid beam lasers in opposite directions and slowly rotates. Over time, the core bounces around the arena like a paddle ball, randomly changing direction when hitting a wall, making dodging extremely unpredictable."
        self.laser_damage_per_second = 100.0

    def setup(self, world: 'Any', balls: 'List[Any]') -> None:
        if not hasattr(world, "arena") or not hasattr(world.arena, "hazards"):
            return

        arena_w = getattr(world.arena, "width", 800.0)
        arena_h = getattr(world.arena, "height", 600.0)

        # Determine center
        cx = arena_w / 2.0
        cy = arena_h / 2.0

        from arena.procedural_arena import Hazard

        core = Hazard(id=1576, x=cx, y=cy, radius=30.0, kind="bouncing_laser_core", damage=0.0)
        # Give it a random initial velocity and a rotation angle
        angle = random.uniform(0, math.pi * 2)
        speed = 250.0
        core.vx = math.cos(angle) * speed
        core.vy = math.sin(angle) * speed
        core.angle = 0.0 # start at 0
        core.rotation_speed = 1.0 # radians per second

        world.arena.hazards.append(core)

    def tick(self, world: 'Any', balls: 'List[Any]', delta: float = 0.016) -> None:
        if not hasattr(world, "arena") or not hasattr(world.arena, "hazards"):
            return

        arena_w = getattr(world.arena, "width", 800.0)
        arena_h = getattr(world.arena, "height", 600.0)

        # Find the core
        core = next((h for h in world.arena.hazards if getattr(h, "kind", "") == "bouncing_laser_core"), None)

        if not core:
            return

        # Move core
        vx = getattr(core, "vx", 0.0)
        vy = getattr(core, "vy", 0.0)
        core.x += vx * delta
        core.y += vy * delta

        core.angle = getattr(core, "angle", 0.0) + getattr(core, "rotation_speed", 1.0) * delta

        # Handle bouncing on walls
        bounced = False
        if core.x - core.radius < 50.0:
            core.x = 50.0 + core.radius
            core.vx = abs(core.vx)
            bounced = True
        elif core.x + core.radius > arena_w - 50.0:
            core.x = arena_w - 50.0 - core.radius
            core.vx = -abs(core.vx)
            bounced = True

        if core.y - core.radius < 50.0:
            core.y = 50.0 + core.radius
            core.vy = abs(core.vy)
            bounced = True
        elif core.y + core.radius > arena_h - 50.0:
            core.y = arena_h - 50.0 - core.radius
            core.vy = -abs(core.vy)
            bounced = True

        if bounced:
            # Randomly change direction slightly when hitting a wall
            speed = math.hypot(core.vx, core.vy)
            current_angle = math.atan2(core.vy, core.vx)
            # Deflect by up to +/- 30 degrees
            deflection = random.uniform(-math.pi/6, math.pi/6)
            new_angle = current_angle + deflection
            core.vx = math.cos(new_angle) * speed
            core.vy = math.sin(new_angle) * speed

            # Randomly change rotation direction/speed
            core.rotation_speed = random.uniform(0.5, 2.0) * random.choice([-1, 1])

        # Deal damage to balls
        for b in balls:
            if not getattr(b, "alive", True) or getattr(b, "ball_type", "") == "spectator":
                continue

            bx = getattr(b, "x", 0.0)
            by = getattr(b, "y", 0.0)
            br = getattr(b, "radius", 15.0)

            # Line representing the laser beam from the core, passing through it
            # The line passes through (core.x, core.y) with angle `core.angle`
            dx = math.cos(core.angle)
            dy = math.sin(core.angle)

            # Distance from point to line: |(bx - cx)*dy - (by - cy)*dx| (since dx^2 + dy^2 = 1)
            dist_to_line = abs((bx - core.x) * dy - (by - core.y) * dx)

            laser_width = 15.0

            if dist_to_line <= br + laser_width:
                # Inside the beam width, check if it's actually along the beam
                # The beam extends infinitely in both directions (since it fires two solid beams in opposite directions)
                # So we only need to deal damage
                dmg = self.laser_damage_per_second * delta
                if hasattr(b, "take_damage"):
                    b.take_damage(dmg)
                else:
                    b.hp -= dmg
                    if b.hp <= 0:
                        b.hp = 0
                        b.alive = False
