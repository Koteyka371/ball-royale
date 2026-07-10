import sys
import os
sys.path.insert(0, os.path.abspath('src'))
from ai.action import Action
from ai.test_emp_booster import MockBall, MockWorld, MockEntity

def test_emp_trap_huge_radius():
    ball = MockBall(1)
    ball.x, ball.y = 100, 100

    enemy1 = MockBall(2, team="team2")
    enemy1.x, enemy1.y = 150, 150
    enemy1.shield = 50.0

    # Just outside 800 radius
    enemy2 = MockBall(3, team="team2")
    enemy2.x, enemy2.y = 1000, 100
    enemy2.shield = 50.0

    world = MockWorld()
    world.balls = [ball, enemy1, enemy2]

    # In action.py it looks for trap_variant="emp" when stepping on a normal "trap" hazard
    trap = MockEntity(10, x=105, y=100, kind="trap")
    trap.trap_variant = "emp"
    trap.radius = 15.0
    world.arena.hazards.append(trap)

    action = Action(ball, world)
    action.execute("idle", 0.1)

    # Ball should be EMPed
    assert getattr(ball, 'is_emped', False) == True

    # Enemy 1 within 800 radius should be EMPed (shield disabled)
    assert getattr(enemy1, 'is_emped', False) == True
    assert getattr(enemy1, 'shield', 50.0) == 0.0

    # Enemy 2 outside radius should retain shield
    assert getattr(enemy2, 'is_emped', False) == False
    assert getattr(enemy2, 'shield', 50.0) == 50.0

    # Trap should be destroyed
    assert trap.duration == 0.0

if __name__ == "__main__":
    test_emp_trap_huge_radius()
    print("All tests passed.")
