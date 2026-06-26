
class HeatmapOverlay:
    def __init__(self):
        self.death_coordinates = []
        self.max_deaths = 1.0

    def update(self, coords):
        self.death_coordinates = coords
        self.max_deaths = max(1.0, len(coords) * 0.1)

    def render_to_console(self):
        print("Heatmap generated with", len(self.death_coordinates), "death points.")
