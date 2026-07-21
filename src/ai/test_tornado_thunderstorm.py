from ai.game_modes import BattleRoyaleMode
import math

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

def test_tornado_roam_thunderstorm():
    world = MockWorld()
    mode = BattleRoyaleMode()
    mode.setup(world, [])

    # Spawn one normally
    mode.weather = "clear"
    for _ in range(int(20.5 / 0.016)):
        mode.tick(world, [], delta=0.016)

    tornados = [h for h in world.arena.hazards if getattr(h, "kind", "") == "tornado"]
    assert len(tornados) >= 1
    t = tornados[0]

    t.x = 500
    t.y = 500
    t.vx = 100
    t.vy = 0
    mode.tick(world, [], delta=0.1)
    # distance moved: 10
    dist1 = abs(t.x - 510)
    assert dist1 < 0.1

    # In thunderstorm
    mode.weather = "thunderstorm"
    t.x = 500
    t.y = 500
    t.vx = 100
    t.vy = 0
    mode.tick(world, [], delta=0.1)

    # distance moved: 10 * 1.5 = 15
    dist2 = abs(t.x - 515)
    assert dist2 < 0.1

    print("Test passed!")

if __name__ == '__main__':
    test_tornado_roam_thunderstorm()
