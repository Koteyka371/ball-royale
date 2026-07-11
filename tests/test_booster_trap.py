import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action
from arena.procedural_arena import ProceduralArena, Hazard

class MockBall:
    def __init__(self, x=0, y=0, radius=10, hp=100, ball_type="base", team="team_1", id="ball_1"):
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = hp
        self.max_hp = 100
        self.ball_type = ball_type
        self.team = team
        self.alive = True
        self.speed = 100
        self.vx = 0
        self.vy = 0
        self.inventory = []
        self.id = id
        self.poison_timer = 0.0
        self.freeze_timer = 0.0
        self.stun_timer = 0.0

class MockBooster:
    def __init__(self, x=0, y=0, radius=10, kind="booster"):
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.duration = 10.0

class MockWorld:
    def __init__(self, arena, balls, boosters=None):
        self.arena = arena
        self.balls = balls
        self.boosters = boosters if boosters is not None else []
    def _deal_damage(self, attacker, target, dmg=None):
        pass
    def _collect_booster(self, ball, booster):
        pass

class MockArena:
    def __init__(self, hazards=None):
        self.hazards = hazards if hazards is not None else []
        self.width = 1000
        self.height = 1000

class MockAction(Action):
    def __init__(self, ball, world):
        self.ball = ball
        self.world = world
    def _get_boosters(self):
        return self.world.boosters + self.world.arena.hazards
    def _get_enemies(self):
        return []
    def _get_allies(self):
        return []
    def _flee(self, delta):
        pass
    def _idle(self, delta):
        pass

def test_booster_trap_collect():
    ball = MockBall(x=50, y=50)
    booster_trap_item = MockBooster(x=50, y=50, kind="booster_trap_item")
    arena = MockArena()
    world = MockWorld(arena, [ball], boosters=[booster_trap_item])
    action = MockAction(ball, world)

    # Trigger collect logic
    action._collect_booster(0.1)

    assert "booster_trap" in ball.inventory
    assert booster_trap_item not in world.boosters

def test_booster_trap_deploy():
    ball = MockBall(x=50, y=50)
    ball.inventory = ["booster_trap"]
    arena = MockArena()
    world = MockWorld(arena, [ball])
    action = MockAction(ball, world)

    # Execute should place the trap
    action.execute("attack", 0.1)

    assert "booster_trap" not in ball.inventory
    assert len(world.arena.hazards) == 1

    placed_trap = world.arena.hazards[0]
    assert placed_trap.kind == "booster_trap"
    assert getattr(placed_trap, "owner_id", None) == ball.id

def test_booster_trap_trigger():
    ball = MockBall(x=50, y=50, id="enemy_ball")
    arena = MockArena()
    world = MockWorld(arena, [ball])
    action = MockAction(ball, world)

    # Place an enemy trap manually
    trap = Hazard(id=1, x=50, y=50, radius=15.0, kind="booster_trap", damage=0.0)
    setattr(trap, "owner_id", "some_other_ball_id")
    setattr(trap, "duration", 10.0)
    arena.hazards.append(trap)

    action.execute("attack", 0.1)

    # Trap should be triggered and destroyed
    assert trap.duration == 0.0

    # Check if one of the random negative effects was applied
    assert ball.poison_timer > 0.0 or ball.freeze_timer > 0.0 or ball.stun_timer > 0.0
