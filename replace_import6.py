with open('src/arena/arena_types.py', 'r') as f:
    content = f.read()

content = content.replace('class ConveyorBelt(ProceduralArena.Hazard):', 'class ConveyorBelt(ProceduralArena):\n    pass\n\n# Or actually we should import Hazard\n')
