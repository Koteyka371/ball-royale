class_name ProfileManager
extends RefCounted

var filename = "user://profile.json"
var data = {}

func _init():
    load_profile()

func load_profile():
    var file = FileAccess.open(filename, FileAccess.READ)
    if file:
        var text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            data = json.get_data()
            return

    # Default profile
    data = {
        "skill_points": 0,
        "unlocked_balls": ["basic"],
        "bonuses": {
            "bonus_hp": 0,
            "bonus_speed": 0,
            "bonus_damage": 0
        }
    }

func save_profile():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))

func add_skill_points(points: int):
    data["skill_points"] += points
    save_profile()

func unlock_ball(ball_name: String, cost: int) -> bool:
    if data["skill_points"] >= cost and not data["unlocked_balls"].has(ball_name):
        data["skill_points"] -= cost
        data["unlocked_balls"].append(ball_name)
        save_profile()
        return true
    return false

func upgrade_bonus(bonus_name: String, cost: int) -> bool:
    if data["bonuses"].has(bonus_name) and data["skill_points"] >= cost:
        data["skill_points"] -= cost
        data["bonuses"][bonus_name] += 1
        save_profile()
        return true
    return false
