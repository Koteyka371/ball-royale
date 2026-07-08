with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

# Add a simple Hazard definition into the modules that use it since we removed the inline ones.
inline = """        try:
            from arena.procedural_arena import Hazard
        except ImportError:
            class Hazard:
                def __init__(self, id, x, y, radius, kind, damage):
                    self.id = id
                    self.x = x
                    self.y = y
                    self.radius = radius
                    self.kind = kind
                    self.damage = damage
                    self.active = True
                    self.target_radius = 0.0
"""

# Let's insert this back right before 'if self.weapon_spawn_timer >= 3.0:' in WeaponCollectionMode
content = content.replace("        if self.weapon_spawn_timer >= 3.0:", inline + "\n        if self.weapon_spawn_timer >= 3.0:")

# Let's insert this back right before 'if self.spawn_timer >= 5.0:' in RollingBouldersMode
content = content.replace("        if self.spawn_timer >= 5.0:", inline + "\n        if self.spawn_timer >= 5.0:")

with open("src/ai/game_modes.py", "w") as f:
    f.write(content)
