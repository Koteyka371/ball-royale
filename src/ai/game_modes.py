from arena import arena_types as ArenaTypes
from typing import List, Optional, Any

class GameMode:
    """Base class for all game modes."""
    def __init__(self):
        self.name = "Unknown"
        self.description = "Base game mode"

    def setup(self, world: Any, balls: List[Any]) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if hasattr(b, "sponsor"):
                if b.sponsor == "aggressor":
                    b.max_hp = getattr(b, "max_hp", 100.0) * 0.8
                    b.hp = min(getattr(b, "hp", 100.0), b.max_hp)
                elif b.sponsor == "juggernaut":
                    b.speed = getattr(b, "speed", 100.0) * 0.8
                    if hasattr(b, "base_speed"):
                        b.base_speed *= 0.8
                elif b.sponsor == "vampiric":
                    b.max_hp = getattr(b, "max_hp", 100.0) * 0.9
                    b.hp = min(getattr(b, "hp", 100.0), b.max_hp)
        """Called at the start of the battle to initialize mode-specific rules/teams."""

        # Apply global season modifier
        season_num = 1
        if hasattr(world, "leaderboard_manager"):
            season_num = world.leaderboard_manager.data.get("current_season", 1)
        elif hasattr(world, "profile_manager") and hasattr(world.profile_manager, "leaderboard_manager"):
            season_num = world.profile_manager.leaderboard_manager.data.get("current_season", 1)

        modifiers = {
            1: {"type": "global_speed", "value": 1.2},
            2: {"type": "global_damage", "value": 0.9},
            3: {"type": "global_hp", "value": 1.15},
            4: {"type": "global_cooldown", "value": 0.8},
        }

        mod_index = ((season_num - 1) % 4) + 1
        mod = modifiers[mod_index]

        # Apply weekly mutator
        import time
        current_week = int(time.time() / (7 * 24 * 3600))
        weekly_mutators = {
            0: {"type": "low_gravity"},
            1: {"type": "double_damage"},
            2: {"type": "high_speed"},
            3: {"type": "vampirism"},
        }
        week_index = current_week % len(weekly_mutators)
        week_mod = weekly_mutators[week_index]
        world.weekly_mutator = week_mod["type"]


        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.experience = getattr(b, "experience", 0.0)
                b.level = getattr(b, "level", 1)

                if mod["type"] == "global_speed":
                    b.base_speed = getattr(b, "base_speed", getattr(b, "speed", 100)) * mod["value"]
                    b.speed = getattr(b, "speed", 100) * mod["value"]
                elif mod["type"] == "global_damage":
                    b.base_damage = getattr(b, "base_damage", getattr(b, "damage", 10)) * mod["value"]
                    b.damage = getattr(b, "damage", 10) * mod["value"]
                elif mod["type"] == "global_hp":
                    b.max_hp = getattr(b, "max_hp", 100) * mod["value"]
                    b.hp = getattr(b, "hp", getattr(b, "max_hp", 100))
                elif mod["type"] == "global_cooldown":
                    b.cooldown_multiplier = getattr(b, "cooldown_multiplier", 1.0) * mod["value"]

                if week_mod["type"] == "double_damage":
                    b.base_damage = getattr(b, "base_damage", getattr(b, "damage", 10)) * 2.0
                    b.damage = getattr(b, "damage", 10) * 2.0
                elif week_mod["type"] == "high_speed":
                    b.base_speed = getattr(b, "base_speed", getattr(b, "speed", 100)) * 1.5
                    b.speed = getattr(b, "speed", 100) * 1.5
                elif week_mod["type"] == "vampirism":
                    b.lifesteal = getattr(b, "lifesteal", 0.0) + 0.5
                elif week_mod["type"] == "low_gravity":
                    b.mass = getattr(b, "mass", 1.0) * 0.5


    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        pass


    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        """Called every tick to check if there is a winner. Returns winner name or None."""
        return None


class DraftRoyaleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Draft Royale"
        self.description = "Before the match, teams take turns picking and banning ball types to create synergies and counter opponents."
        self.phase = "drafting"
        self.draft_state = "ban"
        self.turn_index = 0
        self.banned_types = []
        self.available_types = [
            "time_mage", "assassin", "berserker", "bomber", "brawler", "chaos", "conjurer", "druid",
            "elementalist", "guardian", "healer", "juggernaut", "king", "mage", "mimic",
            "monk", "necromancer", "ninja", "paladin", "phantom", "ranger", "rogue", "drone",
            "scout", "sniper", "swarm", "tank", "templar", "trickster", "vampire",
            "warlock", "warrior"
        ]
        self.team_rosters = {}
        self.teams = ["Team A", "Team B"]
        self.max_bans = 2
        self.picks_per_team = 5
        self.timer = 0.0
        import random
        self.random = random

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.teams = ["Team A", "Team B"]
        self.team_rosters = {"Team A": [], "Team B": []}
        self.banned_types = []
        self.draft_state = "ban"
        self.turn_index = 0
        self.phase = "drafting"
        self.timer = 0.0

        # Initialize balls as spectators during draft
        for b in balls:
            b.original_type = getattr(b, "ball_type", "tank")
            b.ball_type = "spectator"
            b.team = "spectator"
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)
            b.speed = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if self.phase == "drafting":
            self.timer += delta
            if self.timer > 0.5:
                self.timer = 0.0
                current_team = self.teams[self.turn_index % len(self.teams)]

                if self.draft_state == "ban":
                    if len(self.banned_types) < self.max_bans * len(self.teams):
                        choices = [t for t in self.available_types if t not in self.banned_types]
                        if choices:
                            ban = self.random.choice(choices)
                            self.banned_types.append(ban)
                        self.turn_index += 1

                        if len(self.banned_types) >= self.max_bans * len(self.teams):
                            self.draft_state = "pick"
                            self.turn_index = 0

                elif self.draft_state == "pick":
                    team_a_picks = len(self.team_rosters["Team A"])
                    team_b_picks = len(self.team_rosters["Team B"])

                    if team_a_picks < self.picks_per_team or team_b_picks < self.picks_per_team:
                        if len(self.team_rosters[current_team]) < self.picks_per_team:
                            picked_by_a = self.team_rosters["Team A"]
                            picked_by_b = self.team_rosters["Team B"]
                            choices = [t for t in self.available_types if t not in self.banned_types and t not in picked_by_a and t not in picked_by_b]
                            if not choices:
                                choices = [t for t in self.available_types if t not in self.banned_types]
                            if choices:
                                pick = self.random.choice(choices)
                                self.team_rosters[current_team].append(pick)
                        self.turn_index += 1
                    else:
                        self.phase = "combat"
                        self.start_combat(world, balls)
        else:
            # Combat phase
            for b in balls:
                if not getattr(b, "alive", False):
                    continue
                # Implement any combat specific ticks here if needed

    def start_combat(self, world: Any, balls: List[Any]) -> None:
        team_a_balls = [b for b in balls if getattr(b, "original_type", "") != "spectator"][:self.picks_per_team]
        team_b_balls = [b for b in balls if getattr(b, "original_type", "") != "spectator"][self.picks_per_team:self.picks_per_team*2]

        for i, b in enumerate(team_a_balls):
            if i < len(self.team_rosters["Team A"]):
                b.ball_type = self.team_rosters["Team A"][i]
                b.team = "Team A"
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.alive = True

        for i, b in enumerate(team_b_balls):
            if i < len(self.team_rosters["Team B"]):
                b.ball_type = self.team_rosters["Team B"][i]
                b.team = "Team B"
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.alive = True

        # Make remaining balls spectators
        for b in balls:
            if getattr(b, "team", "spectator") == "spectator":
                b.ball_type = "spectator"
                b.alive = False

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        if self.phase == "drafting":
            return None

        alive_a = sum(1 for b in balls if getattr(b, "alive", False) and getattr(b, "team", None) == "Team A")
        alive_b = sum(1 for b in balls if getattr(b, "alive", False) and getattr(b, "team", None) == "Team B")

        if alive_a > 0 and alive_b == 0:
            return "Team A"
        elif alive_b > 0 and alive_a == 0:
            return "Team B"
        elif alive_a == 0 and alive_b == 0:
            return "Draw"

        return None

class BattleRoyaleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Battle Royale"
        self.description = "Last man standing. Everyone for themselves. Includes dynamic weather."
        self.dark_phase_timer = 0.0
        self.is_dark_phase = False
        self.weather = "clear"
        self.weather_timer = 0.0
        self.next_weather = "clear"
        self.weather_warning_issued = False
        self.supply_drop_timer = 0.0
        import random
        self.random = random

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for i, b in enumerate(valid_balls):
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = False
            else:
                b.team = b.ball_type # Default behavior
                if not hasattr(b, "base_perception_radius"):
                    b.base_perception_radius = getattr(b, "perception_radius", 250.0)
                if not hasattr(b, "base_speed"):
                    b.base_speed = getattr(b, "speed", 100.0)
                if not hasattr(b, "base_damage"):
                    b.base_damage = getattr(b, "damage", 10.0)

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        # Weather logic
        controller = None
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "weather_control_timer", 0.0) > 0:
                controller = b
                break

        # Supply Drop Logic
        self.supply_drop_timer += delta
        if self.supply_drop_timer >= 15.0:
            self.supply_drop_timer = 0.0
            if hasattr(world, "boosters"):
                arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
                arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
                rnd = getattr(self, "random", __import__("random"))

                # Mock entity for booster
                class Booster:
                    def __init__(self, id, x, y, kind):
                        self.id = id
                        self.x = x
                        self.y = y
                        self.kind = kind
                        self.radius = 15.0
                        self.ball_type = "booster"
                        self.active = True

                booster_kinds = ["speed_booster", "damage_booster", "hp_booster", "vision_booster", "stamina_booster", "pull_booster", "nemesis_booster", "shadow_booster", "weather_scanner_item", "aura_booster"]
                chosen_kind = rnd.choice(booster_kinds)
                b_id = 9000 + len(world.boosters) + rnd.randint(0, 1000)
                b_x = rnd.uniform(100, arena_width - 100)
                b_y = rnd.uniform(100, arena_height - 100)
                new_booster = Booster(b_id, b_x, b_y, chosen_kind)
                world.boosters.append(new_booster)

                # Also add as a hazard for collision if needed
                if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                    class HazardBooster:
                        def __init__(self, id, x, y, radius, kind, damage):
                            self.id = id
                            self.x = x
                            self.y = y
                            self.radius = radius
                            self.kind = kind
                            self.damage = damage
                            self.active = True
                    world.arena.hazards.append(HazardBooster(b_id, b_x, b_y, 15.0, chosen_kind, 0.0))

                if hasattr(world, "add_event"):
                    world.add_event("supply_drop", {"message": f"A {chosen_kind} supply drop has appeared!"})

        if controller:
            self.weather_timer = 0.0
            ctype = getattr(controller, "ball_type", "default")
            pref = "clear"
            if ctype in ["elementalist"]: pref = "thunderstorm"
            elif ctype in ["druid", "healer"]: pref = "rain"
            elif ctype in ["rogue", "assassin", "stealth"]: pref = "fog"
            elif ctype in ["mage", "conjurer"]: pref = "snow"
            elif ctype in ["speed", "scout"]: pref = "wind"
            elif ctype in ["tank", "brawler"]: pref = "heatwave"
            elif ctype in ["swarm"]: pref = "sandstorm"
            else: pref = "thunderstorm" # Default for others picking it up

            old_weather = self.weather
            if old_weather != pref:
                self.weather = pref
                if hasattr(world, "add_event"):
                    world.add_event("weather_change", {"weather": self.weather})
                if self.weather == "wind":
                    rnd = getattr(self, "random", __import__("random"))
                    self.wind_dx = rnd.uniform(-50.0, 50.0)
                    self.wind_dy = rnd.uniform(-50.0, 50.0)
        else:
            self.weather_timer += delta
            if self.weather_timer > 15.0:
                self.weather_timer = 0.0
                weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm", "heatwave", "blizzard", "magnetic_storm"]
                rnd = getattr(self, "random", __import__("random"))
                old_weather = self.weather
                self.weather = rnd.choice(weathers)

                if old_weather != self.weather and hasattr(world, "add_event"):
                    world.add_event("weather_change", {"weather": self.weather})

                if self.weather == "wind":
                    self.wind_dx = rnd.uniform(-50.0, 50.0)
                    self.wind_dy = rnd.uniform(-50.0, 50.0)

        season_num = 1
        if hasattr(world, "leaderboard_manager"):
            season_num = world.leaderboard_manager.data.get("current_season", 1)
        elif hasattr(world, "profile_manager") and hasattr(world.profile_manager, "leaderboard_manager"):
            season_num = world.profile_manager.leaderboard_manager.data.get("current_season", 1)

        if hasattr(world, "arena"):
            world.arena.is_foggy = (self.weather in ["fog", "snow", "blizzard"])
            world.arena.is_raining = (self.weather in ["rain", "thunderstorm"])
            world.arena.is_sandstorming = (self.weather == "sandstorm")
            world.arena.is_snowing = (self.weather in ["snow", "blizzard"])
            world.arena.is_heatwave = (self.weather == "heatwave")

            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []

            if self.weather == "sandstorm":
                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from ai.ball_types_swarm import Swarm
                    minion = Swarm(ball_id="sand_minion_"+str(getattr(self, "random", __import__("random")).randint(1000,9999)), x=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0), y=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0))
                    minion.team = "Sandstorm"
                    minion.ball_type = "sand_minion"
                    minion.hp = 30.0
                    minion.max_hp = 30.0
                    minion.speed = 120.0
                    minion.damage = 10.0
                    if not hasattr(world, "balls"): world.balls = []
                    world.balls.append(minion)
                    if hasattr(world, "add_event"):
                        world.add_event("minion_spawn", {"type": "minion_spawn", "message": "A Sand Minion emerged from the storm!"})

            if self.weather == "fog":
                if getattr(self, "random", __import__("random")).random() < 0.02 * delta:
                    from ai.ball_types_phantom import Phantom
                    minion = Phantom(ball_id="fog_phantom_"+str(getattr(self, "random", __import__("random")).randint(1000,9999)), x=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0), y=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0))
                    minion.team = "Fog"
                    minion.ball_type = "fog_minion"
                    minion.hp = 40.0
                    minion.max_hp = 40.0
                    minion.speed = 90.0
                    minion.damage = 15.0
                    if not hasattr(world, "balls"): world.balls = []
                    world.balls.append(minion)
                    if hasattr(world, "add_event"):
                        world.add_event("minion_spawn", {"type": "minion_spawn", "message": "A Fog Phantom materialized!"})

            if self.weather == "wind":
                if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn tornado
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    tornado = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=40.0, kind="tornado", damage=20.0)
                    setattr(tornado, 'duration', 5.0)
                    setattr(tornado, 'vx', getattr(self, "random", __import__("random")).uniform(-100.0, 100.0))
                    setattr(tornado, 'vy', getattr(self, "random", __import__("random")).uniform(-100.0, 100.0))
                    world.arena.hazards.append(tornado)
            if self.weather == "blizzard":
                if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                    from arena.procedural_arena import Hazard
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    ice = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=80.0, kind="ice_patch", damage=0.0)
                    setattr(ice, 'duration', 10.0)
                    setattr(ice, 'vx', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    setattr(ice, 'vy', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    world.arena.hazards.append(ice)
            if self.weather in ["snow", "blizzard"]:
                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn ice slicks
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    ice = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=50.0, kind="ice_patch", damage=0.0)
                    setattr(ice, 'duration', 10.0)
                    setattr(ice, 'vx', getattr(self, "random", __import__("random")).uniform(-20.0, 20.0))
                    setattr(ice, 'vy', getattr(self, "random", __import__("random")).uniform(-20.0, 20.0))
                    world.arena.hazards.append(ice)
            if self.weather in ["snow", "blizzard"] and season_num == 4:
                if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn randomly moving ice patches
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    ice = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=50.0, kind="ice_patch", damage=0.0)
                    setattr(ice, 'duration', 10.0)
                    setattr(ice, 'vx', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    setattr(ice, 'vy', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    world.arena.hazards.append(ice)

            elif self.weather == "rain":
                arena_name = getattr(world.arena, "__class__", type(world.arena)).__name__.lower()
                is_dirt_sand = "sand" in arena_name or "dirt" in arena_name or "summer" in arena_name or getattr(world.arena, "is_sandstorming", False)
                if is_dirt_sand and getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn mud pit
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    mud_pit = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=60.0, kind="quicksand", damage=0.0)
                    setattr(mud_pit, 'duration', 15.0)
                    world.arena.hazards.append(mud_pit)
                if season_num == 3:
                    if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                        from arena.procedural_arena import Hazard
                        # Spawn healing puddles
                        x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                        y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                        puddle = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=40.0, kind="healing_spring", damage=-10.0)
                        setattr(puddle, 'duration', 8.0)
                        world.arena.hazards.append(puddle)
                else:
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                        from arena.procedural_arena import Hazard
                        # Spawn lightning strike zone
                        x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                        y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                        lightning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=30.0, kind="lightning_strike", damage=50.0)
                        setattr(lightning, 'duration', 1.0)
                        world.arena.hazards.append(lightning)
            elif self.weather == "thunderstorm":
                if getattr(self, "random", __import__("random")).random() < 0.2 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn lightning strike zone
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    lightning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=30.0, kind="lightning_strike", damage=50.0)
                    setattr(lightning, 'duration', 1.0)
                    world.arena.hazards.append(lightning)
                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn tornado warning
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    warning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=40.0, kind="tornado_warning", damage=0.0)
                    setattr(warning, 'duration', 3.0)
                    if hasattr(world, "add_event"):
                        world.add_event("audio_event", {"sound": "siren_warning", "volume": 1.0, "x": x, "y": y})
                    world.arena.hazards.append(warning)

        valid_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        for b in valid_balls:
            if getattr(b, "is_decoy", False): continue
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

            if self.weather == "clear":
                b.cosmetic = "none"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0)
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                b.attack_accuracy = 1.0
            elif self.weather == "rain":
                b.cosmetic = "umbrella"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.5

                # Check for swamp/water traits
                b_type = str(getattr(b, "ball_type", "")).lower()
                traits = getattr(b, "traits", [])
                has_water_trait = "water" in b_type or "swamp" in b_type or any("water" in str(t).lower() or "swamp" in str(t).lower() for t in traits)

                if not has_water_trait:
                    b.speed = b.base_speed * 0.8
                else:
                    b.speed = getattr(b, "base_speed", 100.0)
                b.damage = b.base_damage
                if hasattr(b, "hp"):
                    max_hp = getattr(b, "max_hp", 100.0)
                    b.hp = min(max_hp, b.hp + 5.0 * delta)
                b.dash_range_mult = 1.5
                b.steering_mult = 0.5
                if getattr(b, "SKILL", "") == "fireball":
                    if hasattr(b, "hp"):
                        b.hp -= 2.0 * delta
                if hasattr(b, "vx") and hasattr(b, "vy"):
                    b.x += getattr(b, "vx") * delta * 0.5
                    b.y += getattr(b, "vy") * delta * 0.5
                b.attack_accuracy = 0.8
            elif self.weather == "fog":
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.4
                b.speed = b.base_speed * 0.8
                b.damage = b.base_damage * 0.9
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
            elif self.weather == "blizzard":
                b.cosmetic = "snow_goggles"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.4
                b.speed = b.base_speed * 0.3
                b.damage = b.base_damage * 1.5
                b.dash_range_mult = 1.0
                b.steering_mult = 0.8
                if getattr(b, "SKILL", "") == "iceball" or getattr(b, "SKILL", "") == "elemental_burst":
                    b.speed = b.base_speed * 1.5
                if not hasattr(b, "chill_stacks"):
                    b.chill_stacks = 0.0
                b.chill_stacks += delta * 2.0
                if b.chill_stacks >= 3.0:
                    b.chill_stacks = 0.0
                    b.stutter_timer = 2.0
            elif self.weather in ["snow", "blizzard"]:
                b.cosmetic = "snow_goggles"
                if getattr(b, "ball_type", "") == "snow_yeti":
                    b.speed = b.base_speed * 1.5
                    b.damage = b.base_damage * 1.5
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.6
                    b.speed = b.base_speed * 0.5
                    b.damage = b.base_damage * 1.2
                    if getattr(b, "SKILL", "") == "iceball" or getattr(b, "SKILL", "") == "elemental_burst":
                        b.speed = b.base_speed * 1.2
                        b.damage = b.base_damage * 1.5
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    if not hasattr(b, "chill_stacks"):
                        b.chill_stacks = 0.0
                    b.chill_stacks += delta
                    if b.chill_stacks >= 3.0: # Arbitrary threshold, let's say 3 seconds in snow
                        b.chill_stacks = 0.0
                        b.stutter_timer = 1.0 # Freeze for 1 second
                    b.attack_accuracy = 0.9
            elif self.weather == "wind":
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.55
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                # push balls in a specific direction
                if hasattr(self, "wind_dx") and hasattr(self, "wind_dy"):
                    b.x += self.wind_dx * delta
                    b.y += self.wind_dy * delta
            elif self.weather == "thunderstorm":
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.8
                b.speed = b.base_speed * 1.1
                b.damage = b.base_damage * 1.5
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
            elif self.weather == "sandstorm":
                b.cosmetic = "dust_mask"
                if getattr(b, "ball_type", "") == "sand_elemental":
                    b.speed = b.base_speed * 1.2
                    b.damage = b.base_damage
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.3
                    b.speed = b.base_speed * 0.7
                    b.damage = b.base_damage
                    b.dash_range_mult = 0.5
                    b.steering_mult = 0.5
                    if not hasattr(b, "sandstorm_timer"):
                        b.sandstorm_timer = 0.0
                    b.sandstorm_timer += delta
                    if b.sandstorm_timer >= 1.0:
                        b.sandstorm_timer = 0.0
                        if hasattr(b, "hp"):
                            b.hp -= 1.0
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                        if hasattr(b, "hp"):
                            b.hp -= 20.0
                    b.attack_accuracy = 0.5
            elif self.weather == "heatwave":
                b.cosmetic = "sunglasses"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.7
                b.speed = b.base_speed * 0.9 # Slightly reduced max speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                if not hasattr(b, "mirage_timer"):
                    b.mirage_timer = getattr(self, "random", __import__("random")).uniform(0.0, 5.0)
                b.mirage_timer += delta
                if b.mirage_timer >= 5.0:
                    b.mirage_timer = 0.0
                    if hasattr(world, "balls") and getattr(self, "random", __import__("random")).random() < 0.3:
                        import copy
                        decoy = copy.copy(b)
                        decoy.id = getattr(world, "next_id", getattr(self, "random", __import__("random")).randint(10000, 99999))
                        decoy.hp = getattr(b, "hp", 100)
                        decoy.max_hp = getattr(b, "max_hp", 100)
                        decoy.damage = 0
                        decoy.speed = 0.0
                        decoy.skill_timer = 9999.0
                        decoy.attack_timer = 9999.0
                        decoy.is_decoy = True
                        decoy.decoy_timer = 3.0
                        decoy.decoy_type = "stun_trap" if getattr(self, "random", __import__("random")).random() < 0.5 else "explosive"
                        if hasattr(b, "SKILL") or getattr(b, "active_skill", None) is not None:
                            decoy.SKILL = None
                            decoy.active_skill = None
                        world.balls.append(decoy)

        self.dark_phase_timer += delta

        # Dark phase cycle: 20s normal, 10s dark
        if not self.is_dark_phase and self.dark_phase_timer >= 20.0:
            self.is_dark_phase = True
            self.dark_phase_timer = 0.0

            # Apply dark phase
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    if not hasattr(b, "base_perception_radius"):
                        b.base_perception_radius = getattr(b, "perception_radius", 250.0)
                    if getattr(b, "vision_booster_timer", 0) > 0:
                        b.perception_radius = b.base_perception_radius
                    else:
                        if b.ball_type == "scout":
                            b.perception_radius = 120.0
                        else:
                            b.perception_radius = 60.0
        elif self.is_dark_phase and self.dark_phase_timer >= 10.0:
            self.is_dark_phase = False
            self.dark_phase_timer = 0.0

            # Restore normal phase
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0)

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            self._award_skill_points()
            return "Draw"

        teams_alive = set(b.team for b in alive if hasattr(b, "team"))
        if not teams_alive:
             types_alive = set(b.ball_type for b in alive)
             if len(types_alive) == 1:
                 self._award_skill_points()
                 return list(types_alive)[0]
        elif len(teams_alive) == 1:
            self._award_skill_points()
            return list(teams_alive)[0]

        if len(alive) == 1:
            self._award_skill_points()
            return alive[0].ball_type

        return None

    def _award_skill_points(self):
        try:
            from system.profile import ProfileManager  # type: ignore
            pm = ProfileManager("profile.json")
            pm.add_skill_points(10)
        except Exception:
            pass

class TeamDeathmatchMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Team Deathmatch"
        self.description = "Two teams fight until one is eliminated."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        # Split into two teams
        mid = len(balls) // 2
        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                b.team = "Red" if i < mid else "Blue"

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", b.ball_type) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]
        return None

class ZombieInfectionMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Zombie Infection"
        self.description = "One zombie infects others. Survivors win if time runs out."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        import random
        # Pick 1 random zombie
        if balls:
            zombie = random.choice([b for b in balls if getattr(b, "ball_type", None) != "spectator"])
            for b in balls:
                if getattr(b, "ball_type", None) != "spectator":
                    if b == zombie:
                        b.team = "Zombie"
                        b.ball_type = "berserker" # A strong type
                    else:
                        b.team = "Survivor"

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        survivors = [b for b in balls if getattr(b, "team", "") == "Survivor"]
        for survivor in survivors:
            if not getattr(survivor, "alive", False):
                survivor.team = "Zombie"
                survivor.ball_type = "berserker"
                survivor.hp = getattr(survivor, "max_hp", 100)
                survivor.alive = True

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        zombies = sum(1 for b in alive if getattr(b, "team", "") == "Zombie")
        survivors = sum(1 for b in alive if getattr(b, "team", "") == "Survivor")

        if survivors == 0:
            return "Zombies"
        elif zombies == 0:
            return "Survivors"

        # Needs simulation tick access or a different way to check time for Survivor win
        # but basic logic allows checking teams
        return None


class BossFightMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Boss Fight"
        self.description = "One giant boss ball faces off against a team of weaker hunters."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        if not valid_balls:
            return

        # First ball is the boss
        boss = valid_balls[0]
        boss.team = "Boss"
        boss.max_hp = getattr(boss, "max_hp", 100) * 10.0
        boss.hp = boss.max_hp
        boss.damage = getattr(boss, "damage", 10.0) * 2.0
        boss.radius = getattr(boss, "radius", 10.0) * 3.0

        # Slower but unstoppable
        boss.base_speed = float(getattr(boss, "base_speed", getattr(boss, "speed", 100.0))) * 0.6
        boss.mass = getattr(boss, "mass", 1.0) * 5.0

        # Position boss in center
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        boss.x = arena_width / 2.0
        boss.y = arena_height / 2.0

        # The rest are hunters
        for b in valid_balls[1:]:
            b.team = "Hunters"
            b.max_hp = getattr(b, "max_hp", 100) * 0.8
            b.hp = b.max_hp

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        # Boss slowly regenerates health
        for b in balls:
            if getattr(b, "team", "") == "Boss" and getattr(b, "alive", False):
                b.hp = min(b.hp + 5.0 * delta, getattr(b, "max_hp", 1000.0))

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        boss_alive = any(getattr(b, "team", "") == "Boss" for b in alive)
        hunters_alive = any(getattr(b, "team", "") == "Hunters" for b in alive)

        if not boss_alive:
            return "Hunters"
        if not hunters_alive:
            return "Boss"

        return None



class DualPayloadMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Dual Payload"
        self.description = "Two payloads move towards the center, the team that destroys the enemy payload first wins."
        self.payload_red = None
        self.payload_blue = None

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        mid = len(valid_balls) // 2

        red_team = []
        blue_team = []

        for i, b in enumerate(valid_balls):
            if i < mid:
                b.team = "Red"
                red_team.append(b)
            else:
                b.team = "Blue"
                blue_team.append(b)

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        if red_team:
            self.payload_red = red_team[0]
            self.payload_red.ball_type = "payload"
            self.payload_red.is_payload = True
            self.payload_red.speed = 10.0
            self.payload_red.base_speed = 10.0
            self.payload_red.damage = 0.0
            self.payload_red.base_damage = 0.0
            self.payload_red.max_hp = getattr(self.payload_red, "max_hp", 100.0) * 5.0
            self.payload_red.hp = self.payload_red.max_hp
            self.payload_red.x = 100.0
            self.payload_red.y = arena_height / 2.0

        if blue_team:
            self.payload_blue = blue_team[0]
            self.payload_blue.ball_type = "payload"
            self.payload_blue.is_payload = True
            self.payload_blue.speed = 10.0
            self.payload_blue.base_speed = 10.0
            self.payload_blue.damage = 0.0
            self.payload_blue.base_damage = 0.0
            self.payload_blue.max_hp = getattr(self.payload_blue, "max_hp", 100.0) * 5.0
            self.payload_blue.hp = self.payload_blue.max_hp
            self.payload_blue.x = arena_width - 100.0
            self.payload_blue.y = arena_height / 2.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        center_x = arena_width / 2.0
        center_y = arena_height / 2.0

        import math

        if self.payload_red and getattr(self.payload_red, "alive", False):
            dx = center_x - getattr(self.payload_red, "x", 0)
            dy = center_y - getattr(self.payload_red, "y", 0)
            dist = math.hypot(dx, dy)
            if dist > 5.0:
                self.payload_red.x += (dx / dist) * getattr(self.payload_red, "speed", 10.0) * delta
                self.payload_red.y += (dy / dist) * getattr(self.payload_red, "speed", 10.0) * delta

        if self.payload_blue and getattr(self.payload_blue, "alive", False):
            dx = center_x - getattr(self.payload_blue, "x", 0)
            dy = center_y - getattr(self.payload_blue, "y", 0)
            dist = math.hypot(dx, dy)
            if dist > 5.0:
                self.payload_blue.x += (dx / dist) * getattr(self.payload_blue, "speed", 10.0) * delta
                self.payload_blue.y += (dy / dist) * getattr(self.payload_blue, "speed", 10.0) * delta

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        red_alive = self.payload_red and getattr(self.payload_red, "alive", False)
        blue_alive = self.payload_blue and getattr(self.payload_blue, "alive", False)

        if not red_alive and blue_alive:
            return "Blue"
        elif not blue_alive and red_alive:
            return "Red"
        elif not red_alive and not blue_alive:
            return "Draw"

        return None


class EscortMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Escort Mode"
        self.description = "One team defends an invulnerable payload moving towards a goal. The other tries to delay it until time runs out."
        self.payload = None
        self.goal_x = 900.0
        self.goal_y = 500.0
        self.timer = 180.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        mid = len(balls) // 2
        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                if i < mid:
                    b.team = "Defenders"
                else:
                    b.team = "Attackers"

        # Transform a defender into the payload, or just use the first defender
        defenders = [b for b in balls if getattr(b, "team", "") == "Defenders"]
        if defenders:
            self.payload = defenders[0]
            self.payload.ball_type = "payload"
            self.payload.is_invulnerable = True
            self.payload.speed = 0.5
            self.payload.damage = 0.0
            self.payload.x = 100.0
            self.payload.y = 500.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if getattr(self, "timer", 0) > 0:
            self.timer -= delta

        if not hasattr(self, "pulse_timer"):
            self.pulse_timer = 0.0

        self.pulse_timer += delta
        if self.pulse_timer >= 5.0:
            self.pulse_timer = 0.0
            if self.payload and getattr(self.payload, "alive", False):
                for b in balls:
                    if b == self.payload or not getattr(b, "alive", False):
                        continue
                    if getattr(b, "ball_type", None) == "spectator":
                        continue

                    import math
                    dx = getattr(b, "x", 0) - getattr(self.payload, "x", 0)
                    dy = getattr(b, "y", 0) - getattr(self.payload, "y", 0)
                    dist = math.hypot(dx, dy)

                    if dist <= 300.0:
                        if getattr(b, "team", "") == "Defenders":
                            b.hp = min(getattr(b, "max_hp", 100.0), getattr(b, "hp", 100.0) + 20.0)
                        elif getattr(b, "team", "") == "Attackers":
                            b.hp = max(0.0, getattr(b, "hp", 100.0) - 20.0)
                            if b.hp <= 0:
                                b.alive = False

        if self.payload and getattr(self.payload, "alive", False):
            import math
            dx = self.goal_x - getattr(self.payload, "x", 0)
            dy = self.goal_y - getattr(self.payload, "y", 0)
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.payload.x += (dx / dist) * getattr(self.payload, "speed", 0.5)
                self.payload.y += (dy / dist) * getattr(self.payload, "speed", 0.5)

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        if not self.payload:
            return None

        import math
        dx = self.goal_x - getattr(self.payload, "x", 0)
        dy = self.goal_y - getattr(self.payload, "y", 0)

        if getattr(self, "timer", 0) <= 0:
            return "Attackers"

        if math.hypot(dx, dy) < 10.0:
            return "Defenders"

        return None

        import math
        dx = self.goal_x - self.payload["x"]
        dy = self.goal_y - self.payload["y"]

        if getattr(self.payload, "hp", self.payload.get("hp", 0)) <= 0 or not self.payload.get("alive", True):
            self.payload["alive"] = False
            return "Attackers"

        if math.hypot(dx, dy) < 10.0:
            return "Defenders"

        return None

class VIPDefenseMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "VIP Defense"
        self.description = "Protect the VIP. If the VIP dies, the attackers win."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        mid = len(balls) // 2
        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                if i < mid:
                    b.team = "Defenders"
                else:
                    b.team = "Attackers"

        defenders = [b for b in balls if getattr(b, "team", "") == "Defenders"]
        if defenders:
            vip = defenders[0]
            vip.team = "VIP"
            vip.ball_type = "king" # King fits VIP

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        vip_alive = any(getattr(b, "team", "") == "VIP" and getattr(b, "alive", False) for b in balls)
        if not vip_alive:
            return "Attackers"

        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        attackers_alive = any(getattr(b, "team", "") == "Attackers" for b in alive)

        if not attackers_alive:
            return "Defenders"

        return None

class SurvivalMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Survival"
        self.description = "Players team up to survive against waves of enemies (simulated by having many enemies)."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        players_count = min(4, len(balls))
        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                if i < players_count:
                    b.team = "Players"
                else:
                    b.team = "Enemies"

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        players_alive = any(getattr(b, "team", "") == "Players" for b in alive)
        enemies_alive = any(getattr(b, "team", "") == "Enemies" for b in alive)

        if not players_alive:
            return "Enemies"
        if not enemies_alive:
            return "Players"

        return None


class CaptureTheFlagMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Capture The Flag"
        self.description = "Teams try to steal the enemy's flag (a special booster) and return it to their base."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        mid = len(balls) // 2
        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                if i < mid:
                    b.team = "Red"
                else:
                    b.team = "Blue"

        # Add flags (special boosters) if world has them
        if hasattr(world, "boosters"):
            # Add dicts that represent flag boosters
            class FlagBooster:
                def __init__(self, id, x, y, team):
                    self.id = id
                    self.x = x
                    self.y = y
                    self.is_flag = True
                    self.team = team
                    self.carrier = None
                    self.ball_type = "booster"
            red_flag = FlagBooster("red_flag", 100, 100, "Red")
            blue_flag = FlagBooster("blue_flag", 900, 900, "Blue")
            world.boosters.extend([red_flag, blue_flag])
            if not hasattr(world, "flags"):
                world.flags = {"Red": red_flag, "Blue": blue_flag}

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        # Basic check if someone scored or all enemies are dead
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        teams_alive = set(getattr(b, "team", "") for b in alive)

        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        # Simplified win condition for tests
        if hasattr(world, "scores"):
            if world.scores.get("Red", 0) >= 3:
                return "Red"
            if world.scores.get("Blue", 0) >= 3:
                return "Blue"
        return None


class EvolutionarySimulationMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Evolutionary Simulation"
        self.description = "Only Neural Balls compete. After the match, a genetic algorithm breeds top performers."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        # Convert everyone to Neural
        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                b.ball_type = "neural"
                b.team = f"Neural_{i}"

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        if len(alive) == 1:
            return alive[0].team

        return None


class VampireRoyaleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Vampire Royale"
        self.description = "All balls slowly lose HP over time but regain HP when dealing damage. Last one standing wins."
        self.tick_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        self.tick_timer += delta
        if self.tick_timer >= 1.0:
            self.tick_timer = 0.0
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    b.hp = max(0, getattr(b, "hp", 100) - 5.0)
                    if b.hp <= 0:
                        b.alive = False

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            if hasattr(self, '_award_skill_points'):
                self._award_skill_points()
            return list(teams_alive)[0]

        if len(alive) == 1:
            if hasattr(self, '_award_skill_points'):
                self._award_skill_points()
            return alive[0].ball_type

        return None


class KingOfTheHillMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "King of the Hill"
        self.description = "Control a central shrinking zone. First to 100 points wins."
        self.tick_timer = 0.0
        self.game_time = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        self.game_time = 0.0
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.score = 0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        self.game_time += delta
        self.tick_timer += delta
        if self.tick_timer >= 0.5:
            self.tick_timer = 0.0

            # Find the arena dimensions
            arena_width = 1000
            arena_height = 1000
            if hasattr(world, "arena") and world.arena:
                arena_width = getattr(world.arena, "width", 1000)
                arena_height = getattr(world.arena, "height", 1000)

            center_x = arena_width / 2.0
            center_y = arena_height / 2.0

            max_radius = min(arena_width, arena_height) * 0.5
            min_radius = min(arena_width, arena_height) * 0.05
            zone_radius = max(min_radius, max_radius - self.game_time * 5.0)

            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    dist_sq = (b.x - center_x) ** 2 + (b.y - center_y) ** 2
                    if dist_sq <= zone_radius ** 2:
                        b.score = getattr(b, "score", 0) + 1

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        best_score = -1
        best_team = None
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                score = getattr(b, "score", 0)
                if score >= 100:
                    return getattr(b, "team", b.ball_type)
                if score > best_score:
                    best_score = score
                    best_team = getattr(b, "team", b.ball_type)  # noqa: F841

        # We don't have access to game timer here directly.
        # So we just return when score >= 100. If time runs out, game loop usually handles it and can just pick the one with max score.
        return None


class BlackHoleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Black Hole"
        self.description = "The entire arena is slowly sucked into a massive black hole in the center. Avoid the center!"
        self.black_hole_radius = 50.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        import math
        arena_width = 1000
        arena_height = 1000
        if hasattr(world, "arena") and world.arena:
            arena_width = getattr(world.arena, "width", 1000)
            arena_height = getattr(world.arena, "height", 1000)

        center_x = arena_width / 2.0
        center_y = arena_height / 2.0

        # The black hole slowly grows over time
        self.black_hole_radius += 2.0 * delta

        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                dx = center_x - b.x
                dy = center_y - b.y
                dist = math.hypot(dx, dy)

                if dist < self.black_hole_radius:
                    # Instantly die if inside the event horizon
                    b.hp = 0
                    b.alive = False
                elif dist > 0:
                    # Pull towards center
                    # Force is stronger the closer you are to the event horizon
                    pull_strength = 20000.0 / (dist * dist)

                    # Increase max pull and overall strength as the black hole grows
                    radius_multiplier = self.black_hole_radius / 50.0
                    pull_strength *= radius_multiplier

                    # Cap max pull to avoid crazy speeds, but scale the cap too
                    pull_strength = min(pull_strength, 150.0 * radius_multiplier)

                    b.x += (dx / dist) * pull_strength * delta
                    b.y += (dy / dist) * pull_strength * delta

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return alive[0].ball_type

        return None



class WeatherChaosMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Weather Chaos"
        self.description = "Weather conditions change throughout the match, affecting stats."
        self.weather = "clear"
        self.weather_timer = 0.0
        self.next_weather = "clear"
        self.weather_warning_issued = False
        import random
        self.random = random

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for b in valid_balls:
            b.team = b.ball_type
            if not hasattr(b, "base_perception_radius"):
                b.base_perception_radius = getattr(b, "perception_radius", 250.0)
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        controller = None
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "weather_control_timer", 0.0) > 0:
                controller = b
                break

        if controller:
            self.weather_timer = 0.0
            ctype = getattr(controller, "ball_type", "default")
            pref = "clear"
            if ctype in ["elementalist"]: pref = "thunderstorm"
            elif ctype in ["druid", "healer"]: pref = "rain"
            elif ctype in ["rogue", "assassin", "stealth"]: pref = "fog"
            elif ctype in ["mage", "conjurer"]: pref = "snow"
            elif ctype in ["speed", "scout"]: pref = "wind"
            elif ctype in ["tank", "brawler"]: pref = "heatwave"
            elif ctype in ["swarm"]: pref = "sandstorm"
            else: pref = "thunderstorm"

            old_weather = self.weather
            if old_weather != pref:
                self.weather = pref
                if hasattr(world, "add_event"):
                    world.add_event("weather_change", {"weather": self.weather})
                if self.weather == "wind":
                    rnd = getattr(self, "random", __import__("random"))
                    self.wind_dx = rnd.uniform(-50.0, 50.0)
                    self.wind_dy = rnd.uniform(-50.0, 50.0)
        else:
            self.weather_timer += delta

            warning_threshold = 7.0  # 3s warning
            if self.weather_timer >= warning_threshold and not getattr(self, "weather_warning_issued", False):
                if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                    scanners = [h for h in world.arena.hazards if getattr(h, "kind", "") == "weather_scanner" and getattr(h, "active", True)]
                    if scanners:
                        next_w = getattr(self, "next_weather", "unknown")
                        if hasattr(world, "add_event"):
                            world.add_event("weather_warning", {"type": "weather_warning", "message": f"Scanner warns: {next_w.upper()} incoming in 3s!"})
                        self.weather_warning_issued = True

            if self.weather_timer > 10.0:
                self.weather_timer = 0.0
                weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm", "heatwave", "blizzard", "magnetic_storm"]
                import random
                rnd = getattr(self, "random", random)
                old_weather = self.weather
                self.weather = getattr(self, "next_weather", rnd.choice(weathers))
                self.next_weather = rnd.choice(weathers)
                self.weather_warning_issued = False

                if old_weather != self.weather and hasattr(world, "add_event"):
                    world.add_event("weather_change", {"weather": self.weather})

                if self.weather == "wind":
                    self.wind_dx = rnd.uniform(-50.0, 50.0)
                    self.wind_dy = rnd.uniform(-50.0, 50.0)

        # Apply weather effects to the arena
        season_num = 1
        if hasattr(world, "leaderboard_manager"):
            season_num = world.leaderboard_manager.data.get("current_season", 1)
        elif hasattr(world, "profile_manager") and hasattr(world.profile_manager, "leaderboard_manager"):
            season_num = world.profile_manager.leaderboard_manager.data.get("current_season", 1)

        if hasattr(world, "arena"):
            world.arena.is_foggy = (self.weather in ["fog", "snow", "blizzard"])
            world.arena.is_raining = (self.weather in ["rain", "thunderstorm"])
            world.arena.is_sandstorming = (self.weather == "sandstorm")
            world.arena.is_snowing = (self.weather in ["snow", "blizzard"])
            world.arena.is_heatwave = (self.weather == "heatwave")
            world.arena.wind_dx = getattr(self, "wind_dx", 0.0) if self.weather == "wind" else 0.0
            world.arena.wind_dy = getattr(self, "wind_dy", 0.0) if self.weather == "wind" else 0.0

            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []

            if self.weather == "sandstorm":
                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from ai.ball_types_swarm import Swarm
                    minion = Swarm(ball_id="sand_minion_"+str(getattr(self, "random", __import__("random")).randint(1000,9999)), x=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0), y=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0))
                    minion.team = "Sandstorm"
                    minion.ball_type = "sand_minion"
                    minion.hp = 30.0
                    minion.max_hp = 30.0
                    minion.speed = 120.0
                    minion.damage = 10.0
                    if not hasattr(world, "balls"): world.balls = []
                    world.balls.append(minion)
                    if hasattr(world, "add_event"):
                        world.add_event("minion_spawn", {"type": "minion_spawn", "message": "A Sand Minion emerged from the storm!"})

            if self.weather == "fog":
                if getattr(self, "random", __import__("random")).random() < 0.02 * delta:
                    from ai.ball_types_phantom import Phantom
                    minion = Phantom(ball_id="fog_phantom_"+str(getattr(self, "random", __import__("random")).randint(1000,9999)), x=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0), y=getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0))
                    minion.team = "Fog"
                    minion.ball_type = "fog_minion"
                    minion.hp = 40.0
                    minion.max_hp = 40.0
                    minion.speed = 90.0
                    minion.damage = 15.0
                    if not hasattr(world, "balls"): world.balls = []
                    world.balls.append(minion)
                    if hasattr(world, "add_event"):
                        world.add_event("minion_spawn", {"type": "minion_spawn", "message": "A Fog Phantom materialized!"})

            if self.weather == "wind":
                if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn tornado
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    tornado = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=40.0, kind="tornado", damage=20.0)
                    setattr(tornado, 'duration', 5.0)
                    setattr(tornado, 'vx', getattr(self, "random", __import__("random")).uniform(-100.0, 100.0))
                    setattr(tornado, 'vy', getattr(self, "random", __import__("random")).uniform(-100.0, 100.0))
                    world.arena.hazards.append(tornado)
            if self.weather == "blizzard":
                if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                    from arena.procedural_arena import Hazard
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    ice = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=80.0, kind="ice_patch", damage=0.0)
                    setattr(ice, 'duration', 10.0)
                    setattr(ice, 'vx', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    setattr(ice, 'vy', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    world.arena.hazards.append(ice)
            if self.weather in ["snow", "blizzard"]:
                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn ice slicks
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    ice = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=50.0, kind="ice_patch", damage=0.0)
                    setattr(ice, 'duration', 10.0)
                    setattr(ice, 'vx', getattr(self, "random", __import__("random")).uniform(-20.0, 20.0))
                    setattr(ice, 'vy', getattr(self, "random", __import__("random")).uniform(-20.0, 20.0))
                    world.arena.hazards.append(ice)
            if self.weather in ["snow", "blizzard"] and season_num == 4:
                if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn randomly moving ice patches
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    ice = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=50.0, kind="ice_patch", damage=0.0)
                    setattr(ice, 'duration', 10.0)
                    setattr(ice, 'vx', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    setattr(ice, 'vy', getattr(self, "random", __import__("random")).uniform(-50.0, 50.0))
                    world.arena.hazards.append(ice)

            elif self.weather == "rain":
                arena_name = getattr(world.arena, "__class__", type(world.arena)).__name__.lower()
                is_dirt_sand = "sand" in arena_name or "dirt" in arena_name or "summer" in arena_name or getattr(world.arena, "is_sandstorming", False)
                if is_dirt_sand and getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn mud pit
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    mud_pit = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=60.0, kind="quicksand", damage=0.0)
                    setattr(mud_pit, 'duration', 15.0)
                    world.arena.hazards.append(mud_pit)
                if season_num == 3:
                    if getattr(self, "random", __import__("random")).random() < 0.1 * delta:
                        from arena.procedural_arena import Hazard
                        # Spawn healing puddles
                        x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                        y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                        puddle = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=40.0, kind="healing_spring", damage=-10.0)
                        setattr(puddle, 'duration', 8.0)
                        world.arena.hazards.append(puddle)
                else:
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                        from arena.procedural_arena import Hazard
                        # Spawn lightning strike zone
                        x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                        y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                        lightning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=30.0, kind="lightning_strike", damage=50.0)
                        setattr(lightning, 'duration', 1.0)
                        world.arena.hazards.append(lightning)
            elif self.weather == "thunderstorm":
                if getattr(self, "random", __import__("random")).random() < 0.2 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn lightning strike zone
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    lightning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=30.0, kind="lightning_strike", damage=50.0)
                    setattr(lightning, 'duration', 1.0)
                    world.arena.hazards.append(lightning)
                if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn tornado warning
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    warning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=40.0, kind="tornado_warning", damage=0.0)
                    setattr(warning, 'duration', 3.0)
                    if hasattr(world, "add_event"):
                        world.add_event("audio_event", {"sound": "siren_warning", "volume": 1.0, "x": x, "y": y})
                    world.arena.hazards.append(warning)

        valid_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]

        for b in valid_balls:
            if getattr(b, "is_decoy", False): continue
            if not hasattr(b, "base_perception_radius"):
                b.base_perception_radius = getattr(b, "perception_radius", 250.0)
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

            if self.weather == "clear":
                b.cosmetic = "none"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0)
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                b.attack_accuracy = 1.0
            elif self.weather == "rain":
                b.cosmetic = "umbrella"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.5

                # Check for swamp/water traits
                b_type = str(getattr(b, "ball_type", "")).lower()
                traits = getattr(b, "traits", [])
                has_water_trait = "water" in b_type or "swamp" in b_type or any("water" in str(t).lower() or "swamp" in str(t).lower() for t in traits)

                if not has_water_trait:
                    b.speed = b.base_speed * 0.8
                else:
                    b.speed = getattr(b, "base_speed", 100.0)
                b.damage = b.base_damage
                if hasattr(b, "hp"):
                    max_hp = getattr(b, "max_hp", 100.0)
                    b.hp = min(max_hp, b.hp + 5.0 * delta)
                # rain makes surface slippery/increases dash range but reduces steering
                b.dash_range_mult = 1.5
                b.steering_mult = 0.5
                if getattr(b, "SKILL", "") == "fireball":
                    if hasattr(b, "hp"):
                        b.hp -= 2.0 * delta
                # slide more
                if hasattr(b, "vx") and hasattr(b, "vy"):
                    b.x += getattr(b, "vx") * delta * 0.5
                    b.y += getattr(b, "vy") * delta * 0.5
                b.attack_accuracy = 0.8
            elif self.weather == "fog":
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.4
                b.speed = b.base_speed * 0.5
                b.damage = b.base_damage * 0.8
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                if getattr(b, "ball_type", "") in ["trickster", "phantom", "mimic"]:
                    if not hasattr(b, "mirage_timer"):
                        b.mirage_timer = getattr(self, "random", __import__("random")).uniform(0.0, 5.0)
                    b.mirage_timer += delta
                    if b.mirage_timer >= 5.0:
                        b.mirage_timer = 0.0
                        if hasattr(world, "balls"):
                            import copy
                            decoy = copy.copy(b)
                            decoy.id = getattr(world, "next_id", getattr(self, "random", __import__("random")).randint(10000, 99999))
                            decoy.hp = getattr(b, "hp", 100)
                            decoy.max_hp = getattr(b, "max_hp", 100)
                            decoy.damage = 0
                            decoy.speed = 0.0
                            decoy.skill_timer = 9999.0
                            decoy.attack_timer = 9999.0
                            decoy.is_decoy = True
                            decoy.decoy_timer = 3.0
                            decoy.decoy_type = "stun_trap" if getattr(self, "random", __import__("random")).random() < 0.5 else "explosive"
                            if hasattr(b, "SKILL") or getattr(b, "active_skill", None) is not None:
                                decoy.SKILL = None
                                decoy.active_skill = None
                            world.balls.append(decoy)
            elif self.weather == "blizzard":
                b.cosmetic = "snow_goggles"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.4
                b.speed = b.base_speed * 0.3
                b.damage = b.base_damage * 1.5
                b.dash_range_mult = 1.0
                b.steering_mult = 0.8
                if getattr(b, "SKILL", "") == "iceball" or getattr(b, "SKILL", "") == "elemental_burst":
                    b.speed = b.base_speed * 1.5
                if not hasattr(b, "chill_stacks"):
                    b.chill_stacks = 0.0
                b.chill_stacks += delta * 2.0
                if b.chill_stacks >= 3.0:
                    b.chill_stacks = 0.0
                    b.stutter_timer = 2.0
            elif self.weather in ["snow", "blizzard"]:
                b.cosmetic = "snow_goggles"
                if getattr(b, "ball_type", "") == "snow_yeti":
                    b.speed = b.base_speed * 1.5
                    b.damage = b.base_damage * 1.5
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.6
                    b.speed = b.base_speed * 0.5
                    b.damage = b.base_damage * 1.2
                    if getattr(b, "SKILL", "") == "iceball" or getattr(b, "SKILL", "") == "elemental_burst":
                        b.speed = b.base_speed * 1.2
                        b.damage = b.base_damage * 1.5
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    if not hasattr(b, "chill_stacks"):
                        b.chill_stacks = 0.0
                    b.chill_stacks += delta
                    if b.chill_stacks >= 3.0: # Arbitrary threshold, let's say 3 seconds in snow
                        b.chill_stacks = 0.0
                        b.stutter_timer = 1.0 # Freeze for 1 second
                    b.attack_accuracy = 0.9
            elif self.weather == "wind":
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.55
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                # push balls in a specific direction
            elif self.weather == "thunderstorm":
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.8
                b.speed = b.base_speed * 1.1 # Panic speed
                b.damage = b.base_damage * 1.5 # High damage due to electricity
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
            elif self.weather == "sandstorm":
                b.cosmetic = "dust_mask"
                if getattr(b, "ball_type", "") == "sand_elemental":
                    b.speed = b.base_speed * 1.2
                    b.damage = b.base_damage
                    b.dash_range_mult = 1.0
                    b.steering_mult = 1.0
                    b.attack_accuracy = 1.0
                else:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.3
                    b.speed = b.base_speed * 0.7 # Hard to move
                    b.damage = b.base_damage
                    b.dash_range_mult = 0.5
                    b.steering_mult = 0.5
                    if getattr(b, "ball_type", "") in ["trickster", "phantom", "mimic"]:
                        if not hasattr(b, "mirage_timer"):
                            b.mirage_timer = getattr(self, "random", __import__("random")).uniform(0.0, 5.0)
                        b.mirage_timer += delta
                        if b.mirage_timer >= 5.0:
                            b.mirage_timer = 0.0
                            if hasattr(world, "balls"):
                                import copy
                                decoy = copy.copy(b)
                                decoy.id = getattr(world, "next_id", getattr(self, "random", __import__("random")).randint(10000, 99999))
                                decoy.hp = getattr(b, "hp", 100)
                                decoy.max_hp = getattr(b, "max_hp", 100)
                                decoy.damage = 0
                                decoy.speed = 0.0
                                decoy.skill_timer = 9999.0
                                decoy.attack_timer = 9999.0
                                decoy.is_decoy = True
                                decoy.decoy_timer = 3.0
                                decoy.decoy_type = "stun_trap" if getattr(self, "random", __import__("random")).random() < 0.5 else "explosive"
                                if hasattr(b, "SKILL") or getattr(b, "active_skill", None) is not None:
                                    decoy.SKILL = None
                                    decoy.active_skill = None
                                world.balls.append(decoy)
                    # dot damage
                    if not hasattr(b, "sandstorm_timer"):
                        b.sandstorm_timer = 0.0
                    b.sandstorm_timer += delta
                    if b.sandstorm_timer >= 1.0:
                        b.sandstorm_timer = 0.0
                        if hasattr(b, "hp"):
                            b.hp -= 1.0 # 1 damage per sec
                    # Random lightning strikes
                    if getattr(self, "random", __import__("random")).random() < 0.05 * delta:
                        # Struck by lightning!
                        b.hp = getattr(b, "hp", 100) - 20
                b.attack_accuracy = 0.5
            elif self.weather == "magnetic_storm":
                # Assign polarity if not present
                if not hasattr(b, "polarity"):
                    import random
                    b.polarity = random.choice([1, -1])
                b.cosmetic = "magnet_plus" if b.polarity == 1 else "magnet_minus"

                # Magnetic forces
                if hasattr(world, "balls"):
                    for other in world.balls:
                        if other != b and getattr(other, "alive", False) and hasattr(other, "polarity") and hasattr(b, "x") and hasattr(b, "y") and hasattr(other, "x") and hasattr(other, "y"):
                            import math
                            dx = other.x - b.x
                            dy = other.y - b.y
                            dist = math.sqrt(dx*dx + dy*dy)
                            if 0 < dist < 300:
                                force_mag = 500.0 / (dist + 10.0)
                                if b.polarity != other.polarity:
                                    # Attract
                                    b.x += (dx/dist) * force_mag * delta
                                    b.y += (dy/dist) * force_mag * delta
                                else:
                                    # Repel
                                    b.x -= (dx/dist) * force_mag * delta
                                    b.y -= (dy/dist) * force_mag * delta
            elif self.weather == "heatwave":
                b.cosmetic = "sunglasses"
                b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 0.7
                b.speed = b.base_speed * 0.9 # Slightly reduced max speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                if not hasattr(b, "mirage_timer"):
                    b.mirage_timer = getattr(self, "random", __import__("random")).uniform(0.0, 5.0)
                b.mirage_timer += delta
                if b.mirage_timer >= 5.0:
                    b.mirage_timer = 0.0
                    if hasattr(world, "balls") and getattr(self, "random", __import__("random")).random() < 0.3:
                        import copy
                        decoy = copy.copy(b)
                        decoy.id = getattr(world, "next_id", getattr(self, "random", __import__("random")).randint(10000, 99999))
                        decoy.hp = getattr(b, "hp", 100)
                        decoy.max_hp = getattr(b, "max_hp", 100)
                        decoy.damage = 0
                        decoy.speed = 0.0
                        decoy.skill_timer = 9999.0
                        decoy.attack_timer = 9999.0
                        decoy.is_decoy = True
                        decoy.decoy_timer = 3.0
                        decoy.decoy_type = "stun_trap" if getattr(self, "random", __import__("random")).random() < 0.5 else "explosive"
                        if hasattr(b, "SKILL") or getattr(b, "active_skill", None) is not None:
                            decoy.SKILL = None
                            decoy.active_skill = None
                        world.balls.append(decoy)


    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", "Unknown")) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        return None

class DominationMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Domination"
        self.description = "Capture points to gain global buffs for your team."
        self.points = []

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        mid = len(balls) // 2
        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                if i < mid:
                    b.team = "Red"
                else:
                    b.team = "Blue"

        class ControlPoint:
            def __init__(self, id, x, y):
                self.id = id
                self.x = x
                self.y = y
                self.radius = 150.0
                self.capture_progress = 0.0 # -100 to 100. -100 is Blue, 100 is Red.
                self.owner = None
                self.held_time = 0.0
                self.is_danger_zone = False

        self.points = [
            ControlPoint("A", 300, 500),
            ControlPoint("B", 500, 500),
            ControlPoint("C", 700, 500)
        ]

        if hasattr(world, "boosters"):
            # Attach to boosters list so UI can draw them if needed, or keep them separate.
            # We'll just keep them in self.points for logic.
            pass

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        for pt in self.points:
            red_count = 0
            blue_count = 0
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    dist_sq = (b.x - pt.x)**2 + (b.y - pt.y)**2
                    if dist_sq <= pt.radius**2:
                        if getattr(b, "team", "") == "Red":
                            red_count += 1
                        elif getattr(b, "team", "") == "Blue":
                            blue_count += 1

            if red_count > blue_count:
                pt.capture_progress += 10.0 * delta
                # Award XP to capturing team
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator" and getattr(b, "team", "") == "Red":
                        dist_sq = (b.x - pt.x)**2 + (b.y - pt.y)**2
                        if dist_sq <= pt.radius**2:
                            b.experience = getattr(b, "experience", 0.0) + 5.0 * delta
                            b.level = getattr(b, "level", 1)
                            while b.experience >= 100 * b.level:
                                b.experience -= 100 * b.level
                                b.level += 1
                                import random
                                stat = random.choice(["max_hp", "damage", "speed"])
                                if stat == "max_hp":
                                    b.max_hp = getattr(b, "max_hp", 100) * 1.1
                                    b.hp = getattr(b, "hp", b.max_hp) + getattr(b, "max_hp", 100) * 0.1
                                    if b.hp > b.max_hp: b.hp = b.max_hp
                                elif stat == "damage":
                                    b.damage = getattr(b, "damage", 10) * 1.1
                                    if hasattr(b, "base_damage"): b.base_damage *= 1.1
                                elif stat == "speed":
                                    b.speed = getattr(b, "speed", 100) * 1.1
                                    if hasattr(b, "base_speed"): b.base_speed *= 1.1

            elif blue_count > red_count:
                pt.capture_progress -= 10.0 * delta
                # Award XP to capturing team
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator" and getattr(b, "team", "") == "Blue":
                        dist_sq = (b.x - pt.x)**2 + (b.y - pt.y)**2
                        if dist_sq <= pt.radius**2:
                            b.experience = getattr(b, "experience", 0.0) + 5.0 * delta
                            b.level = getattr(b, "level", 1)
                            while b.experience >= 100 * b.level:
                                b.experience -= 100 * b.level
                                b.level += 1
                                import random
                                stat = random.choice(["max_hp", "damage", "speed"])
                                if stat == "max_hp":
                                    b.max_hp = getattr(b, "max_hp", 100) * 1.1
                                    b.hp = getattr(b, "hp", b.max_hp) + getattr(b, "max_hp", 100) * 0.1
                                    if b.hp > b.max_hp: b.hp = b.max_hp
                                elif stat == "damage":
                                    b.damage = getattr(b, "damage", 10) * 1.1
                                    if hasattr(b, "base_damage"): b.base_damage *= 1.1
                                elif stat == "speed":
                                    b.speed = getattr(b, "speed", 100) * 1.1
                                    if hasattr(b, "base_speed"): b.base_speed *= 1.1

            pt.capture_progress = max(-100.0, min(100.0, pt.capture_progress))

            new_owner = None
            if pt.capture_progress >= 100.0:
                new_owner = "Red"
            elif pt.capture_progress <= -100.0:
                new_owner = "Blue"

            if new_owner and new_owner != pt.owner:
                pt.owner = new_owner
                pt.held_time = 0.0
                pt.is_danger_zone = False
                # Apply global buff
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "team", "") == new_owner:
                        # Give buff
                        if hasattr(b, "damage"):
                            b.damage += 5.0
                        if hasattr(b, "max_hp"):
                            b.max_hp += 20.0
                            b.hp += 20.0

            if pt.owner:
                pt.held_time += delta
                if pt.held_time >= 15.0:
                    pt.is_danger_zone = True

                if pt.is_danger_zone:
                    for b in balls:
                        if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                            dist_sq = (b.x - pt.x)**2 + (b.y - pt.y)**2
                            if dist_sq <= pt.radius**2:
                                if hasattr(b, "hp"):
                                    b.hp -= 20.0 * delta
                                    if b.hp <= 0:
                                        b.alive = False
                                        b.killer = "Danger Zone"


    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        return None


class MovingZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Moving Zone"
        self.description = "Maintain position in the moving zone to score points for your team."
        self.tick_timer = 0.0
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 150.0
        self.zone_target_x = 500.0
        self.zone_target_y = 500.0

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.score = 0
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2
        self.zone_y = arena_height / 2
        self.zone_target_x = self.zone_x
        self.zone_target_y = self.zone_y

    def tick(self, world, balls, delta=0.016):
        import random
        import math
        self.tick_timer += delta

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        # Move zone towards target
        dx = self.zone_target_x - self.zone_x
        dy = self.zone_target_y - self.zone_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            self.zone_x += (dx / dist) * 20.0 * delta
            self.zone_y += (dy / dist) * 20.0 * delta
        else:
            # Pick a new target
            self.zone_target_x = random.uniform(self.zone_radius, arena_width - self.zone_radius)
            self.zone_target_y = random.uniform(self.zone_radius, arena_height - self.zone_radius)

        if self.tick_timer >= 0.5:
            self.tick_timer = 0.0

            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    bdx = b.x - self.zone_x
                    bdy = b.y - self.zone_y
                    if bdx*bdx + bdy*bdy <= self.zone_radius * self.zone_radius:
                        b.score = getattr(b, "score", 0) + 1

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                if getattr(b, "score", 0) >= 100:
                    return getattr(b, "team", b.ball_type)
        return None



class ReverseEventMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Reverse Event"
        self.description = "A random event reverses movement logic for 10 seconds."
        self.event_timer = 0.0
        self.event_active = False
        self.event_duration = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not self.event_active:
            self.event_timer += delta

        if not self.event_active and self.event_timer > 20.0:
            import random
            if random.random() < 0.1:  # 10% chance every 20 seconds to trigger
                self.event_active = True
                self.event_duration = 10.0
                self.event_timer = 0.0
                print("REVERSE EVENT TRIGGERED!")
            else:
                self.event_timer = 0.0

        if self.event_active:
            self.event_duration -= delta
            if self.event_duration <= 0:
                self.event_active = False
                self.event_timer = 0.0
                print("REVERSE EVENT ENDED!")

            # Apply reverse logic directly to balls
            for b in balls:
                if getattr(b, "alive", False):
                    b.x -= getattr(b, "vx", 0) * delta * 2 # Reverse the velocity applied in action.py
                    b.y -= getattr(b, "vy", 0) * delta * 2




class MemoryTrapsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Memory Traps"
        self.description = "The arena is littered with invisible traps. Memorize their locations!"
        self.traps = []

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        import random
        self.traps = []
        for i in range(50):
            x = random.uniform(50, arena_width - 50)
            y = random.uniform(50, arena_height - 50)
            self.traps.append({"x": x, "y": y, "radius": 40.0, "cooldowns": {}})

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            b_id = getattr(b, "id", str(id(b)))
            for trap in self.traps:
                if b_id in trap["cooldowns"]:
                    trap["cooldowns"][b_id] -= delta
                    if trap["cooldowns"][b_id] <= 0:
                        del trap["cooldowns"][b_id]

                if b_id not in trap["cooldowns"]:
                    dx = b.x - trap["x"]
                    dy = b.y - trap["y"]
                    dist_sq = dx*dx + dy*dy
                    if dist_sq < trap["radius"]**2:
                        b.hp -= 20.0
                        trap["cooldowns"][b_id] = 1.0
                        if b.hp <= 0:
                            b.alive = False

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        return None

class CustomMatchMode(GameMode):

    def __init__(self):
        super().__init__()
        self.name = "Custom Match"
        self.description = "Custom match with mutator options if Prestige Level >= 5."
        self.mutators = []
        self._rewards_given = False

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        pm = None
        if hasattr(world, "profile_manager"):
            pm = world.profile_manager

        mutators_unlocked = False
        if pm and hasattr(pm, "are_mutators_unlocked"):
            mutators_unlocked = pm.are_mutators_unlocked()

        self.mutators_active = mutators_unlocked and len(self.mutators) > 0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta






        if getattr(self, "mutators_active", False):
            if "boss" in self.mutators:
                if not hasattr(self, "boss_mutator_timer"):
                    self.boss_mutator_timer = 0.0

                # Check if there is already an active boss (even if dead)
                active_boss = None
                for b in balls:
                    if getattr(b, "_is_boss_mutator", False):
                        active_boss = b
                        break

                if active_boss:
                    # Decrement boss timer
                    if hasattr(active_boss, "_boss_mutator_duration"):
                        active_boss._boss_mutator_duration -= delta
                        if active_boss._boss_mutator_duration <= 0 or not getattr(active_boss, "alive", False):
                            # Revert boss
                            active_boss._is_boss_mutator = False
                            if hasattr(active_boss, "_original_radius"):
                                active_boss.radius = active_boss._original_radius
                            if hasattr(active_boss, "_original_max_hp"):
                                active_boss.max_hp = active_boss._original_max_hp
                            if hasattr(active_boss, "_original_damage"):
                                active_boss.damage = active_boss._original_damage
                            if hasattr(active_boss, "_original_base_damage"):
                                active_boss.base_damage = active_boss._original_base_damage
                            if hasattr(active_boss, "_original_team"):
                                active_boss.team = active_boss._original_team

                            # Restore hp proportionally if alive
                            if getattr(active_boss, "alive", False):
                                hp_pct = active_boss.hp / (active_boss.max_hp * 3) if active_boss.max_hp > 0 else 1.0
                                active_boss.hp = active_boss.max_hp * hp_pct

                            # Revert everyone else's team
                            for b in balls:
                                if getattr(b, "_original_team", None) is not None and b != active_boss:
                                    b.team = b._original_team

                            # Give a little time buffer to prevent immediate respawn and allow tick to increment it next time
                            self.boss_mutator_timer = delta
                else:
                    self.boss_mutator_timer += delta
                    if self.boss_mutator_timer >= 10.0:
                        self.boss_mutator_timer = 0.0
                        import random
                        valid_bosses = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
                        if valid_bosses:
                            new_boss = random.choice(valid_bosses)
                            new_boss._is_boss_mutator = True
                            new_boss._boss_mutator_duration = 15.0

                            new_boss._original_radius = getattr(new_boss, "radius", 15.0)
                            new_boss.radius = new_boss._original_radius * 2.0

                            new_boss._original_max_hp = getattr(new_boss, "max_hp", 100.0)
                            new_boss.max_hp = new_boss._original_max_hp * 3.0
                            hp_pct = getattr(new_boss, "hp", 100.0) / new_boss._original_max_hp if new_boss._original_max_hp > 0 else 1.0
                            new_boss.hp = new_boss.max_hp * hp_pct

                            new_boss._original_damage = getattr(new_boss, "damage", 10.0)
                            new_boss.damage = new_boss._original_damage * 2.0

                            if hasattr(new_boss, "base_damage"):
                                new_boss._original_base_damage = new_boss.base_damage
                                new_boss.base_damage = new_boss._original_base_damage * 2.0

                            new_boss._original_team = getattr(new_boss, "team", getattr(new_boss, "ball_type", "solo"))
                            new_boss.team = "Boss_Mutator"

                            # Everyone else teams up against the boss
                            for b in balls:
                                if b != new_boss and getattr(b, "ball_type", None) != "spectator":
                                    if not hasattr(b, "_original_team"):
                                        b._original_team = getattr(b, "team", getattr(b, "ball_type", "solo"))
                                    b.team = "Hunters"

                            if hasattr(world, "add_event"):
                                world.add_event("boss_mutator", {"message": f"{new_boss.ball_type.capitalize()} has become a Juggernaut Boss!"})

            trigger_reroll = False
            if "random_reroll" in self.mutators:
                if not hasattr(self, "random_reroll_timer"):
                    self.random_reroll_timer = 0.0
                self.random_reroll_timer += delta
                if self.random_reroll_timer >= 10.0:
                    trigger_reroll = True
                    self.random_reroll_timer = 0.0
                    import random
                    types = ['time_mage', 'paladin', 'assassin', 'ninja', 'warrior', 'guardian', 'chaos', 'bomber', 'templar', 'necromancer', 'vampire', 'sniper', 'king', 'easy', 'phantom', 'warlock', 'mimic', 'juggernaut', 'tank', 'berserker', 'druid', 'hard', 'scout', 'brawler', 'medium', 'neural', 'ranger', 'healer', 'rogue', 'drone', 'swarm', 'conjurer', 'monk', 'mage', 'elementalist', 'trickster']

            for b in balls:
                if not getattr(b, "alive", False):
                    continue
                # Mutators are handled primarily in action.py and physics tick.
                # Adding zero_gravity or explosive_collisions specific game_mode ticks here is optional.
                pass
                if "double_speed" in self.mutators:
                    if hasattr(b, "base_speed") and not getattr(b, "_double_speed_applied", False):
                        b.speed = b.base_speed * 2
                        b._double_speed_applied = True

                if trigger_reroll:
                    if getattr(b, "ball_type", None) != "spectator":
                        b.ball_type = random.choice(types)
                        b.max_hp = random.uniform(50.0, 200.0)
                        b.hp = b.max_hp
                        b.base_speed = random.uniform(50.0, 200.0)
                        b.speed = b.base_speed
                        b.base_damage = random.uniform(5.0, 25.0)
                        b.damage = b.base_damage




class EcholocationMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Echolocation"
        self.description = "The arena is completely dark except for a small ring of light around each ball. Echolocation cues and occasional lightning flashes reveal the map."
        self.flash_timer = 0.0
        self.flash_interval = 10.0
        self.is_flashing = False
        self.flash_duration = 0.5
        self.current_flash_time = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.world = world
        self.flash_timer = 0.0
        self.is_flashing = False
        self.current_flash_time = 0.0

        if hasattr(world, "arena"):
            world.arena.is_night = True

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.base_perception_radius = getattr(b, "perception_radius", 250.0)
                b.team = getattr(b, "team", b.ball_type)
                b.perception_radius = 60.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        self.flash_timer += delta

        if self.is_flashing:
            self.current_flash_time += delta
            if self.current_flash_time >= self.flash_duration:
                self.is_flashing = False
                if hasattr(world, "arena"):
                    world.arena.is_night = True
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                        b.perception_radius = 60.0
        else:
            if self.flash_timer >= self.flash_interval:
                self.flash_timer = 0.0
                self.is_flashing = True
                self.current_flash_time = 0.0
                if hasattr(world, "arena"):
                    world.arena.is_night = False

                if hasattr(world, "add_event"):
                    world.add_event("weather_warning", {"type": "weather_warning", "message": "Lightning flash reveals the arena!"})

                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                        b.perception_radius = 1000.0

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return alive[0].ball_type

        return None


class PitchBlackMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Pitch Black"
        self.description = "The screen is completely dark. AI relies entirely on a narrow cone of light matching its perception radius."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if hasattr(world, "arena"):
            world.arena.is_night = True
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.base_perception_radius = getattr(b, "perception_radius", 250)
                b.team = b.ball_type

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        # Ensure it matches their actual base perception radius
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                b.perception_radius = getattr(b, "base_perception_radius", 250.0)

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return alive[0].ball_type

        return None

class VisionReducedMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Vision Reduced"
        self.description = "Visibility is severely reduced. AI relies on narrow cones of light or sonar-like pulses."
        self.pulse_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.base_perception_radius = getattr(b, "perception_radius", 250)
                b.perception_radius = 50.0  # Severely reduced base visibility
                b.team = b.ball_type

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        self.pulse_timer += delta
        is_pulse_active = False
        if self.pulse_timer >= 3.0:
            if self.pulse_timer >= 3.5:
                self.pulse_timer = 0.0
            else:
                is_pulse_active = True

        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                # Sonar-like pulses temporarily restore or enhance perception
                if is_pulse_active:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0) * 1.5
                else:
                    b.perception_radius = 50.0

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return alive[0].ball_type

        return None

class EMPBurstMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "EMP Burst"
        self.description = "Periodic EMP bursts scramble AI targeting!"
        self.spawn_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []
        self.spawn_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        super().tick(world, balls, delta)

        self.spawn_timer += delta
        if self.spawn_timer >= 5.0:
            self.spawn_timer = 0.0

            import random
            from arena.procedural_arena import Hazard

            x = random.uniform(100, world.arena.width - 100)
            y = random.uniform(100, world.arena.height - 100)

            emp = Hazard(id=len(world.arena.hazards) + random.randint(1000, 9999),
                         x=x, y=y, radius=150.0, kind="emp_burst", damage=0.0)
            emp.duration = 1.0  # Burst lasts briefly
            world.arena.hazards.append(emp)

class DynamicHazardsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Dynamic Hazards"
        self.description = "Dynamic map hazards like spikes, fire, and ice traps spawn, move, or change severity."
        self.spawn_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []
        self.spawn_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        self.spawn_timer += delta
        max_hazards = 15

        if self.spawn_timer >= 3.0:
            self.spawn_timer = 0.0
            import random
            from arena.arena_types import Hazard

            active_dynamic_hazards = [h for h in world.arena.hazards if hasattr(h, 'vx') and hasattr(h, 'vy')]
            if len(active_dynamic_hazards) < max_hazards:
                x = 0.0 if random.random() < 0.5 else world.arena.width
                y = random.uniform(0, world.arena.height)
                vx = random.uniform(50, 200) if x == 0.0 else random.uniform(-200, -50)
                vy = random.uniform(-50, 50)

                hazard_type = random.choice([
                    ("lava", 25.0, 40.0),
                    ("spikes", 15.0, 30.0),
                    ("ice_patch", 5.0, 50.0),
                    ("poison_cloud", 10.0, 45.0)
                ])

                time_factor = 1.0 + (getattr(world, "current_tick", 0) / 60.0) / 100.0
                radius_mult = min(2.0, time_factor)
                damage_mult = min(3.0, time_factor)

                kind, base_damage, base_radius = hazard_type

                new_hazard = Hazard(id=len(world.arena.hazards) + random.randint(1000, 9999),
                                    x=x, y=y, radius=base_radius * radius_mult,
                                    kind=kind, damage=base_damage * damage_mult)
                new_hazard.vx = vx
                new_hazard.vy = vy
                new_hazard.base_radius = base_radius * radius_mult
                new_hazard.base_damage = base_damage * damage_mult

                world.arena.hazards.append(new_hazard)

        import math
        current_time = getattr(world, "current_tick", 0) * delta
        surviving_hazards = []
        for hazard in world.arena.hazards:
            if hasattr(hazard, 'vx') and hasattr(hazard, 'vy'):
                hazard.x += hazard.vx * delta
                hazard.y += hazard.vy * delta

                if hasattr(hazard, 'base_radius'):
                    hazard.radius = hazard.base_radius + math.sin(current_time * 2.0) * 5.0
                    hazard.target_radius = hazard.radius

                if hasattr(hazard, 'base_damage'):
                    # Change severity over time by scaling damage with time
                    hazard.damage = hazard.base_damage * (1.0 + math.sin(current_time) * 0.5)

                margin = 200.0
                if (-margin <= hazard.x <= world.arena.width + margin and
                    -margin <= hazard.y <= world.arena.height + margin):
                    surviving_hazards.append(hazard)
            else:
                surviving_hazards.append(hazard)
        world.arena.hazards = surviving_hazards


class PortalNodeMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Portal Node"
        self.description = "Capture and hold the moving portal node."
        self.portal_timer = 0.0
        self.portal_x = 500.0
        self.portal_y = 500.0
        self.capture_radius = 100.0
        self.drain_rate = 5.0
        self.team_scores = {}

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.team_scores = {}
        for b in balls:
            team = getattr(b, "team", "Solo")
            if team not in self.team_scores:
                self.team_scores[team] = 1000.0

        arena_w = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_h = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.portal_x = arena_w / 2.0
        self.portal_y = arena_h / 2.0
        self.portal_timer = 0.0

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)
        import math
        import random

        self.portal_timer += delta
        if self.portal_timer >= 10.0:
            self.portal_timer = 0.0
            arena_w = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            arena_h = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
            self.portal_x = random.uniform(100, arena_w - 100)
            self.portal_y = random.uniform(100, arena_h - 100)
            print(f"Portal moved to {self.portal_x}, {self.portal_y}")

        # Count balls in portal radius per team
        teams_in_radius = {}
        for b in balls:
            if not getattr(b, "alive", False):
                continue
            dx = b.position.x - self.portal_x
            dy = b.position.y - self.portal_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= self.capture_radius:
                team = getattr(b, "team", "Solo")
                teams_in_radius[team] = teams_in_radius.get(team, 0) + 1

        # If exactly one team is in the radius, they capture it and drain others
        if len(teams_in_radius) == 1:
            controlling_team = list(teams_in_radius.keys())[0]
            for t in self.team_scores:
                if t != controlling_team:
                    self.team_scores[t] -= self.drain_rate * delta
                    if self.team_scores[t] < 0:
                        self.team_scores[t] = 0.0




class MovingSafeZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.collapse_triggered = False
        self.name = "Moving Safe Zone"
        self.description = "A dynamic battle royale where the safe zone not only shrinks but also moves around the map, forcing intense combat."
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 500.0
        self.min_zone_radius = 50.0
        self.shrink_rate = 10.0
        self.outside_damage_per_second = 15.0
        self.zone_target_x = 500.0
        self.zone_target_y = 500.0
        self.move_speed = 30.0
        self.tick_timer = 0.0

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.collapse_triggered = False
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2.0
        self.zone_y = arena_height / 2.0
        self.zone_target_x = self.zone_x
        self.zone_target_y = self.zone_y
        self.zone_radius = min(arena_width, arena_height) / 2.0
        self.min_zone_radius = 50.0

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for i, b in enumerate(valid_balls):
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = False
            else:
                b.team = b.ball_type # Default behavior: solo

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def tick(self, world, balls, delta=0.016):
        import math
        import random

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        # Move safe zone
        dx = self.zone_target_x - self.zone_x
        dy = self.zone_target_y - self.zone_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            self.zone_x += (dx / dist) * self.move_speed * delta
            self.zone_y += (dy / dist) * self.move_speed * delta
        else:
            # Pick a new target that is within the arena bounds minus radius buffer
            # Ensuring it drifts in a random direction and doesn't just converge on a single static point
            buffer = max(100.0, self.zone_radius * 0.5)
            self.zone_target_x = random.uniform(buffer, arena_width - buffer)
            self.zone_target_y = random.uniform(buffer, arena_height - buffer)

        # Shrink safe zone
        if self.zone_radius > self.min_zone_radius:
            self.zone_radius -= self.shrink_rate * delta
            if self.zone_radius <= self.min_zone_radius:
                self.zone_radius = self.min_zone_radius
                if not self.collapse_triggered:
                    self.collapse_triggered = True
                    if hasattr(world, "add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif getattr(self, "collapse_triggered", False):
            # Continue shrinking beyond min_zone_radius towards 0
            if self.zone_radius > 0:
                self.zone_radius -= self.shrink_rate * delta
                if self.zone_radius < 0:
                    self.zone_radius = 0.0

            # Apply gravitational pull
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    dx = self.zone_x - b.x
                    dy = self.zone_y - b.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        pull_strength = 2000.0
                        if not hasattr(b, "vx"): b.vx = 0.0
                        if not hasattr(b, "vy"): b.vy = 0.0
                        b.vx += (dx / dist) * pull_strength * delta
                        b.vy += (dy / dist) * pull_strength * delta

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death = getattr(b, "time_since_death", 0.0) + delta
                continue

            # Check if outside safe zone
            bdx = b.position.x - self.zone_x if hasattr(b, "position") else getattr(b, "x", 0.0) - self.zone_x
            bdy = b.position.y - self.zone_y if hasattr(b, "position") else getattr(b, "y", 0.0) - self.zone_y
            bdist = math.sqrt(bdx*bdx + bdy*bdy)

            if bdist > self.zone_radius:
                if hasattr(b, "hp"):
                    damage = self.outside_damage_per_second * (10.0 if getattr(self, 'collapse_triggered', False) else 1.0) * delta
                    b.hp -= damage

                    if not hasattr(b, "danger_effect_timer"):
                        b.danger_effect_timer = 0.0
                    b.danger_effect_timer += delta
                    if b.danger_effect_timer > 0.5:
                        b.danger_effect_timer = 0.0
                        world.add_event("danger_zone_damage", {
                            "x": b.position.x if hasattr(b, "position") else getattr(b, "x", 0.0),
                            "y": b.position.y if hasattr(b, "position") else getattr(b, "y", 0.0)
                        })

                    if b.hp <= 0:
                        b.alive = False
                        b.killer = "Danger Zone"
                        team = getattr(b, "team", "Unknown")
                        world.add_event("danger_zone_death", {"message": f"{b.ball_type.capitalize()} succumbed to the danger zone!"})

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        return None



class ShrinkingDangerZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.collapse_triggered = False
        self.name = "Shrinking Danger Zone"
        self.description = "A shrinking danger zone mode where the safe area slowly decreases, forcing players into close-quarters combat."
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 500.0
        self.min_zone_radius = 50.0
        self.shrink_rate = 15.0
        self.outside_damage_per_second = 20.0
        self.zone_target_x = 500.0
        self.zone_target_y = 500.0

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.collapse_triggered = False
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2.0
        self.zone_y = arena_height / 2.0
        self.zone_target_x = self.zone_x
        self.zone_target_y = self.zone_y
        self.zone_radius = min(arena_width, arena_height) / 2.0
        self.min_zone_radius = 50.0

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for i, b in enumerate(valid_balls):
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = False
            else:
                b.team = b.ball_type # Default behavior

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def tick(self, world, balls, delta=0.016):
        import math
        import random

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        # Drift the safe zone
        dx = self.zone_target_x - self.zone_x
        dy = self.zone_target_y - self.zone_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            move_speed = 10.0
            self.zone_x += (dx / dist) * move_speed * delta
            self.zone_y += (dy / dist) * move_speed * delta
        else:
            arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
            buffer = max(100.0, self.zone_radius * 0.5)
            self.zone_target_x = random.uniform(buffer, arena_width - buffer)
            self.zone_target_y = random.uniform(buffer, arena_height - buffer)

        # Shrink the safe zone
        if self.zone_radius > self.min_zone_radius:
            self.zone_radius -= self.shrink_rate * delta
            if self.zone_radius <= self.min_zone_radius:
                self.zone_radius = self.min_zone_radius
                if not self.collapse_triggered:
                    self.collapse_triggered = True
                    if hasattr(world, "add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif getattr(self, "collapse_triggered", False):
            # Continue shrinking beyond min_zone_radius towards 0
            if self.zone_radius > 0:
                self.zone_radius -= self.shrink_rate * delta
                if self.zone_radius < 0:
                    self.zone_radius = 0.0

            # Apply gravitational pull
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    dx = self.zone_x - b.x
                    dy = self.zone_y - b.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        pull_strength = 2000.0
                        if not hasattr(b, "vx"): b.vx = 0.0
                        if not hasattr(b, "vy"): b.vy = 0.0
                        b.vx += (dx / dist) * pull_strength * delta
                        b.vy += (dy / dist) * pull_strength * delta

        # Apply continuous damage outside the safe zone
        damage_this_tick = self.outside_damage_per_second * (10.0 if getattr(self, 'collapse_triggered', False) else 1.0) * delta
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                dx = b.x - self.zone_x
                dy = b.y - self.zone_y
                dist = math.sqrt(dx*dx + dy*dy)

                # If outside safe zone, take damage
                if dist > self.zone_radius:
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = False
                        b.hp = 0
                        b.killer = "Danger Zone"

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", None))

        return None


class ModifierZonesSafeZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.collapse_triggered = False
        self.name = "Modifier Zones Safe Zone"
        self.description = "The safe zone shrinks, and modifier zones spawn near its center, forcing players to fight for buffs."
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 500.0
        self.min_zone_radius = 50.0
        self.shrink_rate = 10.0
        self.zone_target_x = 500.0
        self.zone_target_y = 500.0
        self.outside_damage_per_second = 10.0
        self.tick_timer = 0.0
        self.zones = []

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.collapse_triggered = False
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2.0
        self.zone_y = arena_height / 2.0
        self.zone_target_x = self.zone_x
        self.zone_target_y = self.zone_y
        self.zone_radius = min(arena_width, arena_height) / 2.0
        self.min_zone_radius = 50.0

        self.zones = [
            {"id": "zone_speed", "x": self.zone_x - 100, "y": self.zone_y - 100, "radius": 75.0, "type": "speed"},
            {"id": "zone_damage", "x": self.zone_x + 100, "y": self.zone_y - 100, "radius": 75.0, "type": "damage"},
            {"id": "zone_heal", "x": self.zone_x, "y": self.zone_y + 100, "radius": 75.0, "type": "heal"},
            {"id": "zone_debuff", "x": self.zone_x, "y": self.zone_y, "radius": 75.0, "type": "debuff"}
        ]

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for i, b in enumerate(valid_balls):
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = False
            else:
                b.team = b.ball_type

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def tick(self, world, balls, delta=0.016):
        import math
        import random

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        # Move the safe zone
        dx = self.zone_target_x - self.zone_x
        dy = self.zone_target_y - self.zone_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            move_speed = 15.0 # pixels per second
            self.zone_x += (dx / dist) * move_speed * delta
            self.zone_y += (dy / dist) * move_speed * delta
        else:
            arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
            buffer = max(100.0, self.zone_radius * 0.5)
            self.zone_target_x = random.uniform(buffer, arena_width - buffer)
            self.zone_target_y = random.uniform(buffer, arena_height - buffer)

        # Shrink the safe zone
        if self.zone_radius > self.min_zone_radius:
            self.zone_radius -= self.shrink_rate * delta
            if self.zone_radius <= self.min_zone_radius:
                self.zone_radius = self.min_zone_radius
                if not self.collapse_triggered:
                    self.collapse_triggered = True
                    if hasattr(world, "add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif getattr(self, "collapse_triggered", False):
            if self.zone_radius > 0:
                self.zone_radius -= self.shrink_rate * delta
                if self.zone_radius < 0:
                    self.zone_radius = 0.0

            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    dx = self.zone_x - b.x
                    dy = self.zone_y - b.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        pull_strength = 2000.0
                        if not hasattr(b, "vx"): b.vx = 0.0
                        if not hasattr(b, "vy"): b.vy = 0.0
                        b.vx += (dx / dist) * pull_strength * delta
                        b.vy += (dy / dist) * pull_strength * delta

        # Update modifier zones positions relative to the center of the safe zone
        # We spawn them around the safe zone center
        self.zones[0]["x"] = self.zone_x - 100
        self.zones[0]["y"] = self.zone_y - 100
        self.zones[1]["x"] = self.zone_x + 100
        self.zones[1]["y"] = self.zone_y - 100
        self.zones[2]["x"] = self.zone_x
        self.zones[2]["y"] = self.zone_y + 100
        self.zones[3]["x"] = self.zone_x
        self.zones[3]["y"] = self.zone_y

        # Apply modifier logic
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

            in_speed_zone = False
            in_damage_zone = False
            in_heal_zone = False
            in_debuff_zone = False

            for zone in self.zones:
                dx = b.x - zone["x"]
                dy = b.y - zone["y"]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist <= zone["radius"]:
                    if zone["type"] == "speed":
                        in_speed_zone = True
                    elif zone["type"] == "damage":
                        in_damage_zone = True
                    elif zone["type"] == "heal":
                        in_heal_zone = True
                    elif zone["type"] == "debuff":
                        in_debuff_zone = True

            if in_speed_zone:
                b.speed = b.base_speed * 1.5
                b.zone_modifier_speed = True
            else:
                if getattr(b, "zone_modifier_speed", False):
                    b.speed = b.base_speed
                    delattr(b, "zone_modifier_speed")

            if in_damage_zone:
                b.damage = b.base_damage * 1.5
                b.zone_modifier_damage = True
            else:
                if getattr(b, "zone_modifier_damage", False):
                    b.damage = b.base_damage
                    delattr(b, "zone_modifier_damage")

            if in_debuff_zone:
                if not hasattr(b, "base_max_hp"):
                    b.base_max_hp = getattr(b, "max_hp", 100.0)
                b.max_hp = b.base_max_hp * 0.5
                if hasattr(b, "hp") and b.hp > b.max_hp:
                    b.hp = b.max_hp
                b.zone_modifier_debuff = True
            else:
                if getattr(b, "zone_modifier_debuff", False):
                    if hasattr(b, "base_max_hp"):
                        b.max_hp = b.base_max_hp
                    delattr(b, "zone_modifier_debuff")

            if in_heal_zone:
                if hasattr(b, "hp") and hasattr(b, "max_hp"):
                    b.hp = min(getattr(b, "max_hp", 100.0), b.hp + 20.0 * delta)

            # Apply continuous damage outside the safe zone
            damage_this_tick = self.outside_damage_per_second * (10.0 if getattr(self, 'collapse_triggered', False) else 1.0) * delta
            dx = b.x - self.zone_x
            dy = b.y - self.zone_y
            dist = math.sqrt(dx*dx + dy*dy)

            if dist > self.zone_radius:
                if hasattr(b, "hp"):
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = False
                        b.hp = 0

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", None))

        return None


class SafeZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.collapse_triggered = False
        self.name = "Safe Zone"
        self.description = "A battle royale mode where the safe zone gradually shrinks, and balls take continuous damage outside of it."
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 500.0
        self.min_zone_radius = 50.0
        self.shrink_rate = 10.0
        self.zone_target_x = 500.0
        self.zone_target_y = 500.0
        self.outside_damage_per_second = 10.0
        self.tick_timer = 0.0

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.collapse_triggered = False
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2.0
        self.zone_y = arena_height / 2.0
        self.zone_target_x = self.zone_x
        self.zone_target_y = self.zone_y
        self.zone_radius = min(arena_width, arena_height) / 2.0
        self.min_zone_radius = 50.0

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for i, b in enumerate(valid_balls):
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = False
            else:
                b.team = b.ball_type # Default behavior

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def tick(self, world, balls, delta=0.016):
        import math

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        # Move the safe zone
        import random
        dx = self.zone_target_x - self.zone_x
        dy = self.zone_target_y - self.zone_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            move_speed = 15.0 # pixels per second
            self.zone_x += (dx / dist) * move_speed * delta
            self.zone_y += (dy / dist) * move_speed * delta
        else:
            # Pick a new target within the current safe zone to ensure it stays mostly within bounds
            # Making it drift in a random direction and not converging on a single static point
            arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
            buffer = max(100.0, self.zone_radius * 0.5)
            self.zone_target_x = random.uniform(buffer, arena_width - buffer)
            self.zone_target_y = random.uniform(buffer, arena_height - buffer)

        # Shrink the safe zone
        if self.zone_radius > self.min_zone_radius:
            self.zone_radius -= self.shrink_rate * delta
            if self.zone_radius <= self.min_zone_radius:
                self.zone_radius = self.min_zone_radius
                if not self.collapse_triggered:
                    self.collapse_triggered = True
                    if hasattr(world, "add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif getattr(self, "collapse_triggered", False):
            # Continue shrinking beyond min_zone_radius towards 0
            if self.zone_radius > 0:
                self.zone_radius -= self.shrink_rate * delta
                if self.zone_radius < 0:
                    self.zone_radius = 0.0

            # Apply gravitational pull
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    dx = self.zone_x - b.x
                    dy = self.zone_y - b.y
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist > 0:
                        pull_strength = 2000.0
                        if not hasattr(b, "vx"): b.vx = 0.0
                        if not hasattr(b, "vy"): b.vy = 0.0
                        b.vx += (dx / dist) * pull_strength * delta
                        b.vy += (dy / dist) * pull_strength * delta

        # Apply continuous damage outside the safe zone
        damage_this_tick = self.outside_damage_per_second * (10.0 if getattr(self, 'collapse_triggered', False) else 1.0) * delta
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                dx = b.x - self.zone_x
                dy = b.y - self.zone_y
                dist = math.sqrt(dx*dx + dy*dy)

                # If outside safe zone, take damage
                if dist > self.zone_radius:
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = False
                        b.hp = 0

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            self._award_skill_points()
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            self._award_skill_points()
            return list(teams_alive)[0]

        if len(alive) == 1:
            self._award_skill_points()
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", None))

        return None

    def _award_skill_points(self):
        try:
            from system.profile import ProfileManager  # type: ignore
            pm = ProfileManager("profile.json")
            pm.add_skill_points(10)
        except Exception:
            pass



class MirrorMatchMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Mirror Match"
        self.description = "Every player spawns with an exact AI clone of themselves on the opposite side of the map. Clones mimic their creator's stats and skills."
        self.world = None

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        self.world = world

        # We need to create clones
        import copy
        import random

        new_clones = []
        arena_width = getattr(getattr(world, "arena", None), "width", 2000.0)
        arena_height = getattr(getattr(world, "arena", None), "height", 2000.0)

        for b in balls:
            clone = copy.copy(b)
            clone.id = getattr(world, "next_id", random.randint(10000, 99999))
            if hasattr(world, "next_id"):
                world.next_id += 1

            # Place on opposite side of map (mirror point relative to center)
            clone.x = arena_width - b.x
            clone.y = arena_height - b.y

            # Make sure it behaves like a normal AI ball but with same stats
            clone.is_clone = True
            clone.clone_owner = b.id
            clone.team = "mirror_team_" + str(b.team) if hasattr(b, "team") else "mirror"

            new_clones.append(clone)

        if hasattr(world, "balls"):
            world.balls.extend(new_clones)


class VolatileClonesMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Volatile Clones"
        self.description = "Similar to Clone Chaos, but when a clone's HP drops to 0, it explodes dealing small area-of-effect damage."
        self.clone_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        for b in balls:
            b.skill = "clone"
            b.active_skill = "clone"
            b.SKILL = "clone"
            b.skill_cooldown = 1.0
            b.skill_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        self.clone_timer += delta
        if self.clone_timer > 3.0:
            self.clone_timer = 0.0
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "skill_timer", 0.0) <= 0:
                    b.skill_timer = 1.0
                    import copy
                    import random
                    num_clones = random.randint(1, 3)
                    for _ in range(num_clones):
                        clone = copy.copy(b)
                        clone.id = getattr(world, "next_id", random.randint(10000, 99999))
                        if hasattr(world, "next_id"):
                            world.next_id += 1
                        clone.x += random.uniform(-30, 30)
                        clone.y += random.uniform(-30, 30)
                        clone.hp = getattr(b, "hp", 100)
                        clone.max_hp = getattr(b, "max_hp", 100)
                        clone.team = getattr(b, "team", getattr(b, "ball_type", getattr(b, "BALL_TYPE", "")))
                        clone.is_clone = True
                        clone.clone_owner = b.id
                        clone.alive = True
                        clone.speed = 0 # static copy
                        clone.damage = 0 # they do no damage
                        clone.is_decoy = True  # treat as decoy so it can explode
                        clone.decoy_type = "explosive" # make sure it explodes
                        clone.traits = ["volatile_decoy"] # higher damage
                        clone.decoy_timer = 9999.0 # wait for HP to reach 0

                        clone.skill_timer = 9999 # no skills
                        clone.skill = None
                        if hasattr(clone, "SKILL"):
                            clone.SKILL = None
                        if hasattr(clone, "active_skill"):
                            clone.active_skill = None

                        if hasattr(world, "balls"):
                            world.balls.append(clone)

class CloneChaosMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Clone Chaos"
        self.description = "Every ball starts with the 'clone' skill with very low cooldown. The arena is quickly filled with static copies, causing mass confusion."
        self.clone_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        for b in balls:
            b.skill = "clone"
            b.active_skill = "clone"
            b.SKILL = "clone"
            b.skill_cooldown = 1.0  # very fast cooldown
            b.skill_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        super().tick(world, balls, delta)
        self.clone_timer += delta
        # occasionally force all balls to cast if available
        if self.clone_timer > 3.0:
            self.clone_timer = 0.0
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "skill_timer", 0.0) <= 0:
                    b.skill_timer = 1.0
                    import copy
                    import random
                    num_clones = random.randint(1, 3)
                    for _ in range(num_clones):
                        clone = copy.copy(b)
                        clone.id = getattr(world, "next_id", random.randint(10000, 99999))
                        if hasattr(world, "next_id"):
                            world.next_id += 1
                        clone.x += random.uniform(-30, 30)
                        clone.y += random.uniform(-30, 30)
                        clone.hp = getattr(b, "hp", 100)
                        clone.max_hp = getattr(b, "max_hp", 100)
                        clone.team = getattr(b, "team", getattr(b, "ball_type", getattr(b, "BALL_TYPE", "")))
                        clone.is_clone = True
                        clone.clone_owner = b.id
                        clone.alive = True
                        clone.speed = 0 # static copy
                        clone.damage = 0 # they do no damage

                        clone.skill_timer = 9999 # no skills
                        clone.skill = None
                        if hasattr(clone, "SKILL"):
                            clone.SKILL = None
                        if hasattr(clone, "active_skill"):
                            clone.active_skill = None

                        if hasattr(world, "balls"):
                            world.balls.append(clone)

class BumperBallsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Bumper Balls"
        self.description = "Balls deal zero damage but bounce each other with much higher knockback. Try to push opponents off the arena!"

    def setup(self, world: Any, balls: List[Any]) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if hasattr(b, "sponsor"):
                if b.sponsor == "aggressor":
                    b.max_hp = getattr(b, "max_hp", 100.0) * 0.8
                    b.hp = min(getattr(b, "hp", 100.0), b.max_hp)
                elif b.sponsor == "juggernaut":
                    b.speed = getattr(b, "speed", 100.0) * 0.8
                    if hasattr(b, "base_speed"):
                        b.base_speed *= 0.8
                elif b.sponsor == "vampiric":
                    b.max_hp = getattr(b, "max_hp", 100.0) * 0.9
                    b.hp = min(getattr(b, "hp", 100.0), b.max_hp)
        for b in balls:
            b.damage = 0.0
            # We can use a special flag or mutator to handle the knockback in action.py
            if not hasattr(b, "mutators"):
                b.mutators = []
            if "bumper_balls" not in b.mutators:
                b.mutators.append("bumper_balls")

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else getattr(world, "width", 1000)
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else getattr(world, "height", 1000)

        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            radius = getattr(b, "radius", 10.0)
            bx = getattr(b, "x", arena_width / 2)
            by = getattr(b, "y", arena_height / 2)
            if bx < -radius or bx > arena_width + radius or by < -radius or by > arena_height + radius:
                b.alive = False

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"
        if len(alive) == 1:
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", "Unknown"))
        return None


class TournamentMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Tournament"
        self.description = "Monthly or seasonal tournament where players compete for exclusive cosmetic ball skins and unique status effects."
        self.tick_timer = 0.0

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        if len(alive) == 1:
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", None))

        return None

class ToxicEnvironmentMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Toxic Environment"
        self.description = "Balls take constant damage over time. Collect temporary immune boosters to survive."
        self.tick_timer = 0.0
        self.spawn_timer = 0.0

    def setup(self, world, balls) -> None:
        super().setup(world, balls)
        if not hasattr(world, "boosters"):
            world.boosters = []
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def tick(self, world, balls, delta: float = 0.016) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        if not hasattr(world, "boosters"):
            world.boosters = []

        import random
        self.spawn_timer += delta
        if self.spawn_timer >= 1.0:
            self.spawn_timer = 0.0
            immune_boosters = [b for b in world.boosters if isinstance(b, dict) and b.get("is_immunity") and b.get("active")]
            if len(immune_boosters) < 5:
                x = random.uniform(100, 900)
                y = random.uniform(100, 900)
                b_id = getattr(world, "next_id", random.randint(10000, 99999))
                if hasattr(world, "next_id"):
                    world.next_id += 1
                world.boosters.append({
                    "id": b_id,
                    "x": x,
                    "y": y,
                    "ball_type": "booster",
                    "active": True,
                    "is_immunity": True,
                    "radius": 15.0
                })

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
                continue

            imm_timer = getattr(b, "immunity_timer", 0.0)
            if imm_timer > 0:
                b.immunity_timer = imm_timer - delta
            else:
                b.immunity_timer = 0.0
                damage = 5.0 * delta
                if hasattr(b, "take_damage"):
                    b.take_damage(damage)

            to_remove = []
            for booster in world.boosters:
                if isinstance(booster, dict) and booster.get("is_immunity") and booster.get("active"):
                    bx, by = booster.get("x", 0), booster.get("y", 0)
                    dist = ((b.x - bx)**2 + (b.y - by)**2)**0.5
                    if dist < getattr(b, "radius", 10.0) + booster.get("radius", 15.0):
                        b.immunity_timer = 5.0
                        booster["active"] = False
                        to_remove.append(booster)

            for booster in to_remove:
                if booster in world.boosters:
                    world.boosters.remove(booster)

    def check_winner(self, world, balls) -> str:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"
        if len(alive) == 1:
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", "Unknown"))
        return None



class ModifierZonesMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Modifier Zones"
        self.description = "Fight over zones that provide different temporary buffs."
        self.zones = []

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        self.zones = [
            {"id": "zone_speed", "x": arena_width * 0.25, "y": arena_height * 0.25, "radius": 150.0, "type": "speed"},
            {"id": "zone_damage", "x": arena_width * 0.75, "y": arena_height * 0.25, "radius": 150.0, "type": "damage"},
            {"id": "zone_heal", "x": arena_width * 0.5, "y": arena_height * 0.75, "radius": 150.0, "type": "heal"},
            {"id": "zone_debuff", "x": arena_width * 0.5, "y": arena_height * 0.25, "radius": 150.0, "type": "debuff"}
        ]

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.team = getattr(b, "team", b.ball_type)

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        super().tick(world, balls, delta)
        import math

        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

            in_speed_zone = False
            in_damage_zone = False
            in_heal_zone = False
            in_debuff_zone = False

            for zone in self.zones:
                dx = b.x - zone["x"]
                dy = b.y - zone["y"]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist <= zone["radius"]:
                    if zone["type"] == "speed":
                        in_speed_zone = True
                    elif zone["type"] == "damage":
                        in_damage_zone = True
                    elif zone["type"] == "heal":
                        in_heal_zone = True
                    elif zone["type"] == "debuff":
                        in_debuff_zone = True

            if in_speed_zone:
                b.speed = b.base_speed * 1.5
                b.zone_modifier_speed = True
            else:
                if getattr(b, "zone_modifier_speed", False):
                    b.speed = b.base_speed
                    delattr(b, "zone_modifier_speed")

            if in_damage_zone:
                b.damage = b.base_damage * 1.5
                b.zone_modifier_damage = True
            else:
                if getattr(b, "zone_modifier_damage", False):
                    b.damage = b.base_damage
                    delattr(b, "zone_modifier_damage")

            if in_debuff_zone:
                if not hasattr(b, "base_max_hp"):
                    b.base_max_hp = getattr(b, "max_hp", 100.0)
                b.max_hp = b.base_max_hp * 0.5
                if hasattr(b, "hp") and b.hp > b.max_hp:
                    b.hp = b.max_hp
                b.zone_modifier_debuff = True
            else:
                if getattr(b, "zone_modifier_debuff", False):
                    if hasattr(b, "base_max_hp"):
                        b.max_hp = b.base_max_hp
                    delattr(b, "zone_modifier_debuff")

            if in_heal_zone:
                if hasattr(b, "hp") and hasattr(b, "max_hp"):
                    b.hp = min(getattr(b, "max_hp", 100.0), b.hp + 20.0 * delta)

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", None))

        return None



class WindstormMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Windstorm"
        self.description = "Periodically pushes all balls in a random direction, forcing them to constantly adjust movement to stay on target."
        self.push_timer = 3.0
        self.push_duration = 0.0
        self.push_dir_x = 0.0
        self.push_dir_y = 0.0
        self.push_strength = 600.0
        import random
        self.random = random

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for b in valid_balls:
            b.team = b.ball_type
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        self.push_timer -= delta
        if self.push_timer <= 0:
            if self.push_duration <= 0:
                # Start push
                import math
                angle = self.random.uniform(0, 2 * math.pi)
                if hasattr(world, 'add_event'):
                    world.add_event('weather_warning', {'type': 'weather_warning', 'message': 'Windstorm is pushing!'})
                self.push_dir_x = math.cos(angle)
                self.push_dir_y = math.sin(angle)
                self.push_duration = self.random.uniform(1.0, 2.0)
            else:
                self.push_duration -= delta
                if self.push_duration <= 0:
                    self.push_timer = self.random.uniform(2.0, 4.0)

        if self.push_duration > 0:
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    if not hasattr(b, "vx"):
                        b.vx = 0.0
                    if not hasattr(b, "vy"):
                        b.vy = 0.0
                    # Kite logic
                    is_kite = getattr(b, "cosmetic", "").lower().replace(" ", "_") == "kite"
                    strength = self.push_strength
                    if is_kite:
                        b.speed = getattr(b, "base_speed", 100.0) * 1.5
                        strength = self.push_strength * 1.5 # Increases jump distance / push force

                    b.vx += self.push_dir_x * strength * delta
                    b.vy += self.push_dir_y * strength * delta

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return getattr(alive[0], "team", getattr(alive[0], "ball_type", None))

        return None



class BlackoutMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Blackout"
        self.description = "Periodically, the arena goes completely dark, reducing vision drastically for all balls."
        self.timer = 0.0
        self.is_blackout = False

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.timer = 0.0
        self.is_blackout = False
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.base_perception_radius = getattr(b, "perception_radius", 250)
                b.team = b.ball_type

    def tick(self, world, balls, delta=0.016):
        self.timer += delta
        if self.timer >= 5.0:
            self.timer = 0.0
            self.is_blackout = not self.is_blackout
            if hasattr(world, "add_event"):
                msg = "The arena went dark!" if self.is_blackout else "Vision restored!"
                world.add_event("weather_warning", {"type": "weather_warning", "message": msg})

        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                if self.is_blackout:
                    b.perception_radius = 50.0
                else:
                    b.perception_radius = getattr(b, "base_perception_radius", 250.0)


class BountyHuntMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Bounty Hunt"
        self.description = "One ball on each team is the Bounty. Destroying the enemy Bounty grants a massive buff and extra skill points."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        red_team = []
        blue_team = []

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        mid = len(valid_balls) // 2
        for i, b in enumerate(valid_balls):
            if i < mid:
                b.team = "Red"
                red_team.append(b)
            else:
                b.team = "Blue"
                blue_team.append(b)

        self.bounties = {}
        import random
        if red_team:
            red_bounty = random.choice(red_team)
            red_bounty.is_bounty = True
            red_bounty.bounty_timer = 0
            self.bounties["Red"] = red_bounty
        if blue_team:
            blue_bounty = random.choice(blue_team)
            blue_bounty.is_bounty = True
            blue_bounty.bounty_timer = 0
            self.bounties["Blue"] = blue_bounty

        self.buffed_teams: set[str] = set()

    def tick(self, world: Any, balls: List[Any], delta: float = 0.0) -> None:
        super().tick(world, balls, delta)

        for team, bounty in list(self.bounties.items()):
            if not getattr(bounty, "alive", False) and team not in self.buffed_teams:
                self.buffed_teams.add(team)
                enemy_team = "Blue" if team == "Red" else "Red"

                # Global stat buff
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "team", "") == enemy_team:
                        b.base_damage = getattr(b, "base_damage", 10.0) * 2.0
                        b.base_speed = getattr(b, "base_speed", 100.0) * 1.5
                        b.max_hp = getattr(b, "max_hp", 100.0) * 1.5
                        b.hp = getattr(b, "max_hp", 100.0)
                        b.skill_uses = getattr(b, "skill_uses", 0) + 3

                # Extra skill points for the player
                if hasattr(self, '_award_skill_points'):
                    self._award_skill_points()
                    self._award_skill_points()
                    self._award_skill_points()

                if hasattr(world, "add_event"):
                    world.add_event("bounty_destroyed", {"message": f"{team} Bounty destroyed! {enemy_team} gets massive buff!"})

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", "")) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]
        return None

class EarthquakeMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Earthquake"
        self.description = "Periodically shakes the screen and applies random impulses to all entities."
        self.timer = 0.0
        self.is_shaking = False
        self.shake_timer = 0.0

    def tick(self, world, balls, delta=0.016):
        import random
        # Handle dead balls
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        if self.is_shaking:
            self.shake_timer -= delta
            if self.shake_timer <= 0.0:
                self.is_shaking = False
            else:
                # Apply random impulses
                for b in balls:
                    if getattr(b, "hp", 0) > 0 and getattr(b, "anchor_booster_timer", 0.0) <= 0:
                        b.x += random.uniform(-50.0, 50.0) * delta
                        b.y += random.uniform(-50.0, 50.0) * delta
                        if hasattr(b, "vx"):
                            b.vx += random.uniform(-50.0, 50.0)
                        if hasattr(b, "vy"):
                            b.vy += random.uniform(-50.0, 50.0)

                if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
                    for hazard in world.arena.hazards:
                        if hasattr(hazard, "x") and hasattr(hazard, "y"):
                            hazard.x += random.uniform(-20.0, 20.0) * delta
                            hazard.y += random.uniform(-20.0, 20.0) * delta

                if hasattr(world, "arena") and hasattr(world.arena, "items"):
                    for item in world.arena.items:
                        if hasattr(item, "x") and hasattr(item, "y"):
                            item.x += random.uniform(-20.0, 20.0) * delta
                            item.y += random.uniform(-20.0, 20.0) * delta

        else:
            self.timer += delta
            # Randomly trigger earthquake every ~10-15 seconds
            if self.timer > 10.0 and random.random() < 0.2 * delta:
                self.timer = 0.0
                self.is_shaking = True
                self.shake_timer = random.uniform(2.0, 5.0)
                if hasattr(world, "add_event"):
                    world.add_event("earthquake", {"type": "earthquake", "intensity": self.shake_timer / 2.0})


class ShiftingMazeMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Shifting Maze"
        self.description = "The arena starts as a complex maze that slowly shifts and shrinks. Walls deal damage."
        self.walls = []
        self.maze_scale = 1.0
        self.shrink_rate = 0.01
        self.wall_damage_per_second = 50.0

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        self.maze_scale = 1.0
        self.walls = []

        cell_size = 200
        cols = int(arena_width / cell_size)
        rows = int(arena_height / cell_size)

        import random
        rng = random.Random(42)
        for c in range(cols):
            for r in range(rows):
                if rng.random() > 0.5:
                    self.walls.append({
                        "x": c * cell_size,
                        "y": r * cell_size,
                        "width": cell_size,
                        "height": 20,
                        "dx": rng.uniform(-10, 10),
                        "dy": rng.uniform(-10, 10)
                    })
                else:
                    self.walls.append({
                        "x": c * cell_size,
                        "y": r * cell_size,
                        "width": 20,
                        "height": cell_size,
                        "dx": rng.uniform(-10, 10),
                        "dy": rng.uniform(-10, 10)
                    })

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)

        if self.maze_scale > 0.2:
            self.maze_scale -= self.shrink_rate * delta

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        center_x = arena_width / 2.0
        center_y = arena_height / 2.0

        for w in self.walls:
            w["x"] += w["dx"] * delta
            w["y"] += w["dy"] * delta

        for b in balls:
            if not getattr(b, "alive", False):
                continue

            bx = getattr(b, "x", 0.0)
            by = getattr(b, "y", 0.0)
            br = getattr(b, "radius", 20.0)

            touching_wall = False
            for w in self.walls:
                wx = center_x + (w["x"] - center_x) * self.maze_scale
                wy = center_y + (w["y"] - center_y) * self.maze_scale
                ww = max(5, w["width"] * self.maze_scale)
                wh = max(5, w["height"] * self.maze_scale)

                nearest_x = max(wx, min(bx, wx + ww))
                nearest_y = max(wy, min(by, wy + wh))

                dist_sq = (bx - nearest_x)**2 + (by - nearest_y)**2
                if dist_sq < br**2:
                    touching_wall = True
                    break

            if touching_wall:
                dmg = self.wall_damage_per_second * delta
                if hasattr(b, "take_damage"):
                    b.take_damage(dmg, "maze_wall")
                else:
                    b.hp = getattr(b, "hp", 100) - dmg
                if getattr(b, "hp", 100) <= 0:
                    b.alive = False

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False)]
        if len(alive) == 1:
            return alive[0].ball_type
        if len(alive) == 0:
            return "Draw"
        return None


class GravityWellMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Gravity Well"
        self.description = "Random gravity wells spawn in the arena, pulling nearby balls towards their center and slightly damaging them over time."
        self.spawn_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []
        self.spawn_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        super().tick(world, balls, delta)
        import random

        self.spawn_timer += delta
        if self.spawn_timer >= 5.0:
            self.spawn_timer = 0.0

            arena_width = getattr(world.arena, "width", 2000.0)
            arena_height = getattr(world.arena, "height", 2000.0)

            x = random.uniform(200.0, arena_width - 200.0)
            y = random.uniform(200.0, arena_height - 200.0)

            h_id = 9000 + len(world.arena.hazards) + random.randint(0, 1000)

            from arena.procedural_arena import Hazard
            gw = Hazard(id=h_id, x=x, y=y, radius=random.uniform(150.0, 300.0), kind="gravity_well", damage=10.0)
            world.arena.hazards.append(gw)

            # Limit total gravity wells to 5 to avoid overcrowding
            gw_hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") == "gravity_well"]
            if len(gw_hazards) > 5:
                # Remove the oldest one
                oldest_gw = gw_hazards[0]
                world.arena.hazards.remove(oldest_gw)


class SupernovaMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Supernova"
        self.description = "Balls take rapidly scaling heat damage as they approach the center. Eventually, the supernova explodes, knocking survivors away."
        self.supernova_radius = 50.0
        self.supernova_exploded = False
        self.explosion_timer = 0.0
        self.heat_multiplier = 1.0

    def tick(self, world, balls, delta: float = 0.016) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
        import math
        arena_width = 1000.0
        arena_height = 1000.0
        if hasattr(world, "arena") and world.arena:
            arena_width = getattr(world.arena, "width", 1000.0)
            arena_height = getattr(world.arena, "height", 1000.0)

        center_x = arena_width / 2.0
        center_y = arena_height / 2.0

        if not self.supernova_exploded:
            self.supernova_radius += 2.0 * delta
            self.explosion_timer += delta

            # Explosion triggers at e.g. 20 seconds
            if self.explosion_timer >= 20.0:
                self.supernova_exploded = True
                self.explosion_timer = 0.0
                # Trigger knockback for all alive balls
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                        dx = b.x - center_x
                        dy = b.y - center_y
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            # Massive outward knockback force
                            knockback = 50000.0 / max(dist, 10.0)
                            b.vx = getattr(b, "vx", 0.0) + (dx / dist) * knockback
                            b.vy = getattr(b, "vy", 0.0) + (dy / dist) * knockback

        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                dx = center_x - b.x
                dy = center_y - b.y
                dist = math.hypot(dx, dy)

                if not self.supernova_exploded:
                    # Pull towards center
                    if dist > 0:
                        pull_strength = 20000.0 / (dist * dist)
                        radius_multiplier = self.supernova_radius / 50.0
                        pull_strength *= radius_multiplier
                        pull_strength = min(pull_strength, 150.0 * radius_multiplier)

                        b.x += (dx / dist) * pull_strength * delta
                        b.y += (dy / dist) * pull_strength * delta

                    # Heat damage
                    max_dist = max(arena_width, arena_height) / 2.0
                    if dist < max_dist:
                        damage_intensity = (max_dist - dist) / max_dist
                        heat_damage = 5.0 * (damage_intensity ** 3) * self.heat_multiplier * delta
                        if hasattr(b, "hp"):
                            b.hp -= heat_damage
                            if b.hp <= 0:
                                b.hp = 0
                                b.alive = False

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return alive[0].ball_type

        return None



class DayNightMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Day/Night Cycle"
        self.description = "Periodically toggles day and night, affecting ball behavior and visibility."
        self.timer = 0.0
        self.phase_duration = 10.0

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        if hasattr(world, "arena"):
            world.arena.is_night = False
        self.timer = 0.0

    def tick(self, world, balls, delta=0.016):
        if hasattr(world, "arena"):
            self.timer += delta
            if self.timer >= self.phase_duration:
                self.timer = 0.0
                world.arena.is_night = not getattr(world.arena, "is_night", False)


