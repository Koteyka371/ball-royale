with open("src/ai/action.py", "r") as f:
    content = f.read()

search = """            if getattr(self.world.arena, "is_foggy", False):
                pass # Fog has no friction effect, snow has speed change
            if getattr(self.world.arena, "is_snowing", False):
                # Snow: reduce speed
                pass"""

content = content.replace(search, "")

with open("src/ai/action.py", "w") as f:
    f.write(content)

with open("src/ai/action.gd", "r") as f:
    content2 = f.read()

search2 = """        if world.arena.get("is_raining") == true:
            if "vx" in my_ball and "vy" in my_ball:
                my_ball.x += my_ball.vx * delta * 0.2
                my_ball.y += my_ball.vy * delta * 0.2
        if world.arena.get("is_snowing") == true:
            pass"""
replace2 = """        if world.arena.get("is_raining") == true:
            if "vx" in my_ball and "vy" in my_ball:
                my_ball.x += my_ball.vx * delta * 0.2
                my_ball.y += my_ball.vy * delta * 0.2"""
content2 = content2.replace(search2, replace2)

with open("src/ai/action.gd", "w") as f:
    f.write(content2)
