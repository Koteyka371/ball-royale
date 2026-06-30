from src.ai.game_modes import BlackoutMode, VisionReducedMode
from src.ai.perception import Perception

class MockArena:
    def __init__(self):
        self.is_night = False
        self.is_foggy = False
        self.is_raining = False
        self.is_sandstorming = False
        self.is_snowing = False
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": [], "boosters": [], "traps": []}

    def add_event(self, event_type, data):
        pass

class MockBall:
    def __init__(self):
        self.perception_radius = 250
        self.ball_type = "dummy"
        self.team = "dummy"
        self.alive = True
        self.x = 0
        self.y = 0
        self.id = 1
        self.time_since_death = 0

print("Files exist and imports work!")
