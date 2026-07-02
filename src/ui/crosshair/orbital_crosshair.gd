extends Control

var crosshair_positions: Array = []
var pulse_time: float = 0.0

func _process(delta: float) -> void:
    if crosshair_positions.size() > 0:
        pulse_time += delta
        queue_redraw()

func update_crosshairs(hazards: Array):
    crosshair_positions.clear()
    for hazard in hazards:
        var is_orbital = false
        var show_ch = false
        var h_x = 0.0
        var h_y = 0.0
        var h_r = 400.0

        if typeof(hazard) == TYPE_DICTIONARY:
            if hazard.get("kind", "") == "orbital_strike":
                is_orbital = true
            show_ch = hazard.get("show_crosshair", false)
            h_x = hazard.get("x", 0.0)
            h_y = hazard.get("y", 0.0)
            h_r = hazard.get("radius", 400.0)
        elif typeof(hazard) == TYPE_OBJECT:
            if "kind" in hazard and hazard.kind == "orbital_strike":
                is_orbital = true
            if hazard.has_method("has_meta") and hazard.has_meta("show_crosshair"):
                show_ch = hazard.get_meta("show_crosshair")
            elif "show_crosshair" in hazard:
                show_ch = hazard.show_crosshair

            if "x" in hazard: h_x = hazard.x
            if "y" in hazard: h_y = hazard.y
            if "radius" in hazard: h_r = hazard.radius

        if is_orbital and show_ch:
            crosshair_positions.append({"x": h_x, "y": h_y, "radius": h_r})

func _draw() -> void:
    for ch in crosshair_positions:
        var pos = Vector2(ch["x"], ch["y"])
        var radius = ch["radius"]

        # Pulse alpha between 0.3 and 0.8
        var alpha = 0.3 + (sin(pulse_time * 10.0) + 1.0) * 0.25
        var color = Color(1.0, 0.0, 0.0, alpha)

        # Draw outer circle
        draw_arc(pos, radius, 0.0, TAU, 32, color, 4.0)

        # Draw crosshair lines
        var inner_r = radius * 0.2
        draw_line(pos + Vector2(-radius, 0), pos + Vector2(-inner_r, 0), color, 6.0)
        draw_line(pos + Vector2(radius, 0), pos + Vector2(inner_r, 0), color, 6.0)
        draw_line(pos + Vector2(0, -radius), pos + Vector2(0, -inner_r), color, 6.0)
        draw_line(pos + Vector2(0, radius), pos + Vector2(0, inner_r), color, 6.0)
