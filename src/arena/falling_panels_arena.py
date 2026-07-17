import math
import random
from typing import Tuple

from arena.procedural_arena import ProceduralArena, Hazard

class FallingPanelsArena(ProceduralArena):
    def __init__(self, arena_size: float = 2000.0, num_rooms: int = 5, seed: int | None = None):
        self.panel_size = 400.0
        self.panels = []
        self.drop_timer = 0.0
        self.drop_interval = 10.0 # Time between a panel glowing and falling
        # Need to call super before generate logic relies on self properties?
        # Actually ProceduralArena.__init__ calls generate() inside it, so we need properties set before.
        super().__init__(arena_size=arena_size, num_rooms=num_rooms, seed=seed)

    def generate(self):
        super().generate()
        self.rooms.clear()
        self.corridors.clear()
        self.hazards.clear()

        cols = int(math.ceil(self.width / self.panel_size))
        rows = int(math.ceil(self.height / self.panel_size))

        self.panels = []
        for i in range(cols):
            for j in range(rows):
                self.panels.append({
                    "col": i,
                    "row": j,
                    "x": i * self.panel_size,
                    "y": j * self.panel_size,
                    "width": self.panel_size,
                    "height": self.panel_size,
                    "state": "normal", # "normal", "glowing", "fallen"
                    "timer": 0.0
                })

    def update_zone(self, current_tick: int, delta: float):
        is_new_tick = current_tick != self.last_tick
        super().update_zone(current_tick, delta)

        if is_new_tick:
            self.drop_timer += delta

            if self.drop_timer >= self.drop_interval:
                self.drop_timer = 0.0
                # Pick a random normal panel to glow
                normal_panels = [p for p in self.panels if p["state"] == "normal"]
                if normal_panels:
                    import random
                    panel = random.choice(normal_panels)
                    panel["state"] = "glowing"
                    panel["timer"] = 3.0 # Glows for 3 seconds before falling

            # Update panels
            for panel in self.panels:
                if panel["state"] == "glowing":
                    panel["timer"] -= delta
                    if panel["timer"] <= 0.0:
                        panel["state"] = "fallen"
                        # Spawn void hazard
                        cx = panel["x"] + self.panel_size / 2.0
                        cy = panel["y"] + self.panel_size / 2.0
                        radius = self.panel_size / 2.0
                        # Needs to instantly kill
                        void_hazard = Hazard(id=-10000 - len(self.hazards), x=cx, y=cy, radius=radius, kind="void_panel", damage=10000.0)
                        # We use square bounds for real check, but Hazard is a circle. We can use a custom kind that we check later in action.py or we can use multiple small hazards, or in action.py we handle it
                        # Let's add it
                        self.hazards.append(void_hazard)

    def is_point_inside(self, x: float, y: float, radius: float) -> bool:
        # Check if point is on a fallen panel
        for p in self.panels:
            if p["state"] == "fallen":
                if p["x"] <= x <= p["x"] + p["width"] and p["y"] <= y <= p["y"] + p["height"]:
                    # Is inside fallen panel, so it shouldn't be inside a safe area
                    # Actually, is_point_inside for ProceduralArena is "is it in a room/corridor". We want to return True if it's on a normal panel?
                    pass
        # ProceduralArena has rooms, we cleared rooms, so super().is_point_inside will use safe_zone which is huge.
        return super().is_point_inside(x, y, radius)
