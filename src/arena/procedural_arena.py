import math
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
    target_radius: float = 0.0


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
        self.wind_dx = 0.0
        self.wind_dy = 0.0

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
        for i in range(num_hazards):
            kind = random.choice(["spikes", "lava", "fake_booster", "decoy_item", "link_booster", "stamina_booster", "weather_booster", "poison_cloud", "proximity_trap", "spinning_laser", "healing_spring", "temporal_rift", "bumper", "tornado", "lightning_storm", "hidden_trap", "silence_booster", "freeze_booster", "switch", "magnet", "quicksand", "magnet_booster", "breakable_wall", "portal_gun_item", "wormhole", "clone_booster", "stealth_zone", "invert_booster", "reverse_gravity_booster", "stamina_drain_zone", "tether_trap", "slip_zone", "tall_grass"])
            if kind == "switch":
                radius = 20.0
                damage = 0.0
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
            elif kind == "hidden_trap":
                radius = random.uniform(20.0, 35.0)
                damage = 15.0
            elif kind == "decoy_item":
                radius = 15.0
                damage = 0.0
            elif kind == "silence_booster":
                radius = 15.0
                damage = 0.0
            elif kind == "freeze_booster":
                radius = 15.0
                damage = 0.0
            elif kind == "link_booster":
                radius = 15.0
                damage = 0.0
            elif kind == "stamina_booster" or kind == "weather_booster" or kind == "magnet_booster" or kind == "clone_booster" or kind == "invert_booster" or kind == "freeze_booster" or kind == "reverse_gravity_booster":
                radius = 15.0
                damage = 0.0
            elif kind == "stealth_zone":
                radius = random.uniform(40.0, 80.0)
                damage = 0.0
            elif kind == "breakable_wall":
                radius = random.uniform(30.0, 60.0)
                damage = 0.0
            elif kind == "tornado":
                radius = random.uniform(30.0, 60.0)
                damage = 15.0
            elif kind == "lightning_storm":
                radius = random.uniform(30.0, 60.0)
                damage = 0.0
            elif kind == "tether_trap":
                radius = random.uniform(50.0, 100.0)
                damage = 0.0
            elif kind == "stamina_drain_zone":
                radius = random.uniform(40.0, 80.0)
                damage = 0.0
            elif kind == "slip_zone":
                radius = random.uniform(40.0, 80.0)
                damage = 0.0
            elif kind == "tall_grass":
                radius = random.uniform(30.0, 60.0)
                damage = 5.0
            elif kind == "spinning_laser":
                radius = random.uniform(100.0, 150.0)
                damage = 100.0
            elif kind == "quicksand":
                radius = random.uniform(40.0, 80.0)
                damage = 0.0
            elif kind == "healing_spring":
                radius = random.uniform(40.0, 80.0)
                damage = -20.0
            elif kind == "temporal_rift":
                radius = random.uniform(60.0, 100.0)
                damage = 0.0
            elif kind == "magnet":
                radius = random.uniform(25.0, 45.0)
                damage = 0.0
            elif kind == "bumper":
                radius = random.uniform(30.0, 60.0)
                damage = 0.0
                hx, hy = self.get_random_spawn_point(radius)
                new_hazard = Hazard(id=i, x=hx, y=hy, radius=radius, kind=kind, damage=damage)

                # Make bumpers dynamic
                if random.random() < 0.4:
                    powerups = ["heal", "speed", "shield", "stamina"]
                    setattr(new_hazard, "powerup_type", random.choice(powerups))
                if kind == "breakable_wall":
                    setattr(new_hazard, "hp", 100.0)
                if random.random() < 0.5:
                    # Orbit another hazard
                    target = None
                    if len(self.hazards) > 0:
                        target = random.choice(self.hazards)
                    if target:
                        setattr(new_hazard, "target_hazard_id", target.id)
                        setattr(new_hazard, "orbit_angle", random.uniform(0, 3.14159 * 2))
                        setattr(new_hazard, "orbit_radius", target.radius + radius + random.uniform(10.0, 50.0))
                        setattr(new_hazard, "orbit_speed", random.uniform(1.0, 3.0))
                else:
                    # Linear moving path with wall bounce
                    angle = random.uniform(0, 3.14159 * 2)
                    speed = random.uniform(50.0, 150.0)
                    setattr(new_hazard, "vx", math.cos(angle) * speed)
                    setattr(new_hazard, "vy", math.sin(angle) * speed)

                self.hazards.append(new_hazard)
                continue
            else:
                radius = 15.0
                damage = 50.0

            hx, hy = self.get_random_spawn_point(radius)
            new_hazard = Hazard(id=i, x=hx, y=hy, radius=radius, kind=kind, damage=damage)
            if kind == "temporal_rift":
                new_hazard.time_scale = random.choice([0.5, 1.5, 2.0])
            elif kind == "magnet":
                setattr(new_hazard, "polarity", random.choice([1, -1]))
            elif kind == "tether_trap":
                setattr(new_hazard, "hp", 100.0)
                setattr(new_hazard, "max_hp", 100.0)
                setattr(new_hazard, "pull_speed", random.uniform(50.0, 150.0))
            self.hazards.append(new_hazard)

        # Generate guaranteed paired portals
        num_portals = max(1, self.num_rooms // 2)
        for p in range(num_portals):
            p1_id = len(self.hazards) + 5000 + p*2
            p2_id = len(self.hazards) + 5000 + p*2 + 1

            p1_x, p1_y = self.get_random_spawn_point(30.0)
            p2_x, p2_y = self.get_random_spawn_point(30.0)

            portal1 = Hazard(id=p1_id, x=p1_x, y=p1_y, radius=30.0, kind="portal", damage=0.0)
            portal1.target_x = p2_x
            portal1.target_y = p2_y

            portal2 = Hazard(id=p2_id, x=p2_x, y=p2_y, radius=30.0, kind="portal", damage=0.0)

            is_two_way = random.random() < 0.5
            if is_two_way:
                portal2.target_x = p1_x
                portal2.target_y = p1_y

            bh_hazards = [h for h in self.hazards if h.kind == "black_hole"]
            if bh_hazards and random.random() < 0.3:
                target_bh = random.choice(bh_hazards)
                # Link portal1 to the black hole ID, so it dynamically tracks the moving hazard
                portal1.target_hazard_id = target_bh.id
                if is_two_way:
                    portal2.target_hazard_id = target_bh.id

            self.hazards.append(portal1)
            self.hazards.append(portal2)


        # Generate guaranteed paired swap portals
        num_swap_portals = max(1, self.num_rooms // 2)
        for p in range(num_swap_portals):
            p1_id = len(self.hazards) + 8000 + p*2
            p2_id = len(self.hazards) + 8000 + p*2 + 1

            p1_x, p1_y = self.get_random_spawn_point(30.0)
            p2_x, p2_y = self.get_random_spawn_point(30.0)

            sp1 = Hazard(id=p1_id, x=p1_x, y=p1_y, radius=30.0, kind="swap_portal", damage=0.0)
            sp1.target_x = p2_x
            sp1.target_y = p2_y
            sp1.pair_id = p2_id

            sp2 = Hazard(id=p2_id, x=p2_x, y=p2_y, radius=30.0, kind="swap_portal", damage=0.0)
            sp2.target_x = p1_x
            sp2.target_y = p1_y
            sp2.pair_id = p1_id

            self.hazards.append(sp1)
            self.hazards.append(sp2)
        # Generate guaranteed paired wormholes
        num_wormholes = max(1, self.num_rooms // 2)
        for p in range(num_wormholes):
            w1_id = len(self.hazards) + 9000 + p*2
            w2_id = len(self.hazards) + 9000 + p*2 + 1

            w1_x, w1_y = self.get_random_spawn_point(30.0)
            w2_x, w2_y = self.get_random_spawn_point(30.0)

            w1 = Hazard(id=w1_id, x=w1_x, y=w1_y, radius=30.0, kind="wormhole", damage=0.0)
            w1.target_x = w2_x
            w1.target_y = w2_y

            w2 = Hazard(id=w2_id, x=w2_x, y=w2_y, radius=30.0, kind="wormhole", damage=0.0)
            w2.target_x = w1_x
            w2.target_y = w1_y

            self.hazards.append(w1)
            self.hazards.append(w2)


        # Generate random one-way teleporters
        num_oneway_teleporters = max(1, self.num_rooms // 2)
        for t in range(num_oneway_teleporters):
            t_id = len(self.hazards) + 6500 + t
            tx, ty = self.get_random_spawn_point(25.0)
            target_x, target_y = self.get_random_spawn_point(25.0)
            teleporter = Hazard(id=t_id, x=tx, y=ty, radius=25.0, kind="one_way_teleporter", damage=0.0)
            teleporter.target_x = target_x
            teleporter.target_y = target_y
            setattr(teleporter, "change_timer", 5.0)
            self.hazards.append(teleporter)

        # Generate random teleporter pads
        num_teleporters = max(2, self.num_rooms)

        # We need to link them in pairs. If there's an odd number, we'll round up to the next even number.
        if num_teleporters % 2 != 0:
            num_teleporters += 1

        teleporters = []
        for t in range(num_teleporters):
            t_id = len(self.hazards) + 6000 + t
            tx, ty = self.get_random_spawn_point(25.0)
            teleporter = Hazard(id=t_id, x=tx, y=ty, radius=25.0, kind="teleporter", damage=0.0)
            teleporters.append(teleporter)

        # Link them in pairs
        for i in range(0, len(teleporters), 2):
            t1 = teleporters[i]
            t2 = teleporters[i+1]
            t1.target_x = t2.x
            t1.target_y = t2.y
            t2.target_x = t1.x
            t2.target_y = t1.y

            self.hazards.append(t1)
            self.hazards.append(t2)

    def get_random_spawn_point(self, radius: float) -> Tuple[float, float]:
        if not self.rooms:
            return (random.uniform(radius, self.width - radius),
                    random.uniform(radius, self.height - radius))
        room = random.choice(self.rooms)
        return (random.uniform(room.x + radius, room.x + room.width - radius),
                random.uniform(room.y + radius, room.y + room.height - radius))

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        import math
        sz_cx, sz_cy = self.safe_zone_center
        sz_radius = self.safe_zone_radius
        dist = math.hypot(x - sz_cx, y - sz_cy)
        if dist > sz_radius - radius:
            return False

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

        import math
        sz_cx, sz_cy = self.safe_zone_center
        sz_radius = self.safe_zone_radius
        dist = math.hypot(nearest_x - sz_cx, nearest_y - sz_cy)

        # If outside the safe zone, push inwards towards safe zone edge
        if dist > sz_radius - radius:
            if dist > 0.0001:
                dir_x = (nearest_x - sz_cx) / dist
                dir_y = (nearest_y - sz_cy) / dist
                nearest_x = sz_cx + dir_x * (sz_radius - radius)
                nearest_y = sz_cy + dir_y * (sz_radius - radius)
            else:
                nearest_x = sz_cx
                nearest_y = sz_cy

        return nearest_x, nearest_y, True



    def update_zone(self, current_tick: int, delta: float):
        if current_tick != self.last_tick:
            import math
            # Process hazard-to-hazard combos
            if hasattr(self, "hazards"):
                for hazard in self.hazards:
                    if hazard.kind == "slip_zone":
                        if not hasattr(hazard, "active_timer"):
                            hazard.active_timer = 0.0
                            hazard.active = True
                        hazard.active_timer += delta
                        if hazard.active_timer >= 5.0:
                            hazard.active_timer = 0.0
                            hazard.active = not hazard.active
                for hazard in self.hazards:
                    if hazard.kind == "magnet":
                        for other_hazard in self.hazards:
                            if hazard.id == other_hazard.id:
                                continue
                            if other_hazard.kind in ("explosive_barrel", "flare"):
                                hx_diff = hazard.x - other_hazard.x
                                hy_diff = hazard.y - other_hazard.y
                                hdist_sq = hx_diff * hx_diff + hy_diff * hy_diff
                                eff_rad = hazard.radius * 3.0

                                if 0.0001 < hdist_sq < eff_rad * eff_rad:
                                    hdist = math.sqrt(hdist_sq)
                                    hnx = hx_diff / hdist
                                    hny = hy_diff / hdist
                                    pull_strength = (eff_rad / max(10.0, hdist)) * 150.0 * delta
                                    pull_strength = min(pull_strength, hdist * 0.5)

                                    other_hazard.x += hnx * pull_strength
                                    other_hazard.y += hny * pull_strength

                                    if hdist < hazard.radius + getattr(other_hazard, "radius", 10.0):
                                        if other_hazard.kind == "explosive_barrel":
                                            if not getattr(other_hazard, "is_exploded", False):
                                                other_hazard.is_exploded = True
                                                other_hazard.radius = getattr(other_hazard, "radius", 50.0) * 3.0
                                                other_hazard.damage = getattr(other_hazard, "damage", 50.0) * 2.0
                                        elif other_hazard.kind == "flare":
                                            if getattr(other_hazard, "active", True):
                                                other_hazard.active = False
                                                other_hazard.duration = 0.0
                                                hazard.kind = "fire_zone"
                                                hazard.radius = getattr(hazard, "radius", 50.0) * 2.0
                                                hazard.damage = getattr(hazard, "damage", 10.0) * 3.0
                                                if not hasattr(hazard, "duration"):
                                                    hazard.duration = 10.0

            self.last_tick = current_tick

            # Massive Black Hole Event logic
            has_mbh = any(h.kind == "massive_black_hole" for h in getattr(self, "hazards", []))
            if self.safe_zone_radius > 50.0:
                if has_mbh:
                    self.safe_zone_radius -= 50.0 * delta
                else:
                    self.safe_zone_radius -= 10.0 * delta
                if self.safe_zone_radius <= 50.0:
                    self.safe_zone_radius = 50.0
            else:
                # Spawn supply drop on the edge of the safe zone periodically
                if current_tick % 300 == 0:
                    import random
                    import math
                    angle = random.uniform(0, math.pi * 2)
                    # Spawn slightly outside or on the edge (e.g. radius to radius + 100)
                    drop_dist = self.safe_zone_radius + random.uniform(-20.0, 100.0)
                    cx, cy = self.safe_zone_center
                    sx = cx + math.cos(angle) * drop_dist
                    sy = cy + math.sin(angle) * drop_dist

                    # Clamp to arena bounds
                    sx = max(50.0, min(self.width - 50.0, sx))
                    sy = max(50.0, min(self.height - 50.0, sy))

                    item_kind = random.choice(["healing_spring", "damage_link", "emp_burst", "nemesis_booster", "stamina_booster", "vision_booster", "reverse_gravity_booster"])

                    item_id = 9000 + len(self.hazards) + random.randint(0, 1000)
                    drop = Hazard(id=item_id, x=sx, y=sy, radius=20.0, kind=item_kind, damage=0.0)

                    self.hazards.append(drop)

                if current_tick % 120 == 0:
                    import random
                    if hasattr(self, "_trigger_event"):
                        self._trigger_event(random.choice(["meteor_shower", "gravity_shift", "orbital_strike", "massive_black_hole_event"]), current_tick)
                    else:
                        event_type = random.choice(["meteor_shower", "gravity_shift"])
                        if event_type == "meteor_shower":
                            for _ in range(10):
                                x = random.uniform(50, self.width - 50)
                                y = random.uniform(50, self.height - 50)
                                # Assuming Hazard is imported in basic_arena

                                m = Hazard(id=len(self.hazards) + random.randint(1000, 9999), x=x, y=y, radius=30.0, kind="meteor", damage=200.0)
                                m.target_radius = 30.0
                                setattr(m, "duration", 5.0)
                                self.hazards.append(m)
                        elif event_type == "anomaly_zone":
                            h_id = 6000 + len(self.hazards)
                            zone = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=400.0, kind="anomaly_zone", damage=0.0)
                            zone.target_radius = 400.0
                            setattr(zone, "duration", 10.0)
                            self.hazards.append(zone)
                        elif event_type == "massive_black_hole_event":
                            h_id = 9000 + len(self.hazards)
                            mbh = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=100.0, kind="massive_black_hole", damage=10.0)
                            mbh.target_radius = 500.0
                            setattr(mbh, "duration", 20.0)
                            setattr(mbh, "pull_strength", 100.0)
                            self.hazards.append(mbh)
                        elif event_type == "gravity_shift":

                            gw = Hazard(id=len(self.hazards) + random.randint(3000, 9999), x=self.width/2, y=self.height/2, radius=self.width/2, kind="gravity_well", damage=10.0)
                            setattr(gw, "duration", 10.0)
                            self.hazards.append(gw)

            new_craters: list[Hazard] = []
            # Slowly expand dynamic hazards and decay others like flares
            for h in self.hazards:
                ft = getattr(h, "frozen_timer", 0.0)
                if ft > 0:
                    h.frozen_timer = ft - delta
                    continue
                if getattr(h, "kind", "") == "flare":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                elif getattr(h, "kind", "") == "weather_scanner":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                elif getattr(h, "kind", "") == "orbital_strike":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.kind = "orbital_strike_active"
                            h.duration = 0.5
                            h.damage = 1000.0
                elif getattr(h, "kind", "") == "lightning_strike":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                elif getattr(h, "kind", "") == "bumper":
                    if hasattr(h, "target_hazard_id"):
                        target = next((x for x in self.hazards if x.id == h.target_hazard_id), None)
                        if target:
                            h.orbit_angle += getattr(h, "orbit_speed", 1.0) * delta
                            h.x = target.x + math.cos(h.orbit_angle) * getattr(h, "orbit_radius", 50.0)
                            h.y = target.y + math.sin(h.orbit_angle) * getattr(h, "orbit_radius", 50.0)
                    else:
                        if hasattr(h, "vx"):
                            h.x += h.vx * delta
                        if hasattr(h, "vy"):
                            h.y += h.vy * delta

                        if h.x < 0 or h.x > self.width:
                            if hasattr(h, "vx"): h.vx *= -1
                        if h.y < 0 or h.y > self.height:
                            if hasattr(h, "vy"): h.vy *= -1

                elif getattr(h, "kind", "") == "one_way_teleporter":
                    if hasattr(h, "change_timer"):
                        h.change_timer -= delta
                        if h.change_timer <= 0:
                            h.change_timer = 5.0
                            h.target_x, h.target_y = self.get_random_spawn_point(25.0)
                elif getattr(h, "kind", "") == "tornado":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                    if hasattr(h, "vx"):
                        h.x += h.vx * delta
                    if hasattr(h, "vy"):
                        h.y += h.vy * delta

                    if h.x < 0 or h.x > self.width:
                        if hasattr(h, "vx"): h.vx *= -1
                    if h.y < 0 or h.y > self.height:
                        if hasattr(h, "vy"): h.vy *= -1
                elif getattr(h, "kind", "") == "tornado_warning":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                            import random
                            tornado_id = 8000 + len(self.hazards) + random.randint(0, 1000)
                            tornado = Hazard(id=tornado_id, x=h.x, y=h.y, radius=h.radius, kind="tornado", damage=20.0)
                            setattr(tornado, 'duration', 5.0)
                            setattr(tornado, 'vx', random.uniform(-100.0, 100.0))
                            setattr(tornado, 'vy', random.uniform(-100.0, 100.0))
                            new_craters.append(tornado)
                elif getattr(h, "kind", "") == "fire_ring" or getattr(h, "kind", "") == "poison_nova":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                        else:
                            shrink_rate = getattr(h, "shrink_rate", 50.0)
                            h.radius = max(0.0, h.radius - shrink_rate * delta)
                elif getattr(h, "kind", "") == "orbital_strike_active":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                elif getattr(h, "kind", "") == "fire_zone":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                elif getattr(h, "kind", "") == "meteor":
                    if hasattr(h, "duration"):
                        h.duration -= delta
                        if h.duration <= 0:
                            h.active = False
                            import random
                            crater_id = 6000 + len(self.hazards) + len(new_craters) + random.randint(0, 1000)
                            crater = Hazard(id=crater_id, x=h.x, y=h.y, radius=h.radius * 1.5, kind="crater", damage=10.0)
                            new_craters.append(crater)

                            fire_id = 7000 + len(self.hazards) + len(new_craters) + random.randint(0, 1000)
                            fire_zone = Hazard(id=fire_id, x=h.x, y=h.y, radius=h.radius * 1.8, kind="fire_zone", damage=50.0)
                            setattr(fire_zone, "duration", 10.0)
                            new_craters.append(fire_zone)

                            # Destroy cover
                            try:
                                from arena.procedural_arena import Room # type: ignore
                                crater_size = h.radius * 3.0
                                new_room = Room(h.x - crater_size/2, h.y - crater_size/2, crater_size, crater_size)
                                self.rooms.append(new_room)
                            except ImportError:
                                pass
                elif h.id >= 1000 and hasattr(h, "target_radius"):
                    if h.radius < h.target_radius:
                        # Grow proportionally to reach target in roughly 600 ticks
                        h.radius += (h.target_radius / 600.0) * delta * 60.0 # Assuming 60 ticks per second
                        if h.radius > h.target_radius:
                            h.radius = h.target_radius

            # Remove inactive flares and meteors
            self.hazards = [h for h in self.hazards if getattr(h, "active", True)]
            self.hazards.extend(new_craters)

        if current_tick % 60 == 0:
            import random
            if random.random() < 0.1:
                x = random.uniform(50, self.width - 50)
                y = random.uniform(50, self.height - 50)
                h_id = 2500 + len(self.hazards) + random.randint(0, 1000)
                meteor = Hazard(id=h_id, x=x, y=y, radius=30.0, kind="meteor", damage=200.0)
                meteor.target_radius = 30.0
                setattr(meteor, "duration", 5.0)
                self.hazards.append(meteor)

        if current_tick % 600 == 0:
            import random

            # Clear old dynamic hazards
            self.hazards = [h for h in self.hazards if h.id < 1000]

            # Periodically trigger random arena-wide events
            event_type = random.choice(["meteor_shower", "gravity_shift", "moving_walls", "orbital_strike", "fire_ring", "anomaly_zone", "massive_black_hole_event", "none"])
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
                is_temporal_rift = random.random() < 0.1
                is_gravity_well = random.random() < 0.2
                is_reverse_gravity = random.random() < 0.1
                is_repulsion_field = random.random() < 0.1
                if random.random() < 0.1:
                    kind = "drone_item"
                    damage = 0.0
                elif random.random() < 0.1:
                    kind = "breakable_wall"
                    damage = 0.0
                elif random.random() < 0.1:
                    kind = "bounce_pad"
                    damage = 0.0
                elif random.random() < 0.1:
                    kind = "explosive_barrel"
                    damage = 0.0
                elif random.random() < 0.05:
                    kind = "stealth_drone_item"
                    damage = 0.0
                elif random.random() < 0.05:
                    kind = "shadow_booster"
                    damage = 0.0
                elif random.random() < 0.05:
                    kind = "decoy_item"
                    damage = 0.0
                elif random.random() < 0.05:
                    kind = "silence_booster"
                    damage = 0.0
                elif random.random() < 0.10:
                    kind = "placeable_trap_item"
                    damage = 0.0
                elif random.random() < 0.05:
                    kind = "vampiric_puddle"
                    damage = 5.0
                elif random.random() < 0.05:
                    kind = "exit_portal_item"
                    damage = 0.0
                elif random.random() < 0.05:
                    kind = "position_swap_item"
                    damage = 0.0
                elif random.random() < 0.05:
                    kind = "portal_gun_item"
                    damage = 0.0
                elif random.random() < 0.15:
                    kind = "quicksand"
                    damage = 10.0
                elif random.random() < 0.10:
                    kind = "sinkhole"
                    damage = 5.0
                else:
                    if is_temporal_rift:
                        kind = "temporal_rift"
                        damage = 0.0
                    elif is_reverse_gravity:
                        kind = "reverse_gravity"
                        damage = 0.0
                    elif is_repulsion_field:
                        kind = "repulsion_field"
                        damage = 0.0
                    elif is_gravity_well:
                        kind = "gravity_well"
                        damage = 0.0
                    else:
                        kind = "trap"
                        damage = 100.0
                new_hazard = Hazard(id=h_id, x=x, y=y, radius=10.0, kind=kind, damage=damage)
                if kind == "temporal_rift":
                    setattr(new_hazard, "time_scale", random.choice([0.5, 1.5, 2.0]))
                elif kind == "breakable_wall":
                    setattr(new_hazard, "hp", 100.0)
                new_hazard.target_radius = target_radius
                self.hazards.append(new_hazard)

        if current_tick % 10 == 0:
            self._update_danger_grid()


    def _trigger_event(self, event_type: str, current_tick: int):
        import random
        if event_type == "orbital_strike":
            h_id = 5000 + len(self.hazards)
            strike = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=400.0, kind="orbital_strike", damage=0.0)
            strike.target_radius = 400.0
            setattr(strike, "duration", 3.0)
            self.hazards.append(strike)
        elif event_type == "meteor_shower":
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
        elif event_type == "anomaly_zone":
            h_id = 6000 + len(self.hazards)
            zone = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=400.0, kind="anomaly_zone", damage=0.0)
            zone.target_radius = 400.0
            setattr(zone, "duration", 10.0)
            self.hazards.append(zone)
        elif event_type == "massive_black_hole_event":
            h_id = 9000 + len(self.hazards)
            mbh = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=100.0, kind="massive_black_hole", damage=10.0)
            mbh.target_radius = 500.0
            setattr(mbh, "duration", 20.0)
            setattr(mbh, "pull_strength", 100.0)
            self.hazards.append(mbh)
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
        elif event_type == "fire_ring":
            h_id = 4500 + len(self.hazards)
            # Starts as a large ring and shrinks to 0 over 10 seconds
            ring = Hazard(id=h_id, x=self.width/2, y=self.height/2, radius=500.0, kind="fire_ring", damage=40.0)
            ring.target_radius = 0.0
            setattr(ring, "duration", 10.0)
            setattr(ring, "shrink_rate", 500.0 / 10.0)
            self.hazards.append(ring)

    def _update_danger_grid(self):
        self.danger_grid.clear()

        # Check hazards
        for h in self.hazards:
            import math
            if math.isnan(h.x) or math.isnan(h.y) or math.isnan(h.radius):
                continue
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

class TimeDistortionArena(ProceduralArena):
    def generate(self):
        super().generate()
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central room
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400))

        # Add the chrono anomaly hazard in the center
        self.hazards.append(Hazard(0, cx, cy, 200.0, "chrono_anomaly", 0.0))
