import sys
import math
sys.path.append("src")
from ai.action import Action
class MockArena:
    def __init__(self):
        self.hazards = []
class MockWorld:
    def __init__(self, balls):
        self.balls = balls
        self.events = []
        self.arena = MockArena()
    def _deal_damage(self, attacker, target, dmg):
        if hasattr(target, "take_damage"):
            target.take_damage(dmg)
        else:
            target.hp -= dmg
class MockBall:
    def __init__(self, id, x, y, team="teamA"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.is_decoy = False
        self.owner_id = 1
        self.decoy_type = "explosive"
        self.decoy_timer = 5.0
        self._decoy_exploded = False
        self.vx = 0
        self.vy = 0
def test():
    b1 = MockBall(2, 100, 100)
    b1.is_decoy = True
    b1.hp = 0

    b2 = MockBall(3, 110, 110)
    b2.is_decoy = True
    b2.hp = 0

    b3 = MockBall(4, 90, 90)
    b3.is_decoy = True
    b3.hp = 0

    enemy = MockBall(5, 120, 120, "teamB")

    world = MockWorld([b1, b2, b3, enemy])
    action = Action(b1, world)
    action.execute("idle", 0.1)

    print(f"Enemy HP: {enemy.hp}, Events: {world.events}")
    print(f"Hazards: {[h.kind for h in world.arena.hazards]}")
    print(f"Enemy Velocity: vx={enemy.vx}, vy={enemy.vy}")
test()
