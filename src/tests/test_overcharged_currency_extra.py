import sys
from ai.game_modes import GameMode
from ai.action import Action

def test_elite_drops_coin():
    class MockBall:
        def __init__(self):
            self.id = 1
            self.x = 100
            self.y = 100
            self.is_elite_minion = True
            self.ball_type = "elite_minion"
            self.team = "Red"

    class MockKiller:
        def __init__(self):
            self.id = 2

    class MockArena:
        def __init__(self):
            self.hazards = []

    class MockWorld:
        def __init__(self):
            self.arena = MockArena()

    world = MockWorld()
    mode = GameMode()
    ball = MockBall()
    killer = MockKiller()

    mode.on_ball_died(world, ball, killer)

    found = False
    if hasattr(world, "currency_pickups"):
        for pickup in world.currency_pickups:
            if pickup.get("type") == "overcharged_coin":
                found = True
    assert found
