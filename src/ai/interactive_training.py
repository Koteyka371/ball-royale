import math
from typing import Any, List, Optional
from ai.game_modes import GameMode # type: ignore

class InteractiveTrainingMode(GameMode):
    """
    Interactive Training Mode:
    A mode where the player (user) fights against or trains alongside neural network-controlled balls.
    The AI adapts based on their interactions, receiving fitness based on their performance against the user.
    """
    def __init__(self):
        super().__init__()
        self.name = "Interactive Training"
        self.description = "Train neural network balls by interacting with them. Your actions shape their strategy."
        self.tick_timer = 0.0
        self.generation = 1
        self.user_ball_id = None
        self.learning_rate = 0.01

    def setup(self, world: Any, balls: List[Any]) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        # Identify user ball and set others to neural
        self.user_ball_id = balls[0].id if balls else None

        for i, b in enumerate(balls):
            if getattr(b, "ball_type", None) != "spectator":
                if b.id == self.user_ball_id:
                    b.team = "User"
                    b.is_user = True  # Avoid modifying ball_type as it might break rendering/stats
                else:
                    b.ball_type = "neural"
                    b.team = "Learning"
                    # Initialize interactive fitness score
                    b.interactive_fitness = 0.0

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        if not hasattr(world, "dead_balls"):
            world.dead_balls = []

        self.tick_timer += delta

        user_ball = next((b for b in balls if b.id == self.user_ball_id and getattr(b, "alive", False)), None)

        for b in balls:
            if not getattr(b, "alive", False):
                if b not in world.dead_balls:
                    b.time_since_death = 0.0
                    world.dead_balls.append(b)
                else:
                    b.time_since_death += delta
                continue

            if getattr(b, "team", "") == "Learning" and user_ball:
                # Basic fitness updates during the match based on interaction with the user

                # Reward for being close to the user (engaging)
                dist_sq = (b.x - user_ball.x)**2 + (b.y - user_ball.y)**2
                dist = math.sqrt(dist_sq)

                if dist < getattr(user_ball, "perception_radius", 300.0):
                    b.interactive_fitness += 1.0 * delta

                # Penalty for dying quickly
                if b.hp < b.max_hp * 0.2:
                    b.interactive_fitness -= 0.5 * delta

                # Reward for dealing damage
                if hasattr(b, "damage_dealt") and b.damage_dealt > 0:
                    b.interactive_fitness += b.damage_dealt * 2.0 * delta

        # Optionally, trigger a micro-evolution or weight adjustment mid-match if timer exceeds a threshold
        if self.tick_timer > 30.0:
            self.tick_timer = 0.0
            self.generation += 1
            # In a full implementation, we'd adjust weights here. For now, just logging/tracking.

    def check_winner(self, world: Any, balls: List[Any]) -> Optional[str]:
        alive = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
        if not alive:
            return "Draw"

        teams_alive = set(getattr(b, "team", getattr(b, "ball_type", None)) for b in alive)
        if len(teams_alive) == 1:
            return list(teams_alive)[0]

        return None
