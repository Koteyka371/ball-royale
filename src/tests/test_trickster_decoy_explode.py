from ai.test_action_advanced import MockWorld, MockBall
from ai.action import Action
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

def test_decoy_explosion_no_confuse():
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
    decoy.ball_type = "trickster"

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

    import random
    original_random = random.random
    random.random = lambda: 0.9

    try:
        action.execute("idle", 0.1)
    finally:
        random.random = original_random

    assert getattr(decoy, "_decoy_exploded", False) is True
    assert getattr(enemy, "is_confused", False) is True  # Now true due to Decoy Scramble Aura
    assert enemy.confusion_timer > 0.0

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

def test_decoy_explosion_trickster_fragments():
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
    decoy.ball_type = "trickster"

    enemy = MockBall(x=120, y=120)
    enemy.id = 222
    enemy.team = "enemy_team"
    enemy.hp = 100
    enemy.stutter_timer = 0.0
    enemy.is_confused = False
    enemy.confusion_timer = 0.0

    class MockArena:
        def __init__(self):
            self.hazards = []

    world = MockWorld()
    world.balls = [owner, decoy, enemy]
    world.arena = MockArena()
    action = Action(decoy, world)

    import random
    original_random = random.random
    random.random = lambda: 0.9

    try:
        action.execute("idle", 0.1)
    finally:
        random.random = original_random

    assert getattr(decoy, "_decoy_exploded", False) is True

    # Verify fragmentation traps are spawned
    fragment_traps = [h for h in world.arena.hazards if getattr(h, "kind", "") == "fragmentation_trap"]
    assert len(fragment_traps) > 0

    # Test a fragmentation trap works
    trap = fragment_traps[0]

    # Move enemy onto trap
    enemy.x = trap.x
    enemy.y = trap.y

    # Setup action for enemy to process hazards
    enemy_action = Action(enemy, world)
    enemy_action.execute("idle", 0.1)

    # Check if trap applied effects
    assert enemy.stutter_timer > 0.0
    assert enemy.hp < 100.0
    assert getattr(trap, "duration", 10.0) == 0.0 or getattr(trap, "active", True) is False
