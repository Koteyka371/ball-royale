extends SceneTree

func _init():
    var script = load("res://src/ai/game_modes.gd")
    var lines = FileAccess.get_file_as_string("res://src/ai/game_modes.gd").split("\n")
    var i = 0
    while i < lines.size():
        if "class BattleRoyaleMode extends GameMode:" in lines[i]:
            print("Found GDScript BR")
        i += 1
    quit()
