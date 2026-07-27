extends "res://src/ai/game_modes.gd"

class_name ReflectiveWallsArena

var walls = []

func _init():
    self.name = "Reflective Walls Arena"
    self.description = "Certain walls bounce projectiles back perfectly, creating more geometry puzzles for aiming."

func setup(world, balls):
    super.setup(world, balls)
    walls = []

    var arena_width = 1000.0
    if "arena" in world and world.arena != null:
        if "width" in world.arena:
            arena_width = world.arena.width

    var arena_height = 1000.0
    if "arena" in world and world.arena != null:
        if "height" in world.arena:
            arena_height = world.arena.height

    var cx = arena_width / 2.0
    var cy = arena_height / 2.0

    walls.append({"x": cx - 250, "y": cy - 150, "width": 20, "height": 300})
    walls.append({"x": cx + 230, "y": cy - 150, "width": 20, "height": 300})
    walls.append({"x": cx - 150, "y": cy - 250, "width": 300, "height": 20})
    walls.append({"x": cx - 150, "y": cy + 230, "width": 300, "height": 20})

func tick(world, balls, delta=0.016):
    var projectiles = []
    if "projectiles" in world:
        projectiles = world.projectiles
    var hazards = []
    if "arena" in world and "hazards" in world.arena:
        hazards = world.arena.hazards

    for lst in [projectiles, hazards]:
        for obj in lst:
            var is_proj = false
            if typeof(obj) == TYPE_OBJECT and obj.has_method("get_meta"):
                if obj.get_meta("is_projectile") == true:
                    is_proj = true
            if "is_projectile" in obj and obj.is_projectile:
                is_proj = true
            var kind = ""
            if "kind" in obj:
                kind = obj.kind
            elif typeof(obj) == TYPE_DICTIONARY and obj.has("kind"):
                kind = obj["kind"]

            if kind in ["projectile", "fireball", "spell", "fireball_projectile", "starlight_projectile", "bullet", "snipe", "laser_beam"]:
                is_proj = true

            if not is_proj:
                continue

            var ox = obj.x if "x" in obj else (obj["x"] if typeof(obj) == TYPE_DICTIONARY else 0.0)
            var oy = obj.y if "y" in obj else (obj["y"] if typeof(obj) == TYPE_DICTIONARY else 0.0)

            for wall in walls:
                var wx = wall.x if "x" in wall else (wall["x"] if typeof(wall) == TYPE_DICTIONARY else 0.0)
                var wy = wall.y if "y" in wall else (wall["y"] if typeof(wall) == TYPE_DICTIONARY else 0.0)
                var ww = wall.width if "width" in wall else (wall["width"] if typeof(wall) == TYPE_DICTIONARY else 0.0)
                var wh = wall.height if "height" in wall else (wall["height"] if typeof(wall) == TYPE_DICTIONARY else 0.0)

                if ox >= wx and ox <= wx + ww and oy >= wy and oy <= wy + wh:
                    var dist_l = abs(ox - wx)
                    var dist_r = abs(ox - (wx + ww))
                    var dist_t = abs(oy - wy)
                    var dist_b = abs(oy - (wy + wh))

                    var min_dist = min(dist_l, min(dist_r, min(dist_t, dist_b)))
                    var nx = 0.0
                    var ny = 0.0

                    if min_dist == dist_l:
                        nx = -1.0
                    elif min_dist == dist_r:
                        nx = 1.0
                    elif min_dist == dist_t:
                        ny = -1.0
                    elif min_dist == dist_b:
                        ny = 1.0

                    var vx = obj.vx if "vx" in obj else (obj["vx"] if typeof(obj) == TYPE_DICTIONARY else 0.0)
                    var vy = obj.vy if "vy" in obj else (obj["vy"] if typeof(obj) == TYPE_DICTIONARY else 0.0)
                    var dot = vx * nx + vy * ny

                    if dot < 0:
                        var nvx = vx - 2 * dot * nx
                        var nvy = vy - 2 * dot * ny
                        if typeof(obj) == TYPE_DICTIONARY:
                            obj["vx"] = nvx
                            obj["vy"] = nvy
                        else:
                            obj.vx = nvx
                            obj.vy = nvy
