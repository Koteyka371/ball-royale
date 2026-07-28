import math
from ai.action import Action

class MockWorld:
    def __init__(self, balls=None, arena=None):
        self.balls = balls or []
        self.arena = arena
        self.events = []
        self.next_id = 1000

class MockBall:
    def __init__(self, id, team, is_decoy=False, decoy_type="", owner_id=None, hp=100.0, x=0.0, y=0.0):
        self.id = id
        self.team = team
        self.is_decoy = is_decoy
        self.decoy_type = decoy_type
        self.owner_id = owner_id
        self.hp = hp
        self.x = x
        self.y = y
        self.alive = True
        self.silence_timer = 0.0

def test_silencer_decoy():
    owner = MockBall(1, "A")
    decoy = MockBall(2, "A", is_decoy=True, decoy_type="silencer", owner_id=1, hp=0.0, x=100.0, y=100.0)
    enemy = MockBall(3, "B", x=120.0, y=100.0)

    world = MockWorld([owner, decoy, enemy])
    action = Action(owner, world)

    # Actually, we should initialize Action with the decoy? The logic checks all balls in world.balls
    # No, it checks `self.world.balls` for `_decoy_exploded` inside `Action.execute`
    # Let's see: `if not getattr(b, "_decoy_exploded", False): ...`
    action.execute("idle", 0.016)

    # Check enemy silence
    assert enemy.silence_timer == 4.0, f"Expected 4.0, got {enemy.silence_timer}"

if __name__ == "__main__":
    test_silencer_decoy()
