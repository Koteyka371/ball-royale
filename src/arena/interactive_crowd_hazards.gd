extends RefCounted

static func process_boredom(excitement_level: float, balls: Array, world) -> float:
    if excitement_level >= 20.0:
        return excitement_level

    var boredom = 20.0 - excitement_level
    var spawn_chance = 0.01 + (boredom / 20.0) * 0.19

    if randf() < spawn_chance:
        var alive_balls = []
        for b in balls:
            if typeof(b) == TYPE_OBJECT and b.has_method("get") and b.get("alive") and b.get("ball_type") != "spectator":
                alive_balls.append(b)
            elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"] and b.get("ball_type") != "spectator":
                alive_balls.append(b)

        if alive_balls.is_empty():
            return excitement_level

        var num_hazards = 1 + int((boredom / 20.0) * 2)
        var hazard_pool = ["temporary_wall", "slow_field"]
        if boredom > 10.0:
            hazard_pool.append("mini_bomb")

        for i in range(num_hazards):
            var target_ball = alive_balls[randi() % alive_balls.size()]
            var hazard_kind = hazard_pool[randi() % hazard_pool.size()]

            if world != null and world.has_method("add_event"):
                var b_x = 0.0
                var b_y = 0.0
                if typeof(target_ball) == TYPE_OBJECT and target_ball.has_method("get"):
                    b_x = float(target_ball.get("x")) if target_ball.get("x") != null else 0.0
                    b_y = float(target_ball.get("y")) if target_ball.get("y") != null else 0.0
                elif typeof(target_ball) == TYPE_DICTIONARY:
                    b_x = float(target_ball.get("x", 0.0))
                    b_y = float(target_ball.get("y", 0.0))

                world.add_event("spawn_hazard", {
                    "x": b_x + (randf() * 100.0 - 50.0),
                    "y": b_y + (randf() * 100.0 - 50.0),
                    "kind": hazard_kind
                })

        if world != null and world.has_method("add_event"):
            var msg = "The crowd boos and throws hazards into the arena!" if num_hazards > 1 else "The crowd boos and throws a hazard into the arena!"
            world.add_event("crowd_throw", {"message": msg})

        excitement_level += 5.0 + (num_hazards * 2.0)

    return excitement_level
