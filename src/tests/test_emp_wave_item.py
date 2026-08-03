from ai.action import Action
import math

class MockBall:
    def __init__(self, id, team, x, y, ball_type="basic"):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.invert_timer = 0.0
        self.alive = True
        self.ball_type = ball_type

class MockWorld:
    def __init__(self):
        self.balls = []
        self.boosters = []
        self.arena = type('obj', (object,), {'hazards': []})
        self.events = []

def test_emp_wave_item_use():
    ball = MockBall(1, "teamA", 0, 0)
    enemy = MockBall(2, "teamB", 100, 0)
    far_enemy = MockBall(3, "teamB", 400, 0)
    world = MockWorld()
    world.balls = [ball, enemy, far_enemy]

    ball.inventory = ["emp_wave_item"]
    ball.use_item = True

    action = Action(ball, world)
    action.execute("attack", 0.016)

    assert enemy.invert_timer >= 3.0
    assert far_enemy.invert_timer == 0.0
    assert "emp_wave_item" not in ball.inventory
    assert not ball.use_item

    # Verify the event was added
    has_event = False
    for ev in world.events:
        if ev.get("type") == "emp_wave" and ev["data"]["radius"] == 300.0:
            has_event = True
    assert has_event, "emp_wave event not spawned"
