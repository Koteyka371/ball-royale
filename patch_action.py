import re

with open("src/ai/action.py", "r") as f:
    content = f.read()

# Add _get_perception_radius
perception_func = """
    def _get_perception_radius(self) -> float:
        pr = float(getattr(self.ball, "perception_radius", 250.0))
        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_raining", False):
            pr *= 0.6  # Reduced perception in rain
        if hasattr(self.world, "arena") and getattr(self.world.arena, "is_foggy", False):
            pr *= 0.4  # Further reduced perception in fog
        return pr
"""

content = re.sub(r'def __init__\(self, ball: Any, world: Any\):\n        self\.ball = ball\n        self\.world = world',
                 r'def __init__(self, ball: Any, world: Any):\n        self.ball = ball\n        self.world = world\n' + perception_func,
                 content)

# Replace all perception_radius = getattr(self.ball, "perception_radius", 250)
content = content.replace('perception_radius = getattr(self.ball, "perception_radius", 250)', 'perception_radius = self._get_perception_radius()')
content = content.replace('perception_radius = getattr(self.ball, "perception_radius", 250.0)', 'perception_radius = self._get_perception_radius()')

# Also increase rain drift from 0.2 to 0.5
content = content.replace('self.ball.x += getattr(self.ball, "vx") * delta * 0.2', 'self.ball.x += getattr(self.ball, "vx", 0.0) * delta * 0.5')
content = content.replace('self.ball.y += getattr(self.ball, "vy") * delta * 0.2', 'self.ball.y += getattr(self.ball, "vy", 0.0) * delta * 0.5')


with open("src/ai/action.py", "w") as f:
    f.write(content)
