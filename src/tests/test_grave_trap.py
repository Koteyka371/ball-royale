from ai.game_modes import GameMode
from ai.test_action_advanced import MockBall, MockWorld

def test_grave_trap_spawn():
    mode = GameMode()
    world = MockWorld()

    # Needs arena hazards to append to
    class MockArena:
        def __init__(self):
            self.hazards = []

    world.arena = MockArena()

    necro = MockBall()
    necro.ball_type = "necromancer"
    necro.id = 1
    necro.x = 100.0
    necro.y = 100.0
    necro.team = "evil"

    world.balls = [necro]

    mode.on_ball_died(world, necro, killer=None)

    assert len(world.arena.hazards) == 1
    trap = world.arena.hazards[0]

    assert trap.kind == "grave_trap"
    assert trap.x == 100.0
    assert trap.y == 100.0
    assert trap.duration == -1.0
    assert getattr(trap, "owner_team", "") == "evil"

def test_grave_trap_explode_and_bone_fragment_tick():
    mode = GameMode()
    world = MockWorld()

    class MockArena:
        def __init__(self):
            self.hazards = []

    world.arena = MockArena()

    class MockHazard:
        def __init__(self, x, y, radius, kind):
            self.x = x
            self.y = y
            self.radius = radius
            self.kind = kind
            self.owner_team = "evil"

    trap = MockHazard(100, 100, 30.0, "grave_trap")
    world.arena.hazards.append(trap)

    enemy = MockBall()
    enemy.id = 2
    enemy.x = 110.0
    enemy.y = 110.0
    enemy.radius = 15.0
    enemy.team = "good"
    enemy.alive = True

    balls = [enemy]

    # 1. Tick should explode the trap and spawn 6 bone fragments
    mode.tick(world, balls, 0.1)

    # Trap should be removed, and 6 bone fragments spawned
    assert trap not in world.arena.hazards
    assert len(world.arena.hazards) == 6
    for h in world.arena.hazards:
        assert h.kind == "bone_fragment"
        assert h.damage == 30.0

    # 2. Tick again so the bone fragment hits the enemy (it spawned at 100,100 which is within 110,110 distance (sqrt(200) ~ 14 < 30)
    mode.tick(world, balls, 0.1)

    # The first bone fragment that checks collision should hit
    assert enemy.hp <= 70.0 # Started at 100, took 30 dmg
    assert enemy.speed <= 50.0 # Slowed
    assert getattr(enemy, "slow_timer", 0.0) == 3.0

    # And that fragment should be removed
    assert len(world.arena.hazards) <= 5
