import pytest
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []
        self.rooms = []
        self.danger_grid = {}
        self.safe_zone_radius = float('inf')
        self.safe_zone_center = (500, 500)
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.next_id = 1000
        self.tick = 1

    def get_nearby_entities(self, ball, radius):
        return []

    def _deal_damage(self, attacker, target):
        pass

class MockBall:
    def __init__(self, id_val, x, y):
        self.id = id_val
        self.x = x
        self.y = y
        self.hp = 100.0
        self.max_hp = 100.0
        self.alive = True
        self.team = "team1"
        self.ball_type = "normal"
        self.speed = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 10.0

class MockHazard:
    def __init__(self, x, y, kind, trap_variant=None):
        self.id = 1
        self.x = x
        self.y = y
        self.radius = 15.0
        self.kind = kind
        self.duration = 5.0
        self.damage = 10.0
        self.last_updated_tick = 0
        if trap_variant:
            self.trap_variant = trap_variant

def test_hologram_trap_spawns_hologram_and_explodes():
    world = MockWorld()
    owner = MockBall(1, 100, 100)
    enemy = MockBall(2, 105, 105)
    enemy.team = "team2"

    world.balls.append(owner)
    world.balls.append(enemy)

    trap = MockHazard(100, 100, "trap", "hologram")
    trap.owner_id = owner.id
    world.arena.hazards.append(trap)

    action = Action(owner, world)
    action.execute("idle", 0.1)

    # After first tick, hologram should be spawned and trap duration set to 0
    assert trap.duration == 0.0

    # Find hologram
    holograms = [b for b in world.balls if getattr(b, "is_hologram", False)]
    assert len(holograms) == 1
    hologram = holograms[0]
    assert hologram.hp == 10.0
    assert hologram.hologram_timer == 10.0
    assert hologram.id != owner.id

    # Simulate hologram exploding (timer expiring)
    hologram.hologram_timer = 0.0
    action2 = Action(hologram, world)
    action2.execute("idle", 0.1)

    # Hologram should be dead, and enemy should take 15 damage
    assert not hologram.alive
    assert enemy.hp == 100.0 - 15.0
    assert getattr(enemy, "is_stunned", False)
    assert getattr(enemy, "stun_timer", 0.0) == 2.0
    assert getattr(enemy, "is_confused", False)
    assert getattr(enemy, "confusion_timer", 0.0) == 3.0
