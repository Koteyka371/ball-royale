import pytest
import math
from src.ai.action import Action

class MockBall:
    def __init__(self, id, x, y, speed=2.0, radius=10.0, ball_type="warrior", perception_radius=250):
        self.id = id
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius
        self.ball_type = ball_type
        self.perception_radius = perception_radius
        self.current_action = "idle"
        self.alive = True
        self.skill_timer = 0

class MockBooster:
    def __init__(self, x, y, active=True):
        self.x = x
        self.y = y
        self.active = active

class MockWorld:
    def __init__(self):
        self.entities = []
        self.boosters = []
        self.width = 1000
        self.height = 1000
        self.damage_dealt = False
        self.booster_collected = False

    def get_nearby_entities(self, ball, radius):
        enemies = []
        allies = []
        for e in self.entities:
            if getattr(e, "id", None) == ball.id:
                continue
            dx = e.x - ball.x
            dy = e.y - ball.y
            if dx*dx + dy*dy <= radius*radius:
                if getattr(e, "ball_type", None) == ball.ball_type:
                    allies.append(e)
                else:
                    enemies.append(e)

        boosters = []
        for b in self.boosters:
            dx = b.x - ball.x
            dy = b.y - ball.y
            if dx*dx + dy*dy <= radius*radius and b.active:
                boosters.append(b)

        return {"enemies": enemies, "allies": allies, "boosters": boosters}

    def _deal_damage(self, attacker, target):
        self.damage_dealt = True

    def _collect_booster(self, ball, booster):
        self.booster_collected = True

def test_attack_stops_at_range():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    target = MockBall(2, 100, 150, ball_type="enemy")
    world.entities.extend([ball, target])

    action = Action(ball, world)

    # Distance is 50, sum of radii is 20 + 5 buffer = 25 attack range
    # Moving towards target
    delta = 0.5  # Large delta to ensure movement covers the distance

    action.execute("attack", delta)

    dist = math.sqrt((ball.x - target.x)**2 + (ball.y - target.y)**2)
    assert dist >= 24.9  # Should not move closer than attack range

    # Needs a second execute when already in range to actually attack
    action.execute("attack", delta)
    assert world.damage_dealt == True

def test_obstacle_avoidance():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    target = MockBall(2, 100, 200, ball_type="enemy")
    obstacle = MockBall(3, 100, 150, ball_type="ally")  # Obstacle right in the middle
    # Place obstacle slightly off center so avoidance vector has an X component
    obstacle.x = 101
    world.entities.extend([ball, target, obstacle])

    action = Action(ball, world)

    action.execute("attack", 0.1)

    # Ball should have moved in X direction to avoid the obstacle
    assert abs(ball.x - 100) > 0.1

def test_flee_obstacle_avoidance():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    enemy = MockBall(2, 100, 50, ball_type="enemy")  # Enemy above
    obstacle = MockBall(3, 105, 120, ball_type="ally")  # Obstacle below (in path of fleeing)
    world.entities.extend([ball, enemy, obstacle])

    action = Action(ball, world)

    action.execute("flee", 0.1)

    # Ball flees from enemy (moves down/positive Y) but obstacle is there
    # So it should also move horizontally to avoid the obstacle
    assert abs(ball.x - 100) > 0.1

def test_collect_booster_with_obstacle():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    booster = MockBooster(100, 200)
    obstacle = MockBall(3, 105, 120, ball_type="ally")  # Obstacle in the middle
    world.boosters.append(booster)
    world.entities.extend([ball, obstacle])

    action = Action(ball, world)

    action.execute("opportunistic", 0.1)

    # Ball should have moved in X direction to avoid the obstacle
    assert abs(ball.x - 100) > 0.1
