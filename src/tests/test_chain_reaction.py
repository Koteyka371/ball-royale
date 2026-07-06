import pytest
from ai.action import Action

class MockBall:
    def __init__(self, id=1, x=0, y=0):
        self.id = id
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.team = "player"
        self.ball_type = "basic"
        self.speed = 100
        self.base_speed = 100
        self.radius = 15.0
        self.skill = None
        self.active_skill = None
        self.damage = 10

class MockHazard:
    def __init__(self, id=100, x=50, y=50, variant="normal"):
        self.id = id
        self.kind = "trap"
        self.trap_variant = variant
        self.owner_id = 999
        self.x = x
        self.y = y
        self.radius = 15.0
        self.damage = 30.0
        self.duration = 5.0
        self.active = True

class MockArena:
    def __init__(self):
        self.hazards = []
        self.width = 1000
        self.height = 1000
    def clamp_position(self, x, y, radius):
        return x, y, False
    def update_zone(self, tick, delta):
        pass

class MockWorld:
    def __init__(self):
        self.balls = []
        self.arena = MockArena()
        self.tick = 0
        self.next_id = 9999
        self.events = []

    def _deal_damage(self, source, target):
        damage = getattr(source, "damage", 10.0)
        target.hp -= damage
        if target.hp <= 0:
            target.alive = False

    def add_event(self, type, data):
        self.events.append((type, data))

def test_chain_reaction_traps():
    ball = MockBall(id=1, x=50, y=50) # on top of trap 1
    enemy1 = MockBall(id=2, x=70, y=50) # within AoE of trap 2
    enemy2 = MockBall(id=3, x=150, y=50) # within AoE of trap 3
    far_enemy = MockBall(id=4, x=500, y=500) # Safe from explosions

    world = MockWorld()
    world.balls.extend([ball, enemy1, enemy2, far_enemy])

    trap1 = MockHazard(id=1, x=50, y=50, variant="chain_reaction")
    trap2 = MockHazard(id=2, x=70, y=50, variant="chain_reaction") # within 150 range of trap 1
    trap3 = MockHazard(id=3, x=150, y=50, variant="chain_reaction") # within 150 range of trap 2
    far_trap = MockHazard(id=4, x=500, y=500, variant="chain_reaction") # Out of range of all

    world.arena.hazards.extend([trap1, trap2, trap3, far_trap])

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Assert domino effect
    assert trap1.duration == 0.0 # Triggered
    assert trap2.duration == 0.0 # Triggered by chain reaction
    assert trap3.duration == 0.0 # Triggered by trap 2 chain reaction

    assert far_trap.duration > 4.5 # Unaffected

    # Assert AoE damage
    assert ball.hp == 10.0 # Damaged by trap 1 and trap 2 (70.0 actually wait, trap 1 and 2 and 3 overlap? ball is at 50. Trap1 is 50 -> dist 0. Trap2 is 70 -> dist 20. Trap3 is 150 -> dist 100 (exactly edge, actually < 100 * 100 is False since 10000 < 10000 is False, so trap3 doesn't hit). So ball takes 30 + 30 = 60 dmg. hp = 40.


    assert enemy1.hp == -20.0 # Enemy1 at 70. Hits trap1(dist 20) -> 30dmg. Hits trap2(dist 0) -> 30dmg. Hits trap3(dist 80) -> 30dmg. Total 90 dmg. HP = 10.

    assert far_enemy.hp == 100.0 # Unharmed

if __name__ == "__main__":
    pytest.main(["-v", "src/tests/test_chain_reaction.py"])
