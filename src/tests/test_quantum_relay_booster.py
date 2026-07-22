import pytest

class MockBooster:
    def __init__(self, kind):
        self.kind = kind
        self.x = 100
        self.y = 100

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.events = []

class MockBall:
    def __init__(self):
        self.id = 1
        self.hp = 100.0
        self.max_hp = 100.0
        self.x = 0.0
        self.y = 0.0
        self.alive = True
        self.speed = 10.0
        self.radius = 10.0
        self.quantum_relay_timer = 0.0

    def take_damage(self, amount: float) -> None:
        self.hp -= amount

        if self.hp <= 0 and getattr(self, "quantum_relay_timer", 0.0) > 0.0:
            self.hp = self.max_hp * 0.2
            self.x = getattr(self, "quantum_relay_x", self.x)
            self.y = getattr(self, "quantum_relay_y", self.y)
            self.quantum_relay_timer = 0.0
            if hasattr(self, "world") and hasattr(self.world, "events"):
                self.world.events.append({"type": "quantum_relay_triggered", "x": self.x, "y": self.y})
            return

        if self.hp <= 0:
            self.alive = False

class MockAction:
    def __init__(self, ball, world):
        self.ball = ball
        self.world = world

    def _get_boosters(self):
        return self.world.boosters

    def _get_enemies(self):
        return []

    def _idle(self, delta):
        pass

    def _apply_obstacle_avoidance(self, nx, ny, nearest, ignore_enemies=False):
        return nx, ny

    def _apply_boid_rules(self, nx, ny):
        return nx, ny

    def _collect_booster(self, delta):
        # We need a proper minimal collect booster for testing
        pass

def test_quantum_relay_booster():
    import sys
    sys.path.append("src")
    from ai.action import Action

    ball = MockBall()
    world = MockWorld()
    ball.world = world

    booster = MockBooster("quantum_relay_booster")
    world.boosters.append(booster)

    action = Action(ball, world)
    action._get_boosters = lambda: world.boosters
    action._get_enemies = lambda: []
    action._apply_obstacle_avoidance = lambda nx, ny, nearest, ignore_enemies=False: (nx, ny)
    action._apply_boid_rules = lambda nx, ny: (nx, ny)

    # Pre-move the ball close to the booster so it picks it up in one tick
    ball.x = 95.0
    ball.y = 95.0

    action._collect_booster(0.1)

    assert ball.quantum_relay_timer == 20.0
    assert ball.quantum_relay_x == ball.x
    assert ball.quantum_relay_y == ball.y
    assert len(world.boosters) == 0

    # Test taking fatal damage
    ball.take_damage(200.0)

    assert ball.hp == 20.0
    assert ball.alive == True
    assert ball.quantum_relay_timer == 0.0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
