import re

with open("src/ai/test_game_modes.py", "r") as f:
    text = f.read()

text = re.sub(
    r"def test_floor_is_lava_mode\(\):.*?def test_cursed_buff_zone_mode\(\):",
    """def test_floor_is_lava_mode():
    from ai.game_modes import FloorIsLavaMode
    mode = FloorIsLavaMode()
    world = MockWorld()
    class MockArena:
        def __init__(self):
            self.width = 1000
            self.height = 1000
            self.hazards = []
    world.arena = MockArena()
    setattr(world, "arena", type("Arena", (), {"width": 1000, "height": 1000, "hazards": []})())

    ball = MockBall(1)
    ball.x = 900
    ball.y = 900
    ball.hp = 100
    ball.radius = 15.0

    mode.setup(world, [ball])
    assert len(mode.platforms) > 0
    assert mode.lava_radius == 0.0
    assert mode.max_lava_radius == 1000.0

    mode.lava_radius = 300.0 # Force lava to expand, but not enough to reach ball (dist 565)
    mode.tick(world, [ball], delta=1.0)
    assert ball.hp == 100

    # Place ball in center
    ball.x = 500
    ball.y = 500
    mode.platforms = [] # Remove safe platforms
    mode.tick(world, [ball], delta=1.0)
    assert ball.hp < 100

def test_cursed_buff_zone_mode():""", text, flags=re.DOTALL
)

with open("src/ai/test_game_modes.py", "w") as f:
    f.write(text)
