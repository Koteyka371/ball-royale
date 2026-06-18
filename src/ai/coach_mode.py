class CoachMode:
    """
    Manages the Coach Mode mechanics, allowing a player to set
    global or team-specific strategies for the AI balls.
    """
    def __init__(self):
        self.strategy = {}

    def set_global_strategy(self, strategy: str):
        """Sets a strategy for all balls."""
        self.strategy = strategy

    def set_team_strategy(self, team: str, strategy: str):
        """Sets a strategy for a specific team or ball type."""
        if not isinstance(self.strategy, dict):
            self.strategy = {}
        self.strategy[team] = strategy

    def get_strategy(self):
        """Returns the current strategy configuration."""
        return self.strategy
