extends "res://src/ai/game_modes.gd"

var echolocation_timer: float = 0.0
var pulse_interval: float = 3.0
var pulse_duration: float = 0.5

func _init():
    name = "Echolocation Only"
    description = "Players cannot see the arena except for a tiny radius. Every few seconds, players emit a sound pulse that reveals enemies and walls momentarily."

func setup(world, balls: Array) -> void:
    .setup(world, balls)
    echolocation_timer = 0.0

    for b in balls:
        var ball_type = ""
        if typeof(b) == TYPE_DICTIONARY:
            ball_type = b.get("ball_type", "")
        elif typeof(b) == TYPE_OBJECT:
            ball_type = b.get("ball_type") if b.get("ball_type") != null else ""

        if ball_type == "spectator":
            continue

        if typeof(b) == TYPE_DICTIONARY:
            if not b.has("base_perception_radius"):
                b["base_perception_radius"] = b.get("perception_radius", 250.0)
            b["perception_radius"] = 50.0
        elif typeof(b) == TYPE_OBJECT:
            if not ("base_perception_radius" in b) and not (b.has_method("has_meta") and b.has_meta("base_perception_radius")):
                var current_radius = b.get("perception_radius") if b.get("perception_radius") != null else 250.0
                if b.has_method("set_meta"):
                    b.set_meta("base_perception_radius", current_radius)
                else:
                    b.set("base_perception_radius", current_radius)

            if b.has_method("set_meta"):
                b.set_meta("perception_radius", 50.0)
            else:
                b.set("perception_radius", 50.0)

func tick(world, balls: Array, delta: float) -> void:
    .tick(world, balls, delta)

    echolocation_timer += delta

    if echolocation_timer > (pulse_interval + pulse_duration):
        echolocation_timer = 0.0

    var is_pulsing = echolocation_timer > pulse_interval
    var current_radius = 1000.0 if is_pulsing else 50.0

    for b in balls:
        var alive = false
        var ball_type = ""

        if typeof(b) == TYPE_DICTIONARY:
            alive = b.get("alive", false)
            ball_type = b.get("ball_type", "")
        elif typeof(b) == TYPE_OBJECT:
            alive = b.get("alive") if b.get("alive") != null else false
            ball_type = b.get("ball_type") if b.get("ball_type") != null else ""

        if not alive or ball_type == "spectator":
            continue

        if typeof(b) == TYPE_DICTIONARY:
            b["perception_radius"] = current_radius
        elif typeof(b) == TYPE_OBJECT:
            if b.has_method("set_meta"):
                b.set_meta("perception_radius", current_radius)
            else:
                b.set("perception_radius", current_radius)
