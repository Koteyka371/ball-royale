1. **Create `ball_types_illusionist.py`:** Create `src/ai/ball_types_illusionist.py` with the `Illusionist` class, defining `SKILL = 'mimic_clone'` and other standard attributes.
2. **Review `action.py` and `action.gd`**: Verify `mimic_clone` behaves exactly as specified (mimics movement, deals no damage, has set HP or duration) and taunts enemies. (Already verified: `is_illusion = True` causes taunting, logic exists for mimicry and expiration).
3. **Add Tests:** Ensure tests cover the `Illusionist` class (e.g. `src/ai/test_ball_types_illusionist.py`). Test that calling `use_skill` sets up the correct action.
4. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
5. **Submit:** Use `submit` to push branch 'idea-339' with a descriptive PR.
