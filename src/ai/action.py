from typing import Any

class Action:
    """
    Action execution system.
    Executes the chosen behavior (strategy) by interacting with the ball.
    Handles movement, pathfinding, timing, and cooldowns.
    """
    def __init__(self, ball: Any, world: Any):
        self.ball = ball
        self.world = world

    def execute(self, strategy: str, delta: float) -> None:
        """
        Executes the chosen strategy.
        """
        # Save the chosen strategy as current_action for testing/debugging
        self.ball.current_action = strategy

        if strategy == "flee":
            if hasattr(self.ball, "flee"):
                self.ball.flee(delta)
        elif strategy == "attack":
            if hasattr(self.ball, "attack"):
                self.ball.attack(delta)
        elif strategy == "defend":
            if hasattr(self.ball, "defend"):
                self.ball.defend(delta)
        elif strategy in ["opportunistic", "collect booster"]:
            if hasattr(self.ball, "collect_booster"):
                self.ball.collect_booster(delta)
        elif strategy == "use skill":
            if hasattr(self.ball, "use_skill"):
                self.ball.use_skill()
        elif strategy == "chase":
            # Note: in MVP, chase might be identical to attack or not yet implemented separately.
            if hasattr(self.ball, "chase"):
                self.ball.chase(delta)
            elif hasattr(self.ball, "attack"):
                self.ball.attack(delta)
        else:
            if hasattr(self.ball, "idle"):
                self.ball.idle(delta)
