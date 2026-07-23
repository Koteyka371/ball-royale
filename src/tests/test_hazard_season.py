from ai.game_modes import GameMode

def test_seasonal_hazard_interaction():
    world = type('MockWorld', (), {})()
    world.balls = []

    mode = GameMode()
    world.seasonal_hazard_timer = 4.9

    class MockLeaderboard:
        def __init__(self):
            self.data = {"current_season": 1}
        def get_theme(self, season):
            return "Frost"

    world.leaderboard_manager = MockLeaderboard()

    class MockHazard:
        def __init__(self, kind):
            self.kind = kind
            self.damage = 10.0

    h1 = MockHazard("trap")
    h2 = MockHazard("trap")

    class MockArena:
        def __init__(self):
            self.hazards = [h1, h2]
            self.width = 1000
            self.height = 1000

    world.arena = MockArena()

    import random
    random.seed(42) # First random() < 0.3 should fail (0.639), second should pass (0.025)

    mode.tick(world, [], delta=0.2)

    assert world.seasonal_hazard_timer == 0.0
    assert h1.kind == "trap"
    assert h2.kind == "ice_patch"
    assert h2.damage == 0.0
    assert getattr(h2, "duration") == 10.0
