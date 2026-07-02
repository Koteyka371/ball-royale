with open("src/ai/action.gd", "r") as f:
    content = f.read()

old = """                elif hazard.kind == "quicksand":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var hd = hazard.damage * delta"""
new = """                elif hazard.kind == "shrinking_zone":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist = sqrt(dx * dx + dy * dy)
                    if dist > hazard.radius:
                        if self.ball.has_method("take_damage"):
                            self.ball.take_damage(hazard.damage * delta, "shrinking_zone")
                        elif "hp" in self.ball:
                            self.ball.hp -= hazard.damage * delta
                            if self.ball.hp <= 0:
                                self.ball.alive = false
                                if "killer" in self.ball:
                                    self.ball.killer = "shrinking_zone"
                elif hazard.kind == "quicksand":
                    var dx = hazard.x - self.ball.x
                    var dy = hazard.y - self.ball.y
                    var dist_sq = dx * dx + dy * dy
                    if dist_sq < hazard.radius * hazard.radius:
                        var hd = hazard.damage * delta"""
content = content.replace(old, new, 1)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
