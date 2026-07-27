extends Node

func ccw(ax, ay, bx, by, cx, cy):
    return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

func lines_intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    return ccw(x1, y1, x3, y3, x4, y4) != ccw(x2, y2, x3, y3, x4, y4) and ccw(x1, y1, x2, y2, x3, y3) != ccw(x1, y1, x2, y2, x4, y4)

func setup(world, balls):
    for b in balls:
        var target = b
        if typeof(b) == TYPE_DICTIONARY:
            target["lightcycle_trail"] = []
            target["last_pos_x"] = b.get("x", 0.0)
            target["last_pos_y"] = b.get("y", 0.0)
            if b.get("base_speed", 0.0) < 400.0:
                target["base_speed"] = 400.0
            if b.get("speed", 0.0) < 400.0:
                target["speed"] = 400.0
        else:
            b.set_meta("lightcycle_trail", [])
            b.set_meta("last_pos_x", b.x)
            b.set_meta("last_pos_y", b.y)
            if b.get("base_speed") != null and b.base_speed < 400.0:
                b.base_speed = 400.0
            if b.get("speed") != null and b.speed < 400.0:
                b.speed = 400.0

func tick(world, balls, delta):
    for b in balls:
        var alive = b.get("alive") if typeof(b) == TYPE_DICTIONARY else b.alive
        if not alive:
            continue

        var speed = b.get("speed") if typeof(b) == TYPE_DICTIONARY else b.speed
        if speed != null and speed < 400.0:
            if typeof(b) == TYPE_DICTIONARY:
                b["speed"] = 400.0
            else:
                b.speed = 400.0

        var b_x = b.get("x", 0.0) if typeof(b) == TYPE_DICTIONARY else b.x
        var b_y = b.get("y", 0.0) if typeof(b) == TYPE_DICTIONARY else b.y

        var last_x = b.get("last_pos_x", b_x) if typeof(b) == TYPE_DICTIONARY else (b.get_meta("last_pos_x") if b.has_meta("last_pos_x") else b_x)
        var last_y = b.get("last_pos_y", b_y) if typeof(b) == TYPE_DICTIONARY else (b.get_meta("last_pos_y") if b.has_meta("last_pos_y") else b_y)

        var dx = b_x - last_x
        var dy = b_y - last_y
        var dist_sq = dx*dx + dy*dy

        if dist_sq > 100.0:
            var trail = b.get("lightcycle_trail") if typeof(b) == TYPE_DICTIONARY else (b.get_meta("lightcycle_trail") if b.has_meta("lightcycle_trail") else [])
            trail.append([last_x, last_y, b_x, b_y])

            if typeof(b) == TYPE_DICTIONARY:
                b["last_pos_x"] = b_x
                b["last_pos_y"] = b_y
            else:
                b.set_meta("last_pos_x", b_x)
                b.set_meta("last_pos_y", b_y)

            var intersected = false

            for other_b in balls:
                var other_trail = other_b.get("lightcycle_trail") if typeof(other_b) == TYPE_DICTIONARY else (other_b.get_meta("lightcycle_trail") if other_b.has_meta("lightcycle_trail") else [])
                var check_trail = []

                if other_b == b:
                    if other_trail.size() > 2:
                        for i in range(other_trail.size() - 2):
                            check_trail.append(other_trail[i])
                else:
                    check_trail = other_trail

                for segment in check_trail:
                    if lines_intersect(last_x, last_y, b_x, b_y, segment[0], segment[1], segment[2], segment[3]):
                        intersected = true
                        break

                if intersected:
                    break

            if intersected:
                if typeof(b) == TYPE_DICTIONARY:
                    b["hp"] = 0
                    b["alive"] = false
                else:
                    b.hp = 0
                    b.alive = false
