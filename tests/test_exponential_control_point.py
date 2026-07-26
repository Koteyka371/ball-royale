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
    def __init__(self, id, team, x, y, hp=100.0, radius=20.0):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.hp = hp
        self.radius = radius
        self.alive = True
        self.ball_type = "normal"
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0

class TestExponentialControlPointMode:
    def test_zone_capture_and_effects(self):
        mode = GAME_MODES["exponential_control_point"]
        mode.control_point = {"x": 500, "y": 500, "radius": 150, "owner": None, "capture_progress": 0.0}
        mode.hold_time = 0.0
        world = MockWorld()

        # Ball 1 inside the zone
        ball1 = MockBall(id=1, team="team_a", x=500.0, y=500.0)
        # Ball 2 outside the zone
        ball2 = MockBall(id=2, team="team_b", x=100.0, y=100.0)
        # Ball 3 inside the zone but same team as ball 1
        ball3 = MockBall(id=3, team="team_a", x=510.0, y=510.0)
        balls = [ball1, ball2, ball3]

        # Tick 1: Progress increases
        mode.apply_dynamic_traits(world, balls, 1.0)
        assert mode.control_point["capture_progress"] == 10.0
        assert mode.control_point["owner"] is None

        # Tick 2: Fast forward to EXACTLY capture (needs 9.0 delta)
        mode.apply_dynamic_traits(world, balls, 9.0)
        assert mode.control_point["capture_progress"] == 100.0
        assert mode.control_point["owner"] == "team_a"

        # Note: during Tick 2, it was captured, so hold_time became 0, then immediately hold_time += 9.0
        # So it's already 9.0. Let's reset it for testing the 1.0 case explicitly.
        mode.hold_time = 0.0
        ball1.hp = 100.0
        ball3.hp = 100.0
        ball1.speed_multiplier = 1.0
        ball1.damage_multiplier = 1.0

        # Tick 3: Hold time increases, buffs and damage applied
        old_hp = ball1.hp
        mode.apply_dynamic_traits(world, balls, 1.0)
        assert mode.hold_time == 1.0

        # Damage should be 1.5 ^ 1.0 * 1.0 = 1.5
        assert ball1.hp == old_hp - 1.5
        assert ball3.hp == old_hp - 1.5

        # Buff should be 1.0 + 0.1 * 1.0 = 1.1
        assert ball1.speed_multiplier == 1.1
        assert ball1.damage_multiplier == 1.1

        # Ball 2 (enemy) should be unaffected
        assert ball2.hp == 100.0
        assert ball2.speed_multiplier == 1.0
        assert ball2.damage_multiplier == 1.0
