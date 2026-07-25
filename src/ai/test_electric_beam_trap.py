import math
from ai.action import Action

class MockHazard:
    def __init__(self, id, x, y, kind, team):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.team = team
        self.radius = 20.0
        self.damage = 0.0
        self.damage = 0.0
        self.active = True
        self.duration = 15.0

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
        self.stamina = 100.0

def test_electric_beam_trap_damage_and_stamina_drain():
    # Place two traps connected to each other
    trap1 = MockHazard("t1", 200, 200, "electric_beam_trap", 2)
    trap2 = MockHazard("t2", 400, 200, "electric_beam_trap", 2)

    arena = MockArena([trap1, trap2])

    # Victim sits exactly between them, intersecting the beam
    victim = MockBall(1, 300, 200, 100, 1)

    world = MockWorld(arena, [victim])
    action = Action(victim, world)

    initial_stamina = victim.stamina
    initial_hp = victim.hp

    # Simulate action tick
    action.execute("none", 1.0)

    # The beam should drain stamina and deal some hp damage
    # There are 2 traps checking the line between t1 and t2, so it might apply twice per tick, which is fine or can be 40 stamina per check.
    assert victim.stamina < initial_stamina, "Stamina should be drained by beam"
    assert victim.hp < initial_hp, "HP should be drained by beam"

def test_electric_beam_trap_node_direct_damage():
    trap1 = MockHazard("t1", 200, 200, "electric_beam_trap", 2)

    arena = MockArena([trap1])

    # Victim sits exactly on the node
    victim = MockBall(1, 200, 200, 100, 1)

    world = MockWorld(arena, [victim])
    action = Action(victim, world)

    initial_stamina = victim.stamina
    initial_hp = victim.hp

    action.execute("none", 1.0)

    # The node direct collision should drain stamina and deal hp damage
    assert victim.stamina < initial_stamina, "Stamina should be drained by node"
    assert victim.hp < initial_hp, "HP should be drained by node"
