import random

from arena.procedural_arena import ProceduralArena, Room, Hazard, Corridor

class CrossArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        self.rooms.append(Room(cx - 150, 50, 300, h - 100))
        self.rooms.append(Room(50, cy - 150, w - 100, 300))

class RingArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        self.rooms.append(Room(50, 50, w-100, 200))
        self.rooms.append(Room(50, h-250, w-100, 200))
        self.rooms.append(Room(50, 50, 200, h-100))
        self.rooms.append(Room(w-250, 50, 200, h-100))

class FourRoomsArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        rw, rh = 400, 400
        self.rooms.append(Room(50, 50, rw, rh))
        self.rooms.append(Room(w-50-rw, 50, rw, rh))
        self.rooms.append(Room(50, h-50-rh, rw, rh))
        self.rooms.append(Room(w-50-rw, h-50-rh, rw, rh))
        self.rooms.append(Room(50+rw, 50+rh/2-50, w-100-2*rw, 100))
        self.rooms.append(Room(50+rw, h-50-rh/2-50, w-100-2*rw, 100))
        self.rooms.append(Room(50+rw/2-50, 50+rh, 100, h-100-2*rh))
        self.rooms.append(Room(w-50-rw/2-50, 50+rh, 100, h-100-2*rh))

class GridArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cols, rows = 3, 3
        cell_w, cell_h = w / cols, h / rows
        rw, rh = cell_w * 0.6, cell_h * 0.6

        for i in range(cols):
            for j in range(rows):
                rx = i * cell_w + (cell_w - rw) / 2
                ry = j * cell_h + (cell_h - rh) / 2
                self.rooms.append(Room(rx, ry, rw, rh))

                if i < cols - 1:
                    self.rooms.append(Room(rx + rw, ry + rh/2 - 40, cell_w - rw, 80))
                if j < rows - 1:
                    self.rooms.append(Room(rx + rw/2 - 40, ry + rh, 80, cell_h - rh))

class LabyrinthArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        self.rooms.append(Room(50, 50, w-100, 150))
        self.rooms.append(Room(w-200, 50, 150, h-100))
        self.rooms.append(Room(50, h-200, w-100, 150))
        self.rooms.append(Room(50, 350, 150, h-550))
        self.rooms.append(Room(50, 350, w-350, 150))
        self.rooms.append(Room(w-500, 350, 150, h-700))
        self.rooms.append(Room(200, h-350, w-700, 150))

class HazardPitArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        self.rooms.append(Room(50, 50, w-100, h-100))
        cx, cy = w/2, h/2
        for i in range(12):
            kind = "lava" if i % 2 == 0 else "spikes"
            radius = 50.0
            damage = 50.0 if kind == "lava" else 20.0
            hx = cx + (random.uniform(-1, 1) * w * 0.3)
            hy = cy + (random.uniform(-1, 1) * h * 0.3)
            self.hazards.append(Hazard(id=i, x=hx, y=hy, radius=radius, kind=kind, damage=damage))

class DuelArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        size = 800
        self.rooms.append(Room(cx - size/2, cy - size/2, size, size))

class LongCorridorArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cy = h/2
        self.rooms.append(Room(50, cy - 200, w - 100, 400))

class ZigZagArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        segment_h = h / 5
        self.rooms.append(Room(50, 50, w-100, 200))
        self.rooms.append(Room(w-250, 250, 200, segment_h + 100))
        self.rooms.append(Room(50, 250 + segment_h, w-100, 200))
        self.rooms.append(Room(50, 450 + segment_h, 200, segment_h + 100))
        self.rooms.append(Room(50, 450 + 2*segment_h, w-100, 200))

class FortressArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))
        self.rooms.append(Room(50, 50, 200, 200))
        self.rooms.append(Room(w-250, 50, 200, 200))
        self.rooms.append(Room(50, h-250, 200, 200))
        self.rooms.append(Room(w-250, h-250, 200, 200))
        self.rooms.append(Room(250, 100, cx - 300 - 250 + 50, 100))
        self.rooms.append(Room(cx + 300 - 50, 100, w - 250 - (cx + 300) + 50, 100))
        self.rooms.append(Room(250, h-200, cx - 300 - 250 + 50, 100))
        self.rooms.append(Room(cx + 300 - 50, h-200, w - 250 - (cx + 300) + 50, 100))

class SplitArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cy = h/2
        self.rooms.append(Room(50, 50, w/2 - 150, h - 100))
        self.rooms.append(Room(w/2 + 100, 50, w/2 - 150, h - 100))
        self.rooms.append(Room(w/2 - 50, cy - 100, 100, 200))


class FlankArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central battle room
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400))

        # Flanking side rooms
        self.rooms.append(Room(50, cy - 100, 150, 200)) # Left flank
        self.rooms.append(Room(w - 200, cy - 100, 150, 200)) # Right flank
        self.rooms.append(Room(cx - 100, 50, 200, 150)) # Top flank
        self.rooms.append(Room(cx - 100, h - 200, 200, 150)) # Bottom flank

        # Corridors connecting flanks
        self.corridors.append(Corridor(200, cy - 50, cx - 400, 100)) # Left to center
        self.corridors.append(Corridor(cx + 200, cy - 50, w - cx - 400, 100)) # Center to right
        self.corridors.append(Corridor(cx - 50, 200, 100, cy - 400)) # Top to center
        self.corridors.append(Corridor(cx - 50, cy + 200, 100, h - cy - 400)) # Center to bottom

class ChokePointArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx = w/2
        self.rooms.append(Room(50, 50, w - 100, h/2 - 150))
        self.rooms.append(Room(50, h/2 + 100, w - 100, h/2 - 150))
        self.rooms.append(Room(cx - 100, h/2 - 50, 200, 150))

class UseShieldArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central large room
        self.rooms.append(Room(cx - 400, cy - 400, 800, 800))

        # Create a dense ring of hazards around the center
        import math
        num_hazards = 24
        radius = 250
        for i in range(num_hazards):
            angle = 2 * math.pi * i / num_hazards
            hx = cx + radius * math.cos(angle)
            hy = cy + radius * math.sin(angle)
            kind = "spikes" if i % 2 == 0 else "lava"
            damage = 20.0 if kind == "spikes" else 40.0
            self.hazards.append(Hazard(id=i, x=hx, y=hy, radius=40.0, kind=kind, damage=damage))

class RetreatToAllyArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central danger zone with hazards
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400))

        # Two ally bases (safe zones)
        self.rooms.append(Room(50, 50, 200, 200))
        self.rooms.append(Room(w - 250, h - 250, 200, 200))

        # Corridors connecting bases to central zone
        self.corridors.append(Corridor(150, 250, 100, cy - 250))
        self.corridors.append(Corridor(250, 150, cx - 250, 100))

        self.corridors.append(Corridor(w - 250, cy, 100, h - cy - 250))
        self.corridors.append(Corridor(cx, h - 250, w - cx - 250, 100))

        # Hazards in central zone to encourage retreat
        import math
        for i in range(8):
            angle = 2 * math.pi * i / 8
            hx = cx + 150 * math.cos(angle)
            hy = cy + 150 * math.sin(angle)
            self.hazards.append(Hazard(id=i, x=hx, y=hy, radius=30.0, kind="lava", damage=30.0))

class BuffAllyArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central battle room
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # Four team bases
        self.rooms.append(Room(cx - 100, 50, 200, 200)) # Top
        self.rooms.append(Room(cx - 100, h - 250, 200, 200)) # Bottom
        self.rooms.append(Room(50, cy - 100, 200, 200)) # Left
        self.rooms.append(Room(w - 250, cy - 100, 200, 200)) # Right

        # Connect to center
        self.corridors.append(Corridor(cx - 50, 250, 100, cy - 300 - 250)) # Top to center
        self.corridors.append(Corridor(cx - 50, cy + 300, 100, h - 250 - (cy + 300))) # Bottom to center
        self.corridors.append(Corridor(250, cy - 50, cx - 300 - 250, 100)) # Left to center
        self.corridors.append(Corridor(cx + 300, cy - 50, w - 250 - (cx + 300), 100)) # Right to center

class AggressiveChaseArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central medium room
        center_size = 300
        self.rooms.append(Room(cx - center_size/2, cy - center_size/2, center_size, center_size))

        # 4 dead-end rooms (narrower)
        room_size = 150
        self.rooms.append(Room(50, cy - room_size/2, room_size, room_size)) # Left
        self.rooms.append(Room(w - 50 - room_size, cy - room_size/2, room_size, room_size)) # Right
        self.rooms.append(Room(cx - room_size/2, 50, room_size, room_size)) # Top
        self.rooms.append(Room(cx - room_size/2, h - 50 - room_size, room_size, room_size)) # Bottom

        # Corridors connecting dead-ends to center
        # These are long and narrow, making escaping hard once cornered
        self.corridors.append(Corridor(50 + room_size, cy - 40, cx - center_size/2 - (50 + room_size), 80)) # Left
        self.corridors.append(Corridor(cx + center_size/2, cy - 40, (w - 50 - room_size) - (cx + center_size/2), 80)) # Right
        self.corridors.append(Corridor(cx - 40, 50 + room_size, 80, cy - center_size/2 - (50 + room_size))) # Top
        self.corridors.append(Corridor(cx - 40, cy + center_size/2, 80, (h - 50 - room_size) - (cy + center_size/2))) # Bottom

class ComebacksArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central battle room
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # Four corner spawn rooms
        self.rooms.append(Room(50, 50, 200, 200)) # Top-Left
        self.rooms.append(Room(w - 250, 50, 200, 200)) # Top-Right
        self.rooms.append(Room(50, h - 250, 200, 200)) # Bottom-Left
        self.rooms.append(Room(w - 250, h - 250, 200, 200)) # Bottom-Right

        # Corridors connecting corners to center (with safe overlaps)
        # Top-Left to Center
        self.corridors.append(Corridor(100, 200, 100, cy - 400))
        self.corridors.append(Corridor(100, cy - 300, cx - 300, 100))
        # Top-Right to Center
        self.corridors.append(Corridor(w - 200, 200, 100, cy - 400))
        self.corridors.append(Corridor(cx + 200, cy - 300, w - cx - 300, 100))
        # Bottom-Left to Center
        self.corridors.append(Corridor(100, cy + 200, 100, h - cy - 400))
        self.corridors.append(Corridor(100, cy + 200, cx - 300, 100))
        # Bottom-Right to Center
        self.corridors.append(Corridor(w - 200, cy + 200, 100, h - cy - 400))
        self.corridors.append(Corridor(cx + 200, cy + 200, w - cx - 300, 100))

        # 16 hazards forming a ring inside the central room
        import math
        for i in range(16):
            angle = 2 * math.pi * i / 16
            hx = cx + 200 * math.cos(angle)
            hy = cy + 200 * math.sin(angle)
            self.hazards.append(Hazard(id=i, x=hx, y=hy, radius=30.0, kind="lava", damage=40.0))


class FunnyFailsArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 4 small corner rooms
        room_size = 150
        self.rooms.append(Room(50, 50, room_size, room_size)) # Top-Left
        self.rooms.append(Room(w - 50 - room_size, 50, room_size, room_size)) # Top-Right
        self.rooms.append(Room(50, h - 50 - room_size, room_size, room_size)) # Bottom-Left
        self.rooms.append(Room(w - 50 - room_size, h - 50 - room_size, room_size, room_size)) # Bottom-Right

        # Narrow bridges between them to make falling easy
        bridge_width = 80
        self.corridors.append(Corridor(50 + room_size, 50 + (room_size - bridge_width)/2, w - 100 - 2*room_size, bridge_width)) # Top bridge
        self.corridors.append(Corridor(50 + room_size, h - 50 - room_size + (room_size - bridge_width)/2, w - 100 - 2*room_size, bridge_width)) # Bottom bridge
        self.corridors.append(Corridor(50 + (room_size - bridge_width)/2, 50 + room_size, bridge_width, h - 100 - 2*room_size)) # Left bridge
        self.corridors.append(Corridor(w - 50 - room_size + (room_size - bridge_width)/2, 50 + room_size, bridge_width, h - 100 - 2*room_size)) # Right bridge

        # Cross bridges in the middle
        self.corridors.append(Corridor(cx - bridge_width/2, 50 + room_size, bridge_width, h - 100 - 2*room_size)) # Vertical middle bridge
        self.corridors.append(Corridor(50 + room_size, cy - bridge_width/2, w - 100 - 2*room_size, bridge_width)) # Horizontal middle bridge

        # Center small room (intersection)
        self.rooms.append(Room(cx - 100, cy - 100, 200, 200))

        # Huge amounts of hazards in the gaps
        import math
        # Ring of lava around the center room
        num_hazards = 12
        radius = 250
        for i in range(num_hazards):
            angle = 2 * math.pi * i / num_hazards
            hx = cx + radius * math.cos(angle)
            hy = cy + radius * math.sin(angle)
            self.hazards.append(Hazard(id=i, x=hx, y=hy, radius=50.0, kind="lava", damage=50.0))

        # Add bounce pads / spikes to push into the lava
        # (Using spikes since they exist and deal damage, or we can use generic hazards)
        for i in range(4):
            # Place 4 large spike balls near the outer corners
            hx = cx + 500 * math.cos(2 * math.pi * i / 4 + math.pi/4)
            hy = cy + 500 * math.sin(2 * math.pi * i / 4 + math.pi/4)
            self.hazards.append(Hazard(id=i+100, x=hx, y=hy, radius=70.0, kind="spikes", damage=30.0))

ARENAS = {
    "funny_fails": FunnyFailsArena,
    "buff_ally": BuffAllyArena,
    "retreat_to_ally": RetreatToAllyArena,
    "procedural": ProceduralArena,
    "cross": CrossArena,
    "ring": RingArena,
    "four_rooms": FourRoomsArena,
    "grid": GridArena,
    "labyrinth": LabyrinthArena,
    "hazard_pit": HazardPitArena,
    "duel": DuelArena,
    "long_corridor": LongCorridorArena,
    "zigzag": ZigZagArena,
    "fortress": FortressArena,
    "split": SplitArena,
    "flank": FlankArena,
    "choke_point": ChokePointArena,
    "use_shield": UseShieldArena,
    "aggressive_chase": AggressiveChaseArena,
    "comebacks": ComebacksArena
}

def get_arena(arena_type: str, arena_size: float = 2000.0, seed: int | None = None) -> ProceduralArena:
    arena_class = ARENAS.get(arena_type, ProceduralArena)
    if arena_class == ProceduralArena:
        return ProceduralArena(arena_size=arena_size, num_rooms=5, seed=seed)
    return arena_class(arena_size=arena_size, seed=seed)
