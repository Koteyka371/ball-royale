from arena.procedural_arena import ProceduralArena
from typing import List, Any
import random
import math

class TagTeamArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, num_rooms: int = 5, seed: int | None = None):
        super().__init__(arena_size=arena_size, num_rooms=num_rooms, seed=seed)
        self.boundary_states = {"top": "bouncy", "bottom": "bouncy", "left": "bouncy", "right": "bouncy"}
        self.boundary_health = {"top": 2000.0, "bottom": 2000.0, "left": 2000.0, "right": 2000.0}
        self.swap_cooldown = 5.0
        self.team_cooldowns = {}
        self.last_tick = -1
        self.name = "Tag Team Arena"

    def generate(self):
        super().generate()
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        self.team_cooldowns = {}

    def update_zone(self, current_tick: int, delta: float):
        super().update_zone(current_tick, delta)

        # Update cooldowns
        for team_id in list(self.team_cooldowns.keys()):
            if self.team_cooldowns[team_id] > 0:
                self.team_cooldowns[team_id] -= delta
            if self.team_cooldowns[team_id] <= 0:
                self.team_cooldowns[team_id] = 0.0

    def trigger_swap(self, team_id: int, ball1: Any, ball2: Any):
        if self.team_cooldowns.get(team_id, 0.0) <= 0:
            # Execute swap
            temp_x, temp_y = ball1.x, ball1.y
            ball1.x, ball1.y = ball2.x, ball2.y
            ball2.x, ball2.y = temp_x, temp_y

            # Put ability on cooldown
            self.team_cooldowns[team_id] = self.swap_cooldown
            return True
        return False
