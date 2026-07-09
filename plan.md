1. Add `slow_motion_zone` logic to python backend in `src/ai/action.py`.
   - Update `action.py` in the `_apply_hazards` or similar loop processing hazards in `execute` where we iterate `self.world.arena.hazards` and apply things.
   - When inside a `slow_motion_zone` hazard:
     - Halve the entity's speed (we can modify `b.speed` or use a multiplier or just do `delta *= 0.5` similarly to `temporal_rift` which just does `delta *= time_scale`). Wait, the prompt says "Any entities entering the zone have their speed and cooldown reduction halved, while projectiles passing through it stay suspended for a set duration before resuming travel."
     - Actually, "speed and cooldown reduction halved".
     - So `self.ball.speed` gets multiplied by 0.5, or we can use `cooldown_mult`. Let's just manually apply `self.ball.speed *= 0.5` and `cooldown_mult *= 0.5`. Or maybe we can just create a new hazard kind `slow_motion_zone`.
   - Projectiles: Ball Royale doesn't have a rigid `Projectile` class, but there are projectile-like hazards (e.g. `explosive_barrel`, `shrapnel`, `homing_missile`?) Wait, the prompt specifies "while projectiles passing through it stay suspended for a set duration before resuming travel". Maybe we need to track if something is a projectile? We can look at hazards that have a `vx` and `vy` or a specific kind, like `shrapnel`, `thrown_status_absorber`, `homing_missile`, `local_tornado`, `orbital_debris` etc. and suspend them? Or perhaps there is a `projectile` type we can identify.

Let me check `src/ai/game_modes.py` to see what kind of hazards are treated as projectiles. Or I can just check if `hasattr(hazard, 'is_projectile')` or `hazard.kind in ["shrapnel", "homing_missile", "thrown_status_absorber"]`. We can add a `suspension_timer` to hazards that enter the zone.

2. Add same logic to `src/ai/action.gd`.
3. Create tests in `src/ai/test_slow_motion_zone.py`.
4. Generate ideas.
