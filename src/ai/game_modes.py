from typing import List, Optional, Any

class GameMode:
    """Base class for all game modes."""
    def __init__(self):
        self.name = "Unknown"
        self.description = "Base game mode"

    def setup(self, world: Any, balls: List[Any]) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
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

        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
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

class BattleRoyaleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Battle Royale"
        self.description = "Last man standing. Everyone for themselves. Includes dynamic weather."
        self.dark_phase_timer = 0.0
        self.is_dark_phase = False
        self.weather = "clear"
        self.weather_timer = 0.0
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
        self.weather_timer += delta
        if self.weather_timer > 15.0:
            self.weather_timer = 0.0
            weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm"]
            rnd = getattr(self, "random", __import__("random"))
            self.weather = rnd.choice(weathers)

            if self.weather == "wind":
                self.wind_dx = rnd.uniform(-50.0, 50.0)
                self.wind_dy = rnd.uniform(-50.0, 50.0)

        if hasattr(world, "arena"):
            world.arena.is_foggy = (self.weather in ["fog", "snow"])
            world.arena.is_raining = (self.weather in ["rain", "thunderstorm"])
            world.arena.is_sandstorming = (self.weather == "sandstorm")
            world.arena.is_snowing = (self.weather == "snow")

            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []

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
            elif self.weather == "rain" or self.weather == "thunderstorm":
                if getattr(self, "random", __import__("random")).random() < (0.2 if self.weather == "thunderstorm" else 0.05) * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn lightning strike zone
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    lightning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=30.0, kind="lightning_strike", damage=50.0)
                    setattr(lightning, 'duration', 1.0) # short duration strike
                    world.arena.hazards.append(lightning)

        valid_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        for b in valid_balls:
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

            if self.weather == "clear":
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                b.attack_accuracy = 1.0
            elif self.weather == "rain":
                b.speed = b.base_speed * 0.8
                b.damage = b.base_damage
                b.dash_range_mult = 1.5
                b.steering_mult = 0.5
                if hasattr(b, "vx") and hasattr(b, "vy"):
                    b.x += getattr(b, "vx") * delta * 0.5
                    b.y += getattr(b, "vy") * delta * 0.5
                b.attack_accuracy = 0.8
            elif self.weather == "fog":
                b.speed = b.base_speed * 0.8
                b.damage = b.base_damage * 0.9
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
            elif self.weather == "snow":
                b.speed = b.base_speed * 0.5
                b.damage = b.base_damage * 1.2
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
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                # push balls in a specific direction
                if hasattr(self, "wind_dx") and hasattr(self, "wind_dy"):
                    b.x += self.wind_dx * delta
                    b.y += self.wind_dy * delta
            elif self.weather == "thunderstorm":
                b.speed = b.base_speed * 1.1
                b.damage = b.base_damage * 1.5
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
            elif self.weather == "sandstorm":
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
                    if hasattr(b, "hp"): b.hp -= 20.0
                b.attack_accuracy = 0.5

        self.dark_phase_timer += delta

        # Dark phase cycle: 20s normal, 10s dark
        if not self.is_dark_phase and self.dark_phase_timer >= 20.0:
            self.is_dark_phase = True
            self.dark_phase_timer = 0.0

            # Apply dark phase
            for b in balls:
                if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator":
                    b.base_perception_radius = getattr(b, "perception_radius", 250.0)
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
        self.description = "Multiple players fight one giant boss."
    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        if balls:
            boss = balls[0]
            boss.team = "Boss"
            boss.max_hp *= 10
            boss.hp = boss.max_hp
            boss.damage = getattr(boss, "damage", 10) * 2

            # Position the boss in the center of the arena
            arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
            arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
            boss.x = arena_width / 2
            boss.y = arena_height / 2

            # Make the boss bigger (radius)
            if hasattr(boss, "radius"):
                boss.radius *= 3
            else:
                boss.radius = 30

            # Make the boss heavier/slower (optional, but requested boss ball)
            if hasattr(boss, "base_speed"):
                boss.base_speed = getattr(boss, "base_speed", 50) * 0.8

            for b in balls[1:]:
                if getattr(b, "ball_type", None) != "spectator":
                    b.team = "Hunters"

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
        self.weather_timer += delta
        if self.weather_timer > 10.0:
            self.weather_timer = 0.0
            weathers = ["clear", "rain", "fog", "snow", "wind", "thunderstorm", "sandstorm"]
            import random
            rnd = getattr(self, "random", random)
            self.weather = rnd.choice(weathers)

            if self.weather == "wind":
                self.wind_dx = rnd.uniform(-50.0, 50.0)
                self.wind_dy = rnd.uniform(-50.0, 50.0)

        # Apply weather effects to the arena
        if hasattr(world, "arena"):
            world.arena.is_foggy = (self.weather in ["fog", "snow"])
            world.arena.is_raining = (self.weather == "rain")
            world.arena.is_sandstorming = (self.weather == "sandstorm")
            world.arena.is_snowing = (self.weather == "snow")

            if not hasattr(world.arena, "hazards"):
                world.arena.hazards = []

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
            elif self.weather == "rain" or self.weather == "thunderstorm":
                if getattr(self, "random", __import__("random")).random() < (0.2 if self.weather == "thunderstorm" else 0.05) * delta:
                    from arena.procedural_arena import Hazard
                    # Spawn lightning strike zone
                    x = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.width - 100.0)
                    y = getattr(self, "random", __import__("random")).uniform(100.0, world.arena.height - 100.0)
                    lightning = Hazard(id=len(world.arena.hazards) + getattr(self, "random", __import__("random")).randint(1000, 9999), x=x, y=y, radius=30.0, kind="lightning_strike", damage=50.0)
                    setattr(lightning, 'duration', 1.0) # short duration strike
                    world.arena.hazards.append(lightning)

        valid_balls = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]

        for b in valid_balls:
            if not hasattr(b, "base_speed"):
                b.base_speed = getattr(b, "speed", 100.0)
            if not hasattr(b, "base_damage"):
                b.base_damage = getattr(b, "damage", 10.0)

            if self.weather == "clear":
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                b.attack_accuracy = 1.0
            elif self.weather == "rain":
                b.speed = b.base_speed * 0.8
                b.damage = b.base_damage
                # rain makes surface slippery/increases dash range but reduces steering
                b.dash_range_mult = 1.5
                b.steering_mult = 0.5
                # slide more
                if hasattr(b, "vx") and hasattr(b, "vy"):
                    b.x += getattr(b, "vx") * delta * 0.5
                    b.y += getattr(b, "vy") * delta * 0.5
                b.attack_accuracy = 0.8
            elif self.weather == "fog":
                b.speed = b.base_speed * 0.5
                b.damage = b.base_damage * 0.8
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
            elif self.weather == "snow":
                b.speed = b.base_speed * 0.5
                b.damage = b.base_damage * 1.2
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
                b.speed = b.base_speed
                b.damage = b.base_damage
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
                # push balls in a specific direction
                if hasattr(self, "wind_dx") and hasattr(self, "wind_dy"):
                    b.x += self.wind_dx * delta
                    b.y += self.wind_dy * delta
            elif self.weather == "thunderstorm":
                b.speed = b.base_speed * 1.1 # Panic speed
                b.damage = b.base_damage * 1.5 # High damage due to electricity
                b.dash_range_mult = 1.0
                b.steering_mult = 1.0
            elif self.weather == "sandstorm":
                b.speed = b.base_speed * 0.7 # Hard to move
                b.damage = b.base_damage
                b.dash_range_mult = 0.5
                b.steering_mult = 0.5
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
            elif blue_count > red_count:
                pt.capture_progress -= 10.0 * delta

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

class DynamicHazardsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Dynamic Hazards"
        self.description = "Watch out for moving hazards that traverse the arena!"
        self.spawn_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        if not hasattr(world.arena, "hazards"):
            world.arena.hazards = []

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        self.spawn_timer += delta
        if self.spawn_timer >= 5.0:
            self.spawn_timer = 0.0

            import random
            from src.arena.arena_types import Hazard

            x = 0.0 if random.random() < 0.5 else world.arena.width
            y = random.uniform(0, world.arena.height)
            vx = random.uniform(50, 150) if x == 0.0 else random.uniform(-150, -50)
            vy = random.uniform(-50, 50)

            new_hazard = Hazard(id=len(world.arena.hazards) + random.randint(1000, 9999),
                                x=x, y=y, radius=40.0, kind="lava", damage=25.0)
            new_hazard.vx = vx
            new_hazard.vy = vy

            world.arena.hazards.append(new_hazard)

        for hazard in list(world.arena.hazards):
            if hasattr(hazard, 'vx') and hasattr(hazard, 'vy'):
                hazard.x += hazard.vx * delta
                hazard.y += hazard.vy * delta

                if (hazard.x < -100 or hazard.x > world.arena.width + 100 or
                    hazard.y < -100 or hazard.y > world.arena.height + 100):
                    world.arena.hazards.remove(hazard)


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



class SafeZoneMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Safe Zone"
        self.description = "A battle royale mode where the safe zone gradually shrinks, and balls take continuous damage outside of it."
        self.zone_x = 500.0
        self.zone_y = 500.0
        self.zone_radius = 500.0
        self.min_zone_radius = 50.0
        self.shrink_rate = 10.0
        self.outside_damage_per_second = 10.0
        self.tick_timer = 0.0

    def setup(self, world, balls):
        super().setup(world, balls)
        arena_width = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_height = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000
        self.zone_x = arena_width / 2.0
        self.zone_y = arena_height / 2.0
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

        # Shrink the safe zone
        if self.zone_radius > self.min_zone_radius:
            self.zone_radius -= self.shrink_rate * delta
            if self.zone_radius < self.min_zone_radius:
                self.zone_radius = self.min_zone_radius

        # Apply continuous damage outside the safe zone
        damage_this_tick = self.outside_damage_per_second * delta
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


class BumperBallsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Bumper Balls"
        self.description = "Balls deal zero damage but bounce each other with much higher knockback. Try to push opponents off the arena!"

    def setup(self, world: Any, balls: List[Any]) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []
        for b in balls:
            b.damage = 0.0
            # We can use a special flag or mutator to handle the knockback in action.py
            if not hasattr(b, "mutators"):
                b.mutators = []
            if "bumper_balls" not in b.mutators:
                b.mutators.append("bumper_balls")

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

GAME_MODES = {
    "tournament": TournamentMode(),
    "bumper_balls": BumperBallsMode(),
    "portal_node": PortalNodeMode(),
    "memory_traps": MemoryTrapsMode(),
    "vision_reduced": VisionReducedMode(),
    "dynamic_hazards": DynamicHazardsMode(),
    "custom_match": CustomMatchMode(),
    "reverse_event": ReverseEventMode(),
    "weather_chaos": WeatherChaosMode(),
    "domination": DominationMode(),
    "black_hole": BlackHoleMode(),
    "king_of_the_hill": KingOfTheHillMode(),
    "moving_zone": MovingZoneMode(),
    "vampire_royale": VampireRoyaleMode(),
    "battle_royale": BattleRoyaleMode(),
    "team_deathmatch": TeamDeathmatchMode(),
    "zombie_infection": ZombieInfectionMode(),
    "boss_fight": BossFightMode(),
    "vip_defense": VIPDefenseMode(),
    "survival": SurvivalMode(),
    "capture_the_flag": CaptureTheFlagMode(),
    "evolutionary_simulation": EvolutionarySimulationMode(),
    "safe_zone": SafeZoneMode()
}

try:
    from ai.interactive_training import InteractiveTrainingMode
    GAME_MODES["interactive_training"] = InteractiveTrainingMode()
except ImportError:
    pass
