import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

content = content.replace("""									if capacity < 0:
										var remainder_damage = -capacity
										if "is_in_quicksand" in self.ball and self.ball.is_in_quicksand:
											remainder_damage *= 2.0
										if self.ball.has_method("take_damage"):
											self.ball.take_damage(remainder_damage)
										elif "hp" in self.ball:
											self.ball.hp -= remainder_damage
											if self.ball.hp <= 0:
												self.ball.alive = false""", """									if capacity < 0:
										var remainder_damage = -capacity
										if "is_in_quicksand" in self.ball and self.ball.is_in_quicksand:
											remainder_damage *= 2.0
										if self.ball.has_method("take_damage"):
											self.ball.take_damage(remainder_damage)
										elif "hp" in self.ball:
											self.ball.hp -= remainder_damage
											if self.ball.hp <= 0:
												self.ball.alive = false

										var explosion_radius = 80.0
										if self.world != null and "balls" in self.world:
											for other in self.world.balls:
												var other_alive = false
												if "alive" in other:
													other_alive = other.alive
												elif other.has_method("get_meta") and other.has_meta("alive"):
													other_alive = other.get_meta("alive")

												var other_id = null
												if "id" in other:
													other_id = other.id

												var target_id = null
												if "id" in self.ball:
													target_id = self.ball.id

												if other_alive and other_id != target_id:
													var dx = 0.0
													if "x" in other: dx = other.x
													if "x" in self.ball: dx -= self.ball.x
													var dy = 0.0
													if "y" in other: dy = other.y
													if "y" in self.ball: dy -= self.ball.y

													var dist = sqrt(dx*dx + dy*dy)
													if dist <= explosion_radius:
														if self.world != null and self.world.has_method("_deal_damage"):
															var old_atk_dmg = 10.0
															if "damage" in self.ball: old_atk_dmg = self.ball.damage
															if "damage" in self.ball: self.ball.damage = remainder_damage
															elif self.ball.has_method("set_meta"): self.ball.set_meta("damage", remainder_damage)
															self.world._deal_damage(self.ball, other)
															if "damage" in self.ball: self.ball.damage = old_atk_dmg
															elif self.ball.has_method("set_meta"): self.ball.set_meta("damage", old_atk_dmg)
														elif other.has_method("take_damage"):
															other.take_damage(remainder_damage)
														elif "hp" in other:
															other.hp -= remainder_damage
															if other.hp <= 0:
																if "alive" in other: other.alive = false
																elif other.has_method("set_meta"): other.set_meta("alive", false)""", 1)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
