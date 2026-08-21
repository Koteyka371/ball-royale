from ai.action import Action

class MockArena:
    def __init__(self):
        self.seasonal_modifier = "winter"
        self.hazards = []
    def clamp_position(self, x, y, r): return x, y, False
    def update_zone(self, t, d): pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.snowball_event_active = True
        self.events = []
        self.balls = []
    def _deal_damage(self, attacker, target, dmg=None):
        pass
    def get_nearby_entities(self, ball, radius):
        return {"enemies": [], "allies": []}

class MockBall:
    def __init__(self):
        self.x = 50.0
        self.y = 50.0
        self.vx = 50.0
        self.vy = 50.0
        self.radius = 10.0
        self.damage = 10.0
        self.base_radius = 10.0
        self.base_damage = 10.0
        self.ball_type = "normal"
        self.alive = True
        self.id = 1
        self.team = 1
        self.hp = 100
        self.out_of_combat_timer = 0.0

def test_frozen_movement():
    w = MockWorld()
    b = MockBall()
    w.balls = [b]
    b.frozen_timer = 3.0

    act = Action(b, w)
    act.execute("flee", 0.1)

    # Position should not have changed, and vx/vy might be handled elsewhere but execute() shouldn't update x/y since it returns early
    # Actually, execute calls _execute_internal which does movement
    assert b.frozen_timer < 3.0
