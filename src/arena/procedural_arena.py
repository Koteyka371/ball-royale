import random
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


@dataclass
class Hazard:
    id: int
    x: float
    y: float
    radius: float
    kind: str
    damage: float
    active: bool = True
    target_x: float = 0.0
    target_y: float = 0.0


class ProceduralArena:
    def __init__(self, arena_size: float = 2000.0, num_rooms: int = 5, seed: int | None = None):
        if seed is not None:
            random.seed(seed)
        self.width = arena_size
        self.height = arena_size
        self.num_rooms = num_rooms
        self.rooms: List[Room] = []
        self.corridors: List[Corridor] = []
        self.hazards: List[Hazard] = []

        # Shrinking zone
        self.safe_zone_radius = arena_size * 0.7
        self.safe_zone_center = (arena_size / 2, arena_size / 2)
        self.last_tick = -1
        self.danger_grid: dict[tuple[int, int], float] = {}

        self.generate()

    def generate(self):
        # Generate non-overlapping rooms
        attempts = 0
        while len(self.rooms) < self.num_rooms and attempts < 1000:
            attempts += 1
            # Adjust max room size based on arena size to ensure they fit better
            max_size = min(600, self.width / 2)
            rw = random.uniform(200, max_size)
            rh = random.uniform(200, max_size)
            rx = random.uniform(50, self.width - rw - 50)
            ry = random.uniform(50, self.height - rh - 50)

            overlap = False
            for r in self.rooms:
                if not (rx + rw + 50 < r.x or rx > r.x + r.width + 50 or
                        ry + rh + 50 < r.y or ry > r.y + r.height + 50):
                    overlap = True
                    break

            if not overlap:
                self.rooms.append(Room(rx, ry, rw, rh))

        # Connect rooms with corridors using closest-neighbor connection
        if not self.rooms:
            return

        connected = [self.rooms[0]]
        unconnected = self.rooms[1:]

        while unconnected:
            best_dist = float('inf')
            best_pair = (None, None)

            for c_room in connected:
                c_cx = c_room.x + c_room.width / 2
                c_cy = c_room.y + c_room.height / 2
                for u_room in unconnected:
                    u_cx = u_room.x + u_room.width / 2
                    u_cy = u_room.y + u_room.height / 2
                    dist = (c_cx - u_cx)**2 + (c_cy - u_cy)**2
                    if dist < best_dist:
                        best_dist = dist
                        best_pair = (c_room, u_room)

            r1, r2 = best_pair
            if r1 is None or r2 is None:
                break

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

            connected.append(r2)
            unconnected.remove(r2)

        # Generate hazards
        num_hazards = self.num_rooms * 2

        # Add portals
        if len(self.rooms) >= 2:
            portal_count = random.randint(1, 3)
            for p in range(portal_count):
                r1 = random.choice(self.rooms)
                r2 = random.choice(self.rooms)
                while r1 == r2:
                    r2 = random.choice(self.rooms)

                hx1 = random.uniform(r1.x + 30, r1.x + r1.width - 30)
                hy1 = random.uniform(r1.y + 30, r1.y + r1.height - 30)
                hx2 = random.uniform(r2.x + 30, r2.x + r2.width - 30)
                hy2 = random.uniform(r2.y + 30, r2.y + r2.height - 30)

                h1 = Hazard(id=len(self.hazards) + 10000 + p*2, x=hx1, y=hy1, radius=25.0, kind="portal", damage=0.0)
                h1.target_x = hx2
                h1.target_y = hy2
                self.hazards.append(h1)

                h2 = Hazard(id=len(self.hazards) + 10000 + p*2 + 1, x=hx2, y=hy2, radius=25.0, kind="portal", damage=0.0)
                h2.target_x = hx1
                h2.target_y = hy1
                self.hazards.append(h2)
        for i in range(num_hazards):
            kind = random.choice(["spikes", "lava", "fake_booster", "poison_cloud", "proximity_trap"])
            if kind == "spikes":
                radius = random.uniform(15.0, 30.0)
                damage = 20.0
            elif kind == "lava":
                radius = random.uniform(30.0, 60.0)
                damage = 50.0
            elif kind == "poison_cloud":
                radius = random.uniform(40.0, 70.0)
                damage = 10.0
            elif kind == "proximity_trap":
                radius = random.uniform(20.0, 40.0)
                damage = 30.0
            else:
                radius = 15.0
                damage = 50.0

            hx, hy = self.get_random_spawn_point(radius)
            self.hazards.append(Hazard(id=i, x=hx, y=hy, radius=radius, kind=kind, damage=damage))

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


    def update_zone(self, current_tick: int, delta: float):
        if current_tick != self.last_tick:
            self.last_tick = current_tick
            self.safe_zone_radius -= 10.0 * delta
            if self.safe_zone_radius < 50.0:
                self.safe_zone_radius = 50.0

            # Slowly expand dynamic hazards
            for h in self.hazards:
                if h.id >= 1000 and hasattr(h, "target_radius"):
                    if h.radius < h.target_radius:
                        # Grow proportionally to reach target in roughly 600 ticks
                        h.radius += (h.target_radius / 600.0) * delta * 60.0 # Assuming 60 ticks per second
                        if h.radius > h.target_radius:
                            h.radius = h.target_radius


        if current_tick % 600 == 0:
            import random

            # Clear old dynamic hazards
            self.hazards = [h for h in self.hazards if h.id < 1000]

            # Periodically trigger random arena-wide events
            event_type = random.choice(["meteor_shower", "gravity_shift", "moving_walls", "none"])
            if event_type != "none":
                self._trigger_event(event_type, current_tick)

            num_zones = random.randint(1, 3)
            for _ in range(num_zones):
                x = random.uniform(200, self.width - 200)
                y = random.uniform(200, self.height - 200)
                target_radius = random.uniform(100.0, 250.0)
                # Ensure hazard ID is unique
                h_id = 1000 + len(self.hazards)

                # Start with a very small radius and grow
                is_gravity_well = random.random() < 0.2
                if random.random() < 0.1:
                    kind = "drone_item"
                    damage = 0.0
                else:
                    kind = "gravity_well" if is_gravity_well else "trap"
                    damage = 0.0 if is_gravity_well else 100.0
                new_hazard = Hazard(id=h_id, x=x, y=y, radius=10.0, kind=kind, damage=damage)
                new_hazard.target_radius = target_radius
                self.hazards.append(new_hazard)

        if current_tick % 10 == 0:
            self._update_danger_grid()


    def _trigger_event(self, event_type: str, current_tick: int):
        import random
        if event_type == "meteor_shower":
            # Spawn multiple small, high-damage hazards quickly
            num_meteors = random.randint(5, 15)
            for _ in range(num_meteors):
                x = random.uniform(50, self.width - 50)
                y = random.uniform(50, self.height - 50)
                h_id = 2000 + len(self.hazards) + random.randint(0, 1000)
                meteor = Hazard(id=h_id, x=x, y=y, radius=30.0, kind="meteor", damage=200.0)
                meteor.target_radius = 30.0
                setattr(meteor, "duration", 5.0)
                self.hazards.append(meteor)
        elif event_type == "gravity_shift":
            # Add a massive gravity well in the center
            h_id = 3000 + len(self.hazards)
            gw = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=self.width/2, kind="gravity_well", damage=0.0)
            gw.target_radius = self.width/2
            setattr(gw, "duration", 10.0)
            self.hazards.append(gw)
        elif event_type == "moving_walls":
            # Add horizontal and vertical laser walls
            h_id = 4000 + len(self.hazards)
            wall = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=100.0, kind="laser_wall", damage=50.0)
            wall.target_radius = self.width
            setattr(wall, "duration", 8.0)
            self.hazards.append(wall)

    def _update_danger_grid(self):
        self.danger_grid.clear()

        # Check hazards
        for h in self.hazards:
            grid_x = int(h.x // 100)
            grid_y = int(h.y // 100)
            r_cells = int(h.radius // 100) + 1
            for i in range(grid_x - r_cells, grid_x + r_cells + 1):
                for j in range(grid_y - r_cells, grid_y + r_cells + 1):
                    cx = i * 100 + 50
                    cy = j * 100 + 50
                    dist = ((cx - h.x)**2 + (cy - h.y)**2)**0.5
                    if dist <= h.radius + 50:
                        self.danger_grid[(i, j)] = self.danger_grid.get((i, j), 0.0) + (h.damage / 10.0)

        # Check safe zone
        grid_w = int(self.width // 100) + 1
        grid_h = int(self.height // 100) + 1
        for i in range(grid_w):
            for j in range(grid_h):
                cx = i * 100 + 50
                cy = j * 100 + 50
                dist_to_center = ((cx - self.safe_zone_center[0])**2 + (cy - self.safe_zone_center[1])**2)**0.5
                if dist_to_center > self.safe_zone_radius:
                    self.danger_grid[(i, j)] = self.danger_grid.get((i, j), 0.0) + 5.0