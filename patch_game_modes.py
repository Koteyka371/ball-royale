<<<<<<< SEARCH
GAME_MODES["grapple_node"] = GrappleNodeMode()

class PerfectReflectorHazardMode(GameMode):
=======
GAME_MODES["grapple_node"] = GrappleNodeMode()

class OrbitalMinesMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Orbital Mines"
        self.description = "Orbital mines constantly revolve around the center of the arena."
        self.id = "orbital_mines"
        self.orbit_speed = 1.0 # radians per second
        self.orbit_distance = 300.0

    def tick(self, world, balls, delta=0.016):
        import math
        import random
        super().tick(world, balls, delta)

        if not (hasattr(world, 'arena') and hasattr(world.arena, 'hazards')):
            return

        cx = getattr(world, 'width', 1000) / 2.0
        cy = getattr(world, 'height', 1000) / 2.0

        # Count existing orbital mines
        mines = [h for h in world.arena.hazards if getattr(h, 'kind', '') == 'orbital_mine']

        # Spawn mines if fewer than 5
        if len(mines) < 5:
            from arena.procedural_arena import Hazard
            num_to_spawn = 5 - len(mines)
            for _ in range(num_to_spawn):
                mine_id = len(world.arena.hazards) + random.randint(10000, 99999)
                mine = Hazard(mine_id, cx, cy, 20.0, "orbital_mine", 30.0)
                setattr(mine, 'active', True)
                setattr(mine, 'duration', 9999.0)
                setattr(mine, 'angle', random.uniform(0, 2 * math.pi))
                # Add random orbital distance offset per mine
                setattr(mine, 'orbit_dist', random.uniform(150.0, 450.0))
                # Randomize speed slightly per mine
                setattr(mine, 'speed_mult', random.choice([-1, 1]) * random.uniform(0.8, 1.5))
                world.arena.hazards.append(mine)
                mines.append(mine)

        # Update mine positions
        for m in mines:
            if getattr(m, 'active', True):
                ang = getattr(m, 'angle', 0.0)
                spd = self.orbit_speed * getattr(m, 'speed_mult', 1.0)
                ang += spd * delta
                setattr(m, 'angle', ang)

                dist = getattr(m, 'orbit_dist', self.orbit_distance)
                m.x = cx + math.cos(ang) * dist
                m.y = cy + math.sin(ang) * dist

GAME_MODES["orbital_mines"] = OrbitalMinesMode()

class PerfectReflectorHazardMode(GameMode):
>>>>>>> REPLACE
