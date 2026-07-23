import pytest
from ai.action import AIAction
from arena.procedural_arena import Hazard

class MockWorld:
    def __init__(self):
        self.tick = 0
        self.arena = MockArena()
        self.boosters = []
        self.events = []
        self.balls = []

class MockArena:
    def __init__(self):
        self.hazards = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0
        self.inventory = []
        self.hp = 100.0
        self.max_hp = 100.0
        self.anchor_trap_timer = 0.0
        self.alive = True
        self.team = id

def test_shockwave_mine_deployment():
    world = MockWorld()
    ball = MockBall(1, 100.0, 100.0)
    ball.inventory = ["deployable_shockwave_mine"]
    world.balls.append(ball)

    enemy = MockBall(2, 200.0, 200.0) # distance is approx 141 < 300
    world.balls.append(enemy)

    action = AIAction(world, ball)
    # Using 'flee' strategy directly in execute
    ball.strategy = "flee"

    # We patch _get_nearest_enemy to return the enemy for simplicity or rely on execute
    action._get_nearest_enemy = lambda: enemy

    # Just run the inventory check logic block manually, or we can mock out delta and call execute
    # Actually, execute calls too many things that might break with incomplete mocks.
    # We can invoke execute but it might need more mocks. Let's provide a minimal mock.
    ball.vx = 0
    ball.vy = 0
    ball.target_x = 0
    ball.target_y = 0
    ball.dash_cooldown_timer = 0

    # Run the deployment logic segment directly or the whole execute if safe.
    # The deploy logic is inside execute() -> strategy check. Let's try calling execute.
    try:
        action.execute(0.1)
    except Exception as e:
        pass # Ignore exceptions from later in execute, we only care if the trap deployed

    assert "deployable_shockwave_mine" not in ball.inventory
    mines = [h for h in world.arena.hazards if getattr(h, "kind", "") == "shockwave_mine"]
    assert len(mines) == 1
    assert getattr(mines[0], "owner_id") == 1
    assert mines[0].x == 100.0
    assert mines[0].y == 100.0


def test_shockwave_mine_trigger():
    world = MockWorld()

    # Owner
    owner = MockBall(1, 100.0, 100.0)
    world.balls.append(owner)

    # Enemy, near the mine
    enemy = MockBall(2, 110.0, 100.0)
    world.balls.append(enemy)

    mine = Hazard("mine_1", 100.0, 100.0, 60.0, "shockwave_mine", 0.0)
    mine.duration = 30.0
    mine.owner_id = 1
    world.arena.hazards.append(mine)

    # Action for enemy, which will evaluate hazard interactions
    action = AIAction(world, enemy)
    action.execute(0.1)

    # Check assertions
    assert mine.duration == 0.0 # Mine is destroyed
    assert enemy.hp == 95.0 # took 5.0 damage
    assert enemy.anchor_trap_timer == 1.5 # movement disabled
    assert enemy.vx > 0.0 # pushed away to the right (x=110 vs x=100)

    # Also check if explosion event was emitted
    explosions = [e for e in world.events if getattr(e, "get", lambda x: None)("type") == "visual_effect" and getattr(e, "get", lambda x: {})("data").get("type") == "explosion"]
    assert len(explosions) > 0
