import re
with open("src/ai/action.gd", "r") as f:
    content = f.read()

# find if capacity < 0 in hazard block
hazard_block = """									if capacity < 0:
										var remainder_damage = -capacity
										if "is_in_quicksand" in self.ball and self.ball.is_in_quicksand:
											remainder_damage *= 2.0
										if self.ball.has_method("take_damage"):
											self.ball.take_damage(remainder_damage)
										elif "hp" in self.ball:
											self.ball.hp -= remainder_damage
											if self.ball.hp <= 0:
												self.ball.alive = false"""

print(content.count(hazard_block))
