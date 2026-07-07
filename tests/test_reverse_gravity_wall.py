from ai.action import Action
from test_action_collision import MockBall, MockWorld

def test_reverse_gravity_booster_wall():
    ball = MockBall(x=500.0, y=500.0, team=1)
    ball.id = 1
    ball.reverse_gravity_booster_timer = 5.0

    enemy1 = MockBall(x=550.0, y=550.0, team=2) # close enough to ball
    enemy1.id = 2

    enemy2 = MockBall(x=800.0, y=500.0, team=2) # far from ball
    enemy2.id = 3

    ally = MockBall(x=510.0, y=510.0, team=1) # close ally
    ally.id = 4

    world = MockWorld()
    world.balls = [ball, enemy1, enemy2, ally]
    world.arena = type('MockArena', (), {'hazards': [], 'width': 1000, 'height': 1000})()
    world.game_mode = None

    action = Action(ball, world)
    action.execute("none", 1.0)

    # Assertions
    assert enemy1.x > 550.0 or enemy1.x < 550.0 or enemy1.y > 550.0 or enemy1.y < 550.0, "Enemy1 should have moved"
    assert enemy2.x == 800.0 and enemy2.y == 500.0, "Enemy2 should not have moved"
    assert ally.x == 510.0 and ally.y == 510.0, "Ally should not have moved"
