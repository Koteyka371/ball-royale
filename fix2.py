with open("src/ai/action.gd", "r") as f:
    content_gd = f.read()

# Clean up that broken chunk right before `var old_x = self.ball.x`

search_clean = """    var dist = sqrt(pow(my_ball.x - old_x, 2) + pow(my_ball.y - old_y, 2))
    var act_stamina = 100.0
    var act_max_stamina = 100.0
    if my_ball.has_meta("stamina"): act_stamina = my_ball.get_meta("stamina")
    if my_ball.has_meta("max_stamina"): act_max_stamina = my_ball.get_meta("max_stamina")

    var act_base_speed = 2.0
    if my_ball.has_meta("base_speed"): act_base_speed = my_ball.get_meta("base_speed")

    var is_dash = false
    if my_ball.has_meta("is_dashing"): is_dash = my_ball.get_meta("is_dashing")

    if is_dash:
        my_ball.set_meta("stamina", max(0.0, act_stamina - 50.0 * delta))
    elif dist / max(0.0001, delta * 60) < act_base_speed * 0.5:
        my_ball.set_meta("stamina", min(act_max_stamina, act_stamina + 30.0 * delta))"""

content_gd = content_gd.replace(search_clean, "")

with open("src/ai/action.gd", "w") as f:
    f.write(content_gd)
