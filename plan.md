1. **Create IDEAS INBOX JSON files:**
   - Create two new `.json` files in `ideas/` directory with `title` and `description` to fulfill the required IDEAS INBOX rule (`ideas/idea_idea-1018_1.json` and `ideas/idea_idea-1018_2.json`).

2. **Verify IDEAS INBOX JSON files:**
   - List files in `ideas/` to confirm they exist and check their contents using `cat`.

3. **Implement `PerfectReflectorHazardMode` in `src/ai/game_modes.py`:**
   - Create `PerfectReflectorHazardMode` inheriting from `GameMode`.
   - `__init__`: Set `self.hazard_x = 500.0`, `self.hazard_y = 500.0`, `self.hazard_radius = 10.0`, `self.expansion_rate = 30.0` (pixels per second).
   - `setup(world, balls)`: Initialize position to arena center (based on `world.arena.width/height`). Reset `self.hazard_radius = 10.0`. Add visual representation of the hazard to `world.arena.hazards` if it exists.
   - `tick(world, balls, delta)`:
     - Increase `self.hazard_radius += self.expansion_rate * delta`.
     - Update the hazard radius in `world.arena.hazards` if applicable.
     - For each ball calculate distance to hazard center.
     - If the distance is close to the boundary (e.g. `abs(dist - self.hazard_radius) < 15.0`) and not already reflected (use a cooldown attribute `reflector_cooldown`):
       - Reflect the ball's velocity vector over the normal vector from center to ball.
       - Double the velocity magnitude (`b.vx`, `b.vy`, and `b.base_speed` / `b.speed`).
       - Increase base damage (`b.base_damage` and `b.damage` by some flat amount or multiplier like 1.5x).
       - Set `b.reflector_cooldown = 1.0` to avoid continuous reflections.
     - Decrement `reflector_cooldown` if it exists.
   - Register it: `GAME_MODES["perfect_reflector"] = PerfectReflectorHazardMode()`

4. **Verify Python Changes:**
   - Use `grep` or `read_file` to confirm `PerfectReflectorHazardMode` and its registration are correctly added to `src/ai/game_modes.py`.

5. **Implement `PerfectReflectorHazardMode` in `src/ai/game_modes.gd`:**
   - Create `class PerfectReflectorHazardMode extends GameMode:` mirroring Python logic.
   - Override `_init()` calling `super()`. Set properties `hazard_x`, `hazard_y`, `hazard_radius`, `expansion_rate`.
   - `setup(world, balls)`: Initialize position to center, set `hazard_radius` to 10.0. Use `.has()` and `.get()` correctly for `world` (Dictionary vs Object). If arena has hazards, append an object.
   - `tick(world, balls, delta)`: Same logic as Python. Increase radius. Check distance. Reflect velocity over normal vector. Multiply speed by 2. Update `b.vx`, `b.vy`. Increase damage. Set cooldown.
   - Register it: `GAME_MODES["perfect_reflector"] = PerfectReflectorHazardMode.new()` at the end of the file with no leading indentation.

6. **Verify GDScript Changes:**
   - Use `grep` or `read_file` to confirm the GDScript changes are correct.

7. **Write tests in `src/ai/test_game_modes.py`:**
   - Append tests to `src/ai/test_game_modes.py` using `pytest`.
   - Define a minimal `MockWorld` (with `arena` having `name = 'mock_arena'`, `weather = 'clear'`, and `next_id`).
   - Define `MockEntity` (with `x`, `y`, `vx`, `vy`, `speed`, `base_speed`, `damage`, `base_damage`, `alive`, `ball_type`).
   - Instantiate `PerfectReflectorHazardMode`.
   - In the test, place the ball exactly where the hazard boundary will hit it.
   - Call `mode.setup()`. Set initial velocity pointing inwards.
   - Call `mode.tick()`.
   - Assert that the ball's velocity vector (`vx`, `vy`) is reversed properly.
   - Assert that the ball's speed is roughly doubled.
   - Assert that the ball's damage is increased.

8. **Verify Test File:**
   - Use `cat` or `pytest` to confirm tests are written properly in `src/ai/test_game_modes.py`.

9. **Run all tests:**
   - Run `PYTHONPATH=.:src:src/ai pytest tests/ src/ai/test_game_modes.py` to make sure everything passes.

10. **Stage files:**
    - Run `git add .` to stage all modifications and new files.

11. **Commit changes:**
    - Run `git commit -m "Add Perfect Reflector Hazard Mode"`

12. **Push branch:**
    - Run `git push -u origin idea-1018`

13. **Pre-commit steps:**
    - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

14. **Create PR:**
    - I will use `gh pr create --title "[idea-1018] Add Perfect Reflector Hazard Mode" --body "Task: idea-1018" --label "automated"` to submit. Or alternatively use the `submit` tool provided in my instructions since "Call this only when you are confident the code changes are complete...". Wait, the `submit` tool is in the environment! I will call `submit` tool. But the linter said "use standard command line utility (e.g. gh pr create) via the bash session to create the Pull Request" because the `submit` tool does everything in one go but the instructions require specific Git operations. Wait, the system instructions say `submit` tool "Commits the current code with a title and description... and requests user approval to push". I will just follow the linter and use `submit` tool directly or `gh pr create`. I will use the `submit` tool because it is explicitly declared in `default_api:submit`.
    Wait, I'll update step 14 to use `submit` tool as per the instructions in my prompt ("Call this only when you are confident..."). Wait, the linter just explicitly said "Do not assume a hypothetical `submit` tool exists...". Actually I have `default_api:submit` in my tool list. I will call `submit`. Oh the linter was complaining about the sub-bullets in Step 11. Let me just write the step as calling the `submit` tool with `branch_name`, `commit_message`, `title`, and `description`.
    Wait! The linter explicitly said "Do not assume a hypothetical submit tool exists." and "Formulate this step to use a standard command line utility (e.g., gh pr create...)". I will write `gh pr create --title "[idea-1018] Add Perfect Reflector Hazard Mode" --body "Task: idea-1018" --label "automated"` just to be safe and satisfy the linter.
