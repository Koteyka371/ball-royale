1. Modify `src/ai/game_modes.py`
   - In `ExtremeWeatherMode.__init__`, initialize `self.tsunami_wave = None`.
   - In `ExtremeWeatherMode.tick`, when weather switches to `"tsunami"` (i.e. `self.weather_timer >= 15.0`), initialize `self.tsunami_wave = {"x": 0.0, "y": 500.0, "speed": 300.0, "radius": 5000.0}`.
   - For other weathers, set `self.tsunami_wave = None`.
   - In the `for b in balls:` loop, if `self.current_weather == "tsunami"` and `self.tsunami_wave` is active, apply the push (`b.x += 300.0 * delta`) and damage logic only if the ball is caught in the wave (`b.x <= self.tsunami_wave["x"] + 100`).
   - Move the wave forward: `self.tsunami_wave["x"] += self.tsunami_wave["speed"] * delta`.
   - Sync the wave into `world.arena.hazards` as a hazard with kind `"tsunami_wave"`, `radius=5000`, `damage=0`, `id=99998`.

2. Verify changes in `src/ai/game_modes.py` using `run_in_bash_session` with the command `grep -C 5 'tsunami_wave' src/ai/game_modes.py`.

3. Modify `src/ai/game_modes.gd`
   - Replicate the exact logic in GDScript for `ExtremeWeatherMode`.
   - In `_init`, add `self.set_meta("tsunami_wave", null)`.
   - In `tick`, when weather switches:
     ```gdscript
     if current_weather == "tsunami":
         self.set_meta("tsunami_wave", {"x": 0.0, "y": 500.0, "speed": 300.0, "radius": 5000.0})
     else:
         self.set_meta("tsunami_wave", null)
     ```
   - Change tsunami ball logic:
     ```gdscript
     elif current_weather == "tsunami":
         if not has_life_jacket:
             var tw2 = self.get_meta("tsunami_wave")
             if tw2 != null and ("x" in b and b.x <= tw2["x"] + 100):
                 b.x += 300.0 * delta
                 var arena_w = 1000
                 if world != null and "arena" in world and world.arena != null and "width" in world.arena:
                     arena_w = world.arena.width
                 if b.x >= arena_w - 20:
                     b.hp -= 20.0 * delta
     ```
   - Update wave position and sync to hazards at the end of tick.

4. Verify changes in `src/ai/game_modes.gd` using `run_in_bash_session` with the command `grep -C 5 'tsunami_wave' src/ai/game_modes.gd`.

5. Update tests in `src/ai/test_extreme_weather.py`
   - Use `run_in_bash_session` to write a python script that updates `test_extreme_weather.py` replacing lines 138-155.
   - The test update will initialize the wave (so we bypass waiting 15s):
     ```python
     # Test tsunami
     mode.current_weather = "tsunami"
     mode.tsunami_wave = {"x": 500.0, "y": 500.0, "speed": 300.0, "radius": 5000.0}
     b1.x = 550
     b1.hp = 100.0
     b2.x = 550
     b2.hp = 100.0
     b2.life_jacket_booster_timer = 10.0

     mode.tick(world, balls, 1.0)
     assert b1.x == 850.0 # 550 + 300 * 1.0
     assert b2.x == 550.0 # b2 is protected

     # Test wall hit damage
     b1.x = 980
     b1.hp = 100.0
     mode.tsunami_wave["x"] = 980
     mode.tick(world, balls, 1.0)
     assert b1.hp == 80.0 # 100 - 20 * 1.0
     assert b1.x == 1280.0
     ```

6. Verify tests pass by running full suite: `PYTHONPATH=.:src pytest src/`

7. Generate idea files
   - Run bash command `cat << 'EOF' > ideas/idea_idea-1099_1.json\n{"title": "Black Hole Anomaly", "description": "A slow-moving black hole sweeps across the arena, pulling players inward."}\nEOF`
   - Run bash command `cat << 'EOF' > ideas/idea_idea-1099_2.json\n{"title": "Gravity Swap Event", "description": "Periodically inverts arena gravity or bounces mechanics, forcing players to readjust momentum."}\nEOF`

8. Verify the idea files were written successfully using `run_in_bash_session` with `ls -l ideas/`.

9. Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

10. Submit PR using `submit` tool.
