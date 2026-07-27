import pytest
import math

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.skill = "boomerang"
        self.skill_timer = 0.0
        self.team = "A"
        self.alive = True
        self.radius = 10.0
        self.damage = 25.0
        self.hp = 100.0

    def take_damage(self, damage):
        self.hp -= damage

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'hazards': []})()
        self.balls = []
        self.events = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b.team != ball.team]}

def test_boomerang_skill():
    from ai.action import Action
    from ai.game_modes import GameMode

    ball = MockBall(1, 100, 100)
    world = MockWorld()
    world.balls.append(ball)

    enemy = MockBall(2, 200, 100)
    enemy.team = "B"
    world.balls.append(enemy)

    action = Action(ball, world)

    # Cast boomerang
    action._use_skill()

    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]

    game_mode = GameMode()

    for _ in range(10):
        hazard.active = True
        game_mode.tick(world, world.balls, 0.05)

    print(f"Hazard pos: {hazard.x}, {hazard.y}, State: {hazard.boomerang_state}")
    print(f"Enemy pos: {enemy.x}, {enemy.y}")
    assert enemy.hp < 100.0
