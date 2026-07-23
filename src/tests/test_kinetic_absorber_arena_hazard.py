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

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

class MockBall:
    def __init__(self, id, x, y, vx=0.0, vy=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 10.0
        self.mass = 2.0
        self.alive = True
        self.shield = 200.0

class MockHazard:
    def __init__(self, id, x, y, kind):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 30.0
        self.kinetic_energy_pool = 0.0

def test_kinetic_absorber_arena_hazard_collision_and_shockwave():
    world = MockWorld()

    # Fast ball heading right
    ball = MockBall(1, 70.0, 100.0, vx=100.0, vy=0.0)
    world.balls.append(ball)

    # Hazard right in front of ball
    hazard = MockHazard(2, 100.0, 100.0, "kinetic_absorber")
    world.arena.hazards.append(hazard)

    # Enemy ball nearby
    enemy = MockBall(3, 110.0, 100.0, vx=0.0, vy=0.0)
    world.balls.append(enemy)

    action = Action(ball, world)

    # 1. Collision resolution
    # Trigger collision resolution which should detect the hazard and apply energy
    action._resolve_collisions()

    # Ball should have collided with the hazard, speed reduced, energy transferred
    # Speed is 100 > 50, so energy = 100 * 2.0 * 0.5 = 100
    assert hazard.kinetic_energy_pool > 0.0
    assert ball.vx == 0.0 # Absorbed all

    # Simulate adding enough energy manually for testing the shockwave
    hazard.kinetic_energy_pool = 600.0

    # 2. Trigger execution loop
    action.execute("default", 1.0)

    # Shockwave should trigger and reset pool
    assert hazard.kinetic_energy_pool == 0.0

    # Enemy should be pushed and shield damaged
    assert enemy.vx > 0.0 # pushed right
    assert enemy.shield == 50.0 # 200 - 150

    # Check event
    assert any(e['type'] == 'visual_effect' and e['data']['type'] == 'kinetic_absorber_shockwave' for e in world.events)
