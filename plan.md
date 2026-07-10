1. **Add `gravity_storm` to the list of weathers in procedural arena generation:**
   - In `src/arena/procedural_arena.py`, add `"gravity_storm"` to the `weathers` list in `update_zone` around line 577.
   - Initialize `self.is_gravity_storm = False` in `update_zone` (and also whenever weather flags are initialized around line 580 and line 570, or when resetting the weather to `"clear"`).
   - In `src/arena/procedural_arena.gd`, add `"gravity_storm"` to the `weathers` list in `update_zone` around line 653.
   - Initialize `is_gravity_storm = false` similarly.

2. **Implement `gravity_storm` periodic effect:**
   - In `src/arena/procedural_arena.py`, within the `if current_tick % 120 == 0:` block in `update_zone`, add logic for `gravity_storm`. If `getattr(self, "weather", "") == "gravity_storm"`, randomly spawn 1 to 3 miniature gravity wells.
     ```python
     if getattr(self, "weather", "") == "gravity_storm":
         for _ in range(random.randint(1, 3)):
             gw_id = 8300 + len(self.hazards) + random.randint(0, 1000)
             gw = Hazard(id=gw_id, x=random.uniform(50, self.width - 50), y=random.uniform(50, self.height - 50), radius=random.uniform(80.0, 150.0), kind="gravity_well", damage=2.0)
             setattr(gw, 'duration', 10.0)
             self.hazards.append(gw)
     ```
   - Do the same in `src/arena/procedural_arena.gd`:
     ```gdscript
     if weather == "gravity_storm":
         var num_gws = (randi() % 3) + 1
         for i in range(num_gws):
             var gw_id = 8300 + hazards.size() + (randi() % 1000)
             var gw = Hazard.new(gw_id, randf_range(50, width - 50), randf_range(50, height - 50), randf_range(80.0, 150.0), "gravity_well", 2.0)
             gw.set_meta("duration", 10.0)
             hazards.append(gw)
     ```

3. **Run tests & Complete Pre-commit step:**
   - Run tests. Ensure no regressions are introduced.
   - Run python scripts for CI checks and any pre-commit requirements (following rule 11 / specific PR format).
   - Call `pre_commit_instructions` and follow its instructions to complete pre commit steps.

4. **IDEAS INBOX:**
   - Create 2 JSON files in `ideas/` based on instructions (e.g. `ideas/idea_idea-845_1.json`, `ideas/idea_idea-845_2.json`).

5. **Submit PR:**
   - Push branch and create a PR.
