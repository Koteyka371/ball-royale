1. Add new items in Python (`src/ai/action.py`) logic:
   - Add new weapon attachment boosters:
     - `silencer_attachment`: Grants `silencer_timer = 15.0`, setting `is_silenced = True` and reducing perception by others.
     - `extended_mag_attachment`: Grants `extended_mag_timer = 15.0`, which we can use to reduce `attack_timer` faster or give more ammo/projectiles.
     - `modified_scope_attachment`: Grants `modified_scope_timer = 15.0`, significantly increasing `perception_radius` (similar to `vision_booster`) and maybe increasing attack range/damage slightly.
   - When one of these is collected in `_collect_booster`, apply the respective effect and remove it from `hazards` and `boosters`.

2. Add new items in GDScript (`src/ai/action.gd`) logic:
   - Replicate the exact same collection and effect logic for the new weapon attachments in `_collect_booster`.

3. Update core execution loops (`execute` in `action.py` and `action.gd`):
   - Add timer ticks for the new attachments.
   - Apply the effects (e.g., if `silencer_timer` > 0, hide from map or make less visible. In this simulation, this would mean ignoring them in `_get_enemies()` or `_get_perception_radius` mechanics, or adding a flag `is_silenced = True`).
   - Actually, wait, `silencer` reduces visibility on map. We can add a check in `get_nearby_entities` or just rely on a boolean `is_silenced` which other components check.

4. Add a test file `test_weapon_attachments.py` in `src/tests/` or `src/ai/` to ensure these boosters are properly collected and their timers apply.

5. Execute tests and pre-commit checks.
6. Commit and prepare ideas.
