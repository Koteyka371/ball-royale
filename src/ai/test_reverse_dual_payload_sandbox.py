import pytest

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

class MockBall:
    def __init__(self, id, ball_type="tank"):
        self.id = id
        self.ball_type = ball_type
        self.team = "solo"
        self.x = 500.0
        self.y = 500.0
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.damage = 10.0
        self.is_payload = False

# We'll just define the class here to test its logic
class GameMode:
    def setup(self, world, balls):
        pass
    def tick(self, world, balls, delta):
        pass
    def check_winner(self, world, balls):
        return None

class ReverseDualPayloadMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Reverse Dual Payload"
        self.description = "Each team pushes the enemy's payload to the opposing goal. Standing near your own payload deals damage."
        self.payload_red = None
        self.payload_blue = None

    def setup(self, world, balls) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        mid = len(valid_balls) // 2

        red_team = []
        blue_team = []

        for i, b in enumerate(valid_balls):
            if i < mid:
                b.team = "Red"
                red_team.append(b)
            else:
                b.team = "Blue"
                blue_team.append(b)

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        class PayloadObj:
            pass
        self.payload_red = PayloadObj()
        self.payload_red.ball_type = "payload"
        self.payload_red.is_payload = True
        self.payload_red.is_invulnerable = True
        self.payload_red.speed = 0.0
        self.payload_red.base_speed = 0.0
        self.payload_red.damage = 0.0
        self.payload_red.base_damage = 0.0
        self.payload_red.max_hp = 10000.0
        self.payload_red.hp = 10000.0
        self.payload_red.x = arena_width - 100.0
        self.payload_red.y = arena_height / 2.0
        self.payload_red.alive = True
        self.payload_red.team = "Red"
        self.payload_red.radius = 20.0
        balls.append(self.payload_red)

        self.payload_blue = PayloadObj()
        self.payload_blue.ball_type = "payload"
        self.payload_blue.is_payload = True
        self.payload_blue.is_invulnerable = True
        self.payload_blue.speed = 0.0
        self.payload_blue.base_speed = 0.0
        self.payload_blue.damage = 0.0
        self.payload_blue.base_damage = 0.0
        self.payload_blue.max_hp = 10000.0
        self.payload_blue.hp = 10000.0
        self.payload_blue.x = 100.0
        self.payload_blue.y = arena_height / 2.0
        self.payload_blue.alive = True
        self.payload_blue.team = "Blue"
        self.payload_blue.radius = 20.0
        balls.append(self.payload_blue)

    def tick(self, world, balls, delta: float = 0.016) -> None:
        import math
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000

        if self.payload_red and getattr(self.payload_red, "alive", False):
            pushers = 0
            for b in balls:
                if getattr(b, "ball_type", None) == "spectator" or not getattr(b, "alive", False) or getattr(b, "is_payload", False):
                    continue
                dx = getattr(b, "x", 0) - self.payload_red.x
                dy = getattr(b, "y", 0) - self.payload_red.y
                if math.hypot(dx, dy) <= 150.0:
                    team = getattr(b, "team", "")
                    if team == "Blue":
                        pushers += 1
                    elif team == "Red":
                        b.hp -= 15.0 * delta
                        if b.hp <= 0:
                            b.alive = False

            if pushers > 0:
                speed_mult = 1.0 + ((pushers - 1) * 0.5)
                self.payload_red.x -= 50.0 * delta * pushers * speed_mult
                if self.payload_red.x < 50.0:
                    self.payload_red.x = 50.0

        if self.payload_blue and getattr(self.payload_blue, "alive", False):
            pushers = 0
            for b in balls:
                if getattr(b, "ball_type", None) == "spectator" or not getattr(b, "alive", False) or getattr(b, "is_payload", False):
                    continue
                dx = getattr(b, "x", 0) - self.payload_blue.x
                dy = getattr(b, "y", 0) - self.payload_blue.y
                if math.hypot(dx, dy) <= 150.0:
                    team = getattr(b, "team", "")
                    if team == "Red":
                        pushers += 1
                    elif team == "Blue":
                        b.hp -= 15.0 * delta
                        if b.hp <= 0:
                            b.alive = False

            if pushers > 0:
                speed_mult = 1.0 + ((pushers - 1) * 0.5)
                self.payload_blue.x += 50.0 * delta * pushers * speed_mult
                if self.payload_blue.x > arena_width - 50.0:
                    self.payload_blue.x = arena_width - 50.0

    def check_winner(self, world, balls):
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000

        red_reached = False
        blue_reached = False

        if self.payload_red and self.payload_red.x <= 100.0:
            red_reached = True
        if self.payload_blue and self.payload_blue.x >= arena_width - 100.0:
            blue_reached = True

        if red_reached and blue_reached:
            return "Draw"
        elif red_reached:
            return "Blue"
        elif blue_reached:
            return "Red"

        return None

def test_reverse_dual_payload():
    mode = ReverseDualPayloadMode()
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]
    mode.setup(world, balls)

    assert mode.payload_red.x == 900.0
    assert mode.payload_blue.x == 100.0

    # Red players are 0,1. Blue players are 2,3.
    # Put Red player 0 near Blue payload (100)
    balls[0].x = 100.0
    balls[0].y = 500.0

    # Put Blue player 2 near Blue payload
    balls[2].x = 100.0
    balls[2].y = 500.0

    mode.tick(world, balls, 1.0)

    # Blue payload should move right
    assert mode.payload_blue.x > 100.0

    # Blue player 2 should take damage (started at 100 hp, should be 85)
    assert balls[2].hp == 85.0
    # Red player 0 should not take damage
    assert balls[0].hp == 100.0

if __name__ == "__main__":
    test_reverse_dual_payload()
    print("Test passed!")
