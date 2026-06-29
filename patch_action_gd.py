import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

func_str = """
func _get_perception_radius() -> float:
    var pr = 250.0
    if "perception_radius" in self.ball:
        pr = self.ball.perception_radius
    if world.get("arena") != null:
        if world.arena.get("is_raining") == true:
            pr *= 0.6
        if world.arena.get("is_foggy") == true:
            pr *= 0.4
    return pr
"""

content = content.replace("func _get_perception_radius", "func _dummy") # Prevent double adding

content = re.sub(
    r'(func execute\(strategy: String, delta: float\) -> void:)',
    func_str + r'\n\n\1',
    content
)


content = re.sub(r'var perception_radius = 250\.0\s*if "perception_radius" in self\.ball:\s*perception_radius = self\.ball\.perception_radius',
                 r'var perception_radius = self._get_perception_radius()', content)


content = content.replace('my_ball.x += vx * delta * 0.2', 'my_ball.x += vx * delta * 0.5')
content = content.replace('my_ball.y += vy * delta * 0.2', 'my_ball.y += vy * delta * 0.5')

with open("src/ai/action.gd", "w") as f:
    f.write(content)
