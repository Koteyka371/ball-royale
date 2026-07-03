1. Make sure `fake_booster` logic in `src/ai/action.py` and `src/ai/action.gd` pushes the enemy back. (I already patched this).
2. Ensure Trickster (`src/ai/ball_types_trickster.py`) is set to use the `place_fake_booster` skill. (I already patched this).
3. Ensure there is a unit test testing the fake booster explosion, knockback, and Trickster using it. (I already added `src/ai/test_trickster_decoy.py`).
4. Generate ideas in `ideas/`. (I already did this).
5. Run all tests to make sure my changes don't break anything.
6. Complete pre-commit instructions.
7. Submit the PR.
