1. **Understand the Goal**: Create a mutator where balls constantly take damage over time, unless they collect temporary immune boosters spawning around the map.

2. **Analysis**:
   - We need to create a new `GameMode` subclass (e.g., `ImmuneBoosterMode` or `ToxicZoneMode` or similar). Let's call it `ToxicBoostersMode`.
   - The mode will have a `tick` function where:
     - Balls constantly take damage over time (e.g. `b.hp -= damage_rate * delta`).
     - Unless they have a buff, e.g. `immune_timer > 0`. If they have the buff, we decrement the timer: `b.immune_timer -= delta`.
     - We spawn immune boosters around the map. `booster = {"id": ..., "x": x, "y": y, "ball_type": "booster", "kind": "immune_booster"}`. We append them to `world.boosters` periodically.
     - When a ball collects an `immune_booster` (we might need to intercept the collection logic, or just handle collision manually inside the game mode `tick`), we set `b.immune_timer = X`.
     - But wait, `action.py` and `action.gd` handle booster collection. Let's look at `_collect_booster`. It checks `b_type == "booster"`. If `getattr(nearest, "kind", None) == "immune_booster"`, it could set `b.immune_timer` there, OR we can handle it directly in the mode's `tick` checking distances between balls and boosters. Handling in `tick` is safer and doesn't clutter `action.py` if we don't have to, but since `action.py` actually *moves* the balls to the booster, we should define it as a valid booster. `action.py` handles removing boosters when close enough via `self.world._collect_booster` OR just moving towards them. Wait, if it doesn't match specific kinds, it does:
       `if hasattr(self.world, "_collect_booster"): self.world._collect_booster(self.ball, nearest)`
     - Let's check `_collect_booster` in `action.py` again.

3. **Check `action.py` booster collection logic**:
   - `if dist <= ball_radius + 10:`
     - `if getattr(nearest, "kind", None) == "drone_item": ...`
     - `elif getattr(nearest, "kind", None) == "speed_booster": ...`
     - `elif getattr(nearest, "kind", None) == "shield_booster": ...`
     - `elif getattr(nearest, "kind", None) == "fake_booster": ...`
     - `else:`
       `if hasattr(self.world, "_collect_booster"): self.world._collect_booster(self.ball, nearest)`
   - So if we define our own boosters, we can handle the collection logic in the world's `_collect_booster` method. Wait, does `ToxicBoostersMode` have access to `world._collect_booster`? The `world` object would need that method. But we can just handle the collision check in our GameMode `tick`! That's how `CaptureTheFlagMode` does it maybe? No, `action.py` only removes `drone_item`, `fake_booster`. For others, it calls `world._collect_booster(self.ball, nearest)`. If `world` doesn't have it, the booster is NOT removed.

   So we MUST add support for `immune_booster` in `action.py` and `action.gd` OR we just do manual collision checks in `ToxicBoostersMode.tick` AND manually remove the booster. If we do it in `tick`, balls with `collect_booster` action will move towards it, reach it, and in the next tick our Mode will see they are close, grant the buff, and remove the booster. The ball will then stop trying to collect it because it's gone.
   Let's do manual collision in `GameMode.tick`! Wait, it's actually easier to just check collisions in the GameMode `tick` like we would do for hazards.

4. **New GameMode**: `ToxicBoostersMode` (or `BoosterFrenzyMode` etc.)
   - Name: "Toxic Boosters"
   - Description: "Balls take constant damage over time. Collect immune boosters to stay alive!"
   - `setup(self, world, balls)`:
     - `world.boosters = []` (ensure it exists)
     - `self.spawn_timer = 0.0`
   - `tick(self, world, balls, delta)`:
     - Apply damage to all alive, non-spectator balls, unless they have `immune_timer > 0`.
     - Decrement `immune_timer`.
     - Spawn boosters periodically.
     - Check collisions between balls and boosters of kind `immune_booster`. If colliding:
       - Give ball `immune_timer = 5.0`
       - Remove booster from `world.boosters`.

5. **Python (`src/ai/game_modes.py`)**:
   Add `ToxicBoostersMode` and register in `GAME_MODES`.

6. **GDScript (`src/ai/game_modes.gd`)**:
   Add `ToxicBoostersMode` and register in `GAME_MODES`.

7. **Tests**:
   - Write `test_toxic_boosters_mode.py` in `tests/` or `src/ai/` to ensure it applies damage, grants immunity, and removes boosters.

8. **Ideas Inbox**:
   - Create 2 new JSON ideas in `ideas/`.

9. **Pre-commit & Submit**:
   - Pre-commit steps.
   - Commit, push, PR.
