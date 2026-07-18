1. **Modify `src/ai/action.py`**
   - Locate the logic that handles the explosion of Trickster's decoy (`if getattr(self.ball, "is_decoy_clone", False):` block around line 3467).
   - In the explosion logic, right after dealing damage, check if the enemy was damaged and if so, apply blindness (set `is_blinded = True`, `blindness_timer = 3.0` and handle `perception_radius`).
   - We need to handle this inside the `dist <= 120.0:` block:
     ```python
     if not getattr(b, "is_blinded", False):
         b.is_blinded = True
         b.blindness_timer = 3.0
         if not hasattr(b, "base_perception_radius"):
             b.base_perception_radius = getattr(b, "perception_radius", 100.0)
         b.perception_radius = b.base_perception_radius * 0.5
     ```

2. **Modify `src/ai/action.gd`**
   - Locate the logic handling `is_decoy_clone` death and explosion (`if is_decoy_clone:` block around line 4876).
   - In the loop for `b` in `world.balls`, when dealing damage within the 120.0 radius, apply blindness to `b`.

3. **Add Tests**
   - In `src/ai/test_trickster_decoy.py`, add `test_trickster_decoy_explosion_blindness()`. This test should create a decoy, wait for it to explode by manually setting hp to 0, and ensure an enemy within the explosion radius is damaged and blinded.

4. **Add Ideas JSON Files**
   - Create `ideas/idea_idea-1072_1.json` and `ideas/idea_idea-1072_2.json`.

5. **Pre-commit Instructions**
   - Run verification and check metrics.
