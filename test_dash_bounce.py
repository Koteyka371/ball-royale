import math

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

ball = Ball(50, 50, 10)
arena_width = 100
arena_height = 100

dash_dist = 200
dir_x = 1.0
dir_y = 0.0

remaining_dist = dash_dist
b_rad = ball.radius

for _ in range(10):
    if remaining_dist <= 0:
        break

    dist_to_x_wall = float('inf')
    if dir_x > 0:
        dist_to_x_wall = (arena_width - b_rad - ball.x) / dir_x
    elif dir_x < 0:
        dist_to_x_wall = (b_rad - ball.x) / dir_x

    dist_to_y_wall = float('inf')
    if dir_y > 0:
        dist_to_y_wall = (arena_height - b_rad - ball.y) / dir_y
    elif dir_y < 0:
        dist_to_y_wall = (b_rad - ball.y) / dir_y

    dist_to_wall = min(dist_to_x_wall, dist_to_y_wall)

    if dist_to_wall <= 0.0001:
        if dist_to_x_wall <= 0.0001: dir_x *= -1
        if dist_to_y_wall <= 0.0001: dir_y *= -1
        ball.x = max(b_rad, min(arena_width - b_rad, ball.x))
        ball.y = max(b_rad, min(arena_height - b_rad, ball.y))
        continue

    if remaining_dist <= dist_to_wall:
        ball.x += dir_x * remaining_dist
        ball.y += dir_y * remaining_dist
        break
    else:
        ball.x += dir_x * dist_to_wall
        ball.y += dir_y * dist_to_wall
        remaining_dist -= dist_to_wall

        if dist_to_x_wall < dist_to_y_wall:
            ball.x = arena_width - b_rad if dir_x > 0 else b_rad
            dir_x *= -1
        elif dist_to_y_wall < dist_to_x_wall:
            ball.y = arena_height - b_rad if dir_y > 0 else b_rad
            dir_y *= -1
        else:
            ball.x = arena_width - b_rad if dir_x > 0 else b_rad
            ball.y = arena_height - b_rad if dir_y > 0 else b_rad
            dir_x *= -1
            dir_y *= -1

print(ball.x, ball.y)
