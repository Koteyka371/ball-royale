class HovercraftMode:
    def __init__(self):
        self.name = "Hovercraft"
        self.description = "Friction is reduced to zero, making all balls slide uncontrollably until they hit a wall or use a dash ability."

    def tick(self, world, balls, delta=0.016):
        pass

    def apply_dynamic_traits(self, world, balls, delta: float) -> None:
        for b in balls:
            if hasattr(b, "is_frictionless"):
                b.is_frictionless = True
            elif hasattr(b, "set_meta"):
                b.set_meta("is_frictionless", True)
            elif isinstance(b, dict):
                b["is_frictionless"] = True
