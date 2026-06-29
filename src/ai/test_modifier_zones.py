from ai.game_modes import ModifierZonesMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []

class MockBall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ball_type = "warrior"
        self.alive = True
        self.hp = 50.0
        self.max_hp = 100.0
        self.speed = 2.0
        self.damage = 10.0

def test_modifier_zones_effects():
    world = MockWorld()
    ball1 = MockBall(500, 500) # Center
    ball2 = MockBall(100, 100)
    world.balls = [ball1, ball2]

    mode = ModifierZonesMode()
    mode.setup(world, world.balls)

    # Overwrite zones for testing
    mode.zones = [
        {"id": "speed", "x": 500, "y": 500, "radius": 50.0, "type": "speed_boost"},
        {"id": "damage", "x": 100, "y": 100, "radius": 50.0, "type": "damage_boost"},
        {"id": "healing", "x": 900, "y": 900, "radius": 50.0, "type": "healing"}
    ]

    assert abs(ball1.speed - ball1.base_speed) < 0.001
    assert ball1.damage == 10.0
    assert abs(ball2.speed - ball2.base_speed) < 0.001
    assert ball2.damage == 10.0

    mode.tick(world, world.balls, delta=1.0)

    # ball1 is in speed zone
    assert abs(ball1.speed - ball1.base_speed * 1.5) < 0.001
    assert ball1.damage == 10.0

    # ball2 is in damage zone
    assert abs(ball2.speed - ball2.base_speed) < 0.001
    assert ball2.damage == 15.0

    # move ball1 to healing zone
    ball1.x = 900
    ball1.y = 900
    mode.tick(world, world.balls, delta=1.0)

    # ball1 is now out of speed zone
    assert abs(ball1.speed - ball1.base_speed) < 0.001
    assert ball1.hp == 70.0 # 50.0 + 20.0
