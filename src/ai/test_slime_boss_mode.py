import pytest

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.next_id = 999
        self.events = []
        self.mutators_active = False

    def add_event(self, event_type, data):
        self.events.append((event_type, data))

class MockBall:
    def __init__(self, x=0, y=0, team="hunter"):
        self.id = 1
        self.x = x
        self.y = y
        self.team = team
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.radius = 15
        self.speed = 100
        self.damage = 10

def test_slime_boss_mode_spawn():
    try:
        from ai.game_modes import SlimeBossMode
    except ImportError:
        import sys
        sys.path.append('src')
        from ai.game_modes import SlimeBossMode

    mode = SlimeBossMode()
    world = MockWorld()
    balls = [MockBall()]

    mode.setup(world, balls)

    # Check if boss was added
    bosses = [b for b in balls if getattr(b, "is_slime_boss", False)]
    assert len(bosses) == 1
    boss = bosses[0]

    assert boss.team == "boss"
    assert boss.max_hp == 3000.0
    assert getattr(boss, "slime_trail_timer", -1) != -1

    # Store ID
    assert mode.boss_id == boss.id

def test_slime_boss_trail():
    try:
        from ai.game_modes import SlimeBossMode
    except ImportError:
        import sys
        sys.path.append('src')
        from ai.game_modes import SlimeBossMode

    mode = SlimeBossMode()
    world = MockWorld()
    hunter = MockBall(100, 100)
    balls = [hunter]

    mode.setup(world, balls)
    boss = next((b for b in balls if b.team == "boss"), None)

    # Move time forward by 0.3s so timer triggers
    boss.slime_trail_timer = 0.0
    mode.tick(world, balls, 0.3)

    # Check if a slime hazard was created
    slime_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "slime"]
    assert len(slime_hazards) > 0
    assert slime_hazards[0].radius == 25.0

def test_slime_boss_shoot():
    try:
        from ai.game_modes import SlimeBossMode
    except ImportError:
        import sys
        sys.path.append('src')
        from ai.game_modes import SlimeBossMode

    mode = SlimeBossMode()
    world = MockWorld()
    hunter = MockBall(100, 100)
    balls = [hunter]

    mode.setup(world, balls)
    boss = next((b for b in balls if b.team == "boss"), None)
    boss.x = 200
    boss.y = 200

    # Trigger shoot
    boss.slime_shoot_timer = 0.0
    mode.tick(world, balls, 0.1)

    # Check if projectile was created
    projectiles = [h for h in world.arena.hazards if getattr(h, "kind", "") == "slime_projectile"]
    assert len(projectiles) == 1
    proj = projectiles[0]
    assert hasattr(proj, "vx")
    assert hasattr(proj, "vy")

def test_slime_boss_split():
    try:
        from ai.game_modes import SlimeBossMode
    except ImportError:
        import sys
        sys.path.append('src')
        from ai.game_modes import SlimeBossMode

    mode = SlimeBossMode()
    world = MockWorld()
    balls = []

    mode.setup(world, balls)
    boss = next((b for b in balls if b.team == "boss"), None)

    # Kill boss
    boss.hp = 0
    mode.tick(world, balls, 0.1)

    # Boss should be removed, and 2 minions should spawn
    assert boss not in balls
    minions = [b for b in balls if getattr(b, "is_slime_minion", False)]
    assert len(minions) == 2

    for m in minions:
        assert m.max_hp == boss.max_hp * 0.4
        assert m.speed == boss.speed * 1.5
        assert m.team == "boss"
