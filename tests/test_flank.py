import sys
sys.path.insert(0, 'src')
from ai.action import Action
from ai.personality import Personality

class MockBall:
    def __init__(self, x=0.0, y=0.0, vx=0.0, vy=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.speed = 10.0
        self.radius = 10.0
        self.perception_radius = 500.0
        self.hp = 100
        self.max_hp = 100
        self.damage = 10
        self.alive = True
        self.attack_timer = 0.0
        self.skill_timer = 0.0
        self.skill_cooldown = 5.0
        self.used_skill = False
        self.emotion_state = "neutral"
        self.ball_type = "ninja"
        self.difficulty = "medium"
        self.personality = Personality("cunning")

    def get_hp_percent(self):
        return self.hp / self.max_hp

    def use_skill(self):
        self.used_skill = True

class MockWorld:
    def __init__(self):
        self.balls = []
        self.width = 1000
        self.height = 1000
        self.damage_dealt = 0

    def get_nearby_entities(self, ball, radius):
        return [b for b in self.balls if b != ball]

    def _deal_damage(self, attacker, target):
        self.damage_dealt = attacker.damage
        target.hp -= attacker.damage

def test_flank_movement():
    world = MockWorld()
    attacker = MockBall(x=100.0, y=100.0)
    # Target is moving right
    target = MockBall(x=200.0, y=100.0, vx=1.0, vy=0.0)
    target.ball_type = "scout"
    world.balls = [attacker, target]

    action = Action(attacker, world)

    old_x = attacker.x

    # To trigger the skill usage, skill_timer must be <= 0 and direct_dist > attack_range * 1.5
    # attack_range is 10 + 10 + 5 = 25. 25 * 1.5 = 37.5. Distance is 100 > 37.5.
    attacker.skill_timer = 0.0

    action.execute("flank", 1.0)

    assert attacker.x > old_x
    assert attacker.used_skill

def test_flank_normal_hit():
    world = MockWorld()
    attacker = MockBall(x=220.0, y=100.0)
    target = MockBall(x=200.0, y=100.0, vx=1.0, vy=0.0)
    target.ball_type = "scout"
    world.balls = [attacker, target]

    action = Action(attacker, world)

    attacker.attack_timer = 0.0
    action.execute("flank", 0.01)

    assert world.damage_dealt == 10


def test_flank_critical_hit():
    world = MockWorld()
    attacker = MockBall(x=180.0, y=100.0)
    target = MockBall(x=200.0, y=100.0, vx=1.0, vy=0.0)
    target.ball_type = "scout"
    world.balls = [attacker, target]

    action = Action(attacker, world)

    # Ensure attack timer is exactly 0
    attacker.attack_timer = 0.0

    # Set delta to 0 so it doesn't move out of range while flanking
    action.execute("flank", 0.0)

    # Ninja class now has a 3.0x multiplier on critical hits
    assert world.damage_dealt == 30
def test_flank_edge_cases():
    # Test when target is completely stationary
    world = MockWorld()
    attacker = MockBall(x=100.0, y=100.0)
    # Target is stationary. Default assumption is it faces right (vx=1, vy=0)
    # Flank point will be behind it, i.e., at x = target.x - 1 * 40 = 200 - 40 = 160.
    target = MockBall(x=200.0, y=100.0, vx=0.0, vy=0.0)
    target.ball_type = "scout"
    world.balls = [attacker, target]

    action = Action(attacker, world)

    # Move for a short delta
    action.execute("flank", 1.0)

    # Attacker starts at 100, flank point is 160, so it should move right
    assert attacker.x > 100.0
