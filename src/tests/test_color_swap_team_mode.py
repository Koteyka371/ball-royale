import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.game_modes import GAME_MODES
from ai.action import Action

class MockWorld:
    def __init__(self):
        self.game_mode = GAME_MODES["color_swap_team"]
        self.events = []
        class MockArena:
            hazards = []
        self.arena = MockArena()

class MockBall:
    def __init__(self, id_val):
        self.id = id_val
        self.hp = 100
        self.x = 0
        self.y = 0
        self.ghost_booster_timer = 0
        self.nemesis_shield_active = False
        self.has_aegis_shield = False
        self.is_hologram = False

def test_color_swap_team_mode_setup_and_tick():
    mode = GAME_MODES["color_swap_team"]
    world = MockWorld()
    balls = [MockBall(i) for i in range(4)]

    mode.setup(world, balls)

    assert balls[0].team == "Team A"
    assert balls[1].team == "Team A"
    assert balls[2].team == "Team B"
    assert balls[3].team == "Team B"

    colors_before = [b.current_color for b in balls]

    # Tick past swap_interval
    mode.tick(world, balls, 11.0)

    colors_after = [b.current_color for b in balls]

    for i in range(4):
        assert colors_before[i] != colors_after[i]

    # Check damage blocking logic
    action = Action(None, world)

    b1 = balls[0]
    b2 = balls[3]

    b1.current_color = "red"
    b2.current_color = "blue"

    res = action._attempt_damage_internal(b1, b2)
    assert res is None # Blocked

    b2.current_color = "red"

    b2.ghost_booster_timer = 1.0
    action._attempt_damage_internal(b1, b2) # Should go through the color check and hit the ghost check
