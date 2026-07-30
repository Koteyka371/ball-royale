import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.events = []
        self.next_id = 9999

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.team = "team1"
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.radius = 15
        self.speed = 5.0
        self.skill_timer = 0
        self.SKILL_COOLDOWN = 10.0
        self.attack_timer = 0
        self.is_decoy = False
        self.skill = "deploy_decoy_gas"
        self.active_skill = "deploy_decoy_gas"
        self.vx = 0
        self.vy = 0
        self.rearm_damage_boost = False

def test_deploy_decoy_gas():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    world.balls.append(ball)

    action = Action(ball, world)

    # Use skill to deploy decoy
    action._use_skill()

    decoys = [b for b in world.balls if getattr(b, "is_decoy", False) and getattr(b, "owner_id", None) == 1]
    assert len(decoys) == 2, "Should spawn two decoys"

    decoy = decoys[0]
    assert getattr(decoy, "decoy_type", "") == "gas", "Decoy should be of type gas"

    # Second use swaps with decoy
    ball.skill_timer = 0
    action._use_skill()

    assert decoy.has_swapped == True

    # Third use detonates decoy
    enemy = MockBall(2, decoy.x, decoy.y)
    enemy.team = "team2"
    enemy.confused_timer = 0.0
    world.balls.append(enemy)

    ball.skill_timer = 0
    action._use_skill()

    assert decoy.hp == 0

    # Execute one tick to process explosion
    action.execute("flee", 0.1)

    assert enemy.confused_timer > 0, "Enemy should be confused"
    assert getattr(enemy, "is_confused", False) == True, "Enemy should have is_confused flag set"
