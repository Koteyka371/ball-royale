extends VBoxContainer

var max_lines = 5
var _processed_events = {}

func _ready():
    alignment = BoxContainer.ALIGN_END

func update_feed(kill_log: Array):
    for log in kill_log:
        var tick = log.get("tick", 0)
        if log.has("type") and log.get("type") == "weather_change":
            var weather = log.get("weather", "clear")
            var event_hash = str(tick) + "_weather_" + weather
            if not _processed_events.has(event_hash):
                var message = "Tick %d: Weather changed to %s!" % [tick, weather.to_upper()]
                _add_message(message)
                _processed_events[event_hash] = true
        elif log.has("type") and log.get("type") in ["crowd_cheer", "crowd_throw"]:
            var msg = log.get("message", "")
            var event_hash = str(tick) + "_" + log.get("type") + "_" + msg
            if not _processed_events.has(event_hash):
                var message = "Tick %d: %s" % [tick, msg]
                _add_message(message)
                _processed_events[event_hash] = true
        elif log.has("type") and log.get("type") == "crowd_sign":
            var b_id = log.get("ball_id", "?")
            var msg = log.get("message", "")
            var size = log.get("size", 1.0)
            var event_hash = str(tick) + "_crowd_sign_" + str(b_id) + "_" + msg
            if not _processed_events.has(event_hash):
                _spawn_crowd_sign_popup(msg, size)
                _processed_events[event_hash] = true
        elif log.has("type") and log.get("type") in ["audio_event", "weather_warning", "spawn_booster"]:
            pass
        else:
            var killer_id = str(log.get("killer_id", "?"))
            var victim_id = str(log.get("victim_id", "?"))
            var event_hash = str(tick) + "_" + killer_id + "_" + victim_id
            if not _processed_events.has(event_hash):
                var killer_type = str(log.get("killer_type", "unknown")).to_upper()
                var victim_type = str(log.get("victim_type", "unknown")).to_upper()
                var message = "Tick %d: %s-%s killed %s-%s" % [tick, killer_type, killer_id, victim_type, victim_id]
                _add_message(message)
                _processed_events[event_hash] = true

func _add_message(message: String):
    var label = Label.new()
    label.text = message
    label.autowrap = true
    add_child(label)

    if get_child_count() > max_lines:
        var child_to_remove = get_child(0)
        remove_child(child_to_remove)
        child_to_remove.queue_free()

func clear():
    for child in get_children():
        remove_child(child)
        child.queue_free()
    _processed_events.clear()


func _spawn_crowd_sign_popup(msg: String, size: float):
    if not get_tree():
        return

    var root = get_tree().root
    if not root:
        return

    var label = Label.new()
    label.text = msg
    label.add_theme_font_size_override("font_size", int(16 * size))
    label.add_theme_color_override("font_color", Color(1, 0.8, 0.2)) # Goldish color

    # Position around the edges
    var vp_size = get_viewport_rect().size
    var margin = 50
    var x = margin
    var y = margin

    var edge = randi() % 4
    if edge == 0: # Top
        x = randf_range(margin, vp_size.x - margin)
        y = margin
    elif edge == 1: # Bottom
        x = randf_range(margin, vp_size.x - margin)
        y = vp_size.y - margin
    elif edge == 2: # Left
        x = margin
        y = randf_range(margin, vp_size.y - margin)
    else: # Right
        x = vp_size.x - margin
        y = randf_range(margin, vp_size.y - margin)

    label.position = Vector2(x, y)

    root.add_child(label)

    # Animate it slightly
    var tween = create_tween()
    tween.tween_property(label, "position", label.position + Vector2(0, -30), 2.0).set_trans(Tween.TRANS_SINE)
    tween.parallel().tween_property(label, "modulate", Color(1, 1, 1, 0), 2.0)
    tween.tween_callback(label.queue_free)