class GuildVsGuildMode(GameMode):
    """Guild vs Guild mode where players capture territory on a persistent world map."""
    def __init__(self):
        super().__init__()
        self.name = "gvg"
        self.desc = "Guild vs Guild territory battle"
        self.guilds = {} # mapping of guild name to list of ball ids
        self.control_points = []
        self.territory_captured = False

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.guilds = {}
        self.control_points = [
            {"x": 200, "y": 200, "radius": 50, "owner": None, "progress": 0},
            {"x": 800, "y": 800, "radius": 50, "owner": None, "progress": 0},
            {"x": 500, "y": 500, "radius": 80, "owner": None, "progress": 0}
        ]
        self.territory_captured = False

        # mock assign balls to guilds for testing
        if len(balls) >= 2:
            guild1_balls = balls[:len(balls)//2]
            guild2_balls = balls[len(balls)//2:]
            self.guilds["GuildA"] = [b.id for b in guild1_balls]
            self.guilds["GuildB"] = [b.id for b in guild2_balls]

    def _tick(self, delta):
        # no super()._tick(delta) in GameMode
        if self.territory_captured:
            return

        import math

        # Update control points
        for cp in self.control_points:
            guild_counts = {}
            for guild, members in self.guilds.items():
                count = 0
                for ball in self.world.balls:
                    if ball.id in members and ball.alive:
                        dx = ball.x - cp["x"]
                        dy = ball.y - cp["y"]
                        if math.sqrt(dx*dx + dy*dy) <= cp["radius"]:
                            count += 1
                guild_counts[guild] = count

            # Find dominating guild
            dominating_guild = None
            max_count = 0
            for guild, count in guild_counts.items():
                if count > max_count:
                    max_count = count
                    dominating_guild = guild
                elif count == max_count and count > 0:
                    dominating_guild = None # Contested

            if dominating_guild:
                if cp["owner"] != dominating_guild:
                    cp["progress"] += delta * 10
                    if cp["progress"] >= 100:
                        cp["owner"] = dominating_guild
                        cp["progress"] = 100
            else:
                cp["progress"] = max(0, cp["progress"] - delta * 5)

        # Check win condition (one guild owns all CPs)
        owners = [cp["owner"] for cp in self.control_points if cp["owner"] is not None]
        if len(owners) == len(self.control_points) and len(set(owners)) == 1:
            winner = owners[0]
            self._end_match(winner)

    def _end_match(self, winner_guild):
        self.territory_captured = True
        try:
            from system.guild import GuildManager
            gm = GuildManager()
            gm.capture_territory(winner_guild, "GvG_Arena")

            # record match
            loser = "GuildB" if winner_guild == "GuildA" else "GuildA"
            gm.record_gvg_match(winner_guild, loser, winner_guild)
        except ImportError:
            pass


class MagneticCollisionsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Magnetic Collisions"
        self.description = "Invisible magnetic fields pull or push balls depending on their assigned polarities. Every 10 seconds, polarities randomly flip, causing sudden tactical shifts and chaotic collisions."
        self.polarity_flip_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        import random

        # Setup magnetic fields as invisible hazards
        if hasattr(world, "arena") and world.arena:
            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []

            arena_width = getattr(world.arena, "width", 1000)
            arena_height = getattr(world.arena, "height", 1000)

            # Use Hazard class if possible
            try:
                from arena.procedural_arena import Hazard
                def create_hazard(hid, hx, hy, r, kind):
                    h = Hazard(id=hid, x=hx, y=hy, radius=r, kind=kind, damage=0.0)
                    h.invisible = True
                    return h
            except ImportError:
                class MagHazard:
                    def __init__(self, hid, hx, hy, r, kind):
                        self.id = hid
                        self.x = hx
                        self.y = hy
                        self.radius = r
                        self.kind = kind
                        self.damage = 0.0
                        self.invisible = True
                def create_hazard(hid, hx, hy, r, kind):
                    return MagHazard(hid, hx, hy, r, kind)

            for i in range(5):
                x = random.uniform(200, arena_width - 200)
                y = random.uniform(200, arena_height - 200)
                r = random.uniform(150, 300)
                kind = random.choice(["magnetic_field_positive", "magnetic_field_negative"])
                h = create_hazard(20000 + i, x, y, r, kind)
                world.arena.hazards.append(h)

        # Assign random polarities to balls
        for b in balls:
            if getattr(b, "alive", True) and getattr(b, "ball_type", None) != "spectator":
                b.polarity = random.choice(["positive", "negative"])

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        import math
        import random

        self.polarity_flip_timer += delta

        if self.polarity_flip_timer >= 10.0:
            self.polarity_flip_timer = 0.0
            for b in balls:
                if getattr(b, "alive", True) and getattr(b, "ball_type", None) != "spectator":
                    b.polarity = "positive" if getattr(b, "polarity", "positive") == "negative" else "negative"
            if hasattr(world, "add_event"):
                world.add_event("polarity_flip", {"message": "Polarities have flipped!"})

        # Apply magnetic forces
        if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
            for h in world.arena.hazards:
                h_kind = getattr(h, "kind", "")
                if h_kind in ["magnetic_field_positive", "magnetic_field_negative"]:
                    h_polarity = "positive" if "positive" in h_kind else "negative"
                    hx = getattr(h, "x", 0.0)
                    hy = getattr(h, "y", 0.0)
                    hr = getattr(h, "radius", 0.0)

                    for b in balls:
                        if not getattr(b, "alive", True) or getattr(b, "ball_type", None) == "spectator":
                            continue

                        b_polarity = getattr(b, "polarity", "positive")

                        bx = getattr(b, "x", 0.0)
                        by = getattr(b, "y", 0.0)

                        dx = hx - bx
                        dy = hy - by
                        dist = math.sqrt(dx*dx + dy*dy)

                        if dist > 0 and dist < hr:
                            # Force magnitude inverse to distance
                            force = (hr - dist) / hr * 200.0 * delta

                            # Opposites attract, likes repel
                            if h_polarity != b_polarity:
                                b.x += (dx / dist) * force
                                b.y += (dy / dist) * force
                            else:
                                b.x -= (dx / dist) * force
                                b.y -= (dy / dist) * force


class StaminaRegenMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Stamina Regen modifier"
        self.description = "A game mode modifier where stamina regenerates twice as fast, allowing more frequent use of stamina-based skills."

class ZeroGravityMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Zero Gravity"
        self.description = "Friction and gravity are drastically reduced, causing balls to slide around effortlessly and collisions to produce massive knockback."

class PinballMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Pinball Mode"
        self.description = "Lots of bouncy bumpers and physics-based knockback logic to push balls around the arena."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if hasattr(world, "arena") and world.arena:
            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []
            import random
            arena_width = getattr(world.arena, "width", 1000)
            arena_height = getattr(world.arena, "height", 1000)

            # Use Hazard class if possible, else dict-like
            try:
                from arena.procedural_arena import Hazard
                def create_hazard(hid, hx, hy, r):
                    return Hazard(id=hid, x=hx, y=hy, radius=r, kind="bumper", damage=0.0)
            except ImportError:
                class BumperHazard:
                    def __init__(self, hid, hx, hy, r):
                        self.id = hid
                        self.x = hx
                        self.y = hy
                        self.radius = r
                        self.kind = "bumper"
                        self.damage = 0.0
                def create_hazard(hid, hx, hy, r):
                    return BumperHazard(hid, hx, hy, r)

            for i in range(20):
                x = random.uniform(100, arena_width - 100)
                y = random.uniform(100, arena_height - 100)
                r = random.uniform(30.0, 60.0)
                world.arena.hazards.append(create_hazard(10000 + i, x, y, r))

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:

        super().tick(world, balls, delta)


class MirrorWallsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Mirror Walls"
        self.description = "An arena event where all projectiles are reflected infinitely across mirror walls."

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)


class GeometricZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.collapse_triggered = False
        self.name = "Geometric Zone"
        self.description = "The safe zone shrinks into varied geometric shapes or splits temporarily to disrupt camping."
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 500.0
        self.min_zone_radius = 50.0
        self.shrink_rate = 15.0
        self.outside_damage_per_second = 20.0
        self.zone_target_x = 500.0
        self.zone_target_y = 500.0

        self.shape_timer = 0.0
        self.current_shape = "circle"
        self.shapes = ["circle", "rectangle", "triangle", "split"]

        self.split_zones = []

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.collapse_triggered = False
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2.0
        self.zone_y = arena_height / 2.0
        self.zone_target_x = self.zone_x
        self.zone_target_y = self.zone_y
        self.zone_radius = min(arena_width, arena_height) / 2.0
        self.min_zone_radius = 50.0

        import random
        self.current_shape = random.choice(["circle", "rectangle", "triangle"])

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for i, b in enumerate(valid_balls):
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = False
            else:
                b.team = b.ball_type

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def is_inside_zone(self, x, y, cx, cy, radius, shape):
        import math
        if shape == "circle":
            dx = x - cx
            dy = y - cy
            return math.sqrt(dx*dx + dy*dy) <= radius
        elif shape == "rectangle":
            dx = abs(x - cx)
            dy = abs(y - cy)
            return dx <= radius and dy <= radius
        elif shape == "triangle":
            v0x, v0y = cx, cy - radius
            v1x, v1y = cx - radius * 0.866, cy + radius * 0.5
            v2x, v2y = cx + radius * 0.866, cy + radius * 0.5

            def sign(p1x, p1y, p2x, p2y, p3x, p3y):
                return (p1x - p3x) * (p2y - p3y) - (p2x - p3x) * (p1y - p3y)

            d1 = sign(x, y, v0x, v0y, v1x, v1y)
            d2 = sign(x, y, v1x, v1y, v2x, v2y)
            d3 = sign(x, y, v2x, v2y, v0x, v0y)

            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            return not (has_neg and has_pos)
        return True

    def tick(self, world, balls, delta=0.016):
        import math
        import random

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        self.shape_timer += delta
        if self.shape_timer > 15.0:
            self.shape_timer = 0.0
            old_shape = self.current_shape
            self.current_shape = random.choice(["circle", "rectangle", "triangle", "split"])
            if self.current_shape == "split":
                offset = max(100.0, self.zone_radius * 0.5)
                self.split_zones = [
                    {"x": self.zone_x - offset, "y": self.zone_y, "radius": self.zone_radius * 0.6},
                    {"x": self.zone_x + offset, "y": self.zone_y, "radius": self.zone_radius * 0.6}
                ]

            if hasattr(world, "add_event"):
                world.add_event("zone_shape_change", {"type": "zone_shape_change", "message": f"The zone shifts to {self.current_shape}!"})

        dx = self.zone_target_x - self.zone_x
        dy = self.zone_target_y - self.zone_y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 5.0:
            move_speed = 10.0
            self.zone_x += (dx / dist) * move_speed * delta
            self.zone_y += (dy / dist) * move_speed * delta
        else:
            arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
            buffer = max(100.0, self.zone_radius * 0.5)
            self.zone_target_x = random.uniform(buffer, arena_width - buffer)
            self.zone_target_y = random.uniform(buffer, arena_height - buffer)

        if self.zone_radius > self.min_zone_radius:
            self.zone_radius -= self.shrink_rate * delta
            if self.zone_radius <= self.min_zone_radius:
                self.zone_radius = self.min_zone_radius
                if not self.collapse_triggered:
                    self.collapse_triggered = True
                    if hasattr(world, "add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif getattr(self, "collapse_triggered", False):
            if self.zone_radius > 0:
                self.zone_radius -= self.shrink_rate * delta
                if self.zone_radius < 0:
                    self.zone_radius = 0.0

            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    b_dx = self.zone_x - b.x
                    b_dy = self.zone_y - b.y
                    b_dist = math.sqrt(b_dx*b_dx + b_dy*b_dy)
                    if b_dist > 0:
                        pull_strength = 2000.0
                        if not hasattr(b, "vx"): b.vx = 0.0
                        if not hasattr(b, "vy"): b.vy = 0.0
                        b.vx += (b_dx / b_dist) * pull_strength * delta
                        b.vy += (b_dy / b_dist) * pull_strength * delta

        if self.current_shape == "split":
            for i in range(len(self.split_zones)):
                sz = self.split_zones[i]
                sz["radius"] -= self.shrink_rate * 0.6 * delta
                if sz["radius"] < 20.0:
                    sz["radius"] = 20.0

        if hasattr(world, "arena") and hasattr(world.arena, "danger_grid"):
            if getattr(self, "_last_danger_tick", -1) != getattr(world, "current_tick", 0):
                self._last_danger_tick = getattr(world, "current_tick", 0)
                if self._last_danger_tick % 10 == 0:
                    world.arena.danger_grid.clear()

                    grid_w = int(getattr(world.arena, "width", 1000) // 100) + 1
                    grid_h = int(getattr(world.arena, "height", 1000) // 100) + 1
                    for i in range(grid_w):
                        for j in range(grid_h):
                            cx = i * 100 + 50
                            cy = j * 100 + 50

                            safe = False
                            if self.current_shape == "split":
                                for sz in self.split_zones:
                                    if self.is_inside_zone(cx, cy, sz["x"], sz["y"], sz["radius"], "circle"):
                                        safe = True
                                        break
                            else:
                                if self.is_inside_zone(cx, cy, self.zone_x, self.zone_y, self.zone_radius, self.current_shape):
                                    safe = True

                            if not safe:
                                world.arena.danger_grid[(i, j)] = world.arena.danger_grid.get((i, j), 0.0) + (self.outside_damage_per_second / 10.0)

        damage_this_tick = self.outside_damage_per_second * (10.0 if getattr(self, 'collapse_triggered', False) else 1.0) * delta
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                safe = False
                if self.current_shape == "split":
                    for sz in self.split_zones:
                        if self.is_inside_zone(b.x, b.y, sz["x"], sz["y"], sz["radius"], "circle"):
                            safe = True
                            break
                else:
                    if self.is_inside_zone(b.x, b.y, self.zone_x, self.zone_y, self.zone_radius, self.current_shape):
                        safe = True

                if not safe:
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = False
                        b.hp = 0
                        b.killer = "Geometric Zone"


class BodySwapMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Body Swap"
        self.description = "Periodically swaps player controls/positions to add confusion."
        self.swap_timer = 0.0
        self.swap_interval = 10.0

    def setup(self, world, balls):
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

    def tick(self, world, balls, delta=0.016):
        import random
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta

        self.swap_timer += delta
        if self.swap_timer >= self.swap_interval:
            self.swap_timer = 0.0
            alive_balls = [b for b in balls if getattr(b, "alive", False)]
            if len(alive_balls) >= 2:
                random.shuffle(alive_balls)
                for i in range(0, len(alive_balls) - 1, 2):
                    b1 = alive_balls[i]
                    b2 = alive_balls[i+1]

                    # Swap positions and velocities
                    b1.x, b2.x = b2.x, b1.x
                    b1.y, b2.y = b2.y, b1.y

                    vx1, vy1 = getattr(b1, "vx", 0.0), getattr(b1, "vy", 0.0)
                    vx2, vy2 = getattr(b2, "vx", 0.0), getattr(b2, "vy", 0.0)
                    b1.vx, b1.vy = vx2, vy2
                    b2.vx, b2.vy = vx1, vy1

                    if hasattr(world, "add_event"):
                        world.add_event("body_swap", {"type": "body_swap", "message": "Body Swap! Players swap places!"})

class TugOfWarMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Tug of War"
        self.description = "A single payload is centered. Both teams fight to push/pull the payload to the opposing team's goal."
        self.payload = None
        self.red_goal_x = 100.0
        self.blue_goal_x = 900.0
        self.timer = 180.0

    def setup(self, world, balls) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        mid = len(valid_balls) // 2

        red_team = []
        blue_team = []

        for i, b in enumerate(valid_balls):
            if i < mid:
                b.team = "Red"
                red_team.append(b)
            else:
                b.team = "Blue"
                blue_team.append(b)

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        self.red_goal_x = 100.0
        self.blue_goal_x = arena_width - 100.0

        # Find or create a payload
        class PayloadObj:
            pass
        self.payload = PayloadObj()
        self.payload.ball_type = "payload"
        self.payload.is_payload = True
        self.payload.is_invulnerable = True
        self.payload.speed = 0.0
        self.payload.base_speed = 0.0
        self.payload.damage = 0.0
        self.payload.base_damage = 0.0
        self.payload.max_hp = 10000.0
        self.payload.hp = 10000.0
        self.payload.x = arena_width / 2.0
        self.payload.y = arena_height / 2.0
        self.payload.alive = True
        self.payload.team = "Neutral"
        self.payload.radius = 20.0
        balls.append(self.payload)

    def tick(self, world, balls, delta: float = 0.016) -> None:
        if getattr(self, "timer", 0) > 0:
            self.timer -= delta

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000

        if self.payload and getattr(self.payload, "alive", False):
            import math

            # Count nearby players to determine movement
            red_count = 0
            blue_count = 0

            for b in balls:
                if b == self.payload or not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                    continue

                dx = getattr(b, "x", 0) - getattr(self.payload, "x", 0)
                dy = getattr(b, "y", 0) - getattr(self.payload, "y", 0)
                dist = math.hypot(dx, dy)

                if dist < 150.0:
                    if getattr(b, "team", "") == "Red":
                        red_count += 1
                    elif getattr(b, "team", "") == "Blue":
                        blue_count += 1

            # Payload moves towards Blue goal if Red has more players nearby, and vice versa
            move_speed = 50.0 # base move speed

            if red_count > blue_count:
                # Red pushes towards Blue goal (right)
                self.payload.x += move_speed * delta * (red_count - blue_count)
            elif blue_count > red_count:
                # Blue pushes towards Red goal (left)
                self.payload.x -= move_speed * delta * (blue_count - red_count)

            # Keep in bounds
            if self.payload.x < 50.0:
                self.payload.x = 50.0
            elif self.payload.x > arena_width - 50.0:
                self.payload.x = arena_width - 50.0

    def check_winner(self, world, balls):
        if not self.payload:
            return None

        px = getattr(self.payload, "x", 0)

        # Check if it reached a goal
        if px <= self.red_goal_x:
            return "Blue" # Blue pushed it to Red's goal
        elif px >= self.blue_goal_x:
            return "Red" # Red pushed it to Blue's goal

        if getattr(self, "timer", 0) <= 0:
            # Time up, whoever pushed it further wins
            arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            center_x = arena_width / 2.0

            if px > center_x:
                return "Red"
            elif px < center_x:
                return "Blue"
            else:
                return "Draw"

        return None



class UnstablePortalsEventMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Unstable Portals Event"
        self.description = "Unstable portals spawn randomly. They occasionally collapse, releasing a shockwave that damages and knocks back nearby players."
        self.portals = []
        self.spawn_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        import math
        import random

        self.spawn_timer += delta
        if self.spawn_timer > 5.0:
            self.spawn_timer = 0.0
            if random.random() < 0.5:
                arena_w = getattr(world.arena, "width", 800) if hasattr(world, "arena") else 800
                arena_h = getattr(world.arena, "height", 600) if hasattr(world, "arena") else 600
                self.portals.append({
                    "x": random.uniform(100, arena_w - 100),
                    "y": random.uniform(100, arena_h - 100),
                    "timer": random.uniform(3.0, 7.0),
                    "active": True
                })
                if hasattr(world, "add_event"):
                    world.add_event("portal_spawn", {"message": "An unstable portal has appeared!"})

        for p in self.portals:
            if not p["active"]:
                continue
            p["timer"] -= delta
            if p["timer"] <= 0:
                p["active"] = False
                if hasattr(world, "add_event"):
                    world.add_event("portal_collapse", {"message": "A portal collapsed!", "x": p["x"], "y": p["y"]})
                    world.add_event("explosion", {"x": p["x"], "y": p["y"], "radius": 150.0, "damage": 30.0})

                arena_w = getattr(world.arena, "width", 800) if hasattr(world, "arena") else 800
                arena_h = getattr(world.arena, "height", 600) if hasattr(world, "arena") else 600

                for b in balls:
                    if not getattr(b, "alive", False):
                        continue
                    dx = b.x - p["x"]
                    dy = b.y - p["y"]
                    dist = math.hypot(dx, dy)
                    if dist < 150.0:
                        damage = 30.0
                        if hasattr(b, "take_damage"):
                            b.take_damage(damage)
                        elif hasattr(b, "hp"):
                            b.hp -= damage

                        if dist > 0.0001:
                            nx = dx / dist
                            ny = dy / dist
                            knockback = 500.0 * (1.0 - dist / 150.0)
                            b.x = max(0.0, min(arena_w, b.x + nx * knockback * delta))
                            b.y = max(0.0, min(arena_h, b.y + ny * knockback * delta))

        self.portals = [p for p in self.portals if p["active"]]


class MinefieldEventMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Minefield Event"
        self.description = "A random event where multiple mines appear, detonating on contact."
        self.event_timer = 0.0
        self.event_active = False
        self.event_duration = 0.0
        self.mines = []

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        import math
        import random

        if not self.event_active:
            self.event_timer += delta

        if not self.event_active and self.event_timer > 20.0:
            if random.random() < 0.2:  # 20% chance every 20 seconds to trigger
                self.event_active = True
                self.event_duration = 15.0
                self.event_timer = 0.0
                self.mines = []
                # Spawn some mines
                for _ in range(random.randint(5, 10)):
                    self.mines.append({
                        "x": random.uniform(100, 700),
                        "y": random.uniform(100, 500),
                        "radius": 15,
                        "damage": 50,
                        "active": True,
                        "visible": random.choice([True, False])
                    })
                if hasattr(world, "add_event"):
                    world.add_event("minefield_event", {"message": "MINEFIELD EVENT! Watch your step!"})
            else:
                self.event_timer = 0.0

        if self.event_active:
            self.event_duration -= delta
            if self.event_duration <= 0:
                self.event_active = False
                self.event_timer = 0.0
                self.mines = []
                if hasattr(world, "add_event"):
                    world.add_event("minefield_event_ended", {"message": "Minefield cleared!"})

            for b in balls:
                if not getattr(b, "alive", False):
                    continue
                for m in self.mines:
                    if not m["active"]:
                        continue
                    dx = b.x - m["x"]
                    dy = b.y - m["y"]
                    dist = math.hypot(dx, dy)
                    if dist < b.radius + m["radius"]:
                        m["active"] = False
                        if hasattr(b, "take_damage"):
                            b.take_damage(m["damage"])
                        elif hasattr(b, "hp"):
                            b.hp -= m["damage"]
                        if hasattr(world, "add_event"):
                            world.add_event("mine_explosion", {"x": m["x"], "y": m["y"]})



class StaminaSpeedMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Stamina Speed"
        self.description = "Max stamina dictates base speed. Everyone starts with 200 max stamina but taking damage permanently reduces maximum stamina for the rest of the round."

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        for b in balls:
            b.max_stamina = 200.0
            b.stamina = 200.0
            b.base_speed = 200.0
            if hasattr(b, 'speed'):
                b.speed = 200.0
            setattr(b, 'prev_hp', getattr(b, 'hp', 100.0))

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        for b in balls:
            current_hp = getattr(b, 'hp', 100.0)
            prev_hp = getattr(b, 'prev_hp', current_hp)
            if current_hp < prev_hp:
                damage = prev_hp - current_hp
                b.max_stamina = max(10.0, getattr(b, 'max_stamina', 200.0) - damage)
                b.stamina = min(getattr(b, 'stamina', b.max_stamina), b.max_stamina)

            b.prev_hp = current_hp
            b.base_speed = getattr(b, 'max_stamina', 200.0)



class FactoryMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Factory"
        self.description = "Conveyor belts push you around!"
        self.points_for_kill = 10
        self.arena = ArenaTypes.FactoryArena()

    def update(self, world, delta):
        super().update(world, delta)

        if not hasattr(self.arena, "hazards"):
            return

        conveyors = [h for h in self.arena.hazards if getattr(h, "kind", "") == "conveyor_belt"]
        if not conveyors:
            return

        for c in conveyors:
            if hasattr(world, "items"):
                for item in world.items:
                    dx = c.x - getattr(item, "x", 0)
                    dy = c.y - getattr(item, "y", 0)
                    if dx*dx + dy*dy < c.radius * c.radius:
                        item.x = getattr(item, "x", 0) + c.direction_vector[0] * c.speed_magnitude * delta
                        item.y = getattr(item, "y", 0) + c.direction_vector[1] * c.speed_magnitude * delta

            for h in self.arena.hazards:
                if h is c or getattr(h, "kind", "") == "conveyor_belt":
                    continue
                dx = c.x - getattr(h, "x", 0)
                dy = c.y - getattr(h, "y", 0)
                if dx*dx + dy*dy < c.radius * c.radius:
                    h.x = getattr(h, "x", 0) + c.direction_vector[0] * c.speed_magnitude * delta
                    h.y = getattr(h, "y", 0) + c.direction_vector[1] * c.speed_magnitude * delta

            if hasattr(world, "balls"):
                for b in world.balls:
                    dx = c.x - getattr(b, "x", 0)
                    dy = c.y - getattr(b, "y", 0)
                    if dx*dx + dy*dy < c.radius * c.radius:
                        b.x = getattr(b, "x", 0) + c.direction_vector[0] * c.speed_magnitude * delta
                        b.y = getattr(b, "y", 0) + c.direction_vector[1] * c.speed_magnitude * delta

class HazardBilliardsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Hazard Billiards"
        self.description = "Every ball starts with a reflect shield and no standard attacks work. Players must push map hazards into each other to deal damage!"

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        for b in balls:
            b.damage = 0.0
            b.reflect_shield_active = True
            b.reflect_shield_timer = 99999.0
            b.reflect_shield_capacity = 99999.0

            if not hasattr(b, "mutators"):
                b.mutators = []
            if "hazard_billiards" not in b.mutators:
                b.mutators.append("hazard_billiards")

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        import math

        # Keep reflect shield alive
        for b in balls:
            if not getattr(b, "alive", False): continue
            b.reflect_shield_active = True
            b.reflect_shield_timer = 99999.0
            b.reflect_shield_capacity = 99999.0

        if not hasattr(world, "arena") or not world.arena:
            return

        hazards = getattr(world.arena, "hazards", [])

        # Hazard vs Hazard collisions
        for i, h1 in enumerate(hazards):
            h1x = getattr(h1, "x", 0)
            h1y = getattr(h1, "y", 0)
            h1r = getattr(h1, "radius", 10.0)
            h1vx = getattr(h1, "vx", 0)
            h1vy = getattr(h1, "vy", 0)

            for j in range(i + 1, len(hazards)):
                h2 = hazards[j]
                h2x = getattr(h2, "x", 0)
                h2y = getattr(h2, "y", 0)
                h2r = getattr(h2, "radius", 10.0)
                h2vx = getattr(h2, "vx", 0)
                h2vy = getattr(h2, "vy", 0)

                dx = h2x - h1x
                dy = h2y - h1y
                dist = math.hypot(dx, dy)

                if dist < h1r + h2r and dist > 0.0001:
                    # They collided. If they are moving fast enough, maybe cause an explosion or damage nearby balls?
                    # For now, just elastic bounce.
                    overlap = (h1r + h2r) - dist
                    nx = dx / dist
                    ny = dy / dist

                    h1.x = h1x - nx * (overlap / 2)
                    h1.y = h1y - ny * (overlap / 2)
                    h2.x = h2x + nx * (overlap / 2)
                    h2.y = h2y + ny * (overlap / 2)

                    # Exchange velocity along normal
                    p = 2 * (h1vx * nx + h1vy * ny - h2vx * nx - h2vy * ny) / 2

                    setattr(h1, "vx", h1vx - p * nx)
                    setattr(h1, "vy", h1vy - p * ny)
                    setattr(h2, "vx", h2vx + p * nx)
                    setattr(h2, "vy", h2vy + p * ny)

                    # If high impact, explode and damage nearby balls
                    impact_speed = abs(p)
                    if impact_speed > 100.0:
                        for b in balls:
                            if not getattr(b, "alive", False): continue
                            bdx = getattr(b, "x", 0) - h1x
                            bdy = getattr(b, "y", 0) - h1y
                            bdist = math.hypot(bdx, bdy)
                            if bdist < h1r + h2r + 100.0:
                                b.reflect_shield_active = False # bypass
                                damage = (impact_speed / 100.0) * 20.0
                                if hasattr(b, "take_damage"):
                                    b.take_damage(damage)
                                elif hasattr(b, "hp"):
                                    b.hp -= damage
                                b.reflect_shield_active = True

                                # Add explosion event
                                if hasattr(world, "add_event"):
                                    world.add_event("explosion", {"x": h1x, "y": h1y, "radius": h1r + h2r + 100.0, "damage": damage})

        # Ball pushes Hazard
        for b in balls:
            if not getattr(b, "alive", False):
                continue

            bx = getattr(b, "x", 0)
            by = getattr(b, "y", 0)
            br = getattr(b, "radius", 10.0)

            # Simple assumption: ball's previous position to infer velocity, or just use direction to hazard

            for h in hazards:
                hx = getattr(h, "x", 0)
                hy = getattr(h, "y", 0)
                hr = getattr(h, "radius", 10.0)

                dx = hx - bx
                dy = hy - by
                dist = math.hypot(dx, dy)

                if dist < br + hr and dist > 0.0001:
                    # Ball pushes hazard
                    overlap = (br + hr) - dist
                    nx = dx / dist
                    ny = dy / dist

                    # Move hazard
                    h.x = hx + nx * overlap
                    h.y = hy + ny * overlap

                    # Give hazard velocity (pushes it outward)
                    # We can use ball's base_speed or a constant push speed
                    push_speed = getattr(b, "base_speed", 200.0)
                    setattr(h, "vx", getattr(h, "vx", 0) + nx * push_speed * delta * 5.0)
                    setattr(h, "vy", getattr(h, "vy", 0) + ny * push_speed * delta * 5.0)

        # Hazard movement and collision with balls
        for h in hazards:
            hvx = getattr(h, "vx", 0)
            hvy = getattr(h, "vy", 0)

            # Apply velocity
            if abs(hvx) > 0.1 or abs(hvy) > 0.1:
                h.x = getattr(h, "x", 0) + hvx * delta
                h.y = getattr(h, "y", 0) + hvy * delta

                # Friction
                setattr(h, "vx", hvx * 0.95)
                setattr(h, "vy", hvy * 0.95)

                speed = math.hypot(hvx, hvy)
                if speed > 50.0: # If hazard is moving fast enough
                    for b in balls:
                        if not getattr(b, "alive", False):
                            continue

                        dx = getattr(b, "x", 0) - getattr(h, "x", 0)
                        dy = getattr(b, "y", 0) - getattr(h, "y", 0)
                        dist = math.hypot(dx, dy)

                        if dist < getattr(b, "radius", 10.0) + getattr(h, "radius", 10.0) and dist > 0.0001:
                            # Fast moving hazard hits ball -> deal damage bypassing reflect shield!
                            damage = (speed / 100.0) * 15.0

                            # Temporarily remove reflect shield to deal damage
                            b.reflect_shield_active = False

                            if hasattr(b, "take_damage"):
                                b.take_damage(damage)
                            elif hasattr(b, "hp"):
                                b.hp -= damage

                            b.reflect_shield_active = True

                            # Bounce hazard
                            nx = dx / dist
                            ny = dy / dist
                            setattr(h, "vx", hvx * -0.5)
                            setattr(h, "vy", hvy * -0.5)



class DynamicSafeZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.collapse_triggered = False
        self.name = "Dynamic Safe Zone"
        self.description = "Dynamic safe zones that not only protect from environmental damage but also apply randomized buffs for a short duration, encouraging players to fight for the optimal spot inside the zone."
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 500.0
        self.min_zone_radius = 50.0
        self.shrink_rate = 10.0
        self.zone_target_x = 500.0
        self.zone_target_y = 500.0
        self.outside_damage_per_second = 10.0
        self.buff_zone_radius = 75.0
        self.buff_type = "speed"
        self.buff_timer = 0.0

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        self.collapse_triggered = False
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2.0
        self.zone_y = arena_height / 2.0
        self.zone_target_x = self.zone_x
        self.zone_target_y = self.zone_y
        self.zone_radius = min(arena_width, arena_height) / 2.0
        self.min_zone_radius = 50.0
        self.buff_timer = 0.0

        # Pick random initial buff
        self._pick_new_buff()

    def _pick_new_buff(self):
        import random
        self.buff_type = random.choice(["speed", "damage", "heal", "shield"])
        self.buff_timer = random.uniform(5.0, 10.0)

    def tick(self, world, balls, delta=0.016):
        import math
        import random

        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death = getattr(b, "time_since_death", 0.0) + delta

        # Update buff timer
        self.buff_timer -= delta
        if self.buff_timer <= 0:
            self._pick_new_buff()

        # Move safe zone
        dx = self.zone_target_x - self.zone_x
        dy = self.zone_target_y - self.zone_y
        dist_zone = math.sqrt(dx*dx + dy*dy)
        if dist_zone > 5.0:
            move_speed = 15.0
            self.zone_x += (dx / dist_zone) * move_speed * delta
            self.zone_y += (dy / dist_zone) * move_speed * delta
        else:
            arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
            buffer = max(100.0, self.zone_radius * 0.5)
            self.zone_target_x = random.uniform(buffer, arena_width - buffer)
            self.zone_target_y = random.uniform(buffer, arena_height - buffer)

        # Shrink safe zone
        if self.zone_radius > self.min_zone_radius:
            self.zone_radius -= self.shrink_rate * delta
            if self.zone_radius <= self.min_zone_radius:
                self.zone_radius = self.min_zone_radius
                if not self.collapse_triggered:
                    self.collapse_triggered = True
                    if hasattr(world, "add_event"):
                        world.add_event("collapse_event", {"type": "collapse_event", "message": "COLLAPSE EVENT! The zone collapses!"})
        elif self.collapse_triggered:
            if self.zone_radius > 0:
                self.zone_radius -= self.shrink_rate * delta
                if self.zone_radius < 0:
                    self.zone_radius = 0.0

            # Pull balls into center if fully collapsed
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    dx_pull = self.zone_x - b.x
                    dy_pull = self.zone_y - b.y
                    dist_pull = math.sqrt(dx_pull*dx_pull + dy_pull*dy_pull)
                    if dist_pull > 0:
                        pull_strength = 2000.0
                        b.vx = getattr(b, "vx", 0.0) + (dx_pull / dist_pull) * pull_strength * delta
                        b.vy = getattr(b, "vy", 0.0) + (dy_pull / dist_pull) * pull_strength * delta

        damage_this_tick = self.outside_damage_per_second * (10.0 if self.collapse_triggered else 1.0) * delta

        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

            dx = b.x - self.zone_x
            dy = b.y - self.zone_y
            dist = math.sqrt(dx*dx + dy*dy)

            in_buff_zone = dist <= self.buff_zone_radius

            # Process Buffs
            if in_buff_zone:
                if self.buff_type == "speed":
                    b.speed = b.base_speed * 1.5
                    b.zone_modifier_speed = True
                elif self.buff_type == "damage":
                    b.damage = b.base_damage * 1.5
                    b.zone_modifier_damage = True
                elif self.buff_type == "heal":
                    if hasattr(b, "hp") and hasattr(b, "max_hp"):
                        b.hp = min(getattr(b, "max_hp", 100.0), b.hp + 30.0 * delta)
                elif self.buff_type == "shield":
                    b.shield = getattr(b, "shield", 0.0) + 10.0 * delta
                    if b.shield > 50.0:
                        b.shield = 50.0

            # Remove inactive buffs
            if not in_buff_zone or self.buff_type != "speed":
                if getattr(b, "zone_modifier_speed", False):
                    b.speed = b.base_speed
                    delattr(b, "zone_modifier_speed")

            if not in_buff_zone or self.buff_type != "damage":
                if getattr(b, "zone_modifier_damage", False):
                    b.damage = b.base_damage
                    delattr(b, "zone_modifier_damage")

            # Check if outside safe zone
            if dist > self.zone_radius:
                if hasattr(b, "hp"):
                    b.hp -= damage_this_tick
                    if b.hp <= 0:
                        b.alive = False
                        b.hp = 0

    def check_winner(self, world, balls):
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]
        return None


class DailyMutatorMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Daily Mutator"
        self.description = "Randomly applies extreme global mutators daily. Surviving grants exclusive rewards."
        self.mutators = []
        self._rewards_given = False

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        import time
        current_day = int(time.time() / (24 * 3600))

        mutator_combinations = [
            ["low_gravity", "double_damage"],
            ["invisible_hazards"],
            ["high_speed", "vampirism"],
            ["global_hp", "global_cooldown"]
        ]

        self.mutators = mutator_combinations[current_day % len(mutator_combinations)]

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                if "low_gravity" in self.mutators:
                    b.mass = getattr(b, "mass", 1.0) * 0.5
                if "double_damage" in self.mutators:
                    b.base_damage = getattr(b, "base_damage", getattr(b, "damage", 10)) * 2.0
                    b.damage = getattr(b, "damage", 10) * 2.0
                if "high_speed" in self.mutators:
                    b.base_speed = getattr(b, "base_speed", getattr(b, "speed", 100)) * 1.5
                    b.speed = getattr(b, "speed", 100) * 1.5
                if "vampirism" in self.mutators:
                    b.lifesteal = getattr(b, "lifesteal", 0.0) + 0.5
                if "global_hp" in self.mutators:
                    b.max_hp = getattr(b, "max_hp", 100.0) * 0.5
                    b.hp = getattr(b, "hp", 100.0) * 0.5
                if "global_cooldown" in self.mutators:
                    b.skill_cooldown = getattr(b, "skill_cooldown", 5.0) * 0.5

        if "invisible_hazards" in self.mutators and hasattr(world, "arena") and hasattr(world.arena, "hazards"):
            for h in world.arena.hazards:
                h.invisible = True

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        teams_alive = set()
        balls_alive = []
        for b in balls:
            if getattr(b, "alive", True) and getattr(b, "ball_type", None) != "spectator":
                teams_alive.add(getattr(b, "team", b.ball_type))
                balls_alive.append(b)

        if len(teams_alive) <= 1 and len(balls_alive) > 0 and len(teams_alive) > 0 and not getattr(self, "_rewards_given", False):
            self._rewards_given = True
            # Match is over, give rewards to survivors
            pm = getattr(world, "profile_manager", None)
            if pm:
                if hasattr(pm, "add_cosmetic"):
                    pm.add_cosmetic("Daily Survivor Crown")
                for b in balls_alive:
                    b.skill_points = getattr(b, "skill_points", 0) + 10



class BlackMarketMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Black Market"
        self.description = "Collect currency to buy upgrades from wandering Black Markets."
        self.currency_spawn_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "currency_pickups"):
            world.currency_pickups = []
        if not hasattr(world, "black_markets"):
            world.black_markets = []

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        # Spawn some initial currency
        import random
        for _ in range(15):
            world.currency_pickups.append({
                "x": random.uniform(50, arena_width - 50),
                "y": random.uniform(50, arena_height - 50),
                "type": "currency"
            })

        # Spawn Black Markets
        for _ in range(2):
            world.black_markets.append({
                "x": random.uniform(100, arena_width - 100),
                "y": random.uniform(100, arena_height - 100),
                "vx": random.uniform(-20, 20),
                "vy": random.uniform(-20, 20),
                "radius": 40.0
            })

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.currency = getattr(b, "currency", 0)
                b.team = getattr(b, "team", b.ball_type)
                b.purchase_cooldown = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)
        import math
        import random

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        # Spawn currency
        self.currency_spawn_timer += delta
        if self.currency_spawn_timer >= 2.0:
            self.currency_spawn_timer = 0.0
            if len(world.currency_pickups) < 30:
                world.currency_pickups.append({
                    "x": random.uniform(50, arena_width - 50),
                    "y": random.uniform(50, arena_height - 50),
                    "type": "currency"
                })

        # Move Black Markets
        for bm in world.black_markets:
            bm["x"] += bm["vx"] * delta
            bm["y"] += bm["vy"] * delta

            if bm["x"] < bm["radius"] or bm["x"] > arena_width - bm["radius"]:
                bm["vx"] *= -1
                bm["x"] = max(bm["radius"], min(arena_width - bm["radius"], bm["x"]))
            if bm["y"] < bm["radius"] or bm["y"] > arena_height - bm["radius"]:
                bm["vy"] *= -1
                bm["y"] = max(bm["radius"], min(arena_height - bm["radius"], bm["y"]))

        # Ball interactions
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            b.purchase_cooldown = max(0.0, getattr(b, "purchase_cooldown", 0.0) - delta)

            # Collect currency
            pickups_to_remove = []
            for c in world.currency_pickups:
                dx = b.x - c["x"]
                dy = b.y - c["y"]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist <= getattr(b, "radius", 10.0) + 15.0:
                    b.currency = getattr(b, "currency", 0) + 1
                    pickups_to_remove.append(c)

            for c in pickups_to_remove:
                if c in world.currency_pickups:
                    world.currency_pickups.remove(c)

            # Purchase upgrades
            if getattr(b, "purchase_cooldown", 0.0) <= 0.0 and getattr(b, "currency", 0) >= 5:
                for bm in world.black_markets:
                    dx = b.x - bm["x"]
                    dy = b.y - bm["y"]
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist <= getattr(b, "radius", 10.0) + bm["radius"]:
                        b.currency -= 5
                        b.purchase_cooldown = 5.0

                        # Apply random upgrade
                        upgrade_type = random.choice(["max_hp", "speed", "damage"])
                        if upgrade_type == "max_hp":
                            if not hasattr(b, "base_max_hp"):
                                b.base_max_hp = getattr(b, "max_hp", 100.0)
                            b.base_max_hp += 20.0
                            b.max_hp = b.base_max_hp
                            b.hp = min(getattr(b, "hp", 100.0) + 20.0, b.max_hp)
                        elif upgrade_type == "speed":
                            if not hasattr(b, "base_speed"):
                                b.base_speed = getattr(b, "speed", 100.0)
                            b.base_speed += 15.0
                            b.speed = b.base_speed
                        elif upgrade_type == "damage":
                            if not hasattr(b, "base_damage"):
                                b.base_damage = getattr(b, "damage", 10.0)
                            b.base_damage += 5.0
                            b.damage = b.base_damage

                        if hasattr(world, "add_event"):
                            world.add_event("upgrade_purchased", {"ball": b, "upgrade": upgrade_type})
                        break

class FloorIsLavaMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Floor Is Lava"
        self.description = "The entire arena floor slowly turns into lava starting from the edges. Safe zones are randomly generated platforms that appear for a limited time before submerging. Players must navigate between platforms using bounce pads and careful movement."
        self.lava_radius = 2000.0
        self.min_lava_radius = 0.0
        self.shrink_rate = 15.0
        self.platforms = []
        self.platform_timer = 0.0
        self.bounce_pads = []

    def setup(self, world, balls):
        super().setup(world, balls)
        self.world = world
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.lava_radius = max(arena_width, arena_height)
        self.platforms = []
        self.bounce_pads = []
        self.platform_timer = 0.0
        self._spawn_platform(arena_width/2.0, arena_height/2.0) # Start with center platform

    def _spawn_platform(self, x=None, y=None):
        import random
        import math
        arena_width = getattr(self.world.arena, "width", 1000) if hasattr(self.world, "arena") and self.world.arena else 1000
        arena_height = getattr(self.world.arena, "height", 1000) if hasattr(self.world, "arena") and self.world.arena else 1000

        if x is None:
            x = random.uniform(200, arena_width - 200)
        if y is None:
            y = random.uniform(200, arena_height - 200)

        radius = random.uniform(100.0, 200.0)
        lifetime = random.uniform(10.0, 20.0)

        self.platforms.append({
            "x": x,
            "y": y,
            "radius": radius,
            "timer": lifetime
        })

        # Add a bounce pad near the edge of the platform
        angle = random.uniform(0, 2 * 3.14159)
        pad_x = x + (radius * 0.7) * math.cos(angle)
        pad_y = y + (radius * 0.7) * math.sin(angle)

        self.bounce_pads.append({
            "x": pad_x,
            "y": pad_y,
            "radius": 40.0,
            "timer": lifetime
        })

    def tick(self, world, balls, delta=0.016):
        import math
        import random

        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        center_x = arena_width / 2.0
        center_y = arena_height / 2.0

        self.lava_radius = max(self.min_lava_radius, self.lava_radius - self.shrink_rate * delta)

        # Platform logic
        self.platform_timer -= delta
        if self.platform_timer <= 0:
            self._spawn_platform()
            self.platform_timer = random.uniform(5.0, 10.0)

        # Update lifetimes
        for p in list(self.platforms):
            p["timer"] -= delta
            if p["timer"] <= 0:
                self.platforms.remove(p)

        for bp in list(self.bounce_pads):
            bp["timer"] -= delta
            if bp["timer"] <= 0:
                self.bounce_pads.remove(bp)

        # Make sure bounce pads are placed in arena.hazards
        if hasattr(world, "arena") and hasattr(world.arena, "hazards"):
            # Clean up old bounce pads from hazards list
            world.arena.hazards = [h for h in world.arena.hazards if getattr(h, "kind", "") != "bounce_pad"]

            # Add current bounce pads to hazards
            for idx, bp in enumerate(self.bounce_pads):
                try:
                    from arena.procedural_arena import Hazard
                    new_h = Hazard(id=99000 + idx, x=bp["x"], y=bp["y"], radius=bp["radius"], kind="bounce_pad", damage=0.0)
                    world.arena.hazards.append(new_h)
                except ImportError:
                    # Fallback to dict
                    new_h = type("Hazard", (), {"id": 99000 + idx, "x": bp["x"], "y": bp["y"], "radius": bp["radius"], "kind": "bounce_pad", "damage": 0.0, "active": True})
                    world.arena.hazards.append(new_h)

        # Damage logic
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            dist_to_center = math.hypot(b.x - center_x, b.y - center_y)
            in_lava = dist_to_center > self.lava_radius

            # Check if on a platform
            on_platform = False
            for p in self.platforms:
                if math.hypot(b.x - p["x"], b.y - p["y"]) <= p["radius"]:
                    on_platform = True
                    break

            if in_lava and not on_platform:
                b.hp -= 20.0 * delta # Lava damage
                b.hp = max(0, b.hp)
                if b.hp <= 0:
                    b.alive = False

class MeteorShowerMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Meteor Shower"
        self.description = "High damage hazards fall from the sky."
        self.spawn_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []
        self.spawn_timer = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        self.spawn_timer += delta

        # Spawn meteors periodically
        if self.spawn_timer >= 1.0:
            self.spawn_timer = 0.0
            import random

            # Use fallback dictionary if Hazard is not easily imported, but procedural arena should be available
            try:
                from arena.procedural_arena import Hazard
            except ImportError:
                class Hazard:
                    def __init__(self, id, x, y, radius, kind, damage):
                        self.id = id
                        self.x = x
                        self.y = y
                        self.radius = radius
                        self.kind = kind
                        self.damage = damage
                        self.active = True
                        self.target_radius = 0.0

            arena_width = getattr(world.arena, "width", 1000)
            arena_height = getattr(world.arena, "height", 1000)

            x = random.uniform(50, arena_width - 50)
            y = random.uniform(50, arena_height - 50)

            h_id = 15000 + len(world.arena.hazards) + random.randint(0, 10000)
            meteor = Hazard(id=h_id, x=x, y=y, radius=30.0, kind="meteor", damage=200.0)
            setattr(meteor, "duration", 5.0)
            meteor.target_radius = 30.0

            world.arena.hazards.append(meteor)


class BlizzardMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Blizzard Mode"
        self.description = "Periodically spawns a blizzard that severely reduces all ball movement speed (friction increases) and creates temporary slippery ice patches as hazards that cause balls to slide uncontrollably."
        self.timer = 0.0
        self.is_blizzard = False
        import random
        self.random = random

    def setup(self, world: 'Any', balls: List['Any']) -> None:
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []
        self.timer = 0.0
        self.is_blizzard = False
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                if not hasattr(b, "base_speed"):
                    b.base_speed = getattr(b, "speed", 100.0)
                if not hasattr(b, "original_base_speed"):
                    b.original_base_speed = getattr(b, "base_speed", 100.0)

    def tick(self, world: 'Any', balls: List['Any'], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        self.timer += delta

        if not self.is_blizzard and self.timer >= 10.0:
            self.is_blizzard = True
            self.timer = 0.0
            world.arena.is_snowing = True

            # spawn temporary ice patches
            try:
                from arena.procedural_arena import Hazard
            except ImportError:
                class Hazard:
                    def __init__(self, id, x, y, radius, kind, damage):
                        self.id = id
                        self.x = x
                        self.y = y
                        self.radius = radius
                        self.kind = kind
                        self.damage = damage
                        self.active = True

            for _ in range(5):
                x = self.random.uniform(0, world.arena.width) if hasattr(world.arena, "width") else self.random.uniform(-500, 500)
                y = self.random.uniform(0, world.arena.height) if hasattr(world.arena, "height") else self.random.uniform(-500, 500)
                ice = Hazard(id=len(world.arena.hazards) + self.random.randint(1000, 9999), x=x, y=y, radius=80.0, kind="ice_patch", damage=0.0)
                if not hasattr(ice, "timer"):
                    ice.timer = 0.0
                world.arena.hazards.append(ice)

        elif self.is_blizzard and self.timer >= 5.0:
            self.is_blizzard = False
            self.timer = 0.0
            world.arena.is_snowing = False

        # Manage active ice patches timers and removal
        if hasattr(world.arena, "hazards"):
            hazards_to_remove = []
            for h in world.arena.hazards:
                if getattr(h, "kind", "") == "ice_patch" and hasattr(h, "timer"):
                    h.timer += delta
                    if h.timer >= 15.0: # lasts for 15 seconds
                        hazards_to_remove.append(h)
            for h in hazards_to_remove:
                if h in world.arena.hazards:
                    world.arena.hazards.remove(h)

        # Apply severe movement speed reduction during blizzard
        for b in balls:
            if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                if self.is_blizzard:
                    b.base_speed = getattr(b, "original_base_speed", 100.0) * 0.3 # Severely reduce speed (friction increases)
                else:
                    b.base_speed = getattr(b, "original_base_speed", 100.0)


GAME_MODES = {
    "meteor_shower": MeteorShowerMode(),
    "blizzard_mode": BlizzardMode(),

    "black_market": BlackMarketMode(),
    "floor_is_lava": FloorIsLavaMode(),


    "geometric_zone": GeometricZoneMode(),
    "daily_mutator": DailyMutatorMode(),
    "factory": FactoryMode(),
    "mirror_walls": MirrorWallsMode(),
    "stamina_regen": StaminaRegenMode(),
    "zero_gravity": ZeroGravityMode(),
    "magnetic_collisions": MagneticCollisionsMode(),
    "day_night_mode": DayNightMode(),
    "shifting_maze": ShiftingMazeMode(),
    "stamina_speed": StaminaSpeedMode(),

    "blackout": BlackoutMode(),
    "windstorm": WindstormMode(),
    "modifier_zones": ModifierZonesMode(),
    "modifier_zones_safe_zone": ModifierZonesSafeZoneMode(),
    "draft_royale": DraftRoyaleMode(),
    "dual_payload": DualPayloadMode(),
    "tug_of_war": TugOfWarMode(),
    "escort": EscortMode(),
    "tournament": TournamentMode(),
    "bumper_balls": BumperBallsMode(),
    "pinball": PinballMode(),
    "portal_node": PortalNodeMode(),
    "memory_traps": MemoryTrapsMode(),
    "pitch_black": PitchBlackMode(),
    "vision_reduced": VisionReducedMode(),
    "emp_burst": EMPBurstMode(),
    "dynamic_hazards": DynamicHazardsMode(),
    "custom_match": CustomMatchMode(),
    "reverse_event": ReverseEventMode(),
    "unstable_portals_event": UnstablePortalsEventMode(),
    "minefield_event": MinefieldEventMode(),
    "weather_chaos": WeatherChaosMode(),
    "domination": DominationMode(),
    "black_hole": BlackHoleMode(),
    "gravity_well": GravityWellMode(),
    "king_of_the_hill": KingOfTheHillMode(),
    "moving_zone": MovingZoneMode(),
    "vampire_royale": VampireRoyaleMode(),
    "battle_royale": BattleRoyaleMode(),
    "team_deathmatch": TeamDeathmatchMode(),
    "zombie_infection": ZombieInfectionMode(),
    "boss_fight": BossFightMode(),
    "vip_defense": VIPDefenseMode(),
    "survival": SurvivalMode(),
    "toxic_environment": ToxicEnvironmentMode(),
    "capture_the_flag": CaptureTheFlagMode(),
    "evolutionary_simulation": EvolutionarySimulationMode(),
    "shrinking_danger_zone": ShrinkingDangerZoneMode(),
    "safe_zone": SafeZoneMode(),
    "dynamic_safe_zone": DynamicSafeZoneMode(),
    "moving_safe_zone": MovingSafeZoneMode(),
    "bounty_hunt": BountyHuntMode(),
    "earthquake": EarthquakeMode(),
    "mirror_match": MirrorMatchMode(),
    "clone_chaos": CloneChaosMode(),
    "volatile_clones": VolatileClonesMode(),
    "supernova": SupernovaMode(),
    "echolocation": EcholocationMode(),
    "body_swap": BodySwapMode(),
    "hazard_billiards": HazardBilliardsMode()
}

try:
    from ai.interactive_training import InteractiveTrainingMode
    GAME_MODES["interactive_training"] = InteractiveTrainingMode()
except ImportError:
    pass
