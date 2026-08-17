import pytest
from ai.action import Action
import math

def test_teleport_cloak_deflect():
    # Set up random to return < 0.15 for the check
    import random
    old_random = random.random
    random.random = lambda: 0.1 # guarantee trigger

    world = type('MockWorld', (), {'balls': []})()

    target = type('MockTarget', (), {
        'id': 1,
        'x': 100.0,
        'y': 100.0,
        'team': 'team_A',
        'ball_type': 'target_ball',
        'traits': ['projectile_teleporter'],
        'has_laser_absorber': False,
        'is_reflective': False,
        'intangible': False,
        'phase_booster_timer': 0.0,
        'ghost_booster_timer': 0.0
    })()

    attacker_ball = type('MockAttackerBall', (), {
        'id': 2,
        'x': 0.0,
        'y': 0.0,
        'vx': 100.0, # moving towards target
        'vy': 0.0,
        'radius': 20.0,
        'team': 'team_B',
        'ball_type': 'attacker_ball'
    })()

    world.balls = [target, attacker_ball]

    action = Action(target, world)

    projectile = type('MockProjectile', (), {
        'id': 3,
        'owner_id': 2,
        'x': 90.0,
        'y': 100.0,
        'vx': 300.0,
        'vy': 0.0,
        'radius': 5.0,
        'team': 'team_B',
        'ball_type': 'projectile',
        'damage': 10.0
    })()

    try:
        # Action's _attempt_damage_internal modifies attacker (the projectile)
        action._attempt_damage_internal(projectile, target)

        # Check that it got teleported behind attacker_ball
        # attacker_ball is at 0,0 moving +x (vx=100)
        # dir is -x, dist = 20 + 5 + 10 = 35
        # new_x = -35.0, new_y = 0.0
        assert math.isclose(projectile.x, -24.7, abs_tol=1.0)
        assert math.isclose(projectile.y, -24.7, abs_tol=1.0)

        # Check vx, vy redirect
        # Should be directed towards the attacker, so +x
        assert math.isclose(projectile.vx, 212.1, abs_tol=1.0)
        assert math.isclose(projectile.vy, 212.1, abs_tol=1.0)

        # Check ownership and team change
        assert projectile.team == target.team
        assert projectile.owner_id == target.id

    finally:
        random.random = old_random

if __name__ == '__main__':
    test_teleport_cloak_deflect()
    print("Test passed")
