from ai.action import Action
from arena.basic_arena import BasicArena

class MockWorld:
    def __init__(self):
        self.arena = BasicArena()
        self.balls = []
        self.boosters = []
        self.bullets = []

class MockBall:
    def __init__(self, x=0, y=0, team=1):
        self.x = x
        self.y = y
        self.team = team
        self.speed = 2.0
        self.base_speed = 2.0
        self.damage = 10.0
        self.base_damage = 10.0
        self.hp = 100
        self.max_hp = 100
        self.stamina = 0.0
        self.max_stamina = 100.0
        self.active_skill = "none"
        self.radius = 10
        self.skill_timer = 0
        self._base_speed_set = True

def test_exhaustion():
    ball = MockBall()
    ball.stamina = 0.0
    world = MockWorld()
    world.balls = [ball]
    action = Action(ball, world)

    # Run one tick to apply exhaustion
    action.execute("idle", 0.1)

    # Speed and damage should be reduced
    assert ball.speed < ball.base_speed, f"Speed not reduced: {ball.speed} >= {ball.base_speed}"
    assert ball.damage < ball.base_damage, f"Damage not reduced: {ball.damage} >= {ball.base_damage}"

    # Regenerate stamina
    ball.stamina = 25.0
    action.execute("idle", 0.1)

    # Speed and damage should be restored
    assert ball.speed == ball.base_speed, f"Speed not restored: {ball.speed} != {ball.base_speed}"
    assert ball.damage == ball.base_damage, f"Damage not restored: {ball.damage} != {ball.base_damage}"

    print("Test passed!")

if __name__ == "__main__":
    test_exhaustion()
