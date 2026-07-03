with open("src/ai/action.gd", "r") as f:
    content = f.read()

target = """        if world.arena.get("is_raining") == true and not ignores_mud and not is_wind_riding_f:
            if "vx" in my_ball and "vy" in my_ball:
                my_ball.x += my_ball.vx * delta * 0.2
                my_ball.y += my_ball.vy * delta * 0.2"""

replacement = """        if world.arena.get("is_raining") == true and not ignores_mud and not is_wind_riding_f:
            if "vx" in my_ball and "vy" in my_ball:
                my_ball.x += my_ball.vx * delta * 0.2
                my_ball.y += my_ball.vy * delta * 0.2

            var terrain_type = "grass"
            if world.arena.get("terrain_type") != null: terrain_type = str(world.arena.get("terrain_type"))
            if terrain_type in ["dirt", "sand"]:
                var b_type_mud = ""
                if "ball_type" in my_ball: b_type_mud = str(my_ball.ball_type).to_lower()
                elif "BALL_TYPE" in my_ball: b_type_mud = str(my_ball.BALL_TYPE).to_lower()
                var is_water_or_swamp = b_type_mud in ["elementalist", "healer", "trickster"] or b_type_mud.find("swamp") != -1 or b_type_mud.find("water") != -1
                if not is_water_or_swamp:
                    var base_spd = 100.0
                    if "base_speed" in my_ball: base_spd = float(my_ball.base_speed)
                    elif my_ball.has_method("get_meta") and my_ball.has_meta("base_speed"): base_spd = float(my_ball.get_meta("base_speed"))
                    my_ball.speed = base_spd * 0.5"""

content = content.replace(target, replacement)
with open("src/ai/action.gd", "w") as f:
    f.write(content)
