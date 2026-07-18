import math
from typing import Any, List
from ai.game_modes import GameMode, GAME_MODES

class WeatherStationsMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Weather Stations"
        self.description = "Add capture-able weather stations in the arena that let a team control the weather in their sector."
        self.stations = []

    def setup(self, world: Any, balls: List[Any]) -> None:
        super().setup(world, balls)
        arena_w = getattr(world.arena, "width", 1000) if hasattr(world, "arena") and world.arena else 1000
        arena_h = getattr(world.arena, "height", 1000) if hasattr(world, "arena") and world.arena else 1000

        self.stations = [
            {"x": arena_w * 0.25, "y": arena_h * 0.25, "radius": 150.0, "capture_progress": 0.0, "weather": "heatwave", "owner": None},
            {"x": arena_w * 0.75, "y": arena_h * 0.25, "radius": 150.0, "capture_progress": 0.0, "weather": "blizzard", "owner": None},
            {"x": arena_w * 0.25, "y": arena_h * 0.75, "radius": 150.0, "capture_progress": 0.0, "weather": "acid_rain", "owner": None},
            {"x": arena_w * 0.75, "y": arena_h * 0.75, "radius": 150.0, "capture_progress": 0.0, "weather": "wind", "owner": None}
        ]

        valid_balls = [b for b in balls if getattr(b, "ball_type", None) != "spectator"]
        for b in valid_balls:
            if not hasattr(b, "team"):
                b.team = b.ball_type

    def tick(self, world: Any, balls: List[Any], delta: float = 0.016) -> None:
        super().tick(world, balls, delta)

        # Update capture progress
        for station in self.stations:
            station_cx, station_cy = station["x"], station["y"]
            r = station["radius"]
            r_sq = r * r

            # Find balls inside
            inside_balls = []
            for b in balls:
                if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                    continue
                dx = b.x - station_cx
                dy = b.y - station_cy
                if dx * dx + dy * dy <= r_sq:
                    inside_balls.append(b)

            if inside_balls:
                teams_inside = set(getattr(b, "team", getattr(b, "ball_type", "unknown")) for b in inside_balls)

                if len(teams_inside) == 1:
                    max_team = list(teams_inside)[0]
                    if station["owner"] == max_team:
                        if station["capture_progress"] < 100.0:
                            station["capture_progress"] = min(100.0, station["capture_progress"] + 20.0 * delta)
                    else:
                        station["capture_progress"] -= 20.0 * delta
                        if station["capture_progress"] <= 0:
                            station["owner"] = max_team
                            station["capture_progress"] = 0.0
                else:
                    # Contested, no progress change
                    pass
            else:
                # Decay
                station["capture_progress"] = max(0.0, station["capture_progress"] - 10.0 * delta)
                if station["capture_progress"] == 0.0:
                    station["owner"] = None

        # Apply weather effects based on closest station
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            # Find closest station
            closest_station = None
            min_dist_sq = float('inf')
            for station in self.stations:
                dx = b.x - station["x"]
                dy = b.y - station["y"]
                dist_sq = dx * dx + dy * dy
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    closest_station = station

            base_speed = getattr(b, "base_speed", 100.0)
            base_damage = getattr(b, "base_damage", 10.0)
            team = getattr(b, "team", getattr(b, "ball_type", "unknown"))

            if closest_station and closest_station["capture_progress"] == 100.0:
                is_winner = closest_station["owner"] == team
                weather = closest_station["weather"]

                if is_winner:
                    if weather == "heatwave":
                        b.speed = base_speed * 1.2
                        b.damage = base_damage * 1.5
                    elif weather == "blizzard":
                        b.speed = base_speed * 1.5
                        b.damage = base_damage * 1.2
                    elif weather == "acid_rain":
                        b.speed = base_speed * 1.2
                        b.damage = base_damage * 1.2
                        b.hp = min(getattr(b, "max_hp", 100.0), getattr(b, "hp", 100.0) + 2.0 * delta)
                    elif weather == "wind":
                        b.speed = base_speed * 2.0
                        b.damage = base_damage * 1.0
                    else:
                        b.speed = base_speed
                        b.damage = base_damage
                else:
                    if weather == "heatwave":
                        b.speed = base_speed * 0.8
                        b.damage = base_damage * 1.0
                    elif weather == "blizzard":
                        b.speed = base_speed * 1.0
                        b.damage = base_damage * 0.8
                    elif weather == "acid_rain":
                        b.speed = base_speed * 0.9
                        b.damage = base_damage * 0.9
                        b.hp -= 2.0 * delta
                    elif weather == "wind":
                        b.speed = base_speed * 0.5
                        b.damage = base_damage * 0.8
                    else:
                        b.speed = base_speed
                        b.damage = base_damage
            else:
                # No active weather effect in this sector
                b.speed = base_speed
                b.damage = base_damage

GAME_MODES['weather_stations'] = WeatherStationsMode()
