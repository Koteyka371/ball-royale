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

def test_disruptor_booster():
    ball = MockBall(1, team="team1")
    enemy = MockBall(2, team="team2")
    enemy.x = 50
    enemy.y = 0

    ally = MockBall(3, team="team2")
    ally.x = 60
    ally.y = 0
    ally.ball_type = "advanced"

    enemy_far = MockBall(4, team="team2")
    enemy_far.x = 200
    enemy_far.y = 0

    booster = MockEntity(10, 0, 0, kind="disruptor_booster")

    world = MockWorld()
    world.balls = [ball, enemy, ally, enemy_far]
    world.boosters = [booster]
    world.arena.hazards = [booster]

    action = Action(ball, world)
    action.execute("collect_booster", 1.0)

    # Ball should have disruptor_aura_timer
    assert hasattr(ball, "disruptor_aura_timer")
    # timer is decremented by 1.0 in execute -> _update_skill_timer
    assert ball.disruptor_aura_timer == 4.0
    # booster should be removed
    assert len(world.boosters) == 0

    # Enemy in range should have aura_disruption_timer = 0.5
    assert enemy.aura_disruption_timer == 0.5
    assert ally.aura_disruption_timer == 0.5
    # Far enemy should not
    assert not hasattr(enemy_far, "aura_disruption_timer") or enemy_far.aura_disruption_timer == 0.0

    # Let's check ally aura logic
    action_enemy = Action(enemy, world)
    action_enemy._apply_friendly_aura(1.0)
    # They shouldn't have stacking aura buffs since aura_radius = 0
    assert enemy.hp == 100 # no regen
    assert enemy.speed == 10 # no speed boost

if __name__ == "__main__":
    test_disruptor_booster()
    print("Test passed!")
