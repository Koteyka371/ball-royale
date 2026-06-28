def apply_weather_effects(ball, weather, delta, wind_dx=0.0, wind_dy=0.0, random_module=None):
    if random_module is None:
        import random
        random_module = random

    if not hasattr(ball, "base_speed"):
        ball.base_speed = getattr(ball, "speed", 100.0)
    if not hasattr(ball, "base_damage"):
        ball.base_damage = getattr(ball, "damage", 10.0)

    if weather == "clear":
        ball.speed = ball.base_speed
        ball.damage = ball.base_damage
    elif weather == "rain":
        ball.speed = ball.base_speed * 0.8
        ball.damage = ball.base_damage
        # slide more
        if hasattr(ball, "vx") and hasattr(ball, "vy"):
            ball.x += ball.vx * delta * 0.5
            ball.y += ball.vy * delta * 0.5
    elif weather == "fog":
        ball.speed = ball.base_speed * 0.5
        ball.damage = ball.base_damage * 0.8
    elif weather == "snow":
        ball.speed = ball.base_speed * 0.5 # slowed down
        ball.damage = ball.base_damage * 1.2
    elif weather == "wind":
        ball.speed = ball.base_speed
        ball.damage = ball.base_damage
        # push balls in a specific direction
        ball.x += wind_dx * delta
        ball.y += wind_dy * delta
    elif weather == "thunderstorm":
        ball.speed = ball.base_speed * 1.1 # Panic speed
        ball.damage = ball.base_damage * 1.5 # High damage due to electricity
        # Random lightning strikes
        if random_module.random() < 0.05 * delta:
            # Struck by lightning!
            ball.hp = getattr(ball, "hp", 100) - 20
