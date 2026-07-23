import pytest
from system.profile import ProfileManager
from ai.action import Action
from ai.game_modes import GameMode
import os

class MockEntity:
    def __init__(self, id, x, y, kind="", radius=15.0, ball_type=None, hp=100.0, team=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.ball_type = ball_type
        self.hp = hp
        self.max_hp = hp
        self.speed = 2.0
        self.base_speed = 2.0
        self.vx = 0.0
        self.vy = 0.0
        self.team = team
        self.alive = True
    def take_damage(self, amount):
        self.hp -= amount

class MockProfileManager:
    def is_nemesis(self, a, b):
        return True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = self.MockArena()
        self.profile_manager = MockProfileManager()

    class MockArena:
        def __init__(self):
            self.hazards = []
            self.width = 1000
            self.height = 1000
            self.items = []

def test_nemesis_drone():
    world = MockWorld()

    ball = MockEntity(id=1, x=100.0, y=100.0, ball_type="basic", team="Red")
    nemesis_enemy = MockEntity(id=2, x=200.0, y=100.0, ball_type="nemesis", team="Blue")
    world.balls = [ball, nemesis_enemy]

    booster = MockEntity(id=99, x=105.0, y=100.0, kind="nemesis_drone_booster")
    booster.ball_type = "booster"
    booster.active = True
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)

    # Collect booster
    action._collect_booster(1.0)

    assert booster not in world.boosters
    assert booster not in world.arena.hazards

    drones = [h for h in world.arena.hazards if (getattr(h, "kind", "") if not isinstance(h, dict) else h.get("kind", "")) == "nemesis_drone"]
    assert len(drones) == 1
    drone = drones[0]

    mode = GameMode()
    mode.tick(world, world.balls, 0.5)

    d_x = getattr(drone, "x", 0) if not isinstance(drone, dict) else drone.get("x", 0)
    assert d_x > 100.0
    assert d_x <= 200.0

    # move drone manually to touch nemesis
    if isinstance(drone, dict):
        drone["x"] = 195.0
        drone["y"] = 100.0
    else:
        drone.x = 195.0
        drone.y = 100.0

    mode.tick(world, world.balls, 0.5)

    assert nemesis_enemy.hp < 100.0
    assert drone not in world.arena.hazards

def test_nemesis_drone_ping():
    world = MockWorld()
    world.events = []
    world.add_event = lambda e_type, e_data: world.events.append({"type": e_type, "data": e_data})

    ball = MockEntity(id=1, x=100.0, y=100.0, ball_type="basic", team="Red")
    nemesis_enemy = MockEntity(id=2, x=200.0, y=100.0, ball_type="nemesis", team="Blue")
    world.balls = [ball, nemesis_enemy]

    drone = MockEntity(id=99, x=105.0, y=100.0, kind="nemesis_drone")
    drone.owner_id = 1
    world.arena.hazards = [drone]

    mode = GameMode()
    mode.tick(world, world.balls, 0.5)

    assert len(world.events) == 0

    mode.tick(world, world.balls, 1.6)

    assert len(world.events) == 2
    assert world.events[0]["type"] == "nemesis_compass"
    assert world.events[1]["type"] == "visual_effect"
