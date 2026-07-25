from ai.game_modes import GAME_MODES

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.tick_timer = 0.0
        self.arena = MockArena()
        self.boosters = []
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})

class MockBall:
    def __init__(self, id, team, x, y, radius=20.0):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.radius = radius
        self.alive = True
        self.ball_type = "normal"

class TestCaptureZonesMode:
    def test_zone_spawning(self):
        mode = GAME_MODES["capture_zones"]
        mode.zones = [] # Reset zones
        world = MockWorld()
        balls = []

        mode.apply_dynamic_traits(world, balls, 0.1)

        assert len(mode.zones) == 3
        for zone in mode.zones:
            assert 200 <= zone["x"] <= 800
            assert 200 <= zone["y"] <= 800
            assert zone["radius"] == 150.0
            assert zone["owner"] is None
            assert zone["capture_progress"] == 0.0

    def test_zone_capture_progress(self):
        mode = GAME_MODES["capture_zones"]
        mode.zones = []
        world = MockWorld()
        # Create a zone explicitly for testing
        zone = {
            "x": 500.0,
            "y": 500.0,
            "radius": 150.0,
            "owner": None,
            "capture_progress": 0.0,
            "capturing_team": None,
            "reward_timer": 5.0
        }
        mode.zones.append(zone)

        # Ball 1 inside the zone
        ball1 = MockBall(id=1, team="team_a", x=500.0, y=500.0)
        balls = [ball1]

        mode.apply_dynamic_traits(world, balls, 1.0)

        assert zone["capturing_team"] == "team_a"
        assert zone["capture_progress"] > 0.0
        assert zone["owner"] is None

        # Fast forward capture
        mode.apply_dynamic_traits(world, balls, 5.0)

        assert zone["capture_progress"] == 100.0
        assert zone["owner"] == "team_a"
        assert any(e["type"] == "zone_captured" and e["data"]["team"] == "team_a" for e in world.events)

    def test_booster_spawning(self):
        import random
        random.seed(42) # Force booster spawning
        mode = GAME_MODES["capture_zones"]
        mode.zones = []
        world = MockWorld()
        zone = {
            "x": 500.0,
            "y": 500.0,
            "radius": 150.0,
            "owner": "team_a",
            "capture_progress": 100.0,
            "capturing_team": "team_a",
            "reward_timer": 0.01 # Expire immediately
        }
        mode.zones.append(zone)
        balls = []

        mode.apply_dynamic_traits(world, balls, 0.1)

        # Depending on random seed, either a booster or hazard is spawned.
        # Since we use random, let's just check one of them was spawned.
        spawned = len(world.boosters) > 0 or len(world.arena.hazards) > 0
        assert spawned

        if len(world.boosters) > 0:
            assert world.boosters[0]["type"] in ["hp", "speed", "damage"]
        else:
            assert world.arena.hazards[0]["type"] == "zone_defense"
            assert world.arena.hazards[0]["owner_team"] == "team_a"

    def test_hazard_spawning(self):
        import random
        random.seed(43)
        mode = GAME_MODES["capture_zones"]
        mode.zones = []
        world = MockWorld()
        zone = {
            "x": 500.0,
            "y": 500.0,
            "radius": 150.0,
            "owner": "team_b",
            "capture_progress": 100.0,
            "capturing_team": "team_b",
            "reward_timer": 0.01
        }
        mode.zones.append(zone)
        balls = []

        mode.apply_dynamic_traits(world, balls, 0.1)

        spawned = len(world.boosters) > 0 or len(world.arena.hazards) > 0
        assert spawned

    def test_zone_decay(self):
        mode = GAME_MODES["capture_zones"]
        mode.zones = []
        world = MockWorld()
        zone = {
            "x": 500.0,
            "y": 500.0,
            "radius": 150.0,
            "owner": None,
            "capture_progress": 50.0,
            "capturing_team": "team_a",
            "reward_timer": 5.0
        }
        mode.zones.append(zone)
        balls = [] # No one in zone

        mode.apply_dynamic_traits(world, balls, 1.0)

        # Should decay
        assert zone["capture_progress"] == 40.0
