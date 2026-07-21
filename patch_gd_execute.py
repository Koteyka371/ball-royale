import re
with open("src/ai/action.gd", "r") as f:
    content = f.read()

# Make sure we didn't duplicate in action.gd too.
print(content.count("func execute(strategy: String, delta: float) -> void:"))
print(content.count("if typeof(ball) == TYPE_OBJECT and \"ball_type\" in ball and ball.ball_type == \"mirror\""))
