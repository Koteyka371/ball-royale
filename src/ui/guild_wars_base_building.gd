class_name GuildWarsBaseBuilding
extends Reference

var guild_manager
var active_guild: String = ""
var defenses: Array = []
var available_defenses: Dictionary = {
    "turret": {"cost": 100, "hp": 500, "damage": 50},
    "wall": {"cost": 50, "hp": 1000, "damage": 0},
    "trap": {"cost": 25, "hp": 100, "damage": 200}
}

func _init(gm = null):
    guild_manager = gm

func set_guild(guild_name: String) -> void:
    active_guild = guild_name
    load_defenses()

func load_defenses() -> void:
    if active_guild == "": return
    if guild_manager != null and guild_manager.data.has("guilds") and guild_manager.data["guilds"].has(active_guild):
        var guild_data = guild_manager.data["guilds"][active_guild]
        if guild_data.has("defenses"):
            defenses = guild_data["defenses"]
        else:
            defenses = []
    else:
        defenses = []

func save_defenses() -> void:
    if active_guild == "": return
    if guild_manager != null and guild_manager.data.has("guilds") and guild_manager.data["guilds"].has(active_guild):
        guild_manager.data["guilds"][active_guild]["defenses"] = defenses
        if guild_manager.has_method("save"):
            guild_manager.save()

func build_defense(defense_type: String, x: float, y: float) -> bool:
    if active_guild == "": return false
    if not available_defenses.has(defense_type): return false

    var cost = available_defenses[defense_type]["cost"]

    if guild_manager != null and guild_manager.data.has("guilds") and guild_manager.data["guilds"].has(active_guild):
        var guild_data = guild_manager.data["guilds"][active_guild]
        var resources = 0
        if guild_data.has("resources"):
            resources = guild_data["resources"]

        if resources >= cost:
            guild_manager.data["guilds"][active_guild]["resources"] = resources - cost
            var new_defense = {
                "type": defense_type,
                "x": x,
                "y": y,
                "hp": available_defenses[defense_type]["hp"]
            }
            defenses.append(new_defense)
            save_defenses()
            return true
    return false

func remove_defense(index: int) -> bool:
    if active_guild == "": return false
    if index >= 0 and index < defenses.size():
        defenses.remove(index)
        save_defenses()
        return true
    return false
