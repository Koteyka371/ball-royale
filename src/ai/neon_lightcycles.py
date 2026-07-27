from ai.game_modes import GameMode

def ccw(A_x, A_y, B_x, B_y, C_x, C_y):
    return (C_y - A_y) * (B_x - A_x) > (B_y - A_y) * (C_x - A_x)

def lines_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)

class NeonLightcyclesMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Neon Lightcycles Mode"

    def setup(self, world, balls):
        for b in balls:
            b.lightcycle_trail = []
            b.last_pos = (getattr(b, "x", 0.0), getattr(b, "y", 0.0))

            base_s = getattr(b, "base_speed", 400.0)
            if base_s < 400.0:
                b.base_speed = 400.0

            s = getattr(b, "speed", 400.0)
            if s < 400.0:
                b.speed = 400.0

    def tick(self, world, balls, delta):
        for b in balls:
            if not getattr(b, "alive", False):
                continue

            s = getattr(b, "speed", 0.0)
            if s < 400.0:
                b.speed = 400.0

            b_x = getattr(b, "x", 0.0)
            b_y = getattr(b, "y", 0.0)
            last_x, last_y = getattr(b, "last_pos", (b_x, b_y))

            dist_sq = (b_x - last_x)**2 + (b_y - last_y)**2

            if dist_sq > 100.0:
                b.lightcycle_trail.append(((last_x, last_y), (b_x, b_y)))
                b.last_pos = (b_x, b_y)

                # Check intersection
                current_segment = ((last_x, last_y), (b_x, b_y))
                intersected = False

                for other_b in balls:
                    trail = getattr(other_b, "lightcycle_trail", [])
                    # Skip the last 2 segments of own trail to prevent self-colliding at joints
                    check_trail = trail[:-2] if other_b == b else trail

                    for segment in check_trail:
                        if lines_intersect(current_segment[0][0], current_segment[0][1],
                                           current_segment[1][0], current_segment[1][1],
                                           segment[0][0], segment[0][1],
                                           segment[1][0], segment[1][1]):
                            intersected = True
                            break

                    if intersected:
                        break

                if intersected:
                    b.hp = 0
                    b.alive = False
                    if hasattr(world, "_deal_damage"):
                        world._deal_damage(None, b, 9999.0)
