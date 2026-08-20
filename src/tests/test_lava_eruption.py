from ai.lava_eruption import LavaEruptionEventMode
from unittest.mock import MagicMock

def test_lava_eruption_launch():
    mode = LavaEruptionEventMode()
    world = MagicMock()

    mode.eruption_timer = 0.0
    mode.eruptions.append({
        "x": 500.0,
        "y": 500.0,
        "timer": 1.9,
        "warning_duration": 2.0,
        "radius": 50.0
    })

    ball = MagicMock(alive=True, x=500.0, y=500.0)
    ball.hp = 100.0
    ball.z_velocity = 0.0
    ball.burn_timer = 0.0
    ball.weather_immunity_timer = 0.0


    mode.apply_dynamic_traits(world, [ball], 0.1)

    assert ball.z_velocity >= 800.0, f"z_velocity={ball.z_velocity}"
    assert ball.burn_timer >= 5.0, f"burn_timer={ball.burn_timer}"
    assert len(mode.puddles) == 1

if __name__ == "__main__":
    test_lava_eruption_launch()
    print("Test passed")
