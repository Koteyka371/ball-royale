def test_temporal_rifts_mode_exists():
    from ai.game_modes import TemporalRiftsMode
    mode = TemporalRiftsMode()
    assert mode.name == "Temporal Rifts"
