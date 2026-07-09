import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action

class MockEntity:
    def __init__(self, id, x, y, kind=None):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.ball_type = "booster"
        self.duration = 5.0
        self.radius = 15.0
        self.damage = 0.0

    def get(self, key, default=None):
        return getattr(self, key, default)

class MockBall:
    def __init__(self, id, team="team1"):
        self.id = id
        self.team = team
        self.x = 0
        self.y = 0
        self.radius = 10
        self.speed = 2
        self.base_speed = 10
        self.hp = 100
        self.max_hp = 100
        self.stamina = 100
        self.alive = True
        self.ball_type = "basic"
        self.perception_radius = 250.0
        self.shield = 50.0
        self.skill_timer = 0.0

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = type('MockArena', (), {'hazards': [], 'update_zone': lambda *args: None, 'width': 1000, 'height': 1000, 'clamp_position': lambda *args: (0, 0, False)})()

    def get_nearby_entities(self, ball, radius):
        return {
            "enemies": [b for b in self.balls if b.team != ball.team],
            "allies": [],
            "boosters": self.boosters
        }

def test_emp_booster():
    ball = MockBall(1, team="team1")
    enemy = MockBall(2, team="team2")
    enemy.x = 50
    enemy.y = 0
    enemy.shield = 100.0
    enemy.skill_timer = 0.0

    enemy_far = MockBall(4, team="team2")
    enemy_far.x = 1000
    enemy_far.y = 0
    enemy_far.shield = 50.0

    booster = MockEntity(10, 0, 0, kind="emp_booster")
    laser = MockEntity(11, 20, 20, kind="laser_beam")
    gravity = MockEntity(12, 50, 50, kind="gravity_well")
    spikes = MockEntity(13, 10, 10, kind="spikes")

    world = MockWorld()
    world.balls = [ball, enemy, enemy_far]
    world.boosters = [booster]
    world.arena.hazards = [booster, laser, gravity, spikes]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # booster should be removed
    assert len(world.boosters) == 0
    assert booster not in world.arena.hazards

    # Enemy in range should have shield = 0, skill_timer = 10
    assert enemy.shield == 0.0
    assert enemy.skill_timer == 10.0

    # Far enemy should remain unaffected
    assert enemy_far.shield == 50.0
    assert enemy_far.skill_timer == 0.0

    # Lasers and gravity well disabled (it was 10.0, but gets decremented by delta 1.0 = 9.0)
    assert getattr(laser, "emp_disabled_timer", 0.0) == 10.0
    assert getattr(gravity, "emp_disabled_timer", 0.0) == 10.0

    # Spikes not affected
    assert getattr(spikes, "emp_disabled_timer", 0.0) == 0.0

if __name__ == "__main__":
    test_emp_booster()
    print("Test passed!")
