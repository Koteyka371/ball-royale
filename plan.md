1. **Analyze Ninja Flank Logic Requirements:**
   - Modify `_chase` and `_attack` methods in Python (`src/ai/action.py`) and GDScript (`src/ai/action.gd`) to handle flank logic for Ninja.
   - When `b_type == "ninja"`, calculate the target's movement direction. The "back" position is the opposite of the target's movement direction relative to the target's position.
   - Steer the Ninja towards this "back" position, rather than moving directly to the target.

2. **Implement in `action.py` (`_chase`)**:
   ```python
   # before 'nx = target_dx / dist_to_target'
   if b_type_chase == "ninja":
       tvx = getattr(target, "vx", 0.0)
       tvy = getattr(target, "vy", 0.0)
       tv_dist_sq = tvx*tvx + tvy*tvy
       if tv_dist_sq > 0.0001:
           tv_dist = math.sqrt(tv_dist_sq)
           # target is moving, the back is in the opposite direction of velocity
           back_x = target.x - (tvx / tv_dist) * (target_radius + ball_radius + 5.0)
           back_y = target.y - (tvy / tv_dist) * (target_radius + ball_radius + 5.0)
           bdx = back_x - self.ball.x
           bdy = back_y - self.ball.y
           b_dist = math.sqrt(bdx*bdx + bdy*bdy)
           if b_dist > 0.01:
               nx = bdx / b_dist
               ny = bdy / b_dist
       else:
           nx = target_dx / dist_to_target
           ny = target_dy / dist_to_target
   else:
       nx = target_dx / dist_to_target
       ny = target_dy / dist_to_target
   ```
   Do the similar thing in `_attack`.

3. **Implement in `action.gd` (`_chase` & `_attack`)**:
   Apply equivalent changes.

4. **Testing and Verification**:
   - Write a unit test specifically for Ninja to confirm it moves to the target's back when the target is moving.
   - Run tests: `PYTHONPATH=src DISABLE_NN_OVERRIDE=1 pytest tests/`
