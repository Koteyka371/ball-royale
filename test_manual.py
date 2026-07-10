from ai.action import Action
from ai.game_modes import PhysicsAnomalyEventMode

class MockProfileManager:
    def is_nemesis(self, b1, b2): return False

class MockWorld:
    def __init__(self):
        self.arena = type('Arena', (), {'width': 1000, 'height': 1000, 'hazards': []})()
        self.events = []
        self.game_mode = PhysicsAnomalyEventMode()
        self.game_mode.event_active = True
        self.profile_manager = MockProfileManager()

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.team = "team1"
        self.radius = 10.0
        self.damage = 10.0
        self.hp = 100.0

world = MockWorld()
attacker = MockBall(1, 100, 500)
target = MockBall(2, 900, 500)
target.team = "team2"
action = Action(attacker, world)
action._attempt_damage(attacker, target)
print(attacker.suspended_projectiles)
action.execute("idle", 0.1)
print(attacker.suspended_projectiles)
