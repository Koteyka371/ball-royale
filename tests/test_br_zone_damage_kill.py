import sys
sys.path.append('src')
from ai.game_modes import BattleRoyaleMode

class MockWorld:
    def __init__(self):
        self.dead_balls = []

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockBall:
    def __init__(self, id, btype):
        self.id = id
        self.ball_type = btype
        self.alive = True
        self.team = btype
        self.x = 0.0
        self.y = 0.0
        self.hp = 10.0

def test_battle_royale_zone_damage_kills():
    mode = BattleRoyaleMode()
    world = MockWorld()
    world.arena = MockArena()
    balls = [MockBall(1, "warrior")]
    balls[0].x = 10000.0  # Far outside zone

    mode.setup(world, balls)
    mode.tick(world, balls, delta=1.0)

    assert balls[0].hp == 0
    assert not balls[0].alive
    assert balls[0].killer == "safe_zone"

test_battle_royale_zone_damage_kills()
print("test_battle_royale_zone_damage_kills passed")
