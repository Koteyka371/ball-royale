import pytest
from ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = MockArena()
        self.balls = []
        self.tick = 0

class MockBall:
    def __init__(self, id, team, x, y, vx=0.0, vy=0.0):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.mass = 2.0
        self.alive = True
        self.shield = 200.0
        self.skill = ""
        self.skill_timer = 0.0

def test_kinetic_trap_deploy_and_interact():
    world = MockWorld()

    ball = MockBall(1, 1, 100.0, 100.0, vx=10.0, vy=0.0)
    world.balls.append(ball)

    action = Action(ball, world)

    # 1. Deploy
    ball.skill = "deploy_kinetic_trap"
    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert hazard.kind == "kinetic_trap"
    assert hazard.x == 100.0
    assert hazard.y == 100.0
    assert hazard.kinetic_energy_pool == 0.0

    # 2. Friendly passes
    friendly = MockBall(2, 1, 120.0, 100.0, vx=50.0, vy=0.0)
    world.balls.append(friendly)

    action._update_skill_timer(1.0)

    assert hazard.kinetic_energy_pool == 100.0
    assert friendly.vx == 50.0 * 1.5  # Speed slightly increased (1.0 + 0.5 * 1.0)

    # 3. Enemy approaches
    enemy = MockBall(3, 2, 110.0, 100.0, vx=0.0, vy=0.0)
    world.balls.append(enemy)

    action._update_skill_timer(1.0)

    assert hazard.active is False
    assert hazard.duration == 0.0
    assert enemy.vx > 0.0 # Huge knockback
    assert enemy.shield == 50.0 # (200 - 150)

    assert any(e['type'] == 'visual_effect' and e['data']['type'] == 'kinetic_trap_explosion' for e in world.events)
