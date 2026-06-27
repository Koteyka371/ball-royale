class_name CoachMode
extends RefCounted

var strategy = {}
var danger_overlay = null

func _init():
    var script = load("res://src/ui/heatmap/danger_grid_overlay.gd")
    if script:
        danger_overlay = script.new()

func set_global_strategy(new_strategy: String):

    strategy = new_strategy

func set_team_strategy(team: String, new_strategy: String):
    if typeof(strategy) != TYPE_DICTIONARY:
        strategy = {}
    strategy[team] = new_strategy

func get_strategy():
    return strategy

func update_danger_ui(grid: Dictionary):
    if danger_overlay:
        danger_overlay.update_danger_grid(grid)
