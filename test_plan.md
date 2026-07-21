1. Modify `src/ai/action.py` to change `enemy.silence_timer = 5.0` to `enemy.silence_timer = 3.0` inside the `silence_aura` skill definition. I will target the string `enemy.silence_timer = 5.0` under `elif skill_name == "silence_aura":` block.
2. Modify `src/ai/action.gd` similarly to change `enemy.silence_timer = 5.0` (and `set_meta` / dictionary accesses) to `3.0` inside `elif skill_name == "silence_aura":`. I will target strings such as `enemy.silence_timer = 5.0`, `enemy.set_meta("silence_timer", 5.0)`, and `enemy["silence_timer"] = 5.0`.
3. Update `src/ai/test_silence_aura.py` to assert `enemy_close.silence_timer == 3.0`, and update initial values of `silence_timer = 3.0` and `silence_timer == 2.0` in the other tests.
4. Run tests with `PYTHONPATH=src pytest`.
5. Ensure proper testing, verification, review, and reflection are done (pre-commit steps).
6. Create 2 ideas in `ideas/`.
7. Submit pull request.
