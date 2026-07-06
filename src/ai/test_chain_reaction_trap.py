import pytest
from ai.action import Action

class MockHazard:
    def __init__(self, id, x, y, kind="chain_reaction_trap", radius=20.0, owner_id=0, last_updated_tick=1):
        self.id = id
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = radius
        self.owner_id = owner_id
        self.duration = 10.0
        self.damage = 25.0
        self.last_updated_tick = 1

class MockBall:
    def __init__(self, id, x, y, radius=10.0, team="red"):
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.team = team
        self.alive = True
        self.hp = 100
        self.max_hp = 100
        self.speed = 100
        self.vx = 0
        self.vy = 0
        self.ball_type = "test_ball"
        self.is_flying = False
        self.current_action = None
        self.perception_radius = 250
        self.skill_timer = 0
        self.skill_cooldown = 0
        self.used_skill_count = 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.events = []
        self.arena = type("Arena", (), {"hazards": [], "width": 1000, "height": 1000, "update_zone": lambda *args: None, "clamp_position": lambda *args: (0, 0, False)})()
        self.tick = 0
        self.time = 0.0

    def add_event(self, type, data):
        pass

def test_chain_reaction_trigger_and_propagation():
    world = MockWorld()

    # Ball to trigger trap
    ball1 = MockBall(id=1, x=50, y=50, team="blue")
    ball1.vx = 10
    ball1.vy = 10
    world.balls.append(ball1)

    # Enemy ball near secondary trap
    ball2 = MockBall(id=2, x=155, y=155, team="blue")
    world.balls.append(ball2)

    # Enemy ball outside of any explosion radius
    ball3 = MockBall(id=3, x=500, y=500, team="blue")
    world.balls.append(ball3)

    # Trap triggered by ball1
    trap1 = MockHazard(id=101, x=50, y=50, kind="chain_reaction_trap", owner_id=99)
    world.arena.hazards.append(trap1)

    # Nearby trap (should explode from trap1)
    trap2 = MockHazard(id=102, x=150, y=150, kind="chain_reaction_trap", owner_id=99)
    world.arena.hazards.append(trap2)

    # Another trap further away (should explode from trap2)
    trap3 = MockHazard(id=103, x=220, y=220, kind="chain_reaction_trap", owner_id=99)
    world.arena.hazards.append(trap3)

    # Trap outside of chain reaction range
    trap_far = MockHazard(id=104, x=500, y=500, kind="chain_reaction_trap", owner_id=99)
    world.arena.hazards.append(trap_far)

    action = Action(ball1, world)

    # The actual physics processing
    if True:
        action.execute("idle", 0.1)

    # Verify trap durations (exploded vs not exploded)
    assert trap1.duration == 0.0, "Triggered trap should be destroyed"
    assert trap2.duration == 0.0, "Nearby trap should chain react"
    assert trap3.duration == 0.0, "Secondary nearby trap should chain react"
    assert trap_far.duration > 0.0, "Distant trap should not chain react"

    # Verify ball damage
    assert ball1.hp == 75.0 or ball1.hp == 72.5, "Trigger ball should take explosion damage from trap 1"
    assert ball2.hp == 75.0, "Nearby ball should take explosion damage from trap 2"
    assert ball3.hp == 100, "Distant ball should take no damage"

    # Verify events
    explosion_events = [e for e in world.events if getattr(e, 'type', e[1].get('type') if isinstance(e, tuple) else '') == 'explosion']
    assert len(explosion_events) == 3, "Should spawn exactly 3 explosion visual effects"

def test_chain_reaction_owner_immunity():
    world = MockWorld()

    owner = MockBall(id=99, x=50, y=50, team="red")
    owner.vx = 10
    owner.vy = 10
    world.balls.append(owner)

    enemy = MockBall(id=1, x=50, y=50, team="blue")
    world.balls.append(enemy)

    trap = MockHazard(id=101, x=50, y=50, kind="chain_reaction_trap", owner_id=99)
    world.arena.hazards.append(trap)

    action = Action(enemy, world)

    if True:
        action.execute("idle", 0.1)

    assert trap.duration == 0.0, "Trap should be triggered by enemy"
    assert owner.hp == 100, "Owner should not take damage from their own trap"
    assert enemy.hp == 75.0 or enemy.hp == 72.5, "Enemy should take damage"
