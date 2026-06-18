import random
import math
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Room:
    x: float
    y: float
    width: float
    height: float

@dataclass
class Corridor:
    x: float
    y: float
    width: float
    height: float

class ProceduralArena:
    def __init__(self, arena_size: float = 2000.0, num_rooms: int = 5, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.width = arena_size
        self.height = arena_size
        self.num_rooms = num_rooms
        self.rooms: List[Room] = []
        self.corridors: List[Corridor] = []
        self.generate()

    def generate(self):
        # Generate rooms
        for _ in range(self.num_rooms):
            rw = random.uniform(200, 600)
            rh = random.uniform(200, 600)
            rx = random.uniform(0, self.width - rw)
            ry = random.uniform(0, self.height - rh)
            self.rooms.append(Room(rx, ry, rw, rh))

        # Connect rooms with corridors
        for i in range(1, len(self.rooms)):
            r1 = self.rooms[i - 1]
            r2 = self.rooms[i]

            # Center points
            c1x = r1.x + r1.width / 2
            c1y = r1.y + r1.height / 2
            c2x = r2.x + r2.width / 2
            c2y = r2.y + r2.height / 2

            # Create L-shaped corridor
            if random.random() < 0.5:
                # Horizontal then vertical
                self.corridors.append(Corridor(min(c1x, c2x) - 25, c1y - 25, abs(c2x - c1x) + 50, 50))
                self.corridors.append(Corridor(c2x - 25, min(c1y, c2y) - 25, 50, abs(c2y - c1y) + 50))
            else:
                # Vertical then horizontal
                self.corridors.append(Corridor(c1x - 25, min(c1y, c2y) - 25, 50, abs(c2y - c1y) + 50))
                self.corridors.append(Corridor(min(c1x, c2x) - 25, c2y - 25, abs(c2x - c1x) + 50, 50))

    def get_random_spawn_point(self, radius: float) -> Tuple[float, float]:
        if not self.rooms:
            return (random.uniform(radius, self.width - radius),
                    random.uniform(radius, self.height - radius))
        room = random.choice(self.rooms)
        return (random.uniform(room.x + radius, room.x + room.width - radius),
                random.uniform(room.y + radius, room.y + room.height - radius))

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        # Check rooms
        for r in self.rooms:
            if r.x + radius <= x <= r.x + r.width - radius and r.y + radius <= y <= r.y + r.height - radius:
                return True
        # Check corridors
        for c in self.corridors:
            if c.x + radius <= x <= c.x + c.width - radius and c.y + radius <= y <= c.y + c.height - radius:
                return True
        return False

    def clamp_position(self, x: float, y: float, radius: float) -> Tuple[float, float, bool]:
        if self.is_point_inside(x, y, radius):
            return x, y, False

        # Find nearest point inside a room or corridor
        min_dist = float('inf')
        nearest_x, nearest_y = x, y

        # Room bounds
        for r in self.rooms:
            cx = max(r.x + radius, min(x, r.x + r.width - radius))
            cy = max(r.y + radius, min(y, r.y + r.height - radius))
            dist = (cx - x)**2 + (cy - y)**2
            if dist < min_dist:
                min_dist = dist
                nearest_x, nearest_y = cx, cy

        # Corridor bounds
        for c in self.corridors:
            cx = max(c.x + radius, min(x, c.x + c.width - radius))
            cy = max(c.y + radius, min(y, c.y + c.height - radius))
            dist = (cx - x)**2 + (cy - y)**2
            if dist < min_dist:
                min_dist = dist
                nearest_x, nearest_y = cx, cy

        return nearest_x, nearest_y, True
