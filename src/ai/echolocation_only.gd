extends "res://src/ai/game_modes.gd".GameMode

class_name EcholocationOnlyMode

var pulse_timer = 0.0
var pulse_interval = 4.0
var is_pulsing = false
var pulse_duration = 0.5
var current_pulse_time = 0.0

func _init().():
    name = "Echolocation Only"
    description = "Players cannot see the arena except for a tiny radius. Every few seconds, players emit a sound pulse that reveals enemies and walls momentarily."

func setup(world, balls: Array) -> void:
    .setup(world, balls)
    pulse_timer = 0.0
    is_pulsing = false
    current_pulse_time = 0.0

    if world != null and "arena" in world and world.arena != null:
        world.arena.is_night = true

    for b in balls:
        var b_type = b.get("ball_type") if typeof(b) == TYPE_DICTIONARY else (b.ball_type if "ball_type" in b else null)
        if b_type != "spectator":
            var base_perc = 250.0
            if typeof(b) == TYPE_DICTIONARY:
                if b.has("perception_radius"):
                    base_perc = float(b.perception_radius)
                b["base_perception_radius"] = base_perc
                b["perception_radius"] = 15.0
            else:
                if "perception_radius" in b:
                    base_perc = float(b.perception_radius)
                if b.has_method("set_meta"):
                    b.set_meta("base_perception_radius", base_perc)
                elif "base_perception_radius" in b:
                    b.base_perception_radius = base_perc
                b.perception_radius = 15.0

func tick(world, balls: Array, delta: float = 0.016) -> void:
    .tick(world, balls, delta)

    pulse_timer += delta

    if is_pulsing:
        current_pulse_time += delta
        if current_pulse_time >= pulse_duration:
            is_pulsing = false
            for b in balls:
                var is_alive = false
                var b_type = null
                if typeof(b) == TYPE_DICTIONARY:
                    is_alive = b.get("alive", false)
                    b_type = b.get("ball_type")
                else:
                    is_alive = b.get("alive") if "alive" in b else false
                    b_type = b.get("ball_type") if "ball_type" in b else null

                if is_alive and b_type != "spectator":
                    if typeof(b) == TYPE_DICTIONARY:
                        b["perception_radius"] = 15.0
                    else:
                        b.perception_radius = 15.0
    else:
        if pulse_timer >= pulse_interval:
            pulse_timer = 0.0
            is_pulsing = true
            current_pulse_time = 0.0

            if world != null and world.has_method("add_event"):
                world.add_event("sound_pulse", {"type": "sound_pulse", "message": "Sound pulse reveals the arena!"})

            for b in balls:
                var is_alive = false
                var b_type = null
                var base_perc = 250.0
                if typeof(b) == TYPE_DICTIONARY:
                    is_alive = b.get("alive", false)
                    b_type = b.get("ball_type")
                    base_perc = b.get("base_perception_radius", 250.0)
                else:
                    is_alive = b.get("alive") if "alive" in b else false
                    b_type = b.get("ball_type") if "ball_type" in b else null
                    if b.has_method("get_meta") and b.has_meta("base_perception_radius"):
                        base_perc = b.get_meta("base_perception_radius")
                    elif "base_perception_radius" in b:
                        base_perc = b.base_perception_radius

                if is_alive and b_type != "spectator":
                    if typeof(b) == TYPE_DICTIONARY:
                        b["perception_radius"] = base_perc
                    else:
                        b.perception_radius = base_perc
