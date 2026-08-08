import sys
import os
sys.path.append(os.path.abspath('src'))
from ai.action import Action
class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self, arena, balls=None, boosters=None):
        self.arena = arena
        self.balls = balls if balls else []
        self.boosters = boosters if boosters else []
        self.events = []
        self.tick = 0
    def add_event(self, event_type, data):
        pass
    def get_nearby_entities(self, b, r):
        return {'boosters': self.boosters, 'hazards': self.arena.hazards, 'enemies': [], 'allies': [], 'items': []}
    def _deal_damage(self, attacker, victim, amount, damage_type="normal"):
        victim.hp -= amount

class MockBall:
    def __init__(self, id, x, y, team="team_a"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100.0
        self.max_hp = 100.0
        self.vx = 0
        self.vy = 0
        self.speed = 100.0
        self.base_speed = 100.0
        self.ball_type = "base"
        self.traits = []
        self.mass = 1.0

def test_decoy_explosion():
    arena = MockArena()
    player = MockBall(id=1, x=100, y=100, team="team_a")
    decoy = MockBall(id=2, x=100, y=100, team="team_a")
    decoy.is_decoy = True
    decoy.decoy_type = "explosive"
    decoy.owner_id = 1
    decoy.decoy_timer = 5.0
    decoy.hp = 0  # Trigger explosion
    decoy.from_decoy_item = True
    enemy = MockBall(id=3, x=110, y=100, team="team_b")

    world = MockWorld(arena, [player, decoy, enemy])
    action = Action(decoy, world)
    action.execute("idle", 0.1)

    assert enemy.hp == 70.0
    assert enemy.speed == 50.0
    assert getattr(enemy, "snare_timer", 0.0) == 3.0
    assert getattr(decoy, "_decoy_exploded", False) is True

if __name__ == "__main__":
    test_decoy_explosion()
