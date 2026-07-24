import pytest
from src.ai.action import Action
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class MockHazard:
    def __init__(self, id, x, y, radius, kind, damage):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        self.damage = damage
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()

class MockBall:
    def __init__(self, id, x, y, team):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.alive = True
        self.active_skill = "throw_vortex_grenade"
        self.skill_timer = 0.0
        self.inventory = []
        self.status_effects = []
        self.hp = 100
        self.max_hp = 100

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False

def test_vortex_grenade_deployment_and_pull():
    world = MockWorld()

    # 1. Setup owner and enemy
    owner = MockBall("owner1", 100, 100, 1)
    enemy = MockBall("enemy1", 200, 100, 2)
    world.balls = [owner, enemy]

    # 2. Deploy grenade
    action = Action(owner, world)

    # Needs skill cast
    owner.active_skill = "throw_vortex_grenade"
    owner.skill_timer = 0.0
    action._use_skill()

    # Verify grenade was deployed
    assert len(world.arena.hazards) == 1
    grenade = world.arena.hazards[0]
    assert grenade.kind == "vortex_grenade"
    assert grenade.owner_id == "owner1"
    assert grenade.duration == 4.0

    # Setup enemy to be exactly inside the radius but off-center
    grenade.x = 200
    grenade.y = 200
    enemy.x = 200
    enemy.y = 150 # 50 units away, inside 150 radius

    enemy.vx = 0.0
    enemy.vy = 0.0
    owner.vx = 0.0
    owner.vy = 0.0

    # 3. Simulate tick to test pull logic
    delta = 0.1
    action.execute("attack", delta)

    # Check that enemy was pulled towards the grenade (y should increase as it moves from 150 towards 200)
    # The pull strength is 250.0. delta = 0.1, so it should gain vy
    # Note: chaotic physics is applied, so it might be slightly off, but it should definitely have changed
    assert enemy.vy > 0.0
    # Owner movement is handled by the base AI strategy, so we ignore its velocity here.

    # 4. Simulate expiration
    grenade.duration = -0.05
    action.execute("attack", delta)
    assert grenade.active == False # Should be deactivated

if __name__ == "__main__":
    test_vortex_grenade_deployment_and_pull()
    print("Tests passed.")
