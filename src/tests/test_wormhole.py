import math
from ai.action import Action
from ai.game_modes import GameMode
import arena.procedural_arena

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = []

class MockBall:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.radius = 15.0
        self.alive = True
        self.hp = 100
        self.inventory = []
        self.use_item = False
        self.team = id

def test_wormhole_item():
    arena = MockArena()
    owner = MockBall(1, 100, 100)
    owner.inventory.append("wormhole_item")
    owner.use_item = True

    enemy = MockBall(2, 300, 300)

    world = MockWorld(arena, [owner, enemy])
    action = Action(owner, world)

    action.execute("attack", 0.016)

    assert "wormhole_item" not in owner.inventory

    wormholes = [h for h in arena.hazards if getattr(h, "kind", "") == "wormhole"]
    assert len(wormholes) == 2, f"Expected 2 wormholes, found {len(wormholes)}"

    wh1, wh2 = wormholes[0], wormholes[1]

    # Tick loop to move the player through the wormhole
    gm = GameMode()

    # move owner to wh1
    owner.x = wh1.x
    owner.y = wh1.y

    # process tick
    gm.tick(world, [owner, enemy], 0.016)

    # player should teleport
    if isinstance(owner.x, (int, float)): assert abs(owner.x - wh1.linked_x) < 200.0
    assert owner.y == wh1.linked_y

if __name__ == "__main__":
    test_wormhole_item()
    print("Tests passed")
