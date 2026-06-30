import math
from dataclasses import dataclass
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.arena = None
        self.balls = []

    def _deal_damage(self, attacker, target):
        if hasattr(target, "hp"):
            target.hp -= getattr(attacker, "damage", 10.0)

@dataclass
class MockHazard:
    id: int
    x: float
    y: float
    radius: float
    kind: str
    damage: float
    hp: float = 100.0
    active: bool = True

class MockBall:
    def __init__(self, id, x, y, hp=100.0, team="", ball_type="basic"):
        self.id = id
        self.x = x
        self.y = y
        self.hp = hp
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.chain_lightning_timer = 5.0
        self.damage = 10.0
        self.ricochet_barrier_timer = 0.0
        self.reflect_shield_active = False

def test_chain_bounce_logic():
    world = MockWorld()
    world.balls = [
        MockBall(1, 0, 0, team="A"),
        MockBall(2, 50, 0, team="B"),
        MockBall(3, 100, 0, team="B"),
    ]
    world.arena = type('Arena', (), {'hazards': [MockHazard(1, 150, 0, 20.0, "breakable_wall", 0.0)]})()

    attacker = world.balls[0]
    target = world.balls[1]

    action = Action(attacker, world)
    action._get_enemies = lambda: [b for b in world.balls if b.team != attacker.team]
    action._spawn_particles = lambda x,y,k: None
    action._spawn_skill_particles = lambda k: None

    action._attempt_damage(attacker, target)

    # Original damage 10.
    # Target takes normal attack -> 10. Target hp = 90
    # Chain jumps to ball 3 (distance 50). Chain damage = 15. Ball 3 hp = 85.
    # Chain jumps to hazard (distance 50 from ball 3). Chain damage = 22.5. Hazard hp = 77.5

    assert world.balls[1].hp == 90.0
    assert world.balls[2].hp == 85.0
    assert world.arena.hazards[0].hp == 77.5
