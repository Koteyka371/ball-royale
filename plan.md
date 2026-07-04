1. **Modify `src/ai/game_modes.py`:**
   - Update `WeatherChaosMode.tick()` (around line 614 where `elif self.weather == "sandstorm":` occurs).
   - Before applying the perception reduction, check if the ball is near a `shelter` hazard or a `flare` hazard. Wait, does `shelter` or `flare` logic need to iterate through hazards? Yes. So we can pre-compute a list of `shelter` and `flare` positions or check for each ball.
   - Wait! The same mode `WeatherChaosMode` exists in `src/ai/game_modes.py` and `src/ai/game_modes.gd`. However, `test_weather_mode.py` covers `src/ai/game_modes.py`.
   - But wait! `is_earth` logic seems to be missing from `src/ai/game_modes.py` in `sandstorm`. It only checks if it's `sand_elemental`. I need to change it to check if `traits` include `earth` or if it is `sand_elemental` or an earth class. Let me check the python `WeatherChaosMode` logic to see if we have `is_earth` available.

2. **Modify `src/ai/game_modes.gd`:**
   - There are TWO places where `elif self.weather == "sandstorm":` or `elif weather == "sandstorm":` occur.
   - The first is around line 700:
     ```gdscript
                elif self.weather == "sandstorm":
     ```
     This one already uses `is_earth` for HP drain. We just need to add the `shelter/flare` vision check.
   - The second is around line 2080:
     ```gdscript
				elif weather == "sandstorm":
     ```
     This one doesn't seem to use `is_earth` (it just drops HP). We should add `is_earth` to it, and also the `shelter/flare` vision check.

3. **Details of Python changes (`src/ai/game_modes.py`):**
   ```python
   # Inside WeatherChaosMode.tick() loop for balls:
            elif self.weather == "sandstorm":
                b.cosmetic = "dust_mask"

                # Precompute traits / is_earth if not already
                b_type = getattr(b, "ball_type", "")
                is_earth = getattr(b, "traits", []) and "earth" in getattr(b, "traits", [])
                if b_type in ["tank", "druid", "juggernaut"]:
                    is_earth = True

                if getattr(b, "ball_type", "") == "sand_elemental":
                    b.speed = b.base_speed * 1.2
                    b.damage = b.base_damage
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    # check shelter/flare
                    near_shelter_or_flare = False
                    if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                        for h in world.arena.hazards:
                            if getattr(h, "kind", "") in ["shelter", "flare"]:
                                dist_sq = (getattr(h, "x", 0) - getattr(b, "x", 0))**2 + (getattr(h, "y", 0) - getattr(b, "y", 0))**2
                                if dist_sq <= getattr(h, "radius", 0)**2:
                                    near_shelter_or_flare = True
                                    break

                    if near_shelter_or_flare:
                        b.perception_radius = getattr(b, "base_perception_radius", 250.0)
                    else:
                        b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.3

                    b.speed = b.base_speed * 0.7 # Hard to move
                    b.damage = b.base_damage
                    b.dash_range_mult = 0.5
                    b.steering_mult = 0.5
                    if getattr(b, "ball_type", "") in ["trickster", "phantom", "mimic"]:
                        ... # mirage logic

                    # dot damage
                    if not hasattr(b, "sandstorm_timer"):
                        b.sandstorm_timer = 0.0
                    b.sandstorm_timer += delta
                    if b.sandstorm_timer >= 1.0:
                        b.sandstorm_timer = 0.0
                        if hasattr(b, "hp") and not is_earth:
                            b.hp -= 1.0 # 1 damage per sec
                    # Random lightning strikes
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta and not is_earth:
                        # Struck by lightning!
                        b.hp = getattr(b, "hp", 100) - 20
                b.attack_accuracy = 0.5
   ```

4. **Testing:**
   - I'll update the test `test_weather_mode_sandstorm_shelter.py` and import it in my plan test loop.
   - Run python `pytest`.

5. **Commit and create ideas.**
