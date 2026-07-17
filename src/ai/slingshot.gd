extends "res://src/ai/game_modes.gd"

class SlingshotMode extends "res://src/ai/game_modes.gd".GameMode:
    func _init():
        #super._init()
        self.name = "Slingshot Mode"
        self.description = "Players can only move by dragging and releasing a slingshot mechanism, and deal damage based on speed upon collision with other players."

    func tick(world, balls, delta=0.016):
        #super.tick(world, balls, delta)
        for b in balls:
            b.speed = 0.0
            if not b.has_meta("slingshot_timer"):
                b.set_meta("slingshot_timer", randf_range(1.0, 3.0))
                b.set_meta("slingshot_pulling", false)

            var pulling = b.get_meta("slingshot_pulling")
            var timer = b.get_meta("slingshot_timer")

            if pulling:
                timer -= delta
                if timer <= 0:
                    b.set_meta("slingshot_pulling", false)
                    b.set_meta("slingshot_timer", randf_range(1.0, 3.0))
                    var angle = randf_range(0, 2 * PI)
                    var force = randf_range(800.0, 1500.0)
                    if "vx" in b: b.vx += cos(angle) * force
                    if "vy" in b: b.vy += sin(angle) * force
                else:
                    b.set_meta("slingshot_timer", timer)
            else:
                timer -= delta
                if timer <= 0:
                    b.set_meta("slingshot_pulling", true)
                    b.set_meta("slingshot_timer", randf_range(0.5, 1.5))
                else:
                    b.set_meta("slingshot_timer", timer)

            var vx = 0.0
            var vy = 0.0
            if "vx" in b: vx = b.vx
            if "vy" in b: vy = b.vy
            var speed_mag = sqrt(vx*vx + vy*vy)
            var base_dmg = 10.0
            if "base_damage" in b: base_dmg = b.base_damage
            if "damage" in b: b.damage = base_dmg + (speed_mag * 0.05)
