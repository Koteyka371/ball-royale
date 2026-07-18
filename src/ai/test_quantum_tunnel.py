import pytest
from ai.game_modes import QuantumTunnelMutatorMode

def test_quantum_tunnel_mutator_high_speed():
    mode = QuantumTunnelMutatorMode()
    world = type('MockWorld', (), {'dead_balls': []})()

    ball1 = type('MockBall', (), {
        'alive': True,
        'vx': 100.0,
        'vy': 100.0,
        'base_speed': 100.0,
        'phase_booster_timer': 0.0
    })()

    # speed is sqrt(20000) = 141.4, threshold is 150.0
    # Not enough to trigger
    balls = [ball1]

    # Let's use a very high speed
    ball2 = type('MockBall', (), {
        'alive': True,
        'vx': 200.0,
        'vy': 0.0,
        'base_speed': 100.0,
        'phase_booster_timer': 0.0
    })()
    balls.append(ball2)

    # We need to run it multiple times since there's a 20% * delta chance
    import random
    random.seed(42) # Ensure reproducibility if needed, but we can just run many ticks

    for _ in range(100):
        mode.tick(world, balls, delta=1.0)

    assert ball1.phase_booster_timer == 0.0, "Ball 1 was too slow and should not have phased"
    assert ball2.phase_booster_timer > 0.0, "Ball 2 was fast enough and should have phased at least once"

def test_quantum_tunnel_mutator_dead_ball():
    mode = QuantumTunnelMutatorMode()
    world = type('MockWorld', (), {'dead_balls': []})()

    ball1 = type('MockBall', (), {
        'alive': False,
        'vx': 200.0,
        'vy': 200.0,
        'base_speed': 100.0,
        'phase_booster_timer': 0.0
    })()

    mode.tick(world, [ball1], delta=1.0)

    assert ball1 in world.dead_balls
    assert getattr(ball1, 'time_since_death', 0.0) == 0.0
    assert ball1.phase_booster_timer == 0.0
