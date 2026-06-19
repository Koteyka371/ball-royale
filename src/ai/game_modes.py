from typing import List, Dict, Optional, Any

class GameMode:
    """Base class for all game modes."""
    def __init__(self):
        self.name = "Unknown"
        self.description = "Base game mode"

    def setup(self, world: Any, balls: List[Any]) -> None:
        """Called at the start of the battle to initialize mode-specific rules/teams."""
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
        for b in balls:
            b.team = b.ball_type # Default behavior

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(b.team for b in alive if hasattr(b, "team"))
        if not teams_alive:
             types_alive = set(b.ball_type for b in alive)
             if len(types_alive) == 1:
                 return list(types_alive)[0]
        elif len(teams_alive) == 1:
            return list(teams_alive)[0]

        if len(alive) == 1:
            return alive[0].ball_type

        return None

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

GAME_MODES = {
    "battle_royale": BattleRoyaleMode(),
    "team_deathmatch": TeamDeathmatchMode(),
    "zombie_infection": ZombieInfectionMode(),
    "boss_fight": BossFightMode(),
    "vip_defense": VIPDefenseMode(),
    "survival": SurvivalMode()
}
