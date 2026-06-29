import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ai.action import Action

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 100.0
        self.y = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.speed = 2.0
        self.radius = 10.0
        self.kills = 2
        self.team = 1

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.balls = []
        self.tick = 0
        self.arena = MockArena()

def test_stamina_dash():
    ball = MockBall()
    enemy = MockBall()
    enemy.id = 2
    enemy.team = 2
    enemy.x = 200.0
    enemy.y = 200.0
    world = MockWorld()
    world.balls.append(ball)
    world.balls.append(enemy)
    action = Action(ball, world)

    # Tick 1: Initialize stamina and apply dash
    action.execute("chase", 0.1)

    # Stamina should be initialized
    assert hasattr(ball, "stamina")
    assert getattr(ball, "is_dashing", False)

    # Tick 2: Stop dashing, regenerate stamina
    # Wait, chase will move the ball and consume stamina. Let's check stamina drain.
    assert ball.stamina < 100.0  # Consumed by dash

    prev_stamina = ball.stamina
    action.execute("idle", 0.1)

    assert ball.stamina > prev_stamina # Regenerated since we didn't move
