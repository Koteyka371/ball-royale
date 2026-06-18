class_name CoachMode
extends RefCounted

var strategy = {}

func set_global_strategy(new_strategy: String):
    strategy = new_strategy

func set_team_strategy(team: String, new_strategy: String):
    if typeof(strategy) != TYPE_DICTIONARY:
        strategy = {}
    strategy[team] = new_strategy

func get_strategy():
    return strategy
