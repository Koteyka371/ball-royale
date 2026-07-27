from ai.game_modes import GameMode
import random

class ReflectiveWallsArena(GameMode):
    """
    An arena feature that includes reflective walls that bounce projectiles perfectly.
    """
    def __init__(self):
        super().__init__()
        self.name = "Reflective Walls Arena"
        self.description = "Certain walls bounce projectiles back perfectly, creating more geometry puzzles for aiming."
        self.walls = []

    class MockWall:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

    def setup(self, world, balls):
        super().setup(world, balls)
        self.walls = []

        # Determine arena size
        arena_width = getattr(world.arena, "width", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0
        arena_height = getattr(world.arena, "height", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0

        # Create some reflective walls randomly around the center
        cx, cy = arena_width / 2.0, arena_height / 2.0

        # Vertical walls
        self.walls.append(self.MockWall(cx - 250, cy - 150, 20, 300))
        self.walls.append(self.MockWall(cx + 230, cy - 150, 20, 300))

        # Horizontal walls
        self.walls.append(self.MockWall(cx - 150, cy - 250, 300, 20))
        self.walls.append(self.MockWall(cx - 150, cy + 230, 300, 20))

    def tick(self, world, balls, delta=0.016):
        import math
        projectiles = getattr(world, 'projectiles', [])
        hazards = getattr(world.arena, 'hazards', []) if hasattr(world, 'arena') else []

        for obj in projectiles + hazards:
            is_proj = getattr(obj, "is_projectile", False) or getattr(obj, "kind", "") in ["projectile", "fireball", "spell", "fireball_projectile", "starlight_projectile", "bullet", "snipe", "laser_beam"]
            if not is_proj:
                continue

            for wall in self.walls:
                # Basic AABB collision for reflective walls
                if obj.x >= wall.x and obj.x <= wall.x + wall.width and obj.y >= wall.y and obj.y <= wall.y + wall.height:
                    # Determine side of hit and reflect
                    nx, ny = 0, 0
                    dist_l = abs(obj.x - wall.x)
                    dist_r = abs(obj.x - (wall.x + wall.width))
                    dist_t = abs(obj.y - wall.y)
                    dist_b = abs(obj.y - (wall.y + wall.height))

                    min_dist = min(dist_l, dist_r, dist_t, dist_b)

                    if min_dist == dist_l:
                        nx = -1.0
                    elif min_dist == dist_r:
                        nx = 1.0
                    elif min_dist == dist_t:
                        ny = -1.0
                    elif min_dist == dist_b:
                        ny = 1.0

                    vx = getattr(obj, "vx", 0.0)
                    vy = getattr(obj, "vy", 0.0)
                    dot = vx * nx + vy * ny

                    if dot < 0:
                        obj.vx = vx - 2 * dot * nx
                        obj.vy = vy - 2 * dot * ny
