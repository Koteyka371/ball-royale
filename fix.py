with open("src/ai/action.py", "r") as f:
    c = f.read()

# We need to make sure that Hazard initialization includes the missing arguments, wait, no. The problem was:
# E           AssertionError: assert (0.0 > 0 or 'molten_rock' in ['starlight_projectile', 'avalanche', 'magnetic_bumper', 'time_dilation_zone', 'temporal_bubble', 'cursed_trap', ...])
# E            +  where 0.0 = Hazard(id=2, x=277.64248528412594, y=731.0316405133019, radius=56.361656334695525, kind='molten_rock', damage=0.0, active=True, target_radius=0.0).damage
# This is from test_procedural_arena.py
