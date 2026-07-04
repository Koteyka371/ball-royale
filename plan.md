1. **Modify Python code (`src/ai/action.py`)**
   - In `action.py`, locate the wall reflection block under `if bounced_wall:`.
   - Before taking damage, check if `getattr(self.ball, "ball_type", getattr(type(self.ball), "BALL_TYPE", "")).lower()` is in a list of allowed ball types for wall bouncing without damage (e.g., `["ninja", "assassin", "rogue", "brawler"]`).
   - If the ball type is allowed, we do NOT take damage.
   - Also, if the ball type is allowed, we apply the `new_speed` and reversed `vx, vy` directly to `self.ball.vx` and `self.ball.vy` (similar to what happens in `is_mirror_walls`), allowing them to bounce off walls with increased velocity.

2. **Modify GDScript code (`src/ai/action.gd`)**
   - Similar to Python code, in `action.gd` find `if bounced_wall:`.
   - Safely retrieve `ball_type` (handle Dictionaries, Objects with meta, and regular properties).
   - If the `ball_type` is in `["ninja", "assassin", "rogue", "brawler"]`:
     - Skip damage.
     - Set `self.ball.vx = nvx` and `self.ball.vy = nvy` directly to reflect off walls with increased velocity.

3. **Add tests**
   - Add a test script `src/ai/test_bouncing_wall_attack.py` to verify that `ninja` bounces off the wall with increased velocity and no damage, whereas a normal ball takes damage.

4. **Run tests**
   - Run tests to ensure no regressions.

5. **Complete pre-commit steps**
   - Run `pre_commit_instructions` to ensure proper testing, verification, review, and reflection are done.

6. **Submit**
   - Submit the PR.
