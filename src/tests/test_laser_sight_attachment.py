from ai.action import Action

class MockWorld:
    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball], 'boosters': self.boosters}
    def __init__(self):
        self.arena = type("Arena", (), {"hazards": []})
        self.boosters = []
        self.next_id = 9999
        self.events = []
        self.balls = []

    def _deal_damage(self, attacker, target):
        target.hp -= getattr(attacker, "damage", 10.0)

class MockBall:
    def __init__(self, id=1, x=0.0, y=0.0):
        self.id = id
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.radius = 10.0
        self.ball_type = "basic"
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 2.0
        self.damage = 10.0
        self.suspended_projectiles = []
        self.state_history = []
        self.last_teleport_tick = -100
        self.skill_timer = 5.0
        self.attack_range = 100.0

def test_laser_sight_attachment_collection_and_effect():
    world = MockWorld()
    ball = MockBall()
    world.balls.append(ball)

    booster = type("Booster", (), {"kind": "laser_sight_attachment", "x": 1.0, "y": 1.0, "radius": 10.0})
    world.boosters.append(booster)

    action = Action(ball, world)

    # Pre-collection skill timer
    assert ball.skill_timer == 5.0

    # Collect the booster
    action._collect_booster(0.1)

    # Verify booster collected
    assert getattr(ball, "laser_sight_active", False) == True
    assert getattr(ball, "attack_range", 100.0) == 150.0  # 100 * 1.5

    # Target
    target = MockBall(id=2, x=20.0, y=20.0)
    world.balls.append(target)

    # Pre-damage skill timer
    assert ball.skill_timer == 5.0

    # Deal damage
    action._attempt_damage(ball, target)

    # Cooldown should be reduced by 0.5
    assert ball.skill_timer == 4.5

    # Deal damage again
    action._attempt_damage(ball, target)

    # Cooldown should be reduced by another 0.5
    assert ball.skill_timer == 4.0
