
import math
import random
from typing import Any, List
from ai.game_modes import GameMode, GAME_MODES

class GoldRushMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Gold Rush"
        self.description = "Gold coins randomly spawn across the arena. The more coins you collect, the larger and slower you get. The player with the most coins at the end of the time limit wins."
        self.coins = []
        self.time_limit = 120.0
        self.coin_spawn_timer = 0.0
        self.coin_spawn_interval = 2.0
        self.max_coins = 20

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        self.time_limit -= delta

        arena_w = getattr(world.arena, "width", 800) if hasattr(world, "arena") and world.arena else 800
        arena_h = getattr(world.arena, "height", 600) if hasattr(world, "arena") and world.arena else 600

        # Spawn coins
        self.coin_spawn_timer += delta
        if self.coin_spawn_timer >= self.coin_spawn_interval and len(self.coins) < self.max_coins:
            self.coin_spawn_timer -= self.coin_spawn_interval

            coin = {
                "id": f"gold_coin_{random.randint(10000, 99999)}",
                "x": random.uniform(50, arena_w - 50),
                "y": random.uniform(50, arena_h - 50),
                "radius": 15.0
            }
            self.coins.append(coin)
            if hasattr(world, "add_event"):
                world.add_event("coin_spawn", {"x": coin["x"], "y": coin["y"]})

        # Initialize coin counts on balls
        for b in balls:
            if not hasattr(b, "collected_coins"):
                b.collected_coins = 0
                b.base_radius = getattr(b, "radius", 15.0)
                b.base_speed = getattr(b, "speed", 100.0)

        # Process coin collection
        coins_to_remove = []
        for coin in self.coins:
            for b in balls:
                if not getattr(b, "alive", False):
                    continue

                dist = math.hypot(b.x - coin["x"], b.y - coin["y"])
                if dist < getattr(b, "radius", 15.0) + coin["radius"]:
                    b.collected_coins += 1
                    # Increase size and decrease speed
                    b.radius = getattr(b, "base_radius", 15.0) + (b.collected_coins * 2.0)
                    b.speed = max(20.0, getattr(b, "base_speed", 100.0) - (b.collected_coins * 2.0))

                    if hasattr(world, "add_event"):
                        world.add_event("coin_collected", {"ball_id": getattr(b, "id", None), "coins": b.collected_coins})

                    coins_to_remove.append(coin)
                    break

        for coin in coins_to_remove:
            if coin in self.coins:
                self.coins.remove(coin)

    def check_winner(self, world: Any, balls: List[Any]) -> Any:
        if self.time_limit <= 0:
            if not balls:
                return None

            alive_balls = [b for b in balls if getattr(b, "alive", False)]
            if not alive_balls:
                return None

            winner = max(alive_balls, key=lambda b: getattr(b, "collected_coins", 0))
            if getattr(winner, "team", None):
                return winner.team
            return getattr(winner, "id", "Unknown")
        return None

GAME_MODES["gold_rush"] = GoldRushMode()
