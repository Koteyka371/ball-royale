import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# For lines: pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 50.0 * delta * lifetime_mult
# We need to modify the push/pull force based on mass: "lighter balls could be thrown farther" -> push_strength / max(mass, 0.1)

# In the first loop:
content = content.replace(
    '''pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 50.0 * delta * lifetime_mult''',
    '''pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 50.0 * delta * lifetime_mult
                                if hazard.kind in ("tornado", "supercell_tornado", "local_tornado", "firenado", "local_firenado", "poison_tornado", "local_poison_tornado"):
                                    mass = getattr(self.ball, "mass", 1.0)
                                    pull_strength = pull_strength / max(mass, 0.1)'''
)

# In the second loop:
content = content.replace(
    '''pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta''',
    '''pull_strength = (hazard.radius * 2.0 * radius_mult / max(10.0, dist)) * 200.0 * delta
                            mass = getattr(self.ball, "mass", 1.0)
                            pull_strength = pull_strength / max(mass, 0.1)'''
)

with open("src/ai/action.py", "w") as f:
    f.write(content)
