class DangerGridOverlay:
    def __init__(self):
        self.danger_grid = {}
        self.max_danger = 1.0

    def update_danger_grid(self, grid: dict, max_val: float = 1.0):
        self.danger_grid = grid
        self.max_danger = max(0.1, max_val)

    def render_to_console(self):
        print(f"DangerGridOverlay active with {len(self.danger_grid)} dangerous cells.")
