import pytest
from unittest.mock import MagicMock
from src.ai.game_modes import PitchBlackMode

def test_pitch_black_mode():
    mode = PitchBlackMode()
    class WorldMock:
        def __init__(self):
            self.arena = MagicMock()
            self.arena.width = 800
            self.arena.height = 600
            self.arena.hazards = []

    world = WorldMock()

    # Mock balls
    class BallMock:
        def __init__(self, bid):
            self.id = bid
            self.ball_type = "player"
            self.x = 400
            self.y = 300
            self.vx = 0
            self.vy = 0
            self.hp = 100
            self.radius = 20
            self.alive = True

    ball1 = BallMock(1)
    ball2 = BallMock(2)
    ball2.x = 450
    balls = [ball1, ball2]

    # Setup
    mode.setup(world, balls)

    # 1. Balls should start invisible
    assert ball1.invisible == True
    assert ball2.invisible == True

    # 2. Bounce visibility
    # Move ball1 to wall and bounce
    ball1.x = 10
    ball1.vx = 100
    ball1.pb_prev_vx = -100
    mode.tick(world, balls, delta=0.1)
    assert ball1.invisible == False
    assert ball1.visibility_timer > 0

    # Reset visibility
    ball1.visibility_timer = 0
    ball2.x = 200
    mode.tick(world, balls, delta=0.1)
    assert ball1.invisible == True

    # 3. Damage visibility
    ball1.hp -= 10
    mode.tick(world, balls, delta=0.1)
    assert ball1.invisible == False

    # 4. Attack visibility (skill shots)
    ball1.visibility_timer = 0
    ball2.x = 200
    ball1.pb_attack_cooldown = 0 # Ready to attack
    mode.tick(world, balls, delta=0.1)

    # Flare shot should be spawned
    assert len(world.arena.hazards) > 0
    flare = world.arena.hazards[0]
    flare_kind = flare.kind if not isinstance(flare, dict) else flare.get("kind")
    assert flare_kind == "flare_shot"

    # Ball 1 attacked, should be visible
    assert ball1.invisible == False

    # 5. Illumination
    # Move ball2 near the flare
    ball2.visibility_timer = 0
    ball2.hp = 100
    ball2.pb_prev_hp = 100
    ball2.x = getattr(flare, "x", flare.get("x") if isinstance(flare, dict) else 0)
    ball2.y = getattr(flare, "y", flare.get("y") if isinstance(flare, dict) else 0)

    mode.tick(world, balls, delta=0.1)
    # Ball 2 should be illuminated by flare!
    assert ball2.invisible == False
