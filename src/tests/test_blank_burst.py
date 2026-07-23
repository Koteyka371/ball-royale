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

class MockBall:
    def __init__(self, x=0, y=0, vx=0, vy=0):
        self.id = "mock_id"
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.hp = 100
        self.team = 1
        self.skill = "blank_burst"
        self.active_skill = "blank_burst"
        self.is_active = True
        self.alive = True
        self.skill_cooldown = 5.0
        self.skill_timer = 0.0
        self.BALL_TYPE = "player"

def test_blank_burst_recoil_and_hazards():
    world = MockWorld()
    world.game_mode = None
    player = MockBall(x=100, y=100, vx=0, vy=0)
    world.balls.append(player)

    enemy = MockBall(x=100, y=200, vx=0, vy=0)
    enemy.team = 2
    world.balls.append(enemy)

    action = Action(player, world)
    action._get_enemies = lambda: [enemy]
    action._use_skill()

    # Assert hazards were created
    assert len(world.arena.hazards) == 5
    for h in world.arena.hazards:
        assert getattr(h, "kind", "") == "blank_projectile"
        assert getattr(h, "damage", 1) == 0.0
        assert getattr(h, "owner_id", None) == "mock_id"

    # Assert recoil was applied
    # Enemy is directly below (y=200 vs y=100), so nx=0, ny=1
    # Thrust should push player back (ny=-1, thrust=800)
    # Wait, in the code: dx=0, dy=100 -> nx=0, ny=1.
    # self.ball.vy = vy - ny * thrust_force = 0 - 1 * 800 = -800
    assert player.vy == -800.0
