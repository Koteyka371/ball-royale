import math

class OrbitalCrosshairUI:
    def __init__(self):
        self.crosshair_positions = []
        self.pulse_time = 0.0

    def update_crosshairs(self, hazards):
        self.crosshair_positions.clear()
        for h in hazards:
            kind = getattr(h, "kind", "")
            if isinstance(kind, str) and kind == "orbital_strike":
                show = getattr(h, "show_crosshair", False)
                if show:
                    self.crosshair_positions.append({
                        "x": getattr(h, "x", 0.0),
                        "y": getattr(h, "y", 0.0),
                        "radius": getattr(h, "radius", 400.0)
                    })

    def process(self, delta):
        if self.crosshair_positions:
            self.pulse_time += delta

    def render_to_console(self):
        for ch in self.crosshair_positions:
            alpha = 0.3 + (math.sin(self.pulse_time * 10.0) + 1.0) * 0.25
            print(f"[UI RENDER] Pulsating Crosshair at ({ch['x']:.1f}, {ch['y']:.1f}) R={ch['radius']} Alpha={alpha:.2f}")
