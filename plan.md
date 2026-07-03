1. **Add `terrain_type` property to `ProceduralArena`**
   - Update `src/arena/procedural_arena.py` so `ProceduralArena.__init__` adds `self.terrain_type = getattr(self, "terrain_type", "grass")`. For random chance to be dirt/sand, we can just pick it: `self.terrain_type = random.choice(["grass", "dirt", "sand", "stone"])`.

2. **Add Mud logic in `Action` when raining and on dirt/sand in Python (`src/ai/action.py`)**
   - In `Action.execute()`, check `if getattr(self.world.arena, "is_raining", False) and getattr(self.world.arena, "terrain_type", "grass") in ["dirt", "sand"]:`
   - Find "Weather friction" section.
   - If unit does not have `swamp` or `water` trait (which means `ball_type` in `["elementalist", "healer", "trickster"]` or `ball_type == "swamp_monster"`, or just `ball_type` having 'swamp' or 'water'), apply a slowdown.
   - To apply the mud slowdown, multiply `self.ball.speed` by 0.5 or set a mud modifier during the frame. The easiest way is `self.ball.speed *= 0.5`.

3. **Add Mud logic in `Action` when raining and on dirt/sand in GDScript (`src/ai/action.gd`)**
   - Similar to python, but in GDScript we check `world.arena.get("is_raining") == true` and `world.arena.get("terrain_type") in ["dirt", "sand"]`.
   - Apply slowdown to `my_ball.speed` if not swamp/water type.

4. **Verify changes and write tests**
   - Write `test_mud_terrain.py` to ensure rain + dirt/sand slows down normal units but not water/swamp units.
   - Run tests.

5. **Pre-commit steps**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

6. **Submit PR**
   - Commit and submit.

7. **Create Idea JSONs**
   - Create 2 new JSON files in `ideas/` directory.
