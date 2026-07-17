import pytest
from ai.game_modes import MirageSwarmMode

class MockBall:
    def __init__(self, id, x, y, team="team_A", ball_type="basic"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.is_decoy = False
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.kind = "regular"

class MockWorld:
    def __init__(self):
        self.balls = []
        self.next_id = 1000

def test_mirage_swarm_basic():
    mode = MirageSwarmMode()
    world = MockWorld()
    b1 = MockBall(1, 100.0, 100.0)
    world.balls = [b1]

    mode.setup(world, world.balls)

    # Tick below spawn_interval, should just record
    for _ in range(5):
        mode.tick(world, world.balls, 1.0)

    assert len(world.balls) == 1
    assert 1 in mode.recordings
    assert len(mode.recordings[1]) == 5

    # Tick past spawn_interval (15.0)
    for _ in range(11):
        mode.tick(world, world.balls, 1.0)

    # Mirages should be spawned
    assert len(world.balls) > 1

    # Find a mirage
    mirages = [b for b in world.balls if getattr(b, "kind", "") == "mirage_ball"]
    assert len(mirages) >= 2

    m = mirages[0]
    assert m.hp == 1.0
    assert m.alive == True
    assert m.is_decoy == True
    assert m.team == "team_A"

    # Damage mirage, should dissipate
    m.take_damage(5.0)
    assert m.hp == 0.0
    assert m.alive == False
