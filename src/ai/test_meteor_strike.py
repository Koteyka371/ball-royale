import sys
sys.path.insert(0, 'src')
from ai.action import Action
import math

class MockBall:
    def __init__(self, x=0, y=0, skill="meteor_strike"):
        self.x = x
        self.y = y
        self.radius = 10.0
        self.skill = skill
        self.skill_timer = 0.0
        self.id = 1
        self.team = 1
        self.traits = []
        self.stamina = 100
        self.max_stamina = 100
        self.alive = True

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.width = 1000
        self.height = 1000
        self.balls = []

def test_meteor_strike():
    ball = MockBall(500, 500)
    enemy = MockBall(600, 600, skill="none")
    enemy.id = 2
    enemy.team = 2

    world = MockWorld()
    world.balls = [ball, enemy]

    action = Action(ball, world)
    action._get_enemies = lambda: [enemy]

    action._use_skill()

    # Check if hazards were created
    assert len(world.arena.hazards) >= 3
    assert len(world.arena.hazards) <= 5

    for h in world.arena.hazards:
        assert h.kind == "meteor"
        assert getattr(h, "duration", 0) == 5.0
        assert h.radius == 30.0
        assert getattr(h, "target_radius", 0) == 30.0

        # Check if they are near the enemy
        dist = math.hypot(h.x - enemy.x, h.y - enemy.y)
        assert dist <= 50.0 * 1.5 # 50 is max offset, with pythagoras max distance is ~70.7
