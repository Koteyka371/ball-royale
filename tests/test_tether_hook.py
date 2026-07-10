from ai.action import Action

class MockBall:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.radius = 10.0
        self.traits = []
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.speed = 100.0
        self.base_speed = 100.0
        self.alive = True
        self.id = id(self)
        self.ball_type = "default"
        self.inventory = []
        self.damage = 10

class MockWorld:
    def __init__(self):
        self.balls = []
        self.game_mode = {}

    def get_nearby_entities(self, ball, radius):
        return {"enemies": [b for b in self.balls if b != ball and b.team != ball.team], "allies": []}

    def _deal_damage(self, attacker, target):
        target.hp -= attacker.damage

def test_tether_hook():
    world = MockWorld()
    b1 = MockBall(0, 0, 1)
    b2 = MockBall(100, 0, 2)
    world.balls = [b1, b2]

    action = Action(b1, world)

    # Give b1 the tether hook item
    b1.inventory = ["tether_hook"]

    # Execute action to use the item
    action.execute("attack", 1.0)

    # Should use the item and set up the tether
    assert "tether_hook" not in b1.inventory
    assert hasattr(b1, "tether_hook_target")
    assert b1.tether_hook_target == b2
    assert hasattr(b1, "tether_hook_timer")
    assert b1.tether_hook_timer > 0

    # Simulate one frame
    b1.base_speed = 0
    b1.speed = 0
    b2.base_speed = 0
    b2.speed = 0
    initial_b2_hp = b2.hp

    action.execute("idle", 0.1)

    # Since it's pulled, b1.x should increase towards b2.x, or b2 towards b1, or both
    assert b1.x > 0 or b2.x < 100

    # Should deal minor damage
    assert b2.hp < initial_b2_hp
