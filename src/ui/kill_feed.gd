extends VBoxContainer

var max_lines = 5
var _processed_events = {}

func _ready():
    alignment = BoxContainer.ALIGN_END

func update_feed(kill_log: Array):
    for log in kill_log:
        var tick = log.get("tick", 0)
        if log.has("type") and log.get("type") == "weather_warning":
            var weather = log.get("weather", "clear")
            var event_hash = str(tick) + "_weather_warning_" + weather
            if not _processed_events.has(event_hash):
                var message = "Tick %d: WARNING! %s approaching!" % [tick, weather.to_upper()]
                _add_message(message)
                _processed_events[event_hash] = true
        elif log.has("type") and log.get("type") == "weather_change":
            var weather = log.get("weather", "clear")
            var event_hash = str(tick) + "_weather_" + weather
            if not _processed_events.has(event_hash):
                var message = "Tick %d: Weather changed to %s!" % [tick, weather.to_upper()]
                _add_message(message)
                _processed_events[event_hash] = true
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
