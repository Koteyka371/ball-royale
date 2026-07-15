# mypy: ignore-errors
import pytest
import random
from tests.simulate_battle import BattleSimulation

# The fuzzer creates extreme game states and ensures the game doesn't crash or hang
# It runs automatically as part of the pytest suite in auto_improve_loop.py

def test_fuzz_extreme_numbers():
    # Spawns balls with negative stats, infinite stats, or NaNs
    sim = BattleSimulation(num_balls=10, max_ticks=10)
    for ball in sim.balls:
        ball.hp = random.choice([-1000, 0, float('inf'), float('nan')])
        ball.speed = random.choice([-5, 0, float('inf')])
        ball.damage = random.choice([-10, 0, float('inf')])
    
    # This shouldn't crash
    try:
        sim.run(record=False)
    except Exception as e:
        pytest.fail(f"Fuzzer crashed the simulation with extreme numbers: {e}")

def test_fuzz_out_of_bounds_positions():
    # Places balls outside the arena
    sim = BattleSimulation(num_balls=20, max_ticks=20, arena_size=100)
    for ball in sim.balls:
        ball.x = random.choice([-10000, 10000, float('inf'), float('nan')])
        ball.y = random.choice([-10000, 10000, float('inf'), float('nan')])

    try:
        sim.run(record=False)
    except Exception as e:
        pytest.fail(f"Fuzzer crashed the simulation with out-of-bounds positions: {e}")

def test_fuzz_massive_density():
    # 200 balls in a tiny 10x10 arena, testing collision and spatial hash edge cases
    sim = BattleSimulation(num_balls=200, max_ticks=20, arena_size=10)
    try:
        sim.run(record=False)
    except Exception as e:
        pytest.fail(f"Fuzzer crashed the simulation with massive density: {e}")

def test_fuzz_zero_balls():
    # Testing how the engine handles empty battles
    sim = BattleSimulation(num_balls=0, max_ticks=50)
    try:
        sim.run(record=False)
    except Exception as e:
        pytest.fail(f"Fuzzer crashed the simulation with zero balls: {e}")

import collections
import string

from src.ui.nemesis_screen.nemesis_screen import *

from src.ui.nemesis_screen import nemesis_screen

from src.system import replay

from src.system import crowd_system
