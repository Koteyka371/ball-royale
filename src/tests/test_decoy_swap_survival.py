import pytest
from ai.decoy_swap_mode import DecoySwapSurvivalMode

class MockArena:
    def __init__(self):
        self.width = 1000
        self.height = 1000

class MockEventList(list):
    def append(self, event):
        pass

class MockWorld:
    def __init__(self, arena, balls):
        self.arena = arena
        self.balls = balls
        self.events = MockEventList()
        self.tick = 1
        self.time = 0
        self.next_id = 9999

    def add_event(self, type_name, data):
        self.events.append({'type': type_name, 'data': data})

class MockBall:
    def __init__(self, id, x, y, team, is_decoy=False, owner_id=None):
        self.id = id
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = team
        self.alive = True
        self.is_decoy = is_decoy
        self.owner_id = owner_id
        self.radius = 10
        self.speed = 100
        self.base_speed = 100
        self.damage = 10

def test_decoy_swap_survival_with_owned_decoy():
    mode = DecoySwapSurvivalMode()

    player = MockBall(1, 100, 100, "teamA")
    decoy1 = MockBall(2, 200, 200, "teamA", is_decoy=True, owner_id=1)
    decoy2 = MockBall(3, 800, 800, "teamA", is_decoy=True, owner_id=1) # Further away
    enemy = MockBall(4, 500, 500, "teamB")

    world = MockWorld(MockArena(), [player, decoy1, decoy2, enemy])

    # Tick past interval
    mode.tick(world, world.balls, delta=11.0)

    # Player should swap with nearest decoy (decoy1 at 200,200)
    assert player.x == 200 and player.y == 200
    assert decoy1.x == 100 and decoy1.y == 100

    # Enemy has no decoy, one should be spawned at its location and it swaps with it (stays in place)
    assert enemy.x == 500 and enemy.y == 500

    # Check if a new decoy was spawned for the enemy
    enemy_decoys = [b for b in world.balls if getattr(b, "is_decoy", False) and getattr(b, "owner_id", None) == enemy.id]
    assert len(enemy_decoys) == 1
    assert enemy_decoys[0].x == 500 and enemy_decoys[0].y == 500

def test_decoy_swap_survival_with_team_decoy_fallback():
    mode = DecoySwapSurvivalMode()

    player = MockBall(1, 100, 100, "teamA")
    # Decoy has no owner_id but same team
    team_decoy = MockBall(2, 300, 300, "teamA", is_decoy=True)

    world = MockWorld(MockArena(), [player, team_decoy])

    mode.tick(world, world.balls, delta=11.0)

    # Player should fallback to team decoy and swap with it
    assert player.x == 300 and player.y == 300
    assert team_decoy.x == 100 and team_decoy.y == 100
