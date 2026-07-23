from ai.action import Action

class MockArena:
    def __init__(self, hazards):
        self.hazards = hazards
    def clamp_position(self, x, y, r):
        return x, y, False

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena([])
        self.boosters = []
        self.events = []
        self.game_mode = type('Mode', (), {'name': 'normal'})()
    def _deal_damage(self, attacker, victim):
        victim.hp -= attacker.damage

class MockHazard:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = 40.0
        self.owner_id = 1
        self.duration = 60.0

class MockBall:
    def __init__(self, id, team, x, y):
        self.id = id
        self.team = team
        self.x = x
        self.y = y
        self.alive = True
        self.hp = 100
        self.damage = 10.0
        self._base_speed_set = True
        self.base_speed = 100.0
        self.base_damage = 10.0
        self.speed_multiplier = 1.0
        self.damage_multiplier = 1.0
        self.inventory = []

def test_aura_amplifier_trap():
    world = MockWorld()
    owner = MockBall(1, "red", 0, 0)
    ally = MockBall(2, "red", 10, 10)
    enemy = MockBall(3, "blue", 10, 10)
    world.balls = [owner, ally, enemy]

    trap = MockHazard("aura_amplifier_trap", 5, 5)
    world.arena.hazards.append(trap)

    action = Action(enemy, world)
    action.execute("idle", 0.1)

    # Ally should get aura buff, enemy should take 15 damage
    assert getattr(ally, "aura_amplifier_timer", 0.0) == 10.0
    assert trap.duration == 0.0
    assert enemy.hp == 85

def test_aura_amplifier_aura_buff():
    world = MockWorld()
    b1 = MockBall(1, "red", 0, 0)
    world.balls = [b1]

    b1.aura_amplifier_timer = 5.0
    action = Action(b1, world)
    action._apply_friendly_aura(1.0)
    assert getattr(b1, "aura_amplifier_timer", 0.0) == 4.0
