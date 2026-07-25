
from src.ai.game_modes import GameMode
from src.ai.action import Action

class MockWorld:
    def __init__(self):
        self.events = []
        self.arena = type('Arena', (object,), {"hazards": []})()

class MockBall:
    def __init__(self):
        self.id = 1
        self.x = 0.0
        self.y = 0.0
        self.hp = 100.0
        self.traits = ["quantum_echo"]
        self.alive = True
        self.team = "team_1"
        self.ball_type = "base"
        self.skill = "quantum_echo"
        self.active_skill = "quantum_echo"
        self.skill_timer = 0.0
        self.radius = 10.0
        self.is_intangible = False
        self.speed = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.bounces_left = 0
        self.max_hp = 100.0

def test_quantum_echo():
    world = MockWorld()
    b = MockBall()
    mode = GameMode()

    # 1. First tick (delta 3.0), leaves a ghost
    mode.apply_dynamic_traits(world, [b], 3.0)
    assert hasattr(b, "quantum_ghosts")
    assert len(b.quantum_ghosts) == 1
    assert b.quantum_ghosts[0]["x"] == 0.0

    # Check event
    assert len(world.events) == 1
    assert world.events[0]["type"] == "quantum_echo_ghost"

    # 2. Move ball and tick again
    b.x = 50.0
    b.y = 50.0
    b.hp = 80.0
    mode.apply_dynamic_traits(world, [b], 3.0)
    assert len(b.quantum_ghosts) == 2
    assert b.quantum_ghosts[0]["x"] == 50.0 # newest ghost at 50,50
    assert b.quantum_ghosts[0]["hp"] == 80.0

    # Move ball again
    b.x = 100.0
    b.y = 100.0
    b.hp = 20.0

    # Execute teleport manually (what Action does)
    world.events = []
    ghosts = getattr(b, "quantum_ghosts", [])
    if ghosts:
        most_recent = ghosts.pop(0)
        b.x = most_recent["x"]
        b.y = most_recent["y"]
        b.hp = most_recent["hp"]
        world.events.append({"type": "quantum_echo_teleport", "id": b.id})

    assert b.x == 50.0
    assert b.y == 50.0
    assert b.hp == 80.0
    assert len(b.quantum_ghosts) == 1

if __name__ == "__main__":
    test_quantum_echo()
    print("Tests passed")
