1. **Create Time Mage Ball Type**
   - Create `src/ai/ball_types_time_mage.py` and `src/ai/ball_types_time_mage.gd` to define a new `Time Mage` ball type.
   - It will have `BALL_TYPE = "time_mage"`, a custom skill `time_recall` (or `temporal_recall`), and high cooldown `SKILL_COOLDOWN = 15.0`.
   - Ensure initialization handles attributes correctly (e.g. `state_history`).

2. **Implement `temporal_recall` Skill Logic**
   - In `src/ai/action.py` and `src/ai/action.gd`, under `elif skill_name == "temporal_recall":`, implement logic to instantly return the Time Mage to its state from 3 seconds ago.
   - Reuse the `state_history` array already tracked for `time_rewind` (which stores x, y, hp). Wait, `time_rewind` currently affects *allies* of a Chronos ball, so this new skill will affect only *self* but will fully restore state (position, hp).
   - Fetch the oldest state in `self.ball.state_history`, apply `x, y, hp` to `self.ball`, and clear `self.ball.state_history` to prevent repeated rewinding. Clear negative status effects (stun, silence, poison). Add `world.add_event` for sound effects/particles if applicable.

3. **Register Time Mage in Game Modes**
   - Update `src/ai/game_modes.py` and `src/ai/game_modes.gd` to include `"time_mage"` in the `available_types` and `types` arrays.

4. **Add Tests**
   - Create `src/ai/test_time_mage.py` to test the `temporal_recall` skill and Time Mage basic initialization.
   - Run tests using `PYTHONPATH=src pytest`.

5. **Generate Ideas**
   - Create two JSON files in the `ideas/` directory with new game ideas.

6. **Complete pre-commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

7. **Submit PR**
   - Create PR using GitHub CLI.
