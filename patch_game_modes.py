with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

setup_search = """    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []"""

setup_insert = """

        arena_w = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_h = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.altars = [{"x": arena_w/2, "y": arena_h/2, "radius": 150.0, "capture_progress": 0.0, "owner": None, "sabotaged_by": None}]
        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for b in valid_balls:
            b.team = b.ball_type
            if not hasattr(b, "base_perception_radius"):
                b.base_perception_radius = getattr(b, "perception_radius", 250.0)
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)"""

idx = content.find(setup_search)
if idx != -1:
    idx += len(setup_search)
    content = content[:idx] + setup_insert + content[idx:]
    with open("src/ai/game_modes.py", "w") as f:
        f.write(content)
    print("Patched setup in Python")
else:
    print("Failed to find setup in Python")

tick_search = """    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        self.apply_dynamic_traits(world, balls, delta)
        for b in balls:
            if not getattr(b, "alive", False):
                continue

        for b in balls:
            w_timer = getattr(b, "weather_immunity_timer", 0.0)
            if isinstance(w_timer, (int, float)) and w_timer > 0.0:
                b.weather_immunity_timer = max(0.0, w_timer - delta)
            w_timer = getattr(b, 'weather_immunity_timer', 0.0)
            is_immune = (w_timer > 0.0) if isinstance(w_timer, (int, float)) else False
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta"""

tick_insert = """
        if not hasattr(self, "altars"):
            self.altars = []
        for altar in self.altars:
            teams_present = {}
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    bx = getattr(b, "x", 0.0)
                    by = getattr(b, "y", 0.0)
                    dist_sq = (bx - altar["x"])**2 + (by - altar["y"])**2
                    if dist_sq <= altar["radius"]**2:
                        team = getattr(b, "team", getattr(b, "ball_type", None))
                        teams_present[team] = teams_present.get(team, 0) + 1

                        if hasattr(b, "inventory") and "negative_modifier" in b.inventory:
                            b.inventory.remove("negative_modifier")
                            altar["sabotaged_by"] = team
                            if hasattr(world, "add_event"):
                                world.add_event("altar_sabotaged", {"team": team})

                        saboteur = altar.get("sabotaged_by")
                        if saboteur and saboteur != team:
                            b.hp = max(0.0, getattr(b, "hp", 100.0) - 15.0 * delta)

            if teams_present:
                max_team = max(teams_present, key=teams_present.get)
                # Check if it is a clear majority
                is_tie = sum(1 for t, v in teams_present.items() if v == teams_present[max_team]) > 1
                if not is_tie:
                    if altar["owner"] == max_team:
                        altar["capture_progress"] = min(100.0, altar["capture_progress"] + 20.0 * delta)
                    else:
                        altar["capture_progress"] -= 20.0 * delta
                        if altar["capture_progress"] <= 0:
                            altar["owner"] = max_team
                            altar["capture_progress"] = 0.0
                            # Weather change triggered
                            self.weather_timer = 0.0
                            ctype = max_team
                            pref = "clear"
                            if ctype in ["elementalist"]: pref = "thunderstorm"
                            elif ctype in ["druid", "healer", "swamp"]: pref = "rain"
                            elif ctype in ["rogue", "assassin", "stealth"]: pref = "fog"
                            elif ctype in ["mage", "conjurer"]: pref = "snow"
                            elif ctype in ["speed", "scout"]: pref = "wind"
                            elif ctype in ["tank", "brawler"]: pref = "heatwave"
                            elif ctype in ["swarm"]: pref = "sandstorm"
                            else: pref = "thunderstorm"

                            if self.weather != pref:
                                self.weather = pref
                                if hasattr(world, "add_event"):
                                    world.add_event("weather_change", {"weather": self.weather})
                                if self.weather == "wind":
                                    rnd = getattr(self, "random", __import__("random"))
                                    self.wind_dx = rnd.uniform(-50.0, 50.0)
                                    self.wind_dy = rnd.uniform(-50.0, 50.0)

            # Decay progress if nobody is there
            if not teams_present:
                altar["capture_progress"] = max(0.0, altar["capture_progress"] - 5.0 * delta)
                if altar["capture_progress"] == 0:
                    altar["owner"] = None

        if not hasattr(self, 'weather'): self.weather = 'clear'
        if not hasattr(self, 'weather_timer'): self.weather_timer = 0.0
        self.weather_timer += delta
        if self.weather_timer > 10.0:
            self.weather_timer = 0.0
            weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm", "heatwave", "blizzard", "magnetic_storm", "meteor_shower"]
            import random
            rnd = getattr(self, "random", random)
            old_weather = self.weather
            self.weather = getattr(self, "next_weather", rnd.choice(weathers))
            self.next_weather = rnd.choice(weathers)
            self.weather_warning_issued = False

            if old_weather != self.weather:
                for b in balls:
                    if getattr(b, "forecast_booster_active", False):
                        b.forecast_booster_active = False
                        b.weather_immunity_timer = 15.0
                    b.forecast_warning_issued = False
                if hasattr(world, "add_event"):
                    world.add_event("weather_change", {"weather": self.weather})

            if self.weather == "wind":
                self.wind_dx = rnd.uniform(-50.0, 50.0)
                self.wind_dy = rnd.uniform(-50.0, 50.0)

        if hasattr(world, "arena"):
            world.arena.is_foggy = (self.weather in ["fog", "snow", "blizzard"])
            world.arena.is_raining = (self.weather in ["rain", "thunderstorm"])
            world.arena.is_sandstorming = (self.weather == "sandstorm")
            world.arena.is_snowing = (self.weather in ["snow", "blizzard"])
            world.arena.is_heatwave = (self.weather == "heatwave")
            world.arena.is_lunar_eclipse = (self.weather == "lunar_eclipse")
            world.arena.is_eclipse = (self.weather == "lunar_eclipse")
            world.arena.wind_dx = getattr(self, "wind_dx", 0.0) if self.weather == "wind" else 0.0
            world.arena.wind_dy = getattr(self, "wind_dy", 0.0) if self.weather == "wind" else 0.0"""

idx = content.find(tick_search)
if idx != -1:
    idx += len(tick_search)
    content = content[:idx] + tick_insert + content[idx:]
    with open("src/ai/game_modes.py", "w") as f:
        f.write(content)
    print("Patched tick in Python for BattleRoyaleMode")
else:
    print("Failed to find tick in Python for BattleRoyaleMode")
