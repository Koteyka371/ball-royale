import pytest
from src.ai.game_modes import BountyExtractionMode

class MockWorld:
    def __init__(self):
        self.events = []

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.radius = 20.0
        self.alive = True
        self.currency = 0
        self.purchase_cooldown = 0.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.base_speed = 100.0
        self.speed = 100.0
        self.base_damage = 10.0
        self.damage = 10.0

def test_spawn_bounty_tag():
    mode = BountyExtractionMode()
    world = MockWorld()

    ball = MockBall(1, 100.0, 100.0)
    ball.currency = 3

    # Ball dies
    mode.on_ball_died(world, ball, None)

    assert len(mode.bounty_tags) == 1
    assert mode.bounty_tags[0]["type"] == "bounty_tag"
    assert mode.bounty_tags[0]["x"] == 100.0
    assert mode.bounty_tags[0]["y"] == 100.0
    assert mode.bounty_tags[0]["value"] == 4  # 3 held + 1 for self

def test_collect_bounty_tag():
    mode = BountyExtractionMode()
    world = MockWorld()

    # Pre-spawn a tag
    mode.bounty_tags = [
        {"type": "bounty_tag", "x": 50.0, "y": 50.0, "value": 2}
    ]

    # Ball is near tag
    ball = MockBall(1, 55.0, 55.0)

    mode.apply_dynamic_traits(world, [ball], 0.016)

    # Tag collected
    assert len(mode.bounty_tags) == 0
    assert ball.currency == 2

    # Event added
    assert any(e[0] == "tag_collected" for e in world.events)

def test_extract_bounty():
    mode = BountyExtractionMode()
    mode.extraction_timer = 100.0
    mode.extraction_zone_x = 200.0
    mode.extraction_zone_y = 200.0
    mode.extraction_zone_radius = 50.0

    world = MockWorld()

    # Ball inside extraction zone with enough currency
    ball = MockBall(1, 210.0, 210.0)
    ball.currency = 6

    mode.apply_dynamic_traits(world, [ball], 0.016)

    # Spent currency
    assert ball.currency == 1
    assert ball.purchase_cooldown > 0.0

    # Check that *some* upgrade was applied
    hp_up = ball.hp > 100.0
    spd_up = ball.speed > 100.0
    dmg_up = ball.damage > 10.0

    assert (hp_up or spd_up or dmg_up) is True
    assert any(e[0] == "upgrade_purchased" for e in world.events)
