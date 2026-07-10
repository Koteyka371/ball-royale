from ai.action import Action
import math

class MockWorld:
    def __init__(self):
        self.events = []
        self.boosters = []
        self.balls = []
        self.arena = MockArena()
        self.game_mode = MockGameMode()
    def add_event(self, kind, data):
        self.events.append((kind, data))
    def _deal_damage(self, attacker, target):
        pass
    def get_nearby_entities(self, ball, radius):
        return {"boosters": [], "hazards": [], "enemies": [e for e in self.balls if e.team != ball.team]}

class MockArena:
    def __init__(self):
        self.hazards = []
    def clamp_position(self, x, y, r):
        return x, y, False

class MockGameMode:
    def __init__(self):
        self.weather = "thunderstorm"

class MockBall:
    def __init__(self, id, x=0, y=0, team="A"):
        self.x = x
        self.y = y
        self.radius = 10
        self.team = team
        self.ball_type = "normal"
        self.hp = 100
        self.id = id
        self.alive = True
        self.damage = 10
        self.SKILL = "chain_bounce_attack"
        self.skill = "chain_bounce_attack"

def test_chain_immunity():
    w = MockWorld()
    b = MockBall(1)
    a = Action(b, w)

    # Test damage chaining skipping immune balls
    e1 = MockBall(2, x=20, y=0, team="B")
    e2 = MockBall(3, x=40, y=0, team="B")

    e1.chain_immunity_timer = 0
    e2.chain_immunity_timer = 5.0

    w.balls = [b, e1, e2]

    b.skill_timer = 0

    a.execute("use_skill", 1.0)

    # e1 should take damage, e2 should be skipped
    print(f"e1 hp: {e1.hp}, e2 hp: {e2.hp}")
    assert e1.hp < 100
    assert e2.hp == 100
    print("Damage test passed!")

if __name__ == "__main__":
    test_chain_immunity()
