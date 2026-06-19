extends RefCounted
class_name ReplaySystem

var frames: Array = []
var current_frame_index: int = 0
var is_recording: bool = false
var is_playing: bool = false
var playback_speed: float = 1.0

func _init():
    pass

func start_recording() -> void:
    frames.clear()
    is_recording = true
    is_playing = false

func stop_recording() -> void:
    is_recording = false

func record_frame(tick: int, entities: Array, events: Array) -> void:
    if not is_recording:
        return

    var entities_copy = []
    for e in entities:
        if typeof(e) == TYPE_DICTIONARY:
            entities_copy.append(e.duplicate(true))
        else:
            entities_copy.append(e) # Basic fallback

    var events_copy = []
    for e in events:
        if typeof(e) == TYPE_DICTIONARY:
            events_copy.append(e.duplicate(true))
        else:
            events_copy.append(e)

    var frame = {
        "tick": tick,
        "entities": entities_copy,
        "events": events_copy
    }
    frames.append(frame)

func start_playback(speed: float = 1.0) -> void:
    is_playing = true
    is_recording = false
    current_frame_index = 0
    playback_speed = speed

func stop_playback() -> void:
    is_playing = false

func get_next_frame():
    if not is_playing or current_frame_index >= frames.size():
        return null

    var frame = frames[current_frame_index]
    current_frame_index += 1
    return frame

func set_frame(index: int) -> void:
    if index >= 0 and index < frames.size():
        current_frame_index = index

func extract_highlight(start_tick: int, end_tick: int) -> ReplaySystem:
    var highlight = get_script().new()
    for f in frames:
        if f["tick"] >= start_tick and f["tick"] <= end_tick:
            highlight.frames.append(f.duplicate(true))
    return highlight

func to_dict() -> Dictionary:
    return {
        "frames": frames.duplicate(true),
        "version": "1.0"
    }

func from_dict(data: Dictionary) -> void:
    if data.has("frames"):
        frames = data["frames"].duplicate(true)
    else:
        frames.clear()
    current_frame_index = 0
    is_recording = false
    is_playing = false

func save_to_file(filepath: String) -> void:
    var file = FileAccess.open(filepath, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(to_dict()))

func load_from_file(filepath: String) -> void:
    var file = FileAccess.open(filepath, FileAccess.READ)
    if file:
        var content = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(content)
        if error == OK:
            from_dict(json.data)
