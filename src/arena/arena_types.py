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


ARENAS = {
    "collect_booster": CollectBoosterArena,
    "reposition": RepositionArena,
    "avoid_trap": AvoidTrapArena,
    "kite": KiteArena,
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
    "group_attack": GroupAttackArena,
    "choke_point": ChokePointArena,
    "use_shield": UseShieldArena,
    "aggressive_chase": AggressiveChaseArena,
    "comebacks": ComebacksArena,
    "circle_strafe": CircleStrafeArena,
    "epic_kills": EpicKillsArena,
    "ball_relationships": BallRelationshipsArena
}

def get_arena(arena_type: str, arena_size: float = 2000.0, seed: int | None = None) -> ProceduralArena:
    arena_class = ARENAS.get(arena_type, ProceduralArena)
    if arena_class == ProceduralArena:
        return ProceduralArena(arena_size=arena_size, num_rooms=5, seed=seed)
    return arena_class(arena_size=arena_size, seed=seed)
