import sys

with open("src/ai/action.gd", "r") as f:
    content = f.read()

target1 = """        elif skill_name == "time_rewind_self":"""
new_code1 = """        elif skill_name == "quantum_echo":
            var ghosts = []
            if typeof(my_ball) == TYPE_DICTIONARY:
                ghosts = my_ball.get("quantum_ghosts", [])
            else:
                if my_ball.has_method("has_meta") and my_ball.has_meta("quantum_ghosts"):
                    ghosts = my_ball.get_meta("quantum_ghosts")
                elif "quantum_ghosts" in my_ball:
                    ghosts = my_ball.quantum_ghosts

            if ghosts.size() > 0:
                var most_recent = ghosts[0]
                ghosts.remove_at(0)
                if typeof(my_ball) == TYPE_DICTIONARY:
                    my_ball["x"] = most_recent["x"]
                    my_ball["y"] = most_recent["y"]
                    my_ball["hp"] = most_recent["hp"]
                else:
                    if "x" in my_ball: my_ball.x = most_recent["x"]
                    elif my_ball.has_method("set_meta"): my_ball.set_meta("x", most_recent["x"])
                    if "y" in my_ball: my_ball.y = most_recent["y"]
                    elif my_ball.has_method("set_meta"): my_ball.set_meta("y", most_recent["y"])
                    if "hp" in my_ball: my_ball.hp = most_recent["hp"]
                    elif my_ball.has_method("set_meta"): my_ball.set_meta("hp", most_recent["hp"])

                if typeof(self.world) == TYPE_DICTIONARY and self.world.has("events"):
                    self.world.events.append({"type": "quantum_echo_teleport"})
                elif typeof(self.world) == TYPE_OBJECT and "events" in self.world:
                    self.world.events.append({"type": "quantum_echo_teleport"})

        elif skill_name == "time_rewind_self":"""

content = content.replace(target1, new_code1, 1)

target2 = """'kinetic_echo', 'kinetic_absorber'"""
new_code2 = """'kinetic_echo', 'kinetic_absorber', 'quantum_echo'"""

content = content.replace(target2, new_code2)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
