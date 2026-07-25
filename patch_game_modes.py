import sys

with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

target = """    def apply_dynamic_traits(self, world: 'Any', balls: 'List[Any]', delta: float) -> None:
"""

new_code = """    def apply_dynamic_traits(self, world: 'Any', balls: 'List[Any]', delta: float) -> None:
        for b in balls:
            if getattr(b, "alive", True) and "quantum_echo" in getattr(b, "traits", []):
                if not hasattr(b, "quantum_echo_timer"):
                    b.quantum_echo_timer = 3.0
                b.quantum_echo_timer -= delta
                if b.quantum_echo_timer <= 0:
                    b.quantum_echo_timer = 3.0
                    if not hasattr(b, "quantum_ghosts"):
                        b.quantum_ghosts = []
                    b.quantum_ghosts.insert(0, {"x": getattr(b, "x", 0.0), "y": getattr(b, "y", 0.0), "hp": getattr(b, "hp", 100)})
                    if hasattr(world, "events"):
                        world.events.append({"type": "quantum_echo_ghost", "x": b.x, "y": b.y, "team": getattr(b, "team", "")})

"""

content = content.replace(target, new_code, 1)

with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
