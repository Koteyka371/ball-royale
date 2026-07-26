class MockBall:
    def __init__(self, x, y, hp=100.0, alive=True):
        self.x = x
        self.y = y
        self.hp = hp
        self.alive = alive
        self.radius = 15.0
        self.ball_type = "test"

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 1
        self.events = []
        self.boosters = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

    def add_combat_log(self, b_id, event, amount):
        pass

def test_hazard_lines_mode():
    from ai.game_modes import GAME_MODES
    world = MockWorld()
    b1 = MockBall(500, 500)
    b2 = MockBall(100, 100)
    world.balls = [b1, b2]

    if "hazard_lines" not in GAME_MODES:
        print("hazard_lines not in GAME_MODES")
        return

    mode = GAME_MODES["hazard_lines"]
    mode.setup(world, world.balls)
    print(f"Hazards after setup: {len(world.arena.hazards)}")

    # Move for a bit
    for _ in range(500):
        mode.tick(world, world.balls, 0.016)

    print(f"Hazards after ticks: {len(world.arena.hazards)}")
