1. **Modify `src/ai/game_modes.py`:**
   - Update `BattleRoyaleMode` and `WeatherChaosMode` (and anywhere else) where `self.weather == "rain"` spawns a `mud_pit` (`quicksand`). Only spawn it if the arena is a "dirt/sand" arena.
   - Example check:
     ```python
     arena_name = getattr(world.arena, "__class__", type(world.arena)).__name__.lower()
     is_dirt_sand = "sand" in arena_name or "dirt" in arena_name or "summer" in arena_name or getattr(world.arena, "is_sandstorming", False) or getattr(world.arena, "is_heatwave", False)
     if is_dirt_sand and getattr(self, "random", __import__("random")).random() < 0.05 * delta:
         # spawn mud pit...
     ```
   - Also, for the `b.speed = b.base_speed * 0.8` effect of rain, exempt units with a `water` or `swamp` trait.

2. **Modify `src/ai/action.py`:**
   - Update the `quicksand` hazard logic.
   - Example check:
     ```python
     b_type = str(getattr(self.ball, "ball_type", "")).lower()
     traits = getattr(self.ball, "traits", [])
     has_water_trait = "water" in b_type or "swamp" in b_type or "water" in traits or "swamp" in traits
     if not has_water_trait:
         # Apply quicksand slow debuff
     ```

3. **Modify `src/ai/game_modes.gd` and `src/ai/action.gd`:**
   - Implement the exact same logic in GDScript.
   - For GDScript trait check:
     ```gdscript
     var has_water_trait = false
     var b_type = ""
     if "ball_type" in b: b_type = str(b.ball_type).to_lower()
     elif b.has_method("get_meta") and b.has_meta("ball_type"): b_type = str(b.get_meta("ball_type")).to_lower()

     var traits = []
     if "traits" in b: traits = b.traits
     elif b.has_method("get_meta") and b.has_meta("traits"): traits = b.get_meta("traits")

     if "water" in b_type or "swamp" in b_type:
         has_water_trait = true
     elif typeof(traits) == TYPE_ARRAY:
         for t in traits:
             if "water" in str(t).to_lower() or "swamp" in str(t).to_lower():
                 has_water_trait = true
                 break
     ```

4. **Testing and Pre-commit:**
   - Run tests.
   - Pre-commit check.
   - Commit and submit.
