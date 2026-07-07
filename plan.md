The objective is to allow the crowd to place bets on which team or player will win. If the underdog wins, the crowd's excitement spikes significantly more, and the winning team gets a huge prestige bonus.

**Implementation Plan:**

1. **Modify `CrowdSystem` in `src/system/crowd_system.py`**
   - In `__init__`: Add properties `self.underdog = None`, `self.match_started = False`.
   - In `tick()`: Detect match start (e.g., when balls populate for the first time). When `not self.match_started` and `len(balls) > 1`:
     - Determine initial team sizes or ball HP to find an `underdog`.
     - The underdog is the team or player with the smallest representation or lowest stats (e.g. if teams are unequal, the smaller team; if teams are equal, pick the one with lowest total HP, or randomly if perfectly balanced but try to find a quantifiable underdog). Let's base it on team size or count of players per team/type.
     - Emit an event like `crowd_bet` saying "The crowd has placed their bets on [not underdog] to win!".
     - Set `self.match_started = True`.
     - Track `self.underdog_team`.
   - In `tick()` or a new method `_check_match_end(balls, tick)`: We need a way to detect when a team wins inside `CrowdSystem`. We can do this by checking `alive` counts (similar to how team wipe works), and if only one team is left (the winner).
   - Alternatively, add an explicit method `on_match_end(winner_team, balls)` to `CrowdSystem`, but since `CrowdSystem` is usually ticked and independent, observing the alive state is standard. If all remaining alive balls belong to `self.underdog_team` and other teams are dead (and there were other teams):
     - Trigger underdog win logic:
       - `self.excitement_level += 50.0`
       - Emit `crowd_cheer` and `audio_event` for underdog victory.
       - Emit a `give_prestige` event or directly modify `ProfileManager` if accessible, but events are safer in `world.add_event`. In `simulate_battle.py`, we can handle this event to grant prestige. Better yet, since `ProfileManager` is not in `world` by default, `CrowdSystem` can't easily import `ProfileManager` without side effects in tests? Wait, `ProfileManager` is in `system.profile`. `CrowdSystem` could import it, but `ProfileManager("profile.json")` is standard.

Let's look at `CrowdSystem` in Python and GDScript.

2. **Modify `CrowdSystem` in `src/system/crowd_system.gd`**
   - Translate the same logic to `crowd_system.gd`.
   - Detect start -> determine underdog.
   - Detect win -> give prestige / excitement.

3. **Verify how ProfileManager is handled in `CrowdSystem`**
   - If `world` can process `give_prestige_bonus`, great, but `CrowdSystem` should just grant it directly:
   ```python
   try:
       from system.profile import ProfileManager
       pm = ProfileManager("profile.json")
       pm.data["prestige_tokens"] = pm.data.get("prestige_tokens", 0) + 10
       pm.save()
   except Exception:
       pass
   ```
   - We will implement this directly when an underdog win is detected in `crowd_system.py` and `crowd_system.gd` (using `ProfileManager.new()` or global `ProfileManager`).

Let's do a request_plan_review with this approach.
