import pytest
from unittest.mock import Mock
from ai.action import Action
from ai.game_modes import GameMode

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.safe_zone_x = 500
        self.safe_zone_y = 500

class MockProfileManager:
    def is_nemesis(self, t1, t2):
        if t1 == "hero" and t2 == "nemesis":
            return True
        return False

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.boosters = []
        self.balls = []
        self.profile_manager = MockProfileManager()

class MockBall:
    def __init__(self, id, x, y, team="red", ball_type="hero"):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = 15.0
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100
        self.inventory = []
        self.max_hp = 100
        self.stun_timer = 0
        self.emp_immunity_timer = 0
        self.base_speed = 300

    def take_damage(self, dmg):
        self.hp -= dmg

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 10.0

def test_nemesis_drone_pickup_and_deploy():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    world.balls.append(ball)

    action = Action(ball, world)

    # Test pickup
    item = MockHazard("nemesis_drone_item", 110, 110)
    world.arena.hazards.append(item)

    # Fake a state where ball is close to the item
    ball.inventory.append("nemesis_drone_item")

    # Run execute
    action.execute("attack", 0.016)

    assert "nemesis_drone_item" not in ball.inventory
    assert len(world.arena.hazards) > 0
    drone = None
    for h in world.arena.hazards:
        if getattr(h, "kind", "") == "nemesis_drone":
            drone = h
            break
    assert drone is not None
    assert drone.owner_id == ball.id
    assert drone.owner_ball_type == "hero"
    assert drone.owner_team == "red"

def test_nemesis_drone_game_mode_logic():
    world = MockWorld()
    ball = MockBall(1, 100, 100)
    nemesis = MockBall(2, 200, 100, team="blue", ball_type="nemesis")
    other = MockBall(3, 100, 200, team="blue", ball_type="other")

    world.balls.extend([ball, nemesis, other])

    # Spawn drone manually
    from arena.procedural_arena import Hazard
    drone = Hazard("d1", 100, 100, 5.0, "nemesis_drone", 25.0)
    drone.owner_id = 1
    drone.owner_ball_type = "hero"
    drone.owner_team = "red"
    world.arena.hazards.append(drone)

    gm = GameMode()

    # Tick should move drone toward nemesis (x=200, y=100)
    gm.tick(world, world.balls, 0.1)

    assert drone.x > 100  # Should have moved towards nemesis (right)
    assert drone.y == 100

    # Place nemesis right on top of drone to test damage
    nemesis.x = drone.x
    nemesis.y = drone.y
    initial_hp = nemesis.hp

    # Also place other on top of drone to test damage
    other.x = drone.x
    other.y = drone.y
    initial_other_hp = other.hp

    gm.tick(world, world.balls, 0.1)

    assert nemesis.hp < initial_hp
    assert other.hp < initial_other_hp

if __name__ == "__main__":
    pytest.main(["-v", "src/ai/test_nemesis_drone.py"])
