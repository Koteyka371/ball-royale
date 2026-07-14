import math
from ai.action import Action

class MockHazard:
    def __init__(self, kind):
        self.kind = kind
        self.trap_variant = "link"
        self.duration = 10.0
        self.x = 200
        self.y = 200
        self.radius = 20
        self.damage = 0
        self.active = True
        self.id = 1
        self.owner_id = 1

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
        self.width = 1000
        self.height = 1000
    def update_zone(self, tick, delta=None):
        pass
    def clamp_position(self, x, y, radius=0):
        nx = max(radius, min(1000 - radius, x))
        ny = max(radius, min(1000 - radius, y))
        return (nx, ny, x != nx or y != ny)

class MockEventList(list):
    def append(self, event):
        super().append(event)

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = MockEventList()
        self.tick = 123
        self.time = 0
        self.next_id = 9999

    def get_nearby_entities(self, ball, radius):
        return {'enemies': [b for b in self.balls if b != ball], 'allies': []}

    def _deal_damage(self, hazard, ball):
        pass

class MockBall:
    def __init__(self, id, x, y, hp, team):
        self.id = id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = hp
        self.max_hp = hp
        self.alive = True
        self.radius = 10
        self.team = team
        self.ball_type = "basic"
        self.speed_multiplier = 1.0

def test_link_trap():
    trap = MockHazard("trap")
    trap.trap_variant = "link"
    trap.owner_id = 2

    arena = MockArena([trap])
    triggerer = MockBall(1, 200, 200, 100, 1)
    enemy = MockBall(2, 500, 500, 100, 2)
    triggerer.team = 1
    enemy.team = 2
    world = MockWorld(arena, [triggerer, enemy])
    action = Action(triggerer, world)

    # Run once to trigger the trap.
    action.execute("none", 0.1)

    # Check if target linked
    assert getattr(triggerer, "trap_link_target", None) == enemy
    assert getattr(triggerer, "trap_link_timer", 0.0) == 10.0

    # Now simulate damage on triggerer
    triggerer.hp -= 20.0  # taking 20 damage

    # Run action again to apply damage sync
    action.execute("none", 0.1)

    # Triggerer HP should be 80. Enemy HP should be 80.
    assert triggerer.hp == 80.0
    assert enemy.hp == 80.0

    # Run again with no damage, enemy HP shouldn't change
    action.execute("none", 0.1)
    assert triggerer.hp == 80.0
    assert enemy.hp == 80.0

    # Deal 10 more damage to triggerer
    triggerer.hp -= 10.0
    action.execute("none", 0.1)
    assert triggerer.hp == 70.0
    assert enemy.hp == 70.0
