from ai.game_modes import BattleRoyaleMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.dead_balls = []
        self.events = []

    def add_event(self, type, data):
        self.events.append((type, data))

def test_tornado_spawn():
    world = MockWorld()
    mode = BattleRoyaleMode()
    mode.setup(world, [])

    for _ in range(int(20.5 / 0.016)):
        mode.tick(world, [], delta=0.016)

    tornados = [h for h in world.arena.hazards if getattr(h, "kind", "") == "tornado"]
    assert len(tornados) == 1, f"Expected 1 tornado, got {len(tornados)}"

    t = tornados[0]
    assert hasattr(t, "vx") and hasattr(t, "vy")

    # test bounce
    t.x = 10
    t.vx = -100
    t.radius = 50
    mode.tick(world, [], delta=0.1)

    # After tick, our injected logic does h.x += h.vx * delta -> 10 + -10 = 0
    # bounce check: if 0 - 50 < 0 -> h.x = 50, h.vx = 100
    assert t.vx > 0

    print("Test passed!")

if __name__ == '__main__':
    test_tornado_spawn()
