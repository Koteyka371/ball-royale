class_name ProfileManager
extends RefCounted

var filename = "user://profile.json"
var data = {}

func _init():
    load_profile()
    get_daily_quests()  # Ensure quests are updated on load

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
        },
        "daily_quests": [],
        "last_login_date": ""
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

func get_daily_quests() -> Array:
    var time_dict = Time.get_datetime_dict_from_system()
    var today = str(time_dict.year) + "-" + str(time_dict.month).pad_zeros(2) + "-" + str(time_dict.day).pad_zeros(2)

    if not data.has("daily_quests"):
        data["daily_quests"] = []
    if not data.has("last_login_date"):
        data["last_login_date"] = ""

    if data["last_login_date"] != today:
        var possible_quests = [
            {"id": "survive_5_min", "description": "Survive for 5 minutes", "type": "survive_time", "target": 300, "progress": 0, "reward": 50, "completed": false},
            {"id": "defeat_10_sniper", "description": "Defeat 10 enemies with sniper ball", "type": "kill_with_sniper", "target": 10, "progress": 0, "reward": 50, "completed": false},
            {"id": "play_3_matches", "description": "Play 3 matches", "type": "play_matches", "target": 3, "progress": 0, "reward": 30, "completed": false},
            {"id": "win_1_match", "description": "Win 1 match", "type": "win_match", "target": 1, "progress": 0, "reward": 100, "completed": false},
            {"id": "deal_1000_damage", "description": "Deal 1000 damage", "type": "deal_damage", "target": 1000, "progress": 0, "reward": 40, "completed": false}
        ]

        possible_quests.shuffle()
        data["daily_quests"] = [possible_quests[0], possible_quests[1], possible_quests[2]]
        data["last_login_date"] = today
        save_profile()

    return data["daily_quests"]

func update_quest_progress(quest_type: String, amount: int = 1) -> void:
    if not data.has("daily_quests"):
        return

    var updated = false
    for i in range(data["daily_quests"].size()):
        var quest = data["daily_quests"][i]
        if quest["type"] == quest_type and not quest["completed"]:
            quest["progress"] = min(quest["progress"] + amount, quest["target"])
            if quest["progress"] >= quest["target"]:
                quest["completed"] = true
                add_skill_points(quest["reward"])
            updated = true

    if updated:
        save_profile()
