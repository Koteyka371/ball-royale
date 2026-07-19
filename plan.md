1. **Modify GameMode weather booster spawns (Python)**
   - Edit `src/ai/game_modes.py`
   - In `ExtremeWeatherMode.tick()`
     ```python
     if self.current_weather == "blizzard":
         booster_kind = self.random.choice(["thermal_booster", "snow_globe_booster"])
     ```
     ```python
     elif self.current_weather == "acid_rain":
         booster_kind = self.random.choice(["hazmat_booster", "umbrella_booster"])
     ```

2. **Modify GameMode weather booster spawns (GDScript)**
   - Edit `src/ai/game_modes.gd`
   - In `ExtremeWeatherMode.tick()`
     ```gdscript
     if current_weather == "blizzard": booster_kind = ["thermal_booster", "snow_globe_booster"][randi() % 2]
     elif current_weather == "acid_rain": booster_kind = ["hazmat_booster", "umbrella_booster"][randi() % 2]
     ```

3. **Implement Booster Collection Logic (Python)**
   - Edit `src/ai/action.py` in `Action._collect_booster()`
     ```python
     elif getattr(nearest, "kind", None) == "snow_globe_booster":
         self.ball.freezing_immunity_timer = 15.0
         if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards") and nearest in self.world.arena.hazards:
             self.world.arena.hazards.remove(nearest)
         if hasattr(self.world, "boosters") and nearest in self.world.boosters:
             self.world.boosters.remove(nearest)
     elif getattr(nearest, "kind", None) == "umbrella_booster":
         self.ball.slippery_immunity_timer = 15.0
         if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards") and nearest in self.world.arena.hazards:
             self.world.arena.hazards.remove(nearest)
         if hasattr(self.world, "boosters") and nearest in self.world.boosters:
             self.world.boosters.remove(nearest)
     ```

4. **Implement Booster Collection Logic (GDScript)**
   - Edit `src/ai/action.gd` in `_collect_booster()`
     ```gdscript
     elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest.kind == "snow_globe_booster":
         if self.ball.has_method("set_meta"): self.ball.set_meta("freezing_immunity_timer", 15.0)
         else: self.ball.freezing_immunity_timer = 15.0
         if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
             var idx = self.world.arena.hazards.find(nearest)
             if idx != -1: self.world.arena.hazards.remove_at(idx)
         if self.world != null and "boosters" in self.world:
             var idx = self.world.boosters.find(nearest)
             if idx != -1: self.world.boosters.remove_at(idx)
     elif typeof(nearest) == TYPE_DICTIONARY and nearest.has("kind") and nearest.kind == "umbrella_booster":
         if self.ball.has_method("set_meta"): self.ball.set_meta("slippery_immunity_timer", 15.0)
         else: self.ball.slippery_immunity_timer = 15.0
         if self.world != null and "arena" in self.world and "hazards" in self.world.arena:
             var idx = self.world.arena.hazards.find(nearest)
             if idx != -1: self.world.arena.hazards.remove_at(idx)
         if self.world != null and "boosters" in self.world:
             var idx = self.world.boosters.find(nearest)
             if idx != -1: self.world.boosters.remove_at(idx)
     ```

5. **Update weather effects to respect immunity (Python & GDScript)**
   - In `src/ai/game_modes.py`:
     - Update timer decrements in `GameMode.tick()` and `ExtremeWeatherMode.tick()`
     - For `ExtremeWeatherMode` in Python: check `getattr(b, "freezing_immunity_timer", 0.0)`.
   - Wait, `GameMode` applies rain effects (slippery, dash) in `GameMode.apply_dynamic_traits`. Add `getattr(b, "slippery_immunity_timer", 0.0) <= 0`.
   - Also add them to the `booster_kinds` arrays everywhere.

6. **Generate Ideas**
   - Create 2 new JSON files in `src/ideas/`.

7. **Pre-commit Steps**
   - Run `pre_commit_instructions` and follow them.
