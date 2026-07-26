class GuildWarsBaseBuildingMode:
    """
    Guild Wars game mode where guilds build defenses (turrets, walls, traps).
    Opposing teams attack the HQ.
    """
    def __init__(self):
        self.name = "Guild Wars Base Building"
        self.description = "Customize HQ and attack opposing guild bases."
        self.hq_hp = 10000.0
        self.defenses = []

    def setup(self, world, balls):
        if not hasattr(world, "arena"):
            return

        # Initialize an HQ if it doesn't exist
        if not hasattr(world.arena, "hq"):
            world.arena.hq = {
                "x": 0.0,
                "y": 0.0,
                "radius": 100.0,
                "hp": self.hq_hp,
                "max_hp": self.hq_hp,
                "team": "defender"
            }

        # Create some defenses based on resources (dummy setup)
        # Read defenses from UI if available, else default dummy
        try:
            from ui.guild_wars_base_building import GuildWarsBaseBuildingUI
            # For simplicity in this game mode mock, we'll assume a global UI state can be accessed
            # or we just instantiate one and populate it. In a real system, it would be passed in.
            ui = GuildWarsBaseBuildingUI()
            # Hardcode some placements for demonstration that the UI is used
            ui.place_defense("turret", 100.0, 100.0)
            ui.place_defense("wall", -100.0, 0.0)
            ui.place_defense("trap", 0.0, 200.0)

            # Map UI layout to game mode format
            self.defenses = []
            for d in ui.get_layout():
                d_copy = dict(d)
                d_copy["team"] = "defender"
                if d_copy["type"] == "turret":
                    d_copy["damage"] = 50.0
                    d_copy["range"] = 300.0
                elif d_copy["type"] == "wall":
                    d_copy["width"] = 50.0
                    d_copy["height"] = 200.0
                    d_copy["hp"] = 1000.0
                elif d_copy["type"] == "trap":
                    d_copy["damage"] = 100.0
                    d_copy["radius"] = 40.0
                self.defenses.append(d_copy)
        except ImportError:
            self.defenses = []
        world.arena.defenses = self.defenses

    def tick(self, world, balls, delta=0.016):
        if not hasattr(world, "arena") or not hasattr(world.arena, "hq") or not hasattr(world.arena, "defenses"):
            return

        import math

        for b in balls:
            if not getattr(b, "alive", True):
                continue

            b_team = getattr(b, "team", None)

            if b_team != world.arena.hq["team"]:
                # Attacking HQ
                dx = b.x - world.arena.hq["x"]
                dy = b.y - world.arena.hq["y"]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist < world.arena.hq["radius"] + getattr(b, "radius", 20.0):
                    # Deal damage to HQ
                    damage = getattr(b, "damage", 10.0) * delta
                    world.arena.hq["hp"] -= damage
                    if world.arena.hq["hp"] < 0:
                        world.arena.hq["hp"] = 0

            # Process defenses
            for defense in world.arena.defenses:
                if defense["team"] != b_team:
                    if defense["type"] == "turret":
                        dx = b.x - defense["x"]
                        dy = b.y - defense["y"]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < defense["range"]:
                            # Turret shoots
                            if hasattr(b, "hp"):
                                b.hp -= defense["damage"] * delta
                    elif defense["type"] == "trap":
                        dx = b.x - defense["x"]
                        dy = b.y - defense["y"]
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < defense["radius"] + getattr(b, "radius", 20.0):
                            if hasattr(b, "hp"):
                                b.hp -= defense["damage"]
                            defense["type"] = "used_trap" # Deactivate
                    elif defense["type"] == "wall":
                        # Simple AABB / point collision logic
                        # Simplified for this simulation
                        pass
