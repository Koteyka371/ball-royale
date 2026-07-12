import pytest
from ai.ball_types_doppelganger import Doppelganger
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.next_id = 100
        self.arena = MockArena()

    def get_nearby_entities(self, ball, radius):
        return {"allies": [], "enemies": [], "boosters": [], "hazards": [], "traps": []}

class MockArena:
    def __init__(self):
        self.hazards = []

def test_doppelganger_initialization():
    ball = Doppelganger(1, x=10, y=20)
    assert ball.id == 1
    assert ball.BALL_TYPE == "doppelganger"
    assert ball.clone_spawn_timer == 0.0

def test_doppelganger_spawn_clone_while_moving():
    world = MockWorld()
    ball = Doppelganger(1)
    ball.team = 1
    ball.ball_type = 'doppelganger'
    ball.ball_type = 'doppelganger'
    ball.vx = 5.0
    ball.vy = 0.0
    world.balls.append(ball)

    action = Action(ball, world)

    # Run once to decrement timer and spawn clone
    action.execute("attack", 0.1)

    # We should have one clone now
    assert len(world.balls) == 2
    clone = world.balls[-1]
    assert getattr(clone, "is_fake_clone", False) == True
    assert getattr(clone, "hp", 0) == 1.0
    assert getattr(clone, "damage", 100) == 0.0
    assert getattr(clone, "is_decoy", False) == True

def test_doppelganger_not_moving():
    world = MockWorld()
    ball = Doppelganger(1)
    ball.vx = 0.0
    ball.vy = 0.0
    world.balls.append(ball)

    action = Action(ball, world)

    action.execute("attack", 0.1)

    # No clones spawned
    assert len(world.balls) == 1

def test_doppelganger_clone_blindness():
    world = MockWorld()
    ball = Doppelganger(1)
    ball.team = 1
    ball.ball_type = 'doppelganger'
    ball.ball_type = 'doppelganger'
    ball.is_fake_clone = True
    world.balls.append(ball)

    attacker = Doppelganger(2)
    attacker.team = 2

    action = Action(ball, world)

    # Call _attempt_damage directly
    action._attempt_damage(attacker, ball)

    # Attacker should be blinded
    assert getattr(attacker, "is_blinded", False) == True
    assert getattr(attacker, "blindness_timer", 0.0) >= 2.0

    # visual effect spawned
    has_explosion = any(e['type'] == 'visual_effect' and e['data']['type'] == 'explosion' for e in world.events)
    assert has_explosion == True
