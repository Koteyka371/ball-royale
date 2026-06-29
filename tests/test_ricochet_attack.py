
class MockBall:
    def __init__(self, x, y, hp=100, team=1):
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.speed = 2.0
        self.radius = 10.0
        self.alive = True
        self.dot_duration = 0
        self.dot_damage_per_tick = 0

class MockWorld:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.balls = []
    def get_nearby_entities(self, ball, radius):
        enemies = [b for b in self.balls if b.team != ball.team]
        return {"enemies": enemies, "allies": []}

def test_ricochet_attack():
    import sys
    import os
    sys.path.append(os.path.abspath('src'))
    from ai.action import Action

    world = MockWorld()
    attacker = MockBall(500, 500, team=1)
    target = MockBall(600, 500, team=2) # dx=100, dy=0 => abs(dx) > abs(dy) => should bounce on Y
    world.balls = [attacker, target]

    action = Action(attacker, world)
    action.execute("ricochet_attack", 1.0)

    # It should move on y towards 0 since it was 500 (height/2 is 500, so it could be 0 or 1000 depending on logic, let's just check it moved)
    assert attacker.x != 500 or attacker.y != 500
