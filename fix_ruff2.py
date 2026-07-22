with open("src/ai/game_modes.py", "r") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Fix Multiple statements on one line (colon)
    if "if not hasattr(b, \"vx\"): b.vx = 0.0" in line:
        new_lines.append(line.replace("if not hasattr(b, \"vx\"): b.vx = 0.0", "if not hasattr(b, \"vx\"):\n                                b.vx = 0.0"))
        continue
    if "if not hasattr(b, \"vy\"): b.vy = 0.0" in line:
        new_lines.append(line.replace("if not hasattr(b, \"vy\"): b.vy = 0.0", "if not hasattr(b, \"vy\"):\n                                b.vy = 0.0"))
        continue
    if "if not getattr(b, 'alive', True) or not getattr(b, 'active', True): continue" in line:
        new_lines.append(line.replace("if not getattr(b, 'alive', True) or not getattr(b, 'active', True): continue", "if not getattr(b, 'alive', True) or not getattr(b, 'active', True):\n                    continue"))
        continue
    if "if getattr(b, 'ball_type', None) == 'spectator': continue" in line:
        new_lines.append(line.replace("if getattr(b, 'ball_type', None) == 'spectator': continue", "if getattr(b, 'ball_type', None) == 'spectator':\n                    continue"))
        continue
    if "if is_anchored: continue" in line:
        new_lines.append(line.replace("if is_anchored: continue", "if is_anchored:\n                    continue"))
        continue

    # Fix Multiple statements on one line (semicolon)
    if "self.id = id; self.x = x; self.y = y; self.radius = radius; self.kind = kind; self.damage = damage" in line:
        new_lines.append(line.replace("self.id = id; self.x = x; self.y = y; self.radius = radius; self.kind = kind; self.damage = damage", "self.id = id\n                            self.x = x\n                            self.y = y\n                            self.radius = radius\n                            self.kind = kind\n                            self.damage = damage"))
        continue

    # Fix F401 `random` imported but unused
    if "import random" in line and "Spawn anchor in the center" in lines[i-1]:
        continue

    # 32730
    if "if other is h or not getattr(other, \"active\", True): continue" in line:
        new_lines.append(line.replace("if other is h or not getattr(other, \"active\", True): continue", "if other is h or not getattr(other, \"active\", True):\n                                continue"))
        continue

    if "if not killer or self.season_ended: return" in line:
        new_lines.append(line.replace("if not killer or self.season_ended: return", "if not killer or self.season_ended:\n            return"))
        continue

    new_lines.append(line)

with open("src/ai/game_modes.py", "w") as f:
    f.writelines(new_lines)
