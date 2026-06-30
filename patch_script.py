import re

with open("src/arena/procedural_arena.py", "r") as f:
    content = f.read()

content = content.replace('teleporters.append(teleporter)\n\n        # Link them in pairs', 'teleporters.append(teleporter)\n\n        # Generate one-way teleporters\n        num_one_way = max(1, self.num_rooms // 2)\n        for t in range(num_one_way):\n            t_id = len(self.hazards) + 9000 + t\n            tx, ty = self.get_random_spawn_point(25.0)\n            one_way = Hazard(id=t_id, x=tx, y=ty, radius=25.0, kind="one_way_teleporter", damage=0.0)\n            one_way.target_x, one_way.target_y = self.get_random_spawn_point(25.0)\n            self.hazards.append(one_way)\n\n        # Link them in pairs')

with open("src/arena/procedural_arena.py", "w") as f:
    f.write(content)
