from typing import Dict, List, Any

class DevelopmentPhase:
    """
    Handles the meta-evolution development phase for balls between battles.
    Balls gain XP based on their survival and kills, which can be spent
    to upgrade their stats (max_hp, damage, speed).
    """

    def __init__(self, xp_for_upgrade: int = 100):
        self.xp_for_upgrade = xp_for_upgrade
        # Track unspent XP across generations
        # Format: { "dna_hash": {"xp": int, "level": int} }
        self.xp_bank: Dict[str, Dict[str, int]] = {}

    def _extract_dna(self, ball: Any) -> Dict[str, Any]:
        """Extracts the genetic traits from a ball instance."""
        return {
            "speed": getattr(ball, "speed", 2.0),
            "damage": getattr(ball, "damage", 15.0),
            "max_hp": getattr(ball, "max_hp", 100.0),
            "color": getattr(ball, "color", "red"),
            "skill": getattr(ball, "skill", "dash"),
            "ball_type": getattr(ball, "ball_type", "unknown")
        }

    def _generate_dna_hash(self, dna: Dict[str, Any]) -> str:
        """Generates a unique but repeatable hash for a set of DNA traits."""
        rounded_dna = {}
        for k, v in dna.items():
            if isinstance(v, float):
                rounded_dna[k] = round(v, 2)
            else:
                rounded_dna[k] = v
        hash_str = "-".join([f"{k}:{rounded_dna[k]}" for k in sorted(rounded_dna.keys())])
        return hash_str

    def calculate_xp(self, ball: Any) -> int:
        """Calculates XP earned by a ball in a battle."""
        xp = 0
        if getattr(ball, "alive", False):
            xp += 50  # Survival bonus

        kills = getattr(ball, "kills", 0)
        xp += kills * 20  # Kill bonus

        return xp

    def process_battle_results(self, balls: List[Any]):
        """Processes a list of balls, awarding XP and applying upgrades if applicable."""
        for ball in balls:
            if getattr(ball, "ball_type", None) == "spectator":
                continue

            dna = self._extract_dna(ball)
            # Remove '_developed' suffix if present to track base DNA correctly across upgrades
            base_dna = dna.copy()
            if base_dna["ball_type"].endswith("_developed"):
                base_dna["ball_type"] = base_dna["ball_type"].replace("_developed", "")

            dna_hash = self._generate_dna_hash(base_dna)

            if dna_hash not in self.xp_bank:
                self.xp_bank[dna_hash] = {"xp": 0, "level": 1}

            earned_xp = self.calculate_xp(ball)
            self.xp_bank[dna_hash]["xp"] += earned_xp

            # Check if an upgrade is possible
            while self.xp_bank[dna_hash]["xp"] >= self.xp_for_upgrade:
                self.xp_bank[dna_hash]["xp"] -= self.xp_for_upgrade
                self.xp_bank[dna_hash]["level"] += 1
                self._apply_upgrade(ball)

    def _apply_upgrade(self, ball: Any):
        """Applies stat upgrades to a ball and marks it as developed."""
        # Increase stats
        ball.max_hp = getattr(ball, "max_hp", 100.0) * 1.1  # +10% hp
        ball.damage = getattr(ball, "damage", 15.0) * 1.1  # +10% damage
        ball.speed = getattr(ball, "speed", 2.0) * 1.05  # +5% speed

        # Heal up the max hp increase if alive
        if getattr(ball, "alive", False):
            ball.hp = getattr(ball, "hp", ball.max_hp) + (ball.max_hp - ball.max_hp / 1.1)

        ball_type = getattr(ball, "ball_type", "unknown")
        if not ball_type.endswith("_developed"):
            ball.ball_type = f"{ball_type}_developed"
