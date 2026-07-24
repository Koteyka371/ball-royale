from ai.action import Action
from ai.game_modes import GameMode

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = MockArena()

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
        self.is_sandstorming = False

class MockBall:
    def __init__(self, id, team="A"):
        self.id = id
        self.team = team
        self.x = 500
        self.y = 500
        self.radius = 10
        self.hp = 100
        self.max_hp = 100
        self.is_decoy = False
        self.alive = True
        self.speed = 10.0
        self.vx = 0.0
        self.vy = 0.0
        self.is_intangible = False
        self.bounces_left = 0
        self.skill_timer = 0.0
        self.silence_timer = 0.0
        self.intangible = False
        self.intangible_timer = 0.0
        self.anchor_trap_timer = 0.0
        self.use_skill = lambda: None
        self.decoy_type = ""
        self.decoy_timer = 0.0
        self.active_skill = None
        self.state_history = []
        self.invert_timer = 0.0

def test_decoy_element_explosion():
    world = MockWorld()

    enemy = MockBall(1, "B")
    enemy.x = 510
    enemy.y = 510

    decoy = MockBall(2, "A")
    decoy.is_decoy = True
    decoy.decoy_type = "explosive"
    decoy.element = "fire"
    decoy.hp = 0
    decoy.decoy_timer = 1.0

    world.balls.extend([enemy, decoy])

    action = Action(decoy, world)
    action.execute("idle", 0.016)

    assert getattr(enemy, "burn_timer", 0) > 0, "Enemy should have a burn timer from fire decoy"
    print("test_decoy_element_explosion passed")

def test_decoy_element_spawn():
    world = MockWorld()
    caster = MockBall(1, "A")
    caster.active_skill = "throw_decoy"
    world.balls.append(caster)

    action = Action(caster, world)

    import random
    original_random = random.random
    random.random = lambda: 0.1

    try:
        action._use_skill()
    finally:
        random.random = original_random

    decoys = [b for b in world.balls if getattr(b, "is_decoy", False) and b.id != 1]
    assert len(decoys) > 0
    decoy = decoys[0]

    assert getattr(decoy, "element", None) in ["fire", "ice", "lightning"], "Decoy should have been assigned an element"
    print("test_decoy_element_spawn passed")

if __name__ == "__main__":
    test_decoy_element_explosion()
    test_decoy_element_spawn()
