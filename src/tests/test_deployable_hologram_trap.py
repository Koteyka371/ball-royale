import pytest
from ai.game_modes import GameMode
from ai.action import Action

class DummyBall:
    def __init__(self, id, x, y, team="red", ball_type="basic"):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.radius = 15.0
        self.hp = 100.0
        self.max_hp = 100.0
        self.damage = 10.0
        self.speed = 100.0
        self.vx = 0.0
        self.vy = 0.0
        self.mass = 1.0

class DummyHazard:
    def __init__(self, id, x, y, kind, radius=30.0, owner_team="blue"):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.owner_team = owner_team

class DummyArena:
    def __init__(self):
        self.hazards = []

class DummyWorld:
    def __init__(self):
        self.balls = []
        self.entities = []
        self.arena = DummyArena()
        self.events = []

    def add_event(self, event_type, data):
        self.events.append({'type': event_type, 'data': data})

    def _deal_damage(self, attacker, target, amount=None):
        if amount is not None and getattr(target, "alive", True) and not getattr(target, "is_hologram", False):
            if hasattr(target, "hp"):
                target.hp -= amount
                if target.hp <= 0:
                    target.alive = False
                    target.killer = attacker.id

def test_deployable_hologram_trap():
    world = DummyWorld()

    player = DummyBall(id=1, x=100.0, y=100.0, team="red")
    enemy = DummyBall(id=2, x=300.0, y=300.0, team="blue")
    world.balls = [player, enemy]
    world.entities = world.balls

    # Deploy trap by enemy team (blue)
    trap = DummyHazard(id=99, x=100.0, y=100.0, kind="deployable_hologram_trap", owner_team="blue")
    world.arena.hazards.append(trap)

    mode = GameMode()

    # Step 1: Player overlaps the trap, triggering it
    mode.tick(world, world.balls, delta=0.1)

    # Trigger mimic update
    player.vx = 50.0
    player.vy = -20.0
    mode.tick(world, world.balls, delta=0.1)

    holograms = [b for b in world.balls if getattr(b, "is_hologram", False) and getattr(b, "hologram_owner_id", None) == player.id]
    for h in holograms:
        assert h.vx == 50.0
        assert h.vy == -20.0


    # Trap should be destroyed, and 3 holograms should be spawned for the player
    assert len(world.arena.hazards) == 0

    holograms = [b for b in world.balls if getattr(b, "is_hologram", False) and getattr(b, "hologram_owner_id", None) == player.id]
    assert len(holograms) == 3

    for h in holograms:
        assert getattr(h, "damage", None) == 0.0
        assert getattr(h, "skill", None) is None
        assert getattr(h, "active_skill", None) is None
        assert getattr(h, "brain", None) is None

    # Step 2: Enemy attacks a hologram
    hologram = holograms[0]
    initial_hp = enemy.hp

    # Action._attempt_damage_internal triggers the logic when enemy attacks hologram
    action = Action(enemy, world)
    action._attempt_damage_internal(enemy, hologram)

    # Check enemy took minor feedback damage (5.0)
    assert enemy.hp == initial_hp - 5.0

    # Check enemy got slowed
    assert getattr(enemy, "speed_mult", 1.0) == 0.9

    # Check enemy revealed on minimap
    assert getattr(enemy, "minimap_ping_timer", 0.0) == 3.0

    minimap_events = [e for e in world.events if e.get('type') == 'minimap_ping']
    assert len(minimap_events) > 0
    assert minimap_events[0]['data']['x'] == enemy.x
