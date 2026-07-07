1. **Modify `src/system/crowd_system.py` using `replace_with_git_merge_diff`**:
   - In `__init__`: Add `self.underdog_team = None`, `self.match_started = False`, and `self.match_ended = False`.
   - In `tick()`: Add a call to `self._check_bets_and_winner(balls, tick)` before `self._update_excitement(tick)`.
   - Add `_check_bets_and_winner(self, balls, tick)` method:
     - Check if `not self.match_started` and `len(balls) > 1`: Initialize `match_started = True`. Count initial balls per team. If multiple teams exist, determine the underdog (team with the fewest members). Set `self.underdog_team`. Emit a `crowd_bet` event.
     - Check if `self.match_started and not self.match_ended`: Count alive teams. If only one team is left and it's `self.underdog_team`:
       - Set `self.match_ended = True`.
       - Boost `self.excitement_level += 50.0`.
       - Emit `crowd_cheer` and `audio_event`.
       - Retrieve the `profile_manager` from `self.world` (e.g., `if hasattr(self.world, 'profile_manager'): pm = self.world.profile_manager`). If present, grant the prestige bonus by modifying `pm.data["prestige_tokens"] = pm.data.get("prestige_tokens", 0) + 10` and `pm.save()`.
2. **Verify Changes in Python**:
   - Use `read_file` or `run_in_bash_session` to check `src/system/crowd_system.py` structure.
3. **Modify `src/system/crowd_system.gd` using `replace_with_git_merge_diff`**:
   - Add variables `var underdog_team = ""` and `var match_started = false` and `var match_ended = false`.
   - In `tick()`: Call `_check_bets_and_winner(balls, current_tick)`.
   - Add `func _check_bets_and_winner(balls: Array, current_tick: int):`
     - If `not match_started and balls.size() > 1`: Count teams, find the underdog (smallest team count). Set `underdog_team = ...` and `match_started = true`. Add `vote_started` or `crowd_bet` events using `world.add_event` if `world` has `add_event`.
     - If `match_started and not match_ended`: Count alive teams. If only one alive team and it equals `underdog_team`:
       - Set `match_ended = true`.
       - `excitement_level += 50.0`.
       - Emits cheers and audio using `world.add_event`.
       - Fetch `profile_manager` via `if world != null and world.has_method('get_profile_manager'): var pm = world.call('get_profile_manager')`. Modify prestige tokens: `if pm != null and pm.data != null: pm.data["prestige_tokens"] = pm.data.get("prestige_tokens", 0) + 10; pm.save()`.
4. **Verify Changes in GDScript**:
   - Use `read_file` or `run_in_bash_session` to check `src/system/crowd_system.gd`.
5. **Run tests across the system to ensure no regressions**:
   - Use `run_in_bash_session` to run `PYTHONPATH=src pytest`.
6. **Pre-commit step**:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
7. **Submit**:
   - Submit changes.
