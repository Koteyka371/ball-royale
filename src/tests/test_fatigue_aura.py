from ai.game_modes import FatigueAuraMode

class MockBall:
    def __init__(self, x=0, y=0, radius=20.0, stamina=100.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.stamina = stamina

def test_fatigue_aura_stamina_drain():
    mode = FatigueAuraMode()
    # Force position and radius
    mode.aura_x = 750.0
    mode.aura_y = 500.0
    mode.aura_radius = 200.0
    mode.drain_rate = 30.0

    b1 = MockBall(x=750, y=500, stamina=100.0) # Inside aura
    b2 = MockBall(x=100, y=100, stamina=100.0) # Outside aura

    # Override angle/speed to keep it at fixed spot for one tick
    mode.aura_angle = 0.0
    mode.aura_speed = 0.0
    mode.orbit_radius = 250.0

    # Actually wait, mode tick overwrites aura_x/aura_y based on orbit_radius and angle.
    # So if aura_angle=0, orbit_radius=250, aura_x = 500 + 250 = 750, aura_y = 500

    mode.tick(None, [b1, b2], delta=1.0)

    assert abs(b1.stamina - 70.0) < 0.1, f"Expected 70.0, got {b1.stamina}"
    assert b2.stamina == 100.0, f"Expected 100.0, got {b2.stamina}"
