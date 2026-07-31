import pytest
from ai.action import Action
from ai.game_modes import GameMode
from arena.procedural_arena import Hazard

class MockBall:
    def __init__(self, x=50.0, y=50.0, team="red", b_id=1, hp=100):
        self.id = b_id
        self.x = x
        self.y = y
        self.team = team
        self.inventory = []
        self.alive = True
        self.ball_type = team  # Used in _get_enemies check
        self.hp = hp
        self.radius = 15.0
        self.vx = 0.0
        self.vy = 0.0

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({"type": event_type, "data": data})

    def get_nearby_entities(self, ball, radius):
        # minimal mock for action._get_enemies_internal
        return [b for b in self.balls if b != ball and b.alive]

def test_deployable_swapper_deployment():
    world = MockWorld()
    ball = MockBall(x=100.0, y=100.0, team="red")
    enemy = MockBall(x=120.0, y=120.0, team="blue")
    ball.inventory.append("deployable_swapper")
    world.balls = [ball, enemy]

    action = Action(ball, world)
    action.execute("attack", 0.1)

    assert "deployable_swapper" not in ball.inventory
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "deployable_swapper"
    assert hazard.x == 100.0
    assert hazard.y == 100.0
    assert getattr(hazard, "duration", 0) == 15.0

def test_deployable_swapper_logic():
    world = MockWorld()
    b1 = MockBall(x=100.0, y=100.0, b_id=1)
    b2 = MockBall(x=110.0, y=110.0, b_id=2)
    b3 = MockBall(x=90.0, y=90.0, b_id=3)
    # Outside radius
    b4 = MockBall(x=500.0, y=500.0, b_id=4)
    world.balls = [b1, b2, b3, b4]

    hazard = Hazard(1, 100.0, 100.0, 100.0, "deployable_swapper", 0.0)
    hazard.stat_tick_timer = 0.0
    hazard.tick_interval = 2.0
    world.arena.hazards = [hazard]

    mode = GameMode()

    # Store initial positions
    initial_pos = {b.id: (b.x, b.y) for b in [b1, b2, b3]}

    mode.apply_dynamic_traits(world, world.balls, 0.1)

    # B4 should be unaffected
    assert b4.x == 500.0 and b4.y == 500.0

    # The others should have swapped positions (though there's a tiny chance of shuffling to same pos for a small set, derangement generation handles this)
    # Specifically, the set of positions among b1, b2, b3 should be exactly the same, but the individuals should have changed.
    final_pos = set((b.x, b.y) for b in [b1, b2, b3])
    expected_pos = set(initial_pos.values())
    assert final_pos == expected_pos

    # Check that at least some balls changed positions
    swapped = any((b.x, b.y) != initial_pos[b.id] for b in [b1, b2, b3])
    assert swapped

    # Timer should be reset
    assert hazard.stat_tick_timer == 2.0
