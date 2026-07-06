# Plan

1. **Create `ball_types_tracker.py` and `ball_types_tracker.gd`**
   - New ball type `tracker`.
   - `SKILL = "sonar_ping"`
   - `SKILL_COOLDOWN = 12.0`
   - Attributes: typical squishy, medium speed, maybe `PERCEPTION_RADIUS = 300` (it will dynamically expand with skill).

2. **Update `src/ai/action.py` and `src/ai/action.gd`**:
   - In `_use_skill`, handle `elif skill_name == "sonar_ping":`
   - Apply a timer to the ball: `self.ball.sonar_ping_timer = 5.0` (in python: `setattr(self.ball, "sonar_ping_timer", 5.0)`). In GDScript: `if typeof(self.ball) == TYPE_OBJECT and self.ball.has_method("set_meta"): self.ball.set_meta("sonar_ping_timer", 5.0)`
   - Add an event to `world.events` (if present) for VFX (e.g., `{"type": "sonar_ping", "x": ..., "y": ..., "radius": 1500.0}`)
   - Make sure to tick down `sonar_ping_timer` in `execute` loop for both files. If it's > 0, decrement by `delta`.

3. **Update `src/ai/perception.py` and `src/ai/perception.gd`**:
   - Check if the ball has an active `sonar_ping_timer > 0`.
   - If it does, force `perception_radius = max(perception_radius, 1500.0)`.
   - AND allow it to ignore stealth drone, shadow booster, sand cloaking, smoke, and eclipse restrictions, revealing ALL nearby enemies/items in that large radius. So, when filtering `entities`, we just bypass the hidden checks if `has_sonar`.

4. **Update `src/ai/game_modes.py` and `src/ai/game_modes.gd`**? Not required unless we want tracker to spawn. Maybe add to tests.

5. **Write tests in `tests/test_sonar_ping.py`**:
   - Create a test verifying `sonar_ping` skill sets the timer.
   - Create a test verifying `Perception` class uses the active `sonar_ping` to detect hidden enemies (stealth, smoke).

6. **Generate 2 ideas in JSON format** in `ideas/`.
