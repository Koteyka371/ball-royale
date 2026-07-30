import pytest

class DummyArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.arena = DummyArena()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

    def _deal_damage(self, hazard, target, amount):
        target.take_damage(amount, "maze_wall")

class DummyBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.hp = 100.0
        self.alive = True
        self.is_dashing = False

    def take_damage(self, amount, source):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_shifting_maze_win():
    from ai.game_modes import GAME_MODES
    mode = GAME_MODES["shifting_maze"]

    world = DummyWorld()
    # Ball 1 starts right at the center!
    b1 = DummyBall(1, 500.0, 500.0)
    b2 = DummyBall(2, 10.0, 10.0)
    balls = [b1, b2]

    mode.setup(world, balls)

    mode.tick(world, balls, 0.016)

    # Ball 1 should be alive, Ball 2 should be dead from center reach loss
    assert b1.alive
    assert not b2.alive

if __name__ == "__main__":
    test_shifting_maze_win()
    print("Tests passed!")
