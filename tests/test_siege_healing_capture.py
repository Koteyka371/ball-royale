from ai.action import Action
from arena.arena_types import SiegeArena
import math

class MockBall:
    def __init__(self, id, team="Defenders", x=100, y=100, current_action="idle"):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.current_action = current_action
        self.hp = 50
        self.max_hp = 100
        self.speed = 10
        self.alive = True
        self.radius = 15.0
        self.ball_type = "player"

class MockWorld:
    def __init__(self):
        real_arena = SiegeArena(2000.0)
        real_arena.generate()
        self.arena = real_arena
        self.balls = []

    def _deal_damage(self, attacker, target):
        pass

def test_attacker_captures_healing_spring():
    world = MockWorld()
    b = MockBall(1, "Attackers")
    b.x = world.arena.hazards[0].x # first hazard is healing spring
    b.y = world.arena.hazards[0].y
    world.balls = [b]

    action = Action(b, world)

    for i in range(10):
        # We need to keep the ball within the hazard's radius
        b.x = world.arena.hazards[0].x
        b.y = world.arena.hazards[0].y
        action.execute(strategy='idle', delta=1.0)

    assert getattr(world.arena.hazards[0], 'active', True) == False
    assert getattr(world.arena.hazards[0], 'capture_progress', 0.0) >= 100.0

def test_defender_heals_from_healing_spring():
    world = MockWorld()
    b = MockBall(1, "Defenders")
    b.x = world.arena.hazards[0].x # first hazard is healing spring
    b.y = world.arena.hazards[0].y
    world.balls = [b]

    action = Action(b, world)

    action.execute(strategy='idle', delta=1.0)

    assert getattr(world.arena.hazards[0], 'active', True) == True
    assert getattr(world.arena.hazards[0], 'capture_progress', 0.0) == 0.0
    assert b.hp > 50

if __name__ == "__main__":
    test_attacker_captures_healing_spring()
    test_defender_heals_from_healing_spring()
    print("Tests passed!")
