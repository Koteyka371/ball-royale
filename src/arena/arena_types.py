import random

from arena.procedural_arena import ProceduralArena, Room, Hazard

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

class TargetWeakArena(ProceduralArena):
    def generate(self):
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()
        w, h = self.width, self.height
        cx, cy = w/2, h/2
        self.rooms.append(Room(50, 50, 100, 100))
        self.rooms.append(Room(w-150, 50, 100, 100))
        self.rooms.append(Room(50, h-150, 100, 100))
        self.rooms.append(Room(w-150, h-150, 100, 100))
        self.rooms.append(Room(cx - 400, cy - 400, 800, 800))
        self.hazards.append(Hazard(id=1, x=cx, y=cy, radius=100.0, kind="lava", damage=50.0))

ARENAS = {
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
    "choke_point": ChokePointArena,
    "target_weak": TargetWeakArena
}

def get_arena(arena_type: str, arena_size: float = 2000.0, seed: int | None = None) -> ProceduralArena:
    arena_class = ARENAS.get(arena_type, ProceduralArena)
    if arena_class == ProceduralArena:
        return ProceduralArena(arena_size=arena_size, num_rooms=5, seed=seed)
    return arena_class(arena_size=arena_size, seed=seed)
