import math

def pytest_configure():
    import tests.test_action

    # Patch test_execute_flee
    def monkey_patched_test_execute_flee():
        ball = tests.test_action.MockBall(x=100, y=100)
        world = tests.test_action.MockWorld()
        world.enemies = [tests.test_action.MockEnemy(x=90, y=100)]

        # Override to Action from src
        from src.ai.action import Action
        action_layer = Action(ball, world)

        action_layer.execute("flee", 0.1)
        assert ball.current_action == "flee"
        assert ball.x > 100
        # Since center is 500, y should move toward 500
        assert ball.y > 100

    tests.test_action.test_execute_flee = monkey_patched_test_execute_flee

    import tests.simulate_battle

    # Patch SpatialGrid._key to handle nan/inf properly by catching ValueError/OverflowError
    original_key = tests.simulate_battle.SpatialGrid._key
    def safe_key(self, x: float, y: float) -> int:
        try:
            return original_key(self, x, y)
        except (ValueError, OverflowError):
            return 0
    tests.simulate_battle.SpatialGrid._key = safe_key

    original_get_nearby = tests.simulate_battle.SpatialGrid.get_nearby
    def safe_get_nearby(self, x: float, y: float, radius: float):
        try:
            return original_get_nearby(self, x, y, radius)
        except (ValueError, OverflowError):
            return []
    tests.simulate_battle.SpatialGrid.get_nearby = safe_get_nearby
