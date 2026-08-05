from ai.game_modes import EscortMode
from typing import Any

class MockBall:
    def __init__(self, x, y, team, ball_type="player"):
        self.x = x
        self.y = y
        self.team = team
        self.ball_type = ball_type
        self.alive = True
        self.hp = 100.0
        self.shield_booster_active = True
        self.speed_boost_timer = 5.0
        self.damage_boost_timer = 5.0
        self.soul_boost_timer = 5.0
        self.invulnerable_timer = 5.0
        self.vampiric_aura_timer = 5.0
        self.radius = 15.0

class MockWorld:
    pass

def test_payload_pulse_disables_buffs():
    mode = EscortMode()
    payload = MockBall(500, 500, "Defenders", "payload")
    payload.alive = True
    mode.payload = payload

    attacker_in_range = MockBall(600, 500, "Attackers")
    attacker_out_range = MockBall(900, 500, "Attackers")
    defender_in_range = MockBall(550, 500, "Defenders")

    balls = [payload, attacker_in_range, attacker_out_range, defender_in_range]
    world = MockWorld()

    # Pulse timer reaches 5
    mode.pulse_timer = 5.0
    mode.tick(world, balls, delta=0.016)

    # Attacker in range should take damage and lose buffs
    assert attacker_in_range.hp == 80.0
    assert attacker_in_range.shield_booster_active == False
    assert attacker_in_range.speed_boost_timer == 0.0
    assert attacker_in_range.damage_boost_timer == 0.0
    assert attacker_in_range.soul_boost_timer == 0.0
    assert attacker_in_range.invulnerable_timer == 0.0
    assert attacker_in_range.vampiric_aura_timer == 0.0

    # Attacker out of range should not lose buffs
    assert attacker_out_range.shield_booster_active == True
    assert attacker_out_range.speed_boost_timer == 5.0

    # Defender in range should not lose buffs
    assert defender_in_range.shield_booster_active == True
    assert defender_in_range.speed_boost_timer == 5.0
