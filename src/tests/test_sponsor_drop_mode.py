import pytest
from ai.game_modes import SponsorDropMode, GAME_MODES

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.next_id = 100
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockEntity:
    def __init__(self, id_val, team):
        self.id = id_val
        self.team = team
        self.ball_type = "basic"
        self.alive = True
        self.x = 500.0
        self.y = 500.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0

def test_sponsor_drop_mode_setup():
    mode = SponsorDropMode()
    world = MockWorld()
    player = MockEntity(1, "team1")
    world.balls.append(player)
    mode.setup(world, [player])
    assert mode.drop_timer == 0.0
    assert mode.name == "Sponsor Drop"

def test_sponsor_drop_mode_spawns_box():
    mode = SponsorDropMode()
    world = MockWorld()
    player = MockEntity(1, "team1")
    world.balls.append(player)

    # Tick past interval
    mode.tick(world, world.balls, 16.0)

    # Should have a box spawned
    boxes = [b for b in world.balls if getattr(b, "ball_type", "") == "sponsor_drop_box"]
    assert len(boxes) == 1
    assert boxes[0].hp == 100.0
    assert len(world.events) > 0
    assert world.events[-1][0] == "drop_box_spawned"

def test_sponsor_drop_mode_destruction_grants_buff():
    mode = SponsorDropMode()
    world = MockWorld()
    player = MockEntity(1, "team1")
    world.balls.append(player)

    # Tick to spawn
    mode.tick(world, world.balls, 16.0)

    box = [b for b in world.balls if getattr(b, "ball_type", "") == "sponsor_drop_box"][0]

    # Destroy box and set last hit
    box.hp = 0
    box.alive = False
    box._last_hit_by_id = player.id

    # Tick again to process destruction
    mode.tick(world, world.balls, 0.1)

    assert getattr(player, "has_sponsor_buff", False) == True
    assert player.base_speed == 120.0 # 100 * 1.2
    assert player.speed == 120.0
    assert player.base_damage == 12.0 # 10 * 1.2
    assert player.damage == 12.0

    # Box should be removed
    assert box not in world.balls
