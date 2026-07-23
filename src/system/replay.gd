extends RefCounted
class_name ReplaySystem

var frames: Array = []
var current_frame_index: int = 0
var is_recording: bool = false
var is_playing: bool = false
var playback_speed: float = 1.0
var commentary: Array = []
var _tts_enabled: bool = false

func _init():
    if ClassDB.class_exists("DisplayServer"):
        if DisplayServer.has_method("tts_speak"):
            _tts_enabled = true

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
    if _tts_enabled and commentary.size() > 0:
        var text = commentary[0]
        var voices = DisplayServer.tts_get_voices()
        var voice_id = voices[0] if voices.size() > 0 else ""
        DisplayServer.tts_speak(text, voice_id)

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

    var kill_count = 0
    var player_ids = []
    for f in highlight.frames:
        if f.has("events"):
            for e in f["events"]:
                if typeof(e) == TYPE_DICTIONARY and e.has("type") and e["type"] == "kill":
                    kill_count += 1
                    if e.has("killer_id") and not player_ids.has(e["killer_id"]):
                        player_ids.append(e["killer_id"])

    if kill_count > 0:
        var pid_str = str(player_ids[0]) if player_ids.size() > 0 else "unknown"
        highlight.commentary.append("Incredible performance! " + str(kill_count) + " eliminations by player " + pid_str + "!")
    else:
        highlight.commentary.append("A very tense moment where survival was the only option.")

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
