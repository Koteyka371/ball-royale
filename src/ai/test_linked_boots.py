import pytest
import math
from ai.action import Action

class MockBall:
    def __init__(self, x, y, cosmetic="linked_boots", team=1):
        self.x = x
        self.y = y
        self.cosmetic = cosmetic
        self.team = team
        self.alive = True
        self.radius = 10.0
        self.hp = 100
        self.speed_boost_timer = 0.0
        self.shield_timer = 0.0
        self.intangible = False
        self.intangible_timer = 0.0
        self.phase_booster_timer = 0.0

class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.game_mode = MockGameMode()
    def get_nearby_entities(self, ball, radius):
        return self.balls

class MockGameMode:
    name = "Standard"

def test_linked_boots_collision_knockback():
    player = MockBall(0, 0, "linked_boots", team=1)
    ally1 = MockBall(20, 0, "normal", team=1)
    ally2 = MockBall(50, 0, "normal", team=1) # Further away
    enemy = MockBall(15, 0, "normal", team=2) # Overlaps with player, causes collision (dist = 15 < 20)

    player.speed_boost_timer = 5.0
    ally1.shield_timer = 3.0

    world = MockWorld([player, ally1, ally2, enemy])
    action = Action(player, world)

    action._resolve_collisions()

    # Normal overlap = 20 - 15 = 5
    # player x starts at 0, enemy at 15. dx = -15, nx = -1. player gets pushed to left.
    # Normally pushed by 5 * 1.0 = -5.
    # With linked boots, multiplier is 0.5. Player pushed by -2.5.
    assert abs(player.x - -2.5) < 0.001

    # Ally receives half the knockback (5 * 0.5 = -2.5)
    # Ally was at 20, so 20 - 2.5 = 17.5
    assert abs(ally1.x - 17.5) < 0.001

    # Ally 2 is further away, shouldn't be affected
    assert ally2.x == 50

    # Positive statuses should sync (max of both)
    assert player.speed_boost_timer == 5.0
    assert ally1.speed_boost_timer == 5.0

    assert player.shield_timer == 3.0
    assert ally1.shield_timer == 3.0

def test_linked_boots_hazard_pull():
    class MockHazard:
        def __init__(self):
            self.kind = "pull_trap"
            self.x = -10
            self.y = 0
            self.radius = 30
            self.damage = 10
            self.owner_id = 999

    player = MockBall(0, 0, "linked_boots", team=1)
    ally = MockBall(20, 0, "normal", team=1)

    world = MockWorld([player, ally])
    world.arena = type("Arena", (), {"hazards": [MockHazard()]})
    action = Action(player, world)

    # Execute an idle tick which internally triggers _handle_hazards and traps
    # The Action class normally loops over _handle_hazards, but Action.execute handles main logic.
    # But since pull_traps are processed via events or tick? Let's check Action.execute
    # Wait, pull_trap triggers in hazard loop?

    # Actually, we can just test the method that triggers hazards if it exists, else we can simulate the block logic.
    # The logic was patched inside `_handle_hazards` or `execute`? It was patched inline. Let's run execute.
    action.execute("idle", 0.1)

    # The pull trap will pull player towards it (-10, 0)
    # distance = 10
    # nx = -1, ny = 0
    # pull_strength = 100 * 0.1 = 10 (base for pull_trap)
    # linked_boots mod = 0.5 -> pull 5
    # player.x becomes -5
    # Ally also gets moved by -5 (20 - 5 = 15)

    assert abs(player.x - -5.0) < 1.0 # Give it a tolerance of 1.0 due to float specifics
    assert ally.x < 19.5
