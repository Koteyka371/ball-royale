import pytest
from ai.action import Action
from ai.game_modes import GAME_MODES

class MockBall:
    def __init__(self, x=500.0, y=500.0):
        self.id = 1
        self.x = x
        self.y = y
        self.speed = 100.0
        self.base_speed = 100.0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.skill_timer = 10.0

class MockArena:
    def __init__(self):
        self.width = 1000.0
        self.height = 1000.0
        self.hazards = []
        self.rooms = []

class MockLeaderboardManager:
    def __init__(self):
        self.data = {"current_season": 0}

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.events = []
        self.boosters = []
        self.leaderboard_manager = MockLeaderboardManager()
        self.next_id = 1000
    def get_weather(self):
        return "clear"
    def get_nearby_entities(self, entity, radius):
        return {"balls": [], "hazards": self.arena.hazards, "boosters": []}
    def add_event(self, event):
        self.events.append(event)

def test_overdrive_zone_mode_setup():
    mode = GAME_MODES["overdrive_zone"]
    world = MockWorld()
    balls = [MockBall()]
    world.balls = balls

    mode.setup(world, balls)

    # Check if hazard was spawned
    assert len(world.arena.hazards) == 1
    hazard = world.arena.hazards[0]
    assert getattr(hazard, "kind", "") == "overdrive_zone"
    assert getattr(hazard, "x", 0) == 500.0
    assert getattr(hazard, "y", 0) == 500.0
    assert getattr(hazard, "radius", 0) == 200.0

def test_overdrive_zone_effect():
    mode = GAME_MODES["overdrive_zone"]
    world = MockWorld()
    ball = MockBall(x=500.0, y=500.0) # Inside the zone
    world.balls = [ball]

    mode.setup(world, world.balls)
    action = Action(ball, world)

    # Tick Action to apply hazard logic
    initial_stamina = ball.stamina
    initial_skill_timer = ball.skill_timer
    delta = 0.1
    action.execute(ball, delta)

    # 1. overdrive_zone_active should be set
    assert getattr(ball, "overdrive_zone_active", False) == True

    # 2. Stamina should decrease by 20.0 * delta
    expected_stamina = 100.0
    assert ball.stamina == expected_stamina

    # 3. Skill cooldown should be 3.0x faster
    expected_timer_reduction = delta * 3.0
    expected_timer = initial_skill_timer - expected_timer_reduction
    assert ball.skill_timer == pytest.approx(expected_timer)

def test_overdrive_zone_slow_when_no_stamina():
    mode = GAME_MODES["overdrive_zone"]
    world = MockWorld()
    ball = MockBall(x=500.0, y=500.0)
    ball.stamina = 0.0
    ball.max_stamina = 0.0 # Prevent natural regen
    world.balls = [ball]

    mode.setup(world, world.balls)
    action = Action(ball, world)

    action.execute(ball, 0.1)

    assert getattr(ball, "overdrive_zone_active", False) == True
    assert ball.stamina == 0.0
    assert ball.speed == 37.5

def test_outside_overdrive_zone():
    mode = GAME_MODES["overdrive_zone"]
    world = MockWorld()
    ball = MockBall(x=900.0, y=900.0) # Outside the zone (zone is at 500,500, radius 200)
    world.balls = [ball]

    mode.setup(world, world.balls)
    action = Action(ball, world)

    initial_stamina = ball.stamina
    initial_skill_timer = ball.skill_timer
    delta = 0.1

    action.execute(ball, delta)

    assert getattr(ball, "overdrive_zone_active", False) == False

    # Stamina shouldn't drop
    assert ball.stamina >= initial_stamina

    # Skill timer shouldn't be sped up by overdrive
    expected_timer_reduction = delta * 1.0 # Normal speed
    expected_timer = initial_skill_timer - expected_timer_reduction
    assert ball.skill_timer == pytest.approx(expected_timer)
