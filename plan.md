1. **Create the `PhysicsAnomalyEventMode` class in `src/ai/game_modes.py` and `src/ai/game_modes.gd`.**
   - The class inherits from `GameMode`.
   - Setup `name = "Physics Anomaly Event"`.
   - Setup `description = "A random event that alters the physics of the arena. Projectiles curve, movement speed is affected depending on the direction of travel relative to the anomaly's center."`
   - Logic: similar to Reverse Gravity, it has an `event_timer` and `event_active` state.
   - Every tick, if the event is active, it affects all balls in `tick`:
     - Calculate vector to the anomaly center (cx, cy).
     - Calculate ball movement vector (vx, vy).
     - Calculate dot product. If positive (moving towards), increase speed. If negative (moving away), decrease speed.
     - Since we just need to set a speed multiplier, we can set `b.speed_multiplier` or adjust `vx`, `vy` directly. Or simply set a custom meta property `b.anomaly_speed_mod`.
     - Actually, the easiest way to affect movement speed is to calculate the dot product and directly modify the ball's velocity in the `tick` loop of the GameMode. But wait, `action.py` overwrites `vx`, `vy` based on `speed` every frame. So it's better to modify a `speed` multiplier.
     - Wait, memory says: "When implementing custom physics in game_modes.py or game_modes.gd that apply both velocity-based speed multipliers and trajectory curvature in the same tick(), calculate the directional dot product before modifying the velocity (vx, vy) to ensure the speed multiplier is based on the original trajectory."
     - Let's do that in `PhysicsAnomalyEventMode.tick()`.

2. **Add the Game Mode to the `GAME_MODES` dictionary.**
   - In `src/ai/game_modes.py` and `.gd`.

3. **Modify `_attempt_damage` in `src/ai/action.py` and `.gd` to make projectiles curve.**
   - If `is_ranged` is true and `PhysicsAnomalyEventMode` is active:
     - Instead of instantaneous damage, append to `suspended_projectiles`.
     - Wait, in memory: "To delay instantaneous combat calculations (such as ranged attacks in _attempt_damage), append the event data and a timer to a list (e.g., suspended_projectiles) on the attacker entity, and decrement the timer in the main execute() loop before re-triggering the calculation."
     - So we add it to `suspended_projectiles`. But the task says "Projectiles curve".
     - To make them curve, we can actually modify the projectile's trajectory over time... but since `suspended_projectiles` only store a target and a timer, how do we curve it?
     - What if we add `x`, `y`, `vx`, `vy` to the suspended projectile? And in `execute()`, update `x`, `y` and curve `vx`, `vy`. When it reaches the target or timer expires, deal damage.
     - Wait, `_attempt_damage` doesn't know about `x` and `y` when it resumes. We can just say: if `world.game_mode` is `PhysicsAnomalyEventMode`, `_attempt_damage` has a chance to miss, or we actually implement the curving projectile logic.
     - Let's check `_attempt_damage`.

4. **Implement projectile curving in `suspended_projectiles` logic in `action.py` and `action.gd`.**
   - When appending to `suspended_projectiles` for this event, add `x`, `y`, `vx`, `vy`.
   - In `execute`, when iterating `suspended_projectiles`:
     - If it has `x`, `y`, `vx`, `vy`:
       - Update `x`, `y` with `vx`, `vy` * delta.
       - Apply a perpendicular force to `vx`, `vy` (curving).
       - Check distance to target. If close, hit target (deal damage).
       - If timer <= 0, remove (missed).

5. **Wait, what if we just add a chance to miss and a visual effect of a curved projectile?**
   - The task says "Projectiles curve". The best way is to actually simulate them in `suspended_projectiles`.

6. **Add tests.**
   - `test_physics_anomaly_event.py` in `src/ai/` to verify speed multiplier and projectile curving.

7. **Complete pre commit steps.**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.

8. **Submit the PR.**
