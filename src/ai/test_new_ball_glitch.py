from ai.new_ball_glitch import GlitchV2
import math

def test_glitch_v2_take_damage_teleports():
    glitch = GlitchV2(1, x=100.0, y=100.0)
    original_x = glitch.x
    original_y = glitch.y

    glitch.take_damage(10)

    # Assert position changed
    assert glitch.x != original_x or glitch.y != original_y

    # Distance should be between 20 and 50
    dx = glitch.x - original_x
    dy = glitch.y - original_y
    dist = math.sqrt(dx*dx + dy*dy)
    assert 20.0 <= dist <= 50.0

def test_glitch_v2_use_skill_cooldown():
    glitch = GlitchV2(1)

    # First use activates skill
    assert glitch.use_skill() == True
    assert glitch.skill_timer == 3.0

    # Second use fails because of cooldown
    assert glitch.use_skill() == False
