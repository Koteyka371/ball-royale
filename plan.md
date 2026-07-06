1. **Understand Goal**: Add placeable energy shields (barrier/wall) that block projectiles (and hitscan attacks), block vision, but allow allies to pass through.
2. **Implement hazard generation in skill `energy_barrier` (Python and GDScript)**
    - Check if it's placed via skill or item. We can add a skill `energy_barrier`.
    - Modify `_use_skill` in `src/ai/action.py` and `src/ai/action.gd`.
    - Add logic for `elif skill_name == "energy_barrier":`
    - Creates a new Hazard of `kind="energy_barrier"` at `self.ball.x`, `self.ball.y` or offset toward nearest enemy.
    - Set `duration=5.0`, `team=self.ball.team`. It should probably be a line/circle hazard.
3. **Modify `_get_enemies_internal` for Vision Blocking**
    - In `src/ai/action.py` and `src/ai/action.gd`.
    - Inside `is_visible(enemy)`, trace line from `self.ball` to `enemy`. If line intersects `energy_barrier` (where `team != self.ball.team`? Or just always block vision except for allies?), block vision. Let's say it blocks vision of enemies if there is a barrier in between. Actually, the prompt says "block vision but allow allies to pass through". Vision of what? Usually, if an enemy is behind the barrier, you can't see them. We can do line-circle intersection.
4. **Modify `_attempt_damage` and projectile logic**
    - The prompt mentions "block projectiles". Currently, melee and hitscan/projectiles might just use `_attempt_damage`.
    - In `_attempt_damage`, we can check if it's a ranged attack (`dist > a_rad + t_rad + 20.0`). If it is, check if line intersects an enemy `energy_barrier`.
5. **Modify `execute` physics loop for barrier collision**
    - In `src/ai/action.py` and `src/ai/action.gd`.
    - Under `elif hazard.kind == "energy_barrier":`
    - If `self.ball.team != hazard.team` (enemy), act as a wall.
    - If `self.ball.team == hazard.team` (ally), ignore collision (allow pass through).
6. **Add test cases**
    - `src/ai/test_energy_barrier.py` to verify:
        - `_use_skill` creates the barrier.
        - Enemy movement is blocked by barrier.
        - Ally movement is not blocked.
        - Vision is blocked across the barrier.
        - Ranged attacks are blocked by the barrier.
7. **Write Ideas to JSON**
    - 2 new ideas.
8. **Pre-commit and submit**
