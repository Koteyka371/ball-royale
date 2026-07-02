from arena.procedural_arena import Hazard
import random

from arena.procedural_arena import ProceduralArena, Room, Hazard, Corridor
from arena.procedural_arena import TimeDistortionArena

class SwapPortal(Hazard):
    def __init__(self, id: int, x: float, y: float, radius: float, target_x: float, target_y: float, pair_id: int):
        super().__init__(id, x, y, radius, "swap_portal", 0.0)
        self.target_x = target_x
        self.target_y = target_y
        self.pair_id = pair_id

class Portal(Hazard):
    def __init__(self, id: int, x: float, y: float, radius: float, target_x: float, target_y: float):
        super().__init__(id, x, y, radius, "portal", 0.0)
        self.target_x = target_x
        self.target_y = target_y

class PortalArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        self.rooms.append(Room(50, 50, 200, 200))
        self.rooms.append(Room(w-250, 50, 200, 200))
        self.rooms.append(Room(50, h-250, 200, 200))
        self.rooms.append(Room(w-250, h-250, 200, 200))
        self.rooms.append(Room(cx-100, cy-100, 200, 200))

        # Paired portals
        self.hazards.append(Portal(id=0, x=150.0, y=150.0, radius=30.0, target_x=w-150.0, target_y=h-150.0))
        self.hazards.append(Portal(id=1, x=w-150.0, y=h-150.0, radius=30.0, target_x=150.0, target_y=150.0))

        self.hazards.append(Portal(id=2, x=w-150.0, y=150.0, radius=30.0, target_x=150.0, target_y=h-150.0))
        self.hazards.append(Portal(id=3, x=150.0, y=h-150.0, radius=30.0, target_x=w-150.0, target_y=150.0))

class ConveyorBelt(Hazard):
    def __init__(self, id: int, x: float, y: float, radius: float, damage: float, direction_vector: tuple[float, float], speed_magnitude: float):
        super().__init__(id, x, y, radius, "conveyor_belt", damage)
        self.direction_vector = direction_vector
        self.speed_magnitude = speed_magnitude

class FactoryArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()

        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central assembly line
        self.rooms.append(Room(w * 0.1, h * 0.3, w * 0.8, h * 0.4))

        # Top and bottom side rooms
        self.rooms.append(Room(w * 0.3, h * 0.1, w * 0.4, h * 0.2))
        self.rooms.append(Room(w * 0.3, h * 0.7, w * 0.4, h * 0.2))

        # Corridors connecting side rooms to main assembly
        self.corridors.append(Corridor(x=cx, y=h * 0.2, width=100, height=h * 0.2))
        self.corridors.append(Corridor(x=cx, y=h * 0.6, width=100, height=h * 0.2))

        # Add conveyor belts in a loop or lines

        # Top line moving right
        self.hazards.append(ConveyorBelt(id=0, x=w*0.3, y=h*0.4, radius=60.0, damage=0.0, direction_vector=(1.0, 0.0), speed_magnitude=200.0))
        self.hazards.append(ConveyorBelt(id=1, x=w*0.5, y=h*0.4, radius=60.0, damage=0.0, direction_vector=(1.0, 0.0), speed_magnitude=200.0))
        self.hazards.append(ConveyorBelt(id=2, x=w*0.7, y=h*0.4, radius=60.0, damage=0.0, direction_vector=(1.0, 0.0), speed_magnitude=200.0))

        # Bottom line moving left
        self.hazards.append(ConveyorBelt(id=3, x=w*0.7, y=h*0.6, radius=60.0, damage=0.0, direction_vector=(-1.0, 0.0), speed_magnitude=200.0))
        self.hazards.append(ConveyorBelt(id=4, x=w*0.5, y=h*0.6, radius=60.0, damage=0.0, direction_vector=(-1.0, 0.0), speed_magnitude=200.0))
        self.hazards.append(ConveyorBelt(id=5, x=w*0.3, y=h*0.6, radius=60.0, damage=0.0, direction_vector=(-1.0, 0.0), speed_magnitude=200.0))

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
            if i % 3 == 0:
                kind = "lava"
            elif i % 3 == 1:
                kind = "spikes"
            else:
                kind = "explosive_barrel"
            radius = 50.0 if kind != "explosive_barrel" else 25.0
            if kind == "explosive_barrel":
                damage = 100.0
            elif kind == "lava":
                damage = 50.0
            else:
                damage = 20.0
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

class GroupAttackArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central battle room (large for group battles)
        self.rooms.append(Room(cx - 400, cy - 400, 800, 800))

        # 4 Staging rooms in corners
        self.rooms.append(Room(50, 50, 300, 300)) # Top-Left
        self.rooms.append(Room(w - 350, 50, 300, 300)) # Top-Right
        self.rooms.append(Room(50, h - 350, 300, 300)) # Bottom-Left
        self.rooms.append(Room(w - 350, h - 350, 300, 300)) # Bottom-Right

        # Corridors connecting staging rooms to the central room
        # Top-Left to Center
        self.corridors.append(Corridor(200, 300, 100, cy - 400 - 300 + 50))
        self.corridors.append(Corridor(200, cy - 400, cx - 400 - 200 + 50, 100))

        # Top-Right to Center
        self.corridors.append(Corridor(w - 300, 300, 100, cy - 400 - 300 + 50))
        self.corridors.append(Corridor(cx + 400 - 50, cy - 400, w - 300 - cx - 400 + 100, 100))

        # Bottom-Left to Center
        self.corridors.append(Corridor(200, cy + 400 - 50, 100, h - 300 - cy - 400 + 100))
        self.corridors.append(Corridor(200, h - 400, cx - 400 - 200 + 50, 100))

        # Bottom-Right to Center
        self.corridors.append(Corridor(w - 300, cy + 400 - 50, 100, h - 300 - cy - 400 + 100))
        self.corridors.append(Corridor(cx + 400 - 50, h - 400, w - 300 - cx - 400 + 100, 100))

        # Hazards in the center to force splitting
        self.hazards.append(Hazard(id=1, x=cx - 150, y=cy - 150, radius=50, kind="lava", damage=10.0))
        self.hazards.append(Hazard(id=2, x=cx + 150, y=cy - 150, radius=50, kind="lava", damage=10.0))
        self.hazards.append(Hazard(id=3, x=cx - 150, y=cy + 150, radius=50, kind="lava", damage=10.0))
        self.hazards.append(Hazard(id=4, x=cx + 150, y=cy + 150, radius=50, kind="lava", damage=10.0))

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

class CircleStrafeArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        rw, rh = 300, 300
        # 4 rooms forming a large square with a central hole
        self.rooms.append(Room(cx - 400, cy - 400, rw, rh)) # Top-Left
        self.rooms.append(Room(cx + 100, cy - 400, rw, rh)) # Top-Right
        self.rooms.append(Room(cx - 400, cy + 100, rw, rh)) # Bottom-Left
        self.rooms.append(Room(cx + 100, cy + 100, rw, rh)) # Bottom-Right

        # 4 corridors connecting them (loop)
        self.corridors.append(Corridor(cx - 150, cy - 350, 300, 200)) # Top
        self.corridors.append(Corridor(cx - 150, cy + 150, 300, 200)) # Bottom
        self.corridors.append(Corridor(cx - 350, cy - 150, 200, 300)) # Left
        self.corridors.append(Corridor(cx + 150, cy - 150, 200, 300)) # Right

class Finals1v1Arena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))
        self.rooms.append(Room(100, cy - 100, 200, 200))
        self.rooms.append(Room(w - 300, cy - 100, 200, 200))

        self.corridors.append(Corridor(250, cy - 50, 500, 100))
        self.corridors.append(Corridor(cx + 250, cy - 50, 500, 100))

        self.hazards.append(Hazard(id=0, x=cx - 200, y=cy - 200, radius=30.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=1, x=cx + 200, y=cy - 200, radius=30.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=2, x=cx - 200, y=cy + 200, radius=30.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=3, x=cx + 200, y=cy + 200, radius=30.0, kind="lava", damage=20.0))

class EpicKillsArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 3 rooms: large central room and two sniper nests
        self.rooms.append(Room(cx - 400, cy - 400, 800, 800))
        self.rooms.append(Room(cx - 700, cy - 100, 200, 200))
        self.rooms.append(Room(cx + 500, cy - 100, 200, 200))

        # 2 corridors bridging the gaps
        self.corridors.append(Corridor(cx - 550, cy - 50, 200, 100))
        self.corridors.append(Corridor(cx + 350, cy - 50, 200, 100))

        # A huge pit of hazards in the middle (8 hazards forming a circle)
        import math
        for i in range(8):
            angle = 2 * math.pi * i / 8
            hx = cx + 200 * math.cos(angle)
            hy = cy + 200 * math.sin(angle)
            self.hazards.append(Hazard(id=i, x=hx, y=hy, radius=100.0, kind="lava", damage=50.0))

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

class KiteArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 4 large corner rooms
        self.rooms.append(Room(100, 100, 400, 400)) # Top-Left
        self.rooms.append(Room(w - 500, 100, 400, 400)) # Top-Right
        self.rooms.append(Room(100, h - 500, 400, 400)) # Bottom-Left
        self.rooms.append(Room(w - 500, h - 500, 400, 400)) # Bottom-Right

        # Long corridors connecting them, forming a giant kiting loop
        # Top corridor
        self.corridors.append(Corridor(300, 200, w - 600, 200))
        # Bottom corridor
        self.corridors.append(Corridor(300, h - 400, w - 600, 200))
        # Left corridor
        self.corridors.append(Corridor(200, 300, 200, h - 600))
        # Right corridor
        self.corridors.append(Corridor(w - 400, 300, 200, h - 600))

        # Add a few central hazards inside the corridors to make kiting interesting
        self.hazards.append(Hazard(id=0, x=cx, y=300, radius=50.0, kind="lava", damage=10.0))
        self.hazards.append(Hazard(id=1, x=cx, y=h-300, radius=50.0, kind="lava", damage=10.0))
        self.hazards.append(Hazard(id=2, x=300, y=cy, radius=50.0, kind="lava", damage=10.0))
        self.hazards.append(Hazard(id=3, x=w-300, y=cy, radius=50.0, kind="lava", damage=10.0))


class AvoidTrapArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        self.rooms.append(Room(100, 100, 200, 200))
        self.rooms.append(Room(600, 100, 200, 200))
        self.rooms.append(Room(350, 400, 200, 200))
        self.corridors.append(Corridor(300, 150, 300, 100))
        self.corridors.append(Corridor(150, 300, 100, 200))
        self.corridors.append(Corridor(150, 450, 200, 100))
        self.hazards.append(Hazard(0, 400, 200, 30, 'spikes', 20.0))
        self.hazards.append(Hazard(1, 450, 200, 30, 'lava', 50.0))
        self.hazards.append(Hazard(2, 500, 200, 30, 'spikes', 20.0))
        self.hazards.append(Hazard(3, 200, 400, 30, 'lava', 50.0))
        self.hazards.append(Hazard(4, 450, 500, 40, 'lava', 50.0))

class RepositionArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central room
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400))
        # Top room
        self.rooms.append(Room(cx - 100, 100, 200, 200))
        # Bottom room
        self.rooms.append(Room(cx - 100, h - 300, 200, 200))
        # Left room
        self.rooms.append(Room(100, cy - 100, 200, 200))
        # Right room
        self.rooms.append(Room(w - 300, cy - 100, 200, 200))

        # Top corridor
        self.corridors.append(Corridor(cx - 50, 300, 100, cy - 200 - 300))
        # Bottom corridor
        self.corridors.append(Corridor(cx - 50, cy + 200, 100, h - 300 - (cy + 200)))
        # Left corridor
        self.corridors.append(Corridor(300, cy - 50, cx - 200 - 300, 100))
        # Right corridor
        self.corridors.append(Corridor(cx + 200, cy - 50, w - 300 - (cx + 200), 100))

        # Central hazard
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=100.0, kind="lava", damage=15.0))


class AICommentaryArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central battle room for commentary
        self.rooms.append(Room(cx - 400, cy - 400, 800, 800))

        # 4 Viewing/Spawn rooms
        self.rooms.append(Room(100, 100, 200, 200))
        self.rooms.append(Room(w - 300, 100, 200, 200))
        self.rooms.append(Room(100, h - 300, 200, 200))
        self.rooms.append(Room(w - 300, h - 300, 200, 200))

        # Connecting corridors (bridging the gaps correctly)
        # Top-Left (200, 300) to Central (cx - 400 = 600, cy - 400 = 600)
        self.corridors.append(Corridor(200, 200, cx - 600, 100)) # horizontal part
        self.corridors.append(Corridor(cx - 450, 200, 100, cy - 600)) # vertical part

        # Top-Right (w-300 = 1700, 300) to Central (cx+400=1400, 600)
        self.corridors.append(Corridor(cx + 400, 200, cx - 600, 100)) # horizontal part
        self.corridors.append(Corridor(cx + 350, 200, 100, cy - 600)) # vertical part

        # Bottom-Left (200, h-300=1700) to Central (600, cy+400=1400)
        self.corridors.append(Corridor(200, cy + 350, cx - 600, 100)) # horizontal part
        self.corridors.append(Corridor(cx - 450, cy + 350, 100, cy - 600)) # vertical part

        # Bottom-Right (1700, 1700) to Central (1400, 1400)
        self.corridors.append(Corridor(cx + 400, cy + 350, cx - 600, 100)) # horizontal part
        self.corridors.append(Corridor(cx + 350, cy + 350, 100, cy - 600)) # vertical part

        # Central hazards for exciting moments
        self.hazards.append(Hazard(id=0, x=cx - 150, y=cy - 150, radius=50, kind="lava", damage=20))
        self.hazards.append(Hazard(id=1, x=cx + 150, y=cy + 150, radius=50, kind="lava", damage=20))

class BallRelationshipsArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central meeting room
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # 4 Spawn rooms
        self.rooms.append(Room(50, 50, 300, 300))
        self.rooms.append(Room(w - 350, 50, 300, 300))
        self.rooms.append(Room(50, h - 350, 300, 300))
        self.rooms.append(Room(w - 350, h - 350, 300, 300))

        # Connecting corridors
        # Top-Left to Center
        self.corridors.append(Corridor(150, 350, 100, cy - 650))
        self.corridors.append(Corridor(150, cy - 300, cx - 450, 100))
        # Top-Right to Center
        self.corridors.append(Corridor(w - 250, 350, 100, cy - 650))
        self.corridors.append(Corridor(cx + 300, cy - 300, w - cx - 550, 100))
        # Bottom-Left to Center
        self.corridors.append(Corridor(150, cy + 200, 100, h - cy - 550))
        self.corridors.append(Corridor(150, cy + 200, cx - 450, 100))
        # Bottom-Right to Center
        self.corridors.append(Corridor(w - 250, cy + 200, 100, h - cy - 550))
        self.corridors.append(Corridor(cx + 300, cy + 200, w - cx - 550, 100))

        # 4 central hazards
        self.hazards.append(Hazard(id=0, x=cx - 150, y=cy - 150, radius=30.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=1, x=cx + 150, y=cy - 150, radius=30.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=2, x=cx - 150, y=cy + 150, radius=30.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=3, x=cx + 150, y=cy + 150, radius=30.0, kind="lava", damage=20.0))

class CollectBoosterArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 9 rooms in a 3x3 grid
        # Top row
        self.rooms.append(Room(cx - 400, cy - 400, 200, 200))
        self.rooms.append(Room(cx - 100, cy - 400, 200, 200))
        self.rooms.append(Room(cx + 200, cy - 400, 200, 200))
        # Middle row
        self.rooms.append(Room(cx - 400, cy - 100, 200, 200))
        self.rooms.append(Room(cx - 100, cy - 100, 200, 200))
        self.rooms.append(Room(cx + 200, cy - 100, 200, 200))
        # Bottom row
        self.rooms.append(Room(cx - 400, cy + 200, 200, 200))
        self.rooms.append(Room(cx - 100, cy + 200, 200, 200))
        self.rooms.append(Room(cx + 200, cy + 200, 200, 200))

        # 12 corridors connecting them
        # Horizontal corridors
        self.corridors.append(Corridor(cx - 200, cy - 350, 100, 100))
        self.corridors.append(Corridor(cx + 100, cy - 350, 100, 100))
        self.corridors.append(Corridor(cx - 200, cy - 50, 100, 100))
        self.corridors.append(Corridor(cx + 100, cy - 50, 100, 100))
        self.corridors.append(Corridor(cx - 200, cy + 250, 100, 100))
        self.corridors.append(Corridor(cx + 100, cy + 250, 100, 100))

        # Vertical corridors
        self.corridors.append(Corridor(cx - 350, cy - 200, 100, 100))
        self.corridors.append(Corridor(cx - 50, cy - 200, 100, 100))
        self.corridors.append(Corridor(cx + 250, cy - 200, 100, 100))
        self.corridors.append(Corridor(cx - 350, cy + 100, 100, 100))
        self.corridors.append(Corridor(cx - 50, cy + 100, 100, 100))
        self.corridors.append(Corridor(cx + 250, cy + 100, 100, 100))

        # Central hazard
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=40.0, kind="lava", damage=25.0))



class ClutchPlaysArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # A very dangerous central room with lots of hazards
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # Safe zones in the corners
        self.rooms.append(Room(50, 50, 200, 200))
        self.rooms.append(Room(w - 250, 50, 200, 200))
        self.rooms.append(Room(50, h - 250, 200, 200))
        self.rooms.append(Room(w - 250, h - 250, 200, 200))

        # Corridors connecting safe zones to center (with proper perpendicular overlaps)
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

        # A lot of hazards in the center
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=100.0, kind="lava", damage=30.0))
        self.hazards.append(Hazard(id=1, x=cx - 150, y=cy - 150, radius=50.0, kind="spikes", damage=20.0))
        self.hazards.append(Hazard(id=2, x=cx + 150, y=cy - 150, radius=50.0, kind="spikes", damage=20.0))
        self.hazards.append(Hazard(id=3, x=cx - 150, y=cy + 150, radius=50.0, kind="spikes", damage=20.0))
        self.hazards.append(Hazard(id=4, x=cx + 150, y=cy + 150, radius=50.0, kind="spikes", damage=20.0))


class SwarmIntelligenceArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 3x3 grid of 9 rooms, 400x400 each
        self.rooms.append(Room(cx - 700, cy - 700, 400, 400))
        self.rooms.append(Room(cx - 200, cy - 700, 400, 400))
        self.rooms.append(Room(cx + 300, cy - 700, 400, 400))
        self.rooms.append(Room(cx - 700, cy - 200, 400, 400))
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400))
        self.rooms.append(Room(cx + 300, cy - 200, 400, 400))
        self.rooms.append(Room(cx - 700, cy + 300, 400, 400))
        self.rooms.append(Room(cx - 200, cy + 300, 400, 400))
        self.rooms.append(Room(cx + 300, cy + 300, 400, 400))

        # 12 connecting corridors, 300x300 to overlap 50px
        # Horizontal
        self.corridors.append(Corridor(cx - 350, cy - 650, 200, 300))
        self.corridors.append(Corridor(cx + 150, cy - 650, 200, 300))
        self.corridors.append(Corridor(cx - 350, cy - 150, 200, 300))
        self.corridors.append(Corridor(cx + 150, cy - 150, 200, 300))
        self.corridors.append(Corridor(cx - 350, cy + 350, 200, 300))
        self.corridors.append(Corridor(cx + 150, cy + 350, 200, 300))

        # Vertical
        self.corridors.append(Corridor(cx - 650, cy - 350, 300, 200))
        self.corridors.append(Corridor(cx - 150, cy - 350, 300, 200))
        self.corridors.append(Corridor(cx + 350, cy - 350, 300, 200))
        self.corridors.append(Corridor(cx - 650, cy + 150, 300, 200))
        self.corridors.append(Corridor(cx - 150, cy + 150, 300, 200))
        self.corridors.append(Corridor(cx + 350, cy + 150, 300, 200))

        # 4 central hazards
        self.hazards.append(Hazard(id=0, x=cx - 100, y=cy - 100, radius=40.0, kind="spikes", damage=25.0))
        self.hazards.append(Hazard(id=1, x=cx + 100, y=cy - 100, radius=40.0, kind="spikes", damage=25.0))
        self.hazards.append(Hazard(id=2, x=cx - 100, y=cy + 100, radius=40.0, kind="spikes", damage=25.0))
        self.hazards.append(Hazard(id=3, x=cx + 100, y=cy + 100, radius=40.0, kind="spikes", damage=25.0))

class TeamWipesArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        self.rooms.append(Room(100.0, cy - 300.0, 400.0, 600.0))
        self.rooms.append(Room(w - 500.0, cy - 300.0, 400.0, 600.0))
        self.rooms.append(Room(cx - 400.0, cy - 400.0, 800.0, 800.0))

        self.corridors.append(Corridor(450.0, cy - 200.0, 200.0, 400.0))
        self.corridors.append(Corridor(w - 650.0, cy - 200.0, 200.0, 400.0))

        self.hazards.append(Hazard(id=0, x=cx - 200.0, y=cy - 200.0, radius=40.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=1, x=cx + 200.0, y=cy - 200.0, radius=40.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=2, x=cx - 200.0, y=cy + 200.0, radius=40.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=3, x=cx + 200.0, y=cy + 200.0, radius=40.0, kind="lava", damage=20.0))


class AmbushArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 1 central combat zone
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # 4 hiding spots (alcoves) in the corners
        self.rooms.append(Room(50, 50, 150, 150))
        self.rooms.append(Room(w - 200, 50, 150, 150))
        self.rooms.append(Room(50, h - 200, 150, 150))
        self.rooms.append(Room(w - 200, h - 200, 150, 150))

        # Narrow corridors connecting hiding spots to the center
        self.corridors.append(Corridor(100, 200, 50, cy - 400)) # Top-Left
        self.corridors.append(Corridor(100, cy - 300, cx - 300, 50))

        self.corridors.append(Corridor(w - 150, 200, 50, cy - 400)) # Top-Right
        self.corridors.append(Corridor(cx + 300, cy - 300, w - cx - 300, 50))

        self.corridors.append(Corridor(100, cy + 250, 50, h - cy - 400)) # Bottom-Left
        self.corridors.append(Corridor(100, cy + 250, cx - 300, 50))

        self.corridors.append(Corridor(w - 150, cy + 250, 50, h - cy - 400)) # Bottom-Right
        self.corridors.append(Corridor(cx + 300, cy + 250, w - cx - 300, 50))

        # 1 central hazard to discourage staying in the open
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=80.0, kind="lava", damage=20.0))


class MetaEvolutionArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Center Room
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400))
        # Top Room
        self.rooms.append(Room(cx - 150, cy - 700, 300, 300))
        # Bottom Left
        self.rooms.append(Room(cx - 700, cy + 100, 300, 300))
        # Bottom Right
        self.rooms.append(Room(cx + 400, cy + 100, 300, 300))

        # Corridors
        self.corridors.append(Corridor(cx - 50, cy - 400, 100, 200))
        self.corridors.append(Corridor(cx - 400, cy + 150, 200, 100))
        self.corridors.append(Corridor(cx + 200, cy + 150, 200, 100))

        # Hazards
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=30.0, kind="lava", damage=10.0))
        self.hazards.append(Hazard(id=1, x=cx - 550, y=cy + 250, radius=80.0, kind="lava", damage=40.0))
        self.hazards.append(Hazard(id=2, x=cx + 550, y=cy + 250, radius=40.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=3, x=cx + 500, y=cy + 180, radius=20.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=4, x=cx + 600, y=cy + 320, radius=20.0, kind="spikes", damage=30.0))


class BodyBlockArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # A central room where the main engagement happens
        self.rooms.append(Room(cx - 400, cy - 200, 800, 400))

        # Two smaller rooms representing "ally base" and "enemy spawn"
        self.rooms.append(Room(cx - 700, cy - 100, 200, 200)) # Left ally base
        self.rooms.append(Room(cx + 500, cy - 100, 200, 200)) # Right enemy base

        # Narrow choke point corridors connecting the bases to the center room to force body blocking
        self.corridors.append(Corridor(cx - 500, cy - 50, 100, 100))
        self.corridors.append(Corridor(cx + 400, cy - 50, 100, 100))

        # A central hazard to force players into tighter chokes
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=50.0, kind="lava", damage=25.0))

class PhysicsChainReactionsArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central hub for bounces
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # 4 outer bounce zones
        self.rooms.append(Room(cx - 700, cy - 200, 200, 400)) # Left
        self.rooms.append(Room(cx + 500, cy - 200, 200, 400)) # Right
        self.rooms.append(Room(cx - 200, cy - 700, 400, 200)) # Top
        self.rooms.append(Room(cx - 200, cy + 500, 400, 200)) # Bottom

        # Corridors with 50px overlap
        self.corridors.append(Corridor(cx - 550, cy - 100, 300, 200)) # Left to Center
        self.corridors.append(Corridor(cx + 250, cy - 100, 300, 200)) # Center to Right
        self.corridors.append(Corridor(cx - 100, cy - 550, 200, 300)) # Top to Center
        self.corridors.append(Corridor(cx - 100, cy + 250, 200, 300)) # Center to Bottom

        # Hazards in center to force chaining
        self.hazards.append(Hazard(id=0, x=cx - 150, y=cy - 150, radius=50.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=1, x=cx + 150, y=cy - 150, radius=50.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=2, x=cx - 150, y=cy + 150, radius=50.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=3, x=cx + 150, y=cy + 150, radius=50.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=4, x=cx, y=cy, radius=80.0, kind="lava", damage=20.0))


class EmotionalContagionArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 1 central contagion room
        self.rooms.append(Room(cx - 300.0, cy - 300.0, 600.0, 600.0))

        # 4 quarantine rooms
        self.rooms.append(Room(100.0, 100.0, 300.0, 300.0))
        self.rooms.append(Room(w - 400.0, 100.0, 300.0, 300.0))
        self.rooms.append(Room(100.0, h - 400.0, 300.0, 300.0))
        self.rooms.append(Room(w - 400.0, h - 400.0, 300.0, 300.0))

        # 4 corridors connecting quarantine rooms to center (with 50px overlap)
        self.corridors.append(Corridor(200.0, 350.0, 100.0, cy - 600.0))
        self.corridors.append(Corridor(w - 300.0, 350.0, 100.0, cy - 600.0))
        self.corridors.append(Corridor(200.0, cy + 250.0, 100.0, h - cy - 600.0))
        self.corridors.append(Corridor(w - 300.0, cy + 250.0, 100.0, h - cy - 600.0))

        # 8 hazards
        self.hazards.append(Hazard(id=0, x=250.0, y=250.0, radius=50.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=1, x=w - 250.0, y=250.0, radius=50.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=2, x=250.0, y=h - 250.0, radius=50.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=3, x=w - 250.0, y=h - 250.0, radius=50.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=4, x=cx - 150.0, y=cy - 150.0, radius=40.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=5, x=cx + 150.0, y=cy - 150.0, radius=40.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=6, x=cx - 150.0, y=cy + 150.0, radius=40.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=7, x=cx + 150.0, y=cy + 150.0, radius=40.0, kind="spikes", damage=30.0))



class BattleRoyaleShrinkingZoneArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central room
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # Top-left room
        self.rooms.append(Room(50, 50, 150, 150))
        # Top-right room
        self.rooms.append(Room(w - 200, 50, 150, 150))
        # Bottom-left room
        self.rooms.append(Room(50, h - 200, 150, 150))
        # Bottom-right room
        self.rooms.append(Room(w - 200, h - 200, 150, 150))

        # Connecting corridors (top-left)
        self.corridors.append(Corridor(100, 200, 50, cy - 400))
        self.corridors.append(Corridor(100, cy - 300, cx - 300, 50))

        # Connecting corridors (top-right)
        self.corridors.append(Corridor(w - 150, 200, 50, cy - 400))
        self.corridors.append(Corridor(cx + 300, cy - 300, w - cx - 300, 50))

        # Connecting corridors (bottom-left)
        self.corridors.append(Corridor(100, cy + 250, 50, h - cy - 400))
        self.corridors.append(Corridor(100, cy + 250, cx - 300, 50))

        # Connecting corridors (bottom-right)
        self.corridors.append(Corridor(w - 150, cy + 250, 50, h - cy - 400))
        self.corridors.append(Corridor(cx + 300, cy + 250, w - cx - 300, 50))

        # 1 central hazard to discourage staying in the open
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=80.0, kind="lava", damage=20.0))

    def update_zone(self, current_tick: int, delta: float):
        if current_tick != self.last_tick:
            self.last_tick = current_tick
            if self.safe_zone_radius > 50.0:
                self.safe_zone_radius -= 15.0 * delta
                if self.safe_zone_radius <= 50.0:
                    self.safe_zone_radius = 50.0
            else:
                if current_tick % 120 == 0:
                    import random
                    if hasattr(self, "_trigger_event"):
                        self._trigger_event(random.choice(["meteor_shower", "gravity_shift", "orbital_strike"]), current_tick)
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
                        elif event_type == "gravity_shift":

                            gw = Hazard(id=len(self.hazards) + random.randint(3000, 9999), x=self.width/2, y=self.height/2, radius=self.width/2, kind="gravity_well", damage=10.0)
                            setattr(gw, "duration", 10.0)
                            self.hazards.append(gw)

class HealAllyArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))
        self.rooms.append(Room(100, 100, 300, 300))
        self.rooms.append(Room(w - 400, 100, 300, 300))
        self.rooms.append(Room(100, h - 400, 300, 300))
        self.rooms.append(Room(w - 400, h - 400, 300, 300))

        self.corridors.append(Corridor(350, 200, cx - 600, 100))
        self.corridors.append(Corridor(cx - 350, 250, 100, cy - 500))
        self.corridors.append(Corridor(cx + 250, 200, w - cx - 600, 100))
        self.corridors.append(Corridor(cx + 250, 250, 100, cy - 500))
        self.corridors.append(Corridor(350, h - 300, cx - 600, 100))
        self.corridors.append(Corridor(cx - 350, cy + 250, 100, h - cy - 500))
        self.corridors.append(Corridor(cx + 250, h - 300, w - cx - 600, 100))
        self.corridors.append(Corridor(cx + 250, cy + 250, 100, h - cy - 500))

class WaitAndWatchArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))
        self.rooms.append(Room(cx - 150, 50, 300, 200))
        self.rooms.append(Room(cx - 150, h - 250, 300, 200))
        self.rooms.append(Room(50, cy - 150, 200, 300))
        self.rooms.append(Room(w - 250, cy - 150, 200, 300))

        self.corridors.append(Corridor(cx - 50, 250, 100, cy - 550))
        self.corridors.append(Corridor(cx - 50, cy + 300, 100, h - 550 - cy))
        self.corridors.append(Corridor(250, cy - 50, cx - 550, 100))
        self.corridors.append(Corridor(cx + 300, cy - 50, w - 550 - cx, 100))

        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=100.0, kind="lava", damage=20.0))
        self.hazards.append(Hazard(id=1, x=cx - 150, y=cy - 150, radius=50.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=2, x=cx + 150, y=cy - 150, radius=50.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=3, x=cx - 150, y=cy + 150, radius=50.0, kind="spikes", damage=30.0))
        self.hazards.append(Hazard(id=4, x=cx + 150, y=cy + 150, radius=50.0, kind="spikes", damage=30.0))


class EscortArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        self.rooms.append(Room(cx - 200, h - 400, 400, 300))
        self.rooms.append(Room(cx - 200, 100, 400, 300))
        self.corridors.append(Corridor(cx - 100, 400, 200, h - 800))
        self.hazards.append(Hazard(id=0, x=cx - 150, y=cy, radius=40, kind="lava", damage=10))
        self.hazards.append(Hazard(id=1, x=cx + 150, y=cy, radius=40, kind="lava", damage=10))

class FunnyFailsArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # 5 rooms
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400)) # Center
        self.rooms.append(Room(cx - 700, cy - 700, 300, 300)) # Top-Left
        self.rooms.append(Room(cx + 400, cy - 700, 300, 300)) # Top-Right
        self.rooms.append(Room(cx - 700, cy + 400, 300, 300)) # Bottom-Left
        self.rooms.append(Room(cx + 400, cy + 400, 300, 300)) # Bottom-Right

        # Corridors overlapping by 50px at each end -> length = gap + 100
        # Center to Top-Left: gap X from (cx-400) to (cx-200) -> 200
        self.corridors.append(Corridor(cx - 450, cy - 600, 300, 100)) # Horizontal TL
        self.corridors.append(Corridor(cx - 250, cy - 650, 100, 500)) # Vertical TL

        # Center to Top-Right
        self.corridors.append(Corridor(cx + 150, cy - 600, 300, 100))
        self.corridors.append(Corridor(cx + 150, cy - 650, 100, 500))

        # Center to Bottom-Left
        self.corridors.append(Corridor(cx - 450, cy + 500, 300, 100))
        self.corridors.append(Corridor(cx - 250, cy + 150, 100, 400))

        # Center to Bottom-Right
        self.corridors.append(Corridor(cx + 150, cy + 500, 300, 100))
        self.corridors.append(Corridor(cx + 150, cy + 150, 100, 400))

        # Hazards
        self.hazards.append(Hazard(0, cx, cy, 50.0, "lava", 20.0))
        self.hazards.append(Hazard(1, cx - 300, cy - 600, 40.0, "lava", 20.0))
        self.hazards.append(Hazard(2, cx + 300, cy - 600, 40.0, "lava", 20.0))
        self.hazards.append(Hazard(3, cx - 300, cy + 500, 40.0, "lava", 20.0))
        self.hazards.append(Hazard(4, cx + 300, cy + 500, 40.0, "lava", 20.0))


class TargetStrongArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))
        self.rooms.append(Room(cx - 500, cy - 100, 200, 200))
        self.rooms.append(Room(cx + 300, cy - 100, 200, 200))

        self.corridors.append(Corridor(cx - 350, cy - 50, 100, 100))
        self.corridors.append(Corridor(cx + 250, cy - 50, 100, 100))

        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=50.0, kind="lava", damage=25.0))


class BallGeneticsArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2.0, h/2.0

        # Main genetics lab room (center)
        self.rooms.append(Room(cx - 300.0, cy - 300.0, 600.0, 600.0))

        # 4 smaller reproduction chambers (corners)
        self.rooms.append(Room(cx - 600.0, cy - 600.0, 200.0, 200.0))
        self.rooms.append(Room(cx + 400.0, cy - 600.0, 200.0, 200.0))
        self.rooms.append(Room(cx - 600.0, cy + 400.0, 200.0, 200.0))
        self.rooms.append(Room(cx + 400.0, cy + 400.0, 200.0, 200.0))

        # Corridors linking chambers to main lab (overlapping)
        # Main lab Y: [cy-300, cy+300]
        # Top chambers Y: [cy-600, cy-400]
        # Top corridors need to span Y from cy-450 to cy-250 (gap closed)
        self.corridors.append(Corridor(cx - 450.0, cy - 450.0, 100.0, 200.0))
        self.corridors.append(Corridor(cx + 350.0, cy - 450.0, 100.0, 200.0))
        # Bottom chambers Y: [cy+400, cy+600]
        # Bottom corridors need to span Y from cy+250 to cy+450
        self.corridors.append(Corridor(cx - 450.0, cy + 250.0, 100.0, 200.0))
        self.corridors.append(Corridor(cx + 350.0, cy + 250.0, 100.0, 200.0))

        # Hazards representing genetic mutation zones
        self.hazards.append(Hazard(id=0, x=cx, y=cy, radius=50.0, kind="lava", damage=10.0))


class FleeArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        self.rooms.append(Room(cx - 200, cy - 200, 400, 400))
        self.rooms.append(Room(50, cy - 100, 200, 200))
        self.rooms.append(Room(w - 250, cy - 100, 200, 200))
        self.rooms.append(Room(cx - 100, 50, 200, 200))
        self.rooms.append(Room(cx - 100, h - 250, 200, 200))
        self.corridors.append(Corridor(200, cy - 50, cx - 350, 100))
        self.corridors.append(Corridor(cx + 150, cy - 50, w - cx - 350, 100))
        self.corridors.append(Corridor(cx - 50, 200, 100, cy - 350))
        self.corridors.append(Corridor(cx - 50, cy + 150, 100, h - cy - 350))
        self.hazards.append(Hazard(0, cx, cy, 100.0, "lava", 20.0))

class NeuralBallArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height

        # Input Layer
        self.rooms.append(Room(w * 0.1, h * 0.2, 150.0, 150.0))
        self.rooms.append(Room(w * 0.1, h * 0.5, 150.0, 150.0))
        self.rooms.append(Room(w * 0.1, h * 0.8, 150.0, 150.0))

        # Hidden Layer
        self.rooms.append(Room(w * 0.5, h * 0.2, 150.0, 150.0))
        self.rooms.append(Room(w * 0.5, h * 0.5, 150.0, 150.0))
        self.rooms.append(Room(w * 0.5, h * 0.8, 150.0, 150.0))

        # Output Layer
        self.rooms.append(Room(w * 0.8, h * 0.35, 150.0, 150.0))
        self.rooms.append(Room(w * 0.8, h * 0.65, 150.0, 150.0))

        # Corridors
        self.corridors.append(Corridor(w * 0.1 + 100.0, h * 0.2 + 50.0, w * 0.4, 50.0))
        self.corridors.append(Corridor(w * 0.1 + 100.0, h * 0.5 + 50.0, w * 0.4, 50.0))
        self.corridors.append(Corridor(w * 0.1 + 100.0, h * 0.8 + 50.0, w * 0.4, 50.0))
        self.corridors.append(Corridor(w * 0.5 + 100.0, h * 0.2 + 50.0, w * 0.3, 50.0))
        self.corridors.append(Corridor(w * 0.5 + 100.0, h * 0.8 + 50.0, w * 0.3, 50.0))

        self.corridors.append(Corridor(w * 0.8 + 50.0, h * 0.2 + 50.0, 50.0, h * 0.15 + 50.0))
        self.corridors.append(Corridor(w * 0.8 + 50.0, h * 0.65 + 50.0, 50.0, h * 0.15 + 50.0))

        # Hazards
        self.hazards.append(Hazard(0, w * 0.5 + 75.0, h * 0.35 + 75.0, 30.0, "spikes", 20.0))
        self.hazards.append(Hazard(1, w * 0.5 + 75.0, h * 0.65 + 75.0, 30.0, "lava", 50.0))


class BlackHoleArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))
        self.rooms.append(Room(50, 50, 200, 200))
        self.rooms.append(Room(w - 250, 50, 200, 200))
        self.rooms.append(Room(50, h - 250, 200, 200))
        self.rooms.append(Room(w - 250, h - 250, 200, 200))
        self.corridors.append(Corridor(100, 200, 100, cy - 400))
        self.corridors.append(Corridor(100, cy - 300, cx - 300, 100))
        self.corridors.append(Corridor(w - 200, 200, 100, cy - 400))
        self.corridors.append(Corridor(cx + 200, cy - 300, w - cx - 300, 100))
        self.corridors.append(Corridor(100, cy + 200, 100, h - cy - 400))
        self.corridors.append(Corridor(100, cy + 200, cx - 300, 100))
        self.corridors.append(Corridor(w - 200, cy + 200, 100, h - cy - 400))
        self.corridors.append(Corridor(cx + 200, cy + 200, w - cx - 300, 100))
        self.hazards.append(Hazard(0, cx, cy, 200.0, "black_hole", 30.0))

class DayNightArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.is_night = False
        self.day_night_timer = 0.0
        self.phase_duration = 10.0
        self.is_eclipse = False
        self.eclipse_timer = 0.0
        if hasattr(self, 'rng'):
            self.time_until_eclipse = self.rng.uniform(20.0, 40.0)
        else:
            import random
            self.time_until_eclipse = random.uniform(20.0, 40.0)

    def generate(self):
        super().generate()
        self.is_eclipse = False
        self.eclipse_timer = 0.0
        if hasattr(self, 'rng'):
            self.time_until_eclipse = self.rng.uniform(20.0, 40.0)
        else:
            import random
            self.time_until_eclipse = random.uniform(20.0, 40.0)

    def update_zone(self, current_tick: int, delta: float):
        super().update_zone(current_tick, delta)
        self.day_night_timer += delta
        if self.day_night_timer >= self.phase_duration:
            self.day_night_timer = 0.0
            self.is_night = not self.is_night

        if self.is_eclipse:
            self.eclipse_timer -= delta
            if self.eclipse_timer <= 0:
                self.is_eclipse = False
                if hasattr(self, 'rng'):
                    self.time_until_eclipse = self.rng.uniform(20.0, 40.0)
                else:
                    import random
                    self.time_until_eclipse = random.uniform(20.0, 40.0)
        else:
            self.time_until_eclipse -= delta
            if self.time_until_eclipse <= 0:
                self.is_eclipse = True
                self.eclipse_timer = 10.0

class ThickFogArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.is_foggy = False
        self.is_raining = False
        self.is_sandstorming = False
        self.is_snowing = False
        self.wind_dx = 0.0
        self.wind_dy = 0.0
        self.fog_timer = 0.0
        self.phase_duration = 20.0

    def update_zone(self, current_tick: int, delta: float):
        super().update_zone(current_tick, delta)
        self.fog_timer += delta
        if self.fog_timer >= self.phase_duration:
            self.fog_timer = 0.0
            self.is_foggy = not self.is_foggy


class ThunderstormArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.lightning_timer = 0.0
        self.strike_interval = 2.0  # seconds between lightning strikes

    def update_zone(self, current_tick: int, delta: float):
        super().update_zone(current_tick, delta)
        self.lightning_timer += delta
        if self.lightning_timer >= self.strike_interval:
            self.lightning_timer = 0.0
            import random
            # Spawn lightning strike
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            h_id = 9000 + len(self.hazards) + random.randint(0, 1000)
            lightning = Hazard(id=h_id, x=x, y=y, radius=60.0, kind="lightning", damage=300.0)
            lightning.target_radius = 60.0
            setattr(lightning, "duration", 0.5)  # Very short duration
            self.hazards.append(lightning)

        # Clean up expired lightning
        surviving_hazards = []
        for h in self.hazards:
            if getattr(h, "kind", "") == "lightning":
                duration = getattr(h, "duration", 0.0)
                duration -= delta
                setattr(h, "duration", duration)
                if duration > 0:
                    surviving_hazards.append(h)
            else:
                surviving_hazards.append(h)
        self.hazards = surviving_hazards

class SiegeArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Attacker Spawn Area (Large, open, plenty of health)
        self.rooms.append(Room(50, h - 400, w - 100, 350))

        # Defender Fortress (High ground/elevated, small, choke points)
        # Main fortress room
        self.rooms.append(Room(cx - 150, 50, 300, 300))

        # Chokepoint corridors leading to fortress
        self.corridors.append(Corridor(cx - 250, 350, 200, h - 400 - 350)) # Left ramp
        self.corridors.append(Corridor(cx + 50, 350, 200, h - 400 - 350)) # Right ramp

        # Add healing springs in attacker spawn
        for i in range(4):
            x = 100 + i * (w - 200) / 3
            y = h - 200
            h_id = len(self.hazards)
            heal = Hazard(id=h_id, x=x, y=y, radius=40.0, kind="healing_spring", damage=-20.0)
            self.hazards.append(heal)

        # Add some defensive structures (like walls/bumpers) near the choke points for defenders
        h_id = len(self.hazards)
        self.hazards.append(Hazard(id=h_id, x=cx - 150, y=350, radius=30.0, kind="bumper", damage=0.0))
        self.hazards.append(Hazard(id=h_id+1, x=cx + 150, y=350, radius=30.0, kind="bumper", damage=0.0))



class PinballArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2

        # Central room
        self.rooms.append(Room(cx - 300, cy - 300, 600, 600))

        # Side rooms
        self.rooms.append(Room(50, cy - 100, 150, 400))
        self.rooms.append(Room(w - 200, cy - 100, 150, 400))

        # Corridors
        self.corridors.append(Corridor(200, cy + 100, cx - 300 - 200, 100))
        self.corridors.append(Corridor(cx + 300, cy + 100, w - 200 - (cx + 300), 100))

        import random
        import math

        # Place Bumpers
        for i in range(12):
            bx = cx + random.uniform(-250, 250)
            by = cy + random.uniform(-250, 250)
            b = Hazard(id=len(self.hazards), x=bx, y=by, radius=30.0, kind="bumper", damage=0.0)
            self.hazards.append(b)

        # Place Flippers (left and right)
        f_left = Hazard(id=len(self.hazards), x=cx - 150, y=cy + 200, radius=50.0, kind="pinball_flipper", damage=10.0)
        setattr(f_left, "flipper_side", "left")
        setattr(f_left, "flip_timer", 0.0)
        self.hazards.append(f_left)

        f_right = Hazard(id=len(self.hazards), x=cx + 150, y=cy + 200, radius=50.0, kind="pinball_flipper", damage=10.0)
        setattr(f_right, "flipper_side", "right")
        setattr(f_right, "flip_timer", 0.0)
        self.hazards.append(f_right)

    def update_zone(self, current_tick: int, delta: float):
        super().update_zone(current_tick, delta)
        import random
        for h in self.hazards:
            if getattr(h, "kind", "") == "pinball_flipper":
                ft = getattr(h, "flip_timer", 0.0)
                if ft > 0:
                    setattr(h, "flip_timer", ft - delta)
                else:
                    if random.random() < 0.05: # Randomly flip
                        setattr(h, "flip_timer", 0.5)

ARENAS = {

    "siege": SiegeArena,
    "thunderstorm": ThunderstormArena,
    "thick_fog": ThickFogArena,
    "black_hole": BlackHoleArena,
    "neural_ball": NeuralBallArena,
    "flee": FleeArena,
    "ball_genetics": BallGeneticsArena,
    "funny_fails": FunnyFailsArena,
    "escort": EscortArena,
    "wait_and_watch": WaitAndWatchArena,
    "battle_royale_shrinking_zone": BattleRoyaleShrinkingZoneArena,
    "emotional_contagion": EmotionalContagionArena,
    "body_block": BodyBlockArena,
    "meta_evolution": MetaEvolutionArena,
    "ambush": AmbushArena,
    "physics_chain_reactions": PhysicsChainReactionsArena,
    "swarm_intelligence": SwarmIntelligenceArena,
    "clutch_plays": ClutchPlaysArena,
    "collect_booster": CollectBoosterArena,
    "reposition": RepositionArena,
    "avoid_trap": AvoidTrapArena,
    "kite": KiteArena,
    "buff_ally": BuffAllyArena,
    "retreat_to_ally": RetreatToAllyArena,
    "health_link": HealAllyArena,
    "procedural": ProceduralArena,
    "time_distortion": TimeDistortionArena,
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
    "group_attack": GroupAttackArena,
    "choke_point": ChokePointArena,
    "use_shield": UseShieldArena,
    "aggressive_chase": AggressiveChaseArena,
    "comebacks": ComebacksArena,
    "circle_strafe": CircleStrafeArena,
    "epic_kills": EpicKillsArena,
    "ai_commentary": AICommentaryArena,
    "ball_relationships": BallRelationshipsArena,
    "finals_1v1": Finals1v1Arena,
    "team_wipes": TeamWipesArena,
    "target_strong": TargetStrongArena,
    "day_night": DayNightArena,
    "pinball": PinballArena
}

class SummerArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.is_heatwave = True











class LavaArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.is_lava_theme = True

    def generate(self):
        super().generate()
        # Add lava cracks
        import random
        for _ in range(5):
            x = random.uniform(100, self.width - 100)
            y = random.uniform(100, self.height - 100)
            h_id = 1000 + len(self.hazards)
            lava_crack = type("Hazard", (object,), {})()
            lava_crack.id = h_id
            lava_crack.x = x
            lava_crack.y = y
            lava_crack.radius = random.uniform(30.0, 80.0)
            lava_crack.kind = "lava"
            lava_crack.damage = 15.0
            lava_crack.active = True
            lava_crack.target_radius = 0.0
            self.hazards.append(lava_crack)

class NeonArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.is_neon_theme = True

    def generate(self):
        super().generate()
        # Add neon speed pads (using conveyor belt or custom speed boost)
        import random
        for _ in range(5):
            x = random.uniform(100, self.width - 100)
            y = random.uniform(100, self.height - 100)
            h_id = 2000 + len(self.hazards)
            speed_pad = type("Hazard", (object,), {})()
            speed_pad.id = h_id
            speed_pad.x = x
            speed_pad.y = y
            speed_pad.radius = random.uniform(40.0, 60.0)
            speed_pad.kind = "bounce_pad" # Acts like a speed/bounce pad
            speed_pad.damage = 0.0
            speed_pad.active = True
            speed_pad.target_radius = 0.0
            self.hazards.append(speed_pad)

class AutumnArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.is_windy = True

    def generate(self):
        super().generate()
        # Add wind tornados
        import random
        for _ in range(3):
            x = random.uniform(100, self.width - 100)
            y = random.uniform(100, self.height - 100)
            h_id = 3000 + len(self.hazards)
            tornado = type("Hazard", (object,), {})()
            tornado.id = h_id
            tornado.x = x
            tornado.y = y
            tornado.radius = random.uniform(50.0, 100.0)
            tornado.kind = "tornado"
            tornado.damage = 5.0
            tornado.active = True
            tornado.target_radius = 0.0
            self.hazards.append(tornado)

class WinterArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, seed: int | None = None):
        super().__init__(arena_size, 5, seed)
        self.is_snowing = True

    def generate(self):
        super().generate()
        # Add ice patches
        import random
        for _ in range(5):
            x = random.uniform(100, self.width - 100)
            y = random.uniform(100, self.height - 100)
            h_id = 4000 + len(self.hazards)
            ice_patch = type("Hazard", (object,), {})()
            ice_patch.id = h_id
            ice_patch.x = x
            ice_patch.y = y
            ice_patch.radius = random.uniform(40.0, 120.0)
            ice_patch.kind = "ice_patch"
            ice_patch.damage = 0.0
            ice_patch.active = True
            ice_patch.target_radius = 0.0
            self.hazards.append(ice_patch)

ARENAS["summer"] = SummerArena
ARENAS["autumn"] = AutumnArena
ARENAS["lava"] = LavaArena
ARENAS["neon"] = NeonArena
ARENAS["winter"] = WinterArena

def get_arena(arena_type: str, arena_size: float = 2000.0, seed: int | None = None) -> ProceduralArena:
    arena_class = ARENAS.get(arena_type, ProceduralArena)
    if arena_class == ProceduralArena:
        return ProceduralArena(arena_size=arena_size, num_rooms=5, seed=seed)
    return arena_class(arena_size=arena_size, seed=seed)
