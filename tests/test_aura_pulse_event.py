import pytest
from src.ai.game_modes import AuraPulseEventMode

class MockBall:
    def __init__(self, id_val, team):
        self.id = id_val
        self.team = team
        self.alive = True
        self.is_decoy = False
        self.vampiric_aura_timer = 0.0
        self.decoy_aura_timer = 0.0
        self.cosmetic_aura_scale = 1.0
        self.aura_inversion_timer = 0.0
        self.aura_disruption_timer = 0.0

class MockWorld:
    pass

def test_aura_pulse_friendly_buff():
    mode = AuraPulseEventMode()
    b1 = MockBall(1, "TeamA")
    b2 = MockBall(2, "TeamA")
    b3 = MockBall(3, "TeamB")

    b1.vampiric_aura_timer = 10.0

    balls = [b1, b2, b3]

    mode.tick(MockWorld(), balls, delta=15.0)

    # Since b1 is the only one pulsing with aura (not inverted) and b2 is the only friendly, b2 gets buffed
    assert b2.vampiric_aura_timer == 5.0
    # b3 should not be buffed because they're an enemy
    assert b3.vampiric_aura_timer == 0.0

def test_aura_pulse_enemy_debuff():
    mode = AuraPulseEventMode()
    b1 = MockBall(1, "TeamA")
    b2 = MockBall(2, "TeamA")
    b3 = MockBall(3, "TeamB")

    b1.decoy_aura_timer = 10.0
    b1.aura_inversion_timer = 10.0 # INVERTED

    balls = [b1, b2, b3]

    mode.tick(MockWorld(), balls, delta=15.0)

    # b1 is inverted, so instead of buffing b2, they debuff b3 (enemies map-wide)
    assert b3.aura_disruption_timer == 5.0
    assert b3.aura_inversion_timer == 5.0

    # friendlies should not get the buff
    assert b2.decoy_aura_timer == 0.0

def test_aura_pulse_does_not_trigger_early():
    mode = AuraPulseEventMode()
    b1 = MockBall(1, "TeamA")
    b2 = MockBall(2, "TeamA")
    b1.vampiric_aura_timer = 10.0

    balls = [b1, b2]

    mode.tick(MockWorld(), balls, delta=10.0)

    assert b2.vampiric_aura_timer == 0.0
