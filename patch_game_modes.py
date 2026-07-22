import re

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

new_class = """
class FallingTilesRoyaleMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Falling Tiles Royale"
        self.description = "A battle royale variant where the arena is made up of a grid of tiles. Every few seconds, some tiles light up and then fall away, turning into bottomless pits."
        self.grid_size = 50.0
        self.tiles = {}
        self.timer = 0.0
        self.phase = "wait"
        self.warning_duration = 2.0
        self.fall_duration = 3.0
        self.active_tiles = []
        self.falling_tiles = []
        self.is_falling_tiles_royale = True
        import random
        self.random = random

    def setup(self, world, balls):
        super().setup(world, balls)
        self.tiles = {}
        arena_width = getattr(world.arena, "width", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0
        arena_height = getattr(world.arena, "height", 1000.0) if hasattr(world, "arena") and world.arena else 1000.0

        self.cols = int(arena_width / self.grid_size)
        self.rows = int(arena_height / self.grid_size)

        for c in range(self.cols):
            for r in range(self.rows):
                self.tiles[(c, r)] = {"state": "normal"} # normal, warning, falling, pit

        self.timer = 5.0
        self.phase = "wait"

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)
        self.timer -= delta

        if self.phase == "wait":
            if self.timer <= 0:
                self.phase = "warning"
                self.timer = self.warning_duration
                # Pick some tiles to light up
                normal_tiles = [k for k, v in self.tiles.items() if v["state"] == "normal"]
                num_to_fall = max(1, int(len(normal_tiles) * 0.1))
                if num_to_fall > len(normal_tiles) - 4:
                    num_to_fall = max(1, len(normal_tiles) - 4) # leave some

                self.falling_tiles = self.random.sample(normal_tiles, min(num_to_fall, len(normal_tiles)))
                for k in self.falling_tiles:
                    self.tiles[k]["state"] = "warning"

                if hasattr(world, "add_event"):
                    world.add_event("tiles_warning", {"message": "Some tiles are lighting up!"})

        elif self.phase == "warning":
            if self.timer <= 0:
                self.phase = "falling"
                self.timer = self.fall_duration
                for k in self.falling_tiles:
                    self.tiles[k]["state"] = "falling"
                if hasattr(world, "add_event"):
                    world.add_event("tiles_falling", {"message": "Tiles are falling!"})

        elif self.phase == "falling":
            if self.timer <= 0:
                self.phase = "wait"
                self.timer = getattr(self.random, "uniform", lambda a,b: 5.0)(4.0, 8.0)
                for k in self.falling_tiles:
                    self.tiles[k]["state"] = "pit"
                self.falling_tiles = []

        # Handle balls over pits
        for b in balls:
            if not getattr(b, "alive", False) or getattr(b, "ball_type", None) == "spectator":
                continue

            bx, by = getattr(b, "x", 0.0), getattr(b, "y", 0.0)
            c = int(bx / self.grid_size)
            r = int(by / self.grid_size)

            if (c, r) in self.tiles:
                state = self.tiles[(c, r)]["state"]
                if state == "pit":
                    # Instant death or massive damage
                    if hasattr(b, "take_damage"):
                        b.take_damage(9999.0)
                    else:
                        b.hp = 0.0
                        b.alive = False

                    if not getattr(b, "alive", False) and hasattr(world, "add_event"):
                        world.add_event("ball_fell", {"id": getattr(b, "id", None)})

GAME_MODES['falling_tiles_royale'] = FallingTilesRoyaleMode()
"""

if "GAME_MODES['falling_tiles_royale'] = FallingTilesRoyaleMode()" not in content:
    content += "\n" + new_class + "\n"
    with open("src/ai/game_modes.py", "w") as f:
        f.write(content)
    print("Added FallingTilesRoyaleMode to src/ai/game_modes.py")
