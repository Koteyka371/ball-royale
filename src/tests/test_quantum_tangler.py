import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.action import Action
from ai.ball_types_quantum_tangler import QuantumTangler
from arena.procedural_arena import Hazard

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, radius):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.next_id = 9999

class MockBall:
    def __init__(self, x, y, hp=100, team="none"):
        self.id = 1
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.alive = True
        self.active = True
        self.radius = 10.0

def test_quantum_tangler_dash_creates_hazard():
    world = MockWorld()
    tangler = QuantumTangler(1, x=0, y=0)
    tangler.leave_tangle_chance = 1.0 # 100% chance for testing
    tangler.dash_range_mult = 1.2

    enemy = MockBall(50, 0, team="enemy")
    enemy.id = 2
    world.balls = [tangler, enemy]

    action = Action(tangler, world)
    action.execute("use_skill", 1.0)

    assert len(world.arena.hazards) > 0
    tangle = world.arena.hazards[-1]
    assert getattr(tangle, "kind", "") == "quantum_tangle" or (isinstance(tangle, dict) and tangle.get("kind") == "quantum_tangle")

    effect_found = False
    for ev in world.events:
        if ev["type"] == "visual_effect" and ev["data"]["type"] == "quantum_node_spawn":
            effect_found = True
            break
    assert effect_found

def test_quantum_tangle_hazard_swaps_positions():
    world = MockWorld()
    tangler = QuantumTangler(1, x=100, y=100)

    enemy = MockBall(0, 0, team="enemy")
    enemy.id = 2
    world.balls = [tangler, enemy]

    tangle = Hazard(id=100, x=0, y=0, radius=20.0, kind="quantum_tangle", damage=0)
    tangle.owner_id = tangler.id
    tangle.duration = 8.0
    world.arena.hazards.append(tangle)

    action = Action(enemy, world)
    action.execute("idle", 1.0)

    assert abs(enemy.x - 100) < 1.0
    assert abs(enemy.y - 100) < 1.0
    assert abs(tangler.x - 0) < 1.0
    assert abs(tangler.y - 0) < 1.0
