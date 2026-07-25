import sys

with open("src/ai/action.py", "r") as f:
    content = f.read()

target1 = """            elif skill_name == "time_rewind_self":"""
new_code1 = """            elif skill_name == "quantum_echo":
                ghosts = getattr(self.ball, "quantum_ghosts", [])
                if ghosts:
                    most_recent = ghosts.pop(0)
                    self.ball.x = most_recent["x"]
                    self.ball.y = most_recent["y"]
                    self.ball.hp = most_recent["hp"]
                    if hasattr(self.world, "events"):
                        self.world.events.append({"type": "quantum_echo_teleport", "id": getattr(self.ball, "id", None)})

            elif skill_name == "time_rewind_self":"""

content = content.replace(target1, new_code1, 1)

target2 = """'kinetic_echo', 'kinetic_absorber'"""
new_code2 = """'kinetic_echo', 'kinetic_absorber', 'quantum_echo'"""

content = content.replace(target2, new_code2)

with open("src/ai/action.py", "w") as f:
    f.write(content)
