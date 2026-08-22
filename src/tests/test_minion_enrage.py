import pytest
from ai.game_modes import GameMode
from ai.ball_types_necromancer import Necromancer

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []

    def add_event(self, t, d):
        pass

class Minion:
    def __init__(self, id, owner_id):
        self.id = id
        self.ball_type = "minion"
        self.minion_owner = owner_id
        self.base_speed = 100.0
        self.speed = 100.0
        self.team = 1

def test_minion_enrage_speed():
    mode = GameMode()
    necro = Necromancer(1, 0.0, 0.0)
    necro.team = 1
    # Ensure ball_type logic triggers
    necro.ball_type = "necromancer"

    minion = Minion(2, necro.id)
    world = MockWorld()
    world.balls = [necro, minion]

    # Simulate necro death
    necro.alive = False

    # Trigger on_ball_died logic
    mode.on_ball_died(world, necro, "someone")

    # Should be 100 * 5 = 500
    assert minion.speed == 500.0

if __name__ == '__main__':
    test_minion_enrage_speed()
