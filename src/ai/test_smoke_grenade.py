import sys
import os

class MockBall:
    def __init__(self):
        self.x = 100
        self.y = 100
        self.id = "my_ball"
        self.inventory = ["smoke_grenade"]
        self.is_stunned = False

class MockWorld:
    def __init__(self):
        self.arena = type("Arena", (), {"hazards": []})()
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

def test_smoke_grenade_deployment():
    from ai.action import Action
    world = MockWorld()
    ball = MockBall()

    action = Action(ball, world)
    action._flee = lambda d: None

    # Avoid other checks
    ball.tracker_booster_timer = 0
    ball.team = "test"
    ball.speed = 10

    action.execute(delta=0.016, strategy="flee")

    assert len(world.arena.hazards) > 0, "No hazards created"
    smoke = world.arena.hazards[0]
    assert getattr(smoke, "kind", "") == "smoke_zone"
    assert "smoke_grenade" not in ball.inventory

test_smoke_grenade_deployment()
print("test_smoke_grenade_deployment passed")

def test_smoke_grenade_perception():
    from ai.perception import Perception

    world = MockWorld()
    ball = MockBall()

    enemy = MockBall()
    enemy.x = 110
    enemy.y = 110
    enemy.id = "enemy1"

    class Hazard:
        def __init__(self, x, y, r, k):
            self.x = x
            self.y = y
            self.radius = r
            self.kind = k
            self.active = True

    smoke = Hazard(100, 100, 100, "smokescreen")
    world.arena.hazards.append(smoke)

    # We are inside the smoke. Enemy is also inside the smoke.
    # What if enemy is outside the smoke?
    enemy_outside = MockBall()
    enemy_outside.x = 500
    enemy_outside.y = 500
    enemy_outside.id = "enemy2"

    world.get_nearby_entities = lambda b, r: {"enemies": [enemy, enemy_outside], "allies": [], "boosters": [], "traps": []}

    perception = Perception(ball, world)
    data = perception.scan()
    print("Enemies detected by ball inside smoke:", [e.id for e in data["enemies"]])

    perception_outside = Perception(enemy_outside, world)
    world.get_nearby_entities = lambda b, r: {"enemies": [ball, enemy], "allies": [], "boosters": [], "traps": []}
    data_outside = perception_outside.scan()
    print("Enemies detected by ball outside smoke:", [e.id for e in data_outside["enemies"]])

test_smoke_grenade_perception()
