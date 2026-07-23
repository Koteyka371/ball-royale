class_name WorldMapManager
extends RefCounted

var filename = "user://world_map.json"
var data = {}

func _init():
    load_map()

func load_map():
    var file = FileAccess.open(filename, FileAccess.READ)
    if file:
        var text = file.get_as_text()
        var json = JSON.new()
        var error = json.parse(text)
        if error == OK:
            data = json.get_data()
            if not data.has("zones"):
                data["zones"] = {}
            return

    data = {"zones": {}}

func save_map():
    var file = FileAccess.open(filename, FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(data, "  "))

func register_zone(zone_name: String, buff_type: String, buff_value: int) -> bool:
    if not data["zones"].has(zone_name):
        data["zones"][zone_name] = {
            "buff_type": buff_type,
            "buff_value": buff_value,
            "owner_type": null,
            "owner_name": null
        }
        save_map()
        return true
    return false

func capture_zone(entity_type: String, entity_name: String, zone_name: String) -> bool:
    if entity_type != "clan" and entity_type != "guild":
        return false

    if data["zones"].has(zone_name):
        data["zones"][zone_name]["owner_type"] = entity_type
        data["zones"][zone_name]["owner_name"] = entity_name
        save_map()
        return true
    return false

func get_zone_owner(zone_name: String) -> Dictionary:
    if data["zones"].has(zone_name):
        var zone = data["zones"][zone_name]
        return {"owner_type": zone.get("owner_type"), "owner_name": zone.get("owner_name")}
    return {"owner_type": null, "owner_name": null}

func get_controlled_zones(entity_type: String, entity_name: String) -> Array:
    var zones = []
    for zone_name in data["zones"].keys():
        var zone_data = data["zones"][zone_name]
        if zone_data.has("owner_type") and zone_data.has("owner_name"):
            if zone_data["owner_type"] == entity_type and zone_data["owner_name"] == entity_name:
                zones.append(zone_name)
    return zones

func get_passive_buffs(entity_type: String, entity_name: String) -> Dictionary:
    var buffs = {}
    var zones = get_controlled_zones(entity_type, entity_name)
    for zone_name in zones:
        var zone_data = data["zones"][zone_name]
        if zone_data.has("buff_type"):
            var b_type = zone_data["buff_type"]
            var b_val = 0
            if zone_data.has("buff_value"):
                b_val = zone_data["buff_value"]

            if buffs.has(b_type):
                buffs[b_type] += b_val
            else:
                buffs[b_type] = b_val
    return buffs

func battle_for_zone(attacker_type: String, attacker_name: String, defender_type: String, defender_name: String, zone_name: String, attacker_score: int, defender_score: int) -> bool:
    var owner_info = get_zone_owner(zone_name)
    var owner_type = owner_info["owner_type"]
    var owner_name = owner_info["owner_name"]

    if owner_name == null:
        if attacker_score > 0:
            return capture_zone(attacker_type, attacker_name, zone_name)
        return false

    if owner_type != defender_type or owner_name != defender_name:
        return false

    if attacker_score > defender_score:
        return capture_zone(attacker_type, attacker_name, zone_name)

    return false
