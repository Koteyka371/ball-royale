import pytest
from src.ai.action import Action

class MockArena:
    def __init__(self):
        self.hazards = []

class MockWorld:
    def __init__(self):
        self.arena = MockArena()
        self.balls = []
        self.tick = 0
        self.game_mode = None

    def _deal_damage(self, attacker, target):
        pass

class MockBall:
    def __init__(self, id, x, y, team="team1", is_decoy=False, hp=100.0, alive=True):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.is_decoy = is_decoy
        self.decoy_timer = 5.0
        self.hp = hp
        self.max_hp = 100.0
        self.alive = alive
        self.speed = 2.0
        self.stutter_timer = 0.0
        self.damage = 10.0
        self.vx = 0.0
        self.vy = 0.0

class MockBallVolatile(MockBall):
    def __init__(self, id, x, y, team="team1", is_decoy=False, hp=100.0, alive=True):
        super().__init__(id, x, y, team, is_decoy, hp, alive)
        self.traits = ["volatile_decoy"]

def test_decoy_explosion_volatile():
    world = MockWorld()
    decoy = MockBallVolatile(1, 0, 0, team="tricksters", is_decoy=True, hp=10.0)
    enemy = MockBall(2, 50, 0, team="enemies", hp=100.0) # within 100
    far_enemy = MockBall(3, 140, 0, team="enemies", hp=100.0) # between 100 and 150
    too_far_enemy = MockBall(4, 200, 0, team="enemies", hp=100.0) # > 150
    ally = MockBall(5, 50, 50, team="tricksters", hp=100.0)

    world.balls = [decoy, enemy, far_enemy, too_far_enemy, ally]
    action = Action(decoy, world)

    decoy.decoy_timer = 0.0
    action.execute("idle", 0.1)

    assert decoy.alive == False
    assert getattr(decoy, "_decoy_exploded", False) == True

    # Enemies in range take 80 damage
    assert enemy.hp == 20.0 # 100 - 80
    assert far_enemy.hp == 20.0 # 100 - 80
    assert too_far_enemy.hp == 100.0 # Unaffected
    assert ally.hp == 100.0

def test_decoy_explosion():
    world = MockWorld()
    decoy = MockBall(1, 0, 0, team="tricksters", is_decoy=True, hp=10.0)
    enemy = MockBall(2, 50, 0, team="enemies", hp=100.0)
    far_enemy = MockBall(3, 200, 0, team="enemies", hp=100.0)
    ally = MockBall(4, 50, 50, team="tricksters", hp=100.0)

    world.balls = [decoy, enemy, far_enemy, ally]

    action = Action(decoy, world)

    # Decoy expires
    decoy.decoy_timer = 0.0
    action.execute("idle", 0.1)

    assert decoy.alive == False
    assert getattr(decoy, "_decoy_exploded", False) == True

    # Enemy close enough, should take damage and stutter
    assert enemy.hp == 70.0 # 100 - 30
    assert enemy.stutter_timer == 2.0

    # Far enemy out of range
    assert far_enemy.hp == 100.0
    assert far_enemy.stutter_timer == 0.0

    # Ally should not be affected
    assert ally.hp == 100.0
    assert ally.stutter_timer == 0.0

if __name__ == "__main__":
    test_decoy_explosion()
    test_decoy_explosion_volatile()
    print("Test passed!")
