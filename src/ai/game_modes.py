from typing import List, Optional, Any

class GameMode:
    """Base class for all game modes."""
    def __init__(self):
        self.name = "Unknown"
        self.description = "Base game mode"

    def setup(self, world: Any, balls: List[Any]) -> None:
        """Called at the start of the battle to initialize mode-specific rules/teams."""
        pass

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        pass


    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        """Called every tick to check if there is a winner. Returns winner name or None."""
        return None

class BattleRoyaleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Battle Royale"
        self.description = "Last man standing. Everyone for themselves."

    def setup(self, world: Any, balls: List[Any]) -> None:
        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for i, b in enumerate(valid_balls):
            if i >= 20:
                b.ball_type = "spectator"
                b.alive = False
            else:
                b.team = b.ball_type # Default behavior

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
        if balls:
            boss = balls[0]
            boss.team = "Boss"
            boss.max_hp *= 10
            boss.hp = boss.max_hp
            boss.damage = getattr(boss, "damage", 10) * 2

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
        self.description = "Stay in the center area to earn points. First to 100 points wins."
        self.tick_timer = 0.0

    def setup(self, world: Any, balls: List[Any]) -> None:
        for b in balls:
            if getattr(b, "ball_type", None) != "spectator":
                b.score = 0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        self.tick_timer += delta
        if self.tick_timer >= 0.5:
            self.tick_timer = 0.0

            # Find the center of the arena
            arena_width = 1000
            arena_height = 1000
            if hasattr(world, "arena") and world.arena:
                arena_width = getattr(world.arena, "width", 1000)
                arena_height = getattr(world.arena, "height", 1000)

            center_x = arena_width / 2
            center_y = arena_height / 2
            zone_radius = min(arena_width, arena_height) * 0.2

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
                    # Cap max pull to avoid crazy speeds
                    pull_strength = min(pull_strength, 150.0)

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


class DominationMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Domination"
        self.description = "Capture points to gain global buffs for your team."
        self.points = []

    def setup(self, world: Any, balls: List[Any]) -> None:
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
                # Apply global buff
                for b in balls:
                    if getattr(b, "alive", False) and getattr(b, "team", "") == new_owner:
                        # Give buff
                        if hasattr(b, "damage"):
                            b.damage += 5.0
                        if hasattr(b, "max_hp"):
                            b.max_hp += 20.0
                            b.hp += 20.0

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
        import random, math
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

GAME_MODES = {
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
    "evolutionary_simulation": EvolutionarySimulationMode()
}
