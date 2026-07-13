import pytest
from ai.game_modes import BlacksmithBossMode
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.boosters = []
        self.events = []
        self.mode = None

    def add_event(self, type, data):
        self.events.append({"type": type, **data})

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockHazard:
    def __init__(self, kind):
        self.id = 100
        self.x = 500
        self.y = 500
        self.radius = 15.0
        self.kind = kind
        self.damage = 0.0

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 500
        self.y = 500
        self.radius = 10.0
        self.damage = 10.0
        self.speed = 100.0
        self.alive = True

def test_blacksmith_boss_spawn():
    world = MockWorld()
    mode = BlacksmithBossMode()
    world.mode = mode

    # 1. Setup mode
    mode.setup(world, [])

    # 2. First tick spawns anvil pieces
    mode.tick(world, [])
    assert mode.anvil_pieces_spawned

    anvil_pieces = [h for h in world.arena.hazards if h.kind == "anvil_piece"]
    assert len(anvil_pieces) == 3

    # 3. Simulate collecting anvil pieces
    ball = MockBall()
    action = Action(ball, world)

    # Collect all three pieces
    for i in range(3):
        piece = anvil_pieces[i]
        piece.active = True
        piece.x, piece.y = 500, 500
        action._collect_booster(0.1)

    assert mode.anvil_pieces_collected == 3

    # 4. Next tick summons boss
    mode.tick(world, [])
    assert mode.boss_spawned

    bosses = [b for b in world.balls if getattr(b, "ball_type", "") == "blacksmith"]
    assert len(bosses) == 1
    boss = bosses[0]

    assert boss.team == "boss"
    assert boss.max_hp == 2000.0

def test_blacksmith_boss_loot():
    world = MockWorld()
    mode = BlacksmithBossMode()
    world.mode = mode
    mode.setup(world, [])
    mode.anvil_pieces_spawned = True
    mode.anvil_pieces_collected = 3

    mode.tick(world, [])
    boss = next(b for b in world.balls if getattr(b, "ball_type", "") == "blacksmith")

    boss.alive = False

    mode.tick(world, [])

    assert boss._loot_dropped

    loot = [h for h in world.arena.hazards if getattr(h, "kind", "") == "legendary_loot"]
    assert len(loot) == 1

    # Simulate collecting loot
    ball = MockBall()
    world.balls = [ball]
    action = Action(ball, world)

    loot_item = loot[0]
    loot_item.active = True
    loot_item.x, loot_item.y = 500, 500
    action._collect_booster(0.1)

    assert "legendary_loot" in getattr(ball, "inventory", [])
    assert ball.damage == 30.0
    assert ball.speed == 150.0

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/test_blacksmith_boss.py"])
