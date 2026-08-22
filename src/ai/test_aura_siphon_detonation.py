from ai.game_modes import AuraPulseEventMode
import sys

def test_aura_siphon_detonation():
    class MockHazard:
        def __init__(self, kind, x, y, radius):
            self.kind = kind
            self.x = x
            self.y = y
            self.radius = radius
            self.owner_team = "team_a"
            self.accumulated_auras = 10.0
            self.duration = 10.0
            self.active = True

    class MockBall:
        def __init__(self, x, y, team, id):
            self.x = x
            self.y = y
            self.radius = 10.0
            self.team = team
            self.id = id
            self.alive = True
            self.is_decoy = False

    class MockArena:
        def __init__(self, hazards):
            self.hazards = hazards

    class MockWorld:
        def __init__(self, arena):
            self.arena = arena
            self.events = []

    trap = MockHazard("aura_siphon_trap", 100, 100, 60.0)
    bh = MockHazard("black_hole", 200, 200, 50.0)
    arena = MockArena([trap, bh])
    world = MockWorld(arena)

    # Friendly ball
    b1 = MockBall(10, 10, "team_a", 1)

    # Enemy ball caught in black hole
    b2 = MockBall(200, 200, "team_b", 2)
    b2.aura_booster_timer = 5.0 # Give some aura to trigger pulse

    balls = [b1, b2]

    mode = AuraPulseEventMode()
    mode.tick(world, balls, delta=15.0)

    assert trap.duration == 0.0
    assert not trap.active
    assert b1.aura_booster_timer == 10.0
    assert b1.vampiric_aura_timer == 10.0

    print("Python test passed.")
