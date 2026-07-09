from src.ai.test_action_advanced import MockWorld, MockBall
from src.ai.action import Action
import pytest

def test_decoy_explosion_trickster_confuse():
    owner = MockBall(x=10, y=10)
    owner.id = 111
    owner.team = "owner_team"
    owner.ball_type = "trickster"

    decoy = MockBall(x=100, y=100)
    decoy.is_decoy = True
    decoy.alive = True
    decoy.hp = 0
    decoy.decoy_type = "explosive"
    decoy.team = "owner_team"
    decoy.owner_id = 111
    decoy.decoy_timer = 5.0
    decoy.id = 999
    decoy.ball_type = "trickster" # Should give trickster effects

    enemy = MockBall(x=120, y=120)
    enemy.id = 222
    enemy.team = "enemy_team"
    enemy.hp = 100
    enemy.stutter_timer = 0.0
    enemy.is_confused = False
    enemy.confusion_timer = 0.0

    world = MockWorld()
    world.balls = [owner, decoy, enemy]
    action = Action(decoy, world)

    # We force random to always return 0 to trigger confusion (threshold is 0.3)
    import random
    original_random = random.random
    random.random = lambda: 0.1

    try:
        action.execute("idle", 0.1)
    finally:
        random.random = original_random

    assert getattr(decoy, "_decoy_exploded", False) is True
    assert enemy.is_confused is True
    assert enemy.confusion_timer == 3.0

def test_decoy_explosion_all_confuse():
    owner = MockBall(x=10, y=10)
    owner.id = 111
    owner.team = "owner_team"
    owner.ball_type = "warrior"

    decoy = MockBall(x=100, y=100)
    decoy.is_decoy = True
    decoy.alive = True
    decoy.hp = 0
    decoy.decoy_type = "explosive"
    decoy.team = "owner_team"
    decoy.owner_id = 111
    decoy.decoy_timer = 5.0
    decoy.id = 999
    decoy.ball_type = "warrior"

    enemy = MockBall(x=120, y=120)
    enemy.id = 222
    enemy.team = "enemy_team"
    enemy.hp = 100
    enemy.stutter_timer = 0.0
    enemy.is_confused = False
    enemy.confusion_timer = 0.0

    world = MockWorld()
    world.balls = [owner, decoy, enemy]
    action = Action(decoy, world)

    action.execute("idle", 0.1)

    assert getattr(decoy, "_decoy_exploded", False) is True
    # If the task says "When a decoy explodes, it can inflict a 'confuse' status on nearby enemies"
    # Maybe we should always apply it, or apply it based on a 30% chance for ALL decoys, not just tricksters.
