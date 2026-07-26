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

func capture_zone(entity_type: String, entity_name: String, zone_name: String, guild_manager: Node = null) -> bool:
    if entity_type != "clan" and entity_type != "guild":
        return false

    if data["zones"].has(zone_name):
        data["zones"][zone_name]["owner_type"] = entity_type
        data["zones"][zone_name]["owner_name"] = entity_name
        save_map()

        if guild_manager != null and entity_type == "guild":
            check_alliance_break(guild_manager)

        return true
    return false

func check_alliance_break(guild_manager: Node):
    if not guild_manager.has_method("get_alliance_cluster") or not guild_manager.has_method("break_alliance"):
        return

    var visited_clusters = []

    for guild_name in guild_manager.data.get("guilds", {}).keys():
        var guild_data = guild_manager.data["guilds"][guild_name]
        if guild_data.has("allies") and guild_data["allies"].size() > 0:
            var cluster = guild_manager.get_alliance_cluster(guild_name)

            # Simple check if we already processed this cluster
            var already_visited = false
            for c in visited_clusters:
                if c.size() == cluster.size():
                    var all_match = true
                    for member in cluster:
                        if not c.has(member):
                            all_match = false
                            break
                    if all_match:
                        already_visited = true
                        break

            if already_visited:
                continue

            visited_clusters.append(cluster)

            var allied_zones = 0
            var total_zones = data["zones"].size()

            if total_zones == 0:
                continue

            for z_name in data["zones"].keys():
                var z = data["zones"][z_name]
                if z.has("owner_type") and z["owner_type"] == "guild" and z.has("owner_name") and z["owner_name"] in cluster:
                    allied_zones += 1

            if allied_zones == total_zones:
                for i in range(cluster.size()):
                    for j in range(i + 1, cluster.size()):
                        guild_manager.break_alliance(cluster[i], cluster[j])

func get_zone_owner(zone_name: String) -> Dictionary:
    if data["zones"].has(zone_name):
        var zone = data["zones"][zone_name]
        return {"owner_type": zone.get("owner_type"), "owner_name": zone.get("owner_name")}
    return {"owner_type": null, "owner_name": null}

func get_controlled_zones(entity_type: String, entity_name: String, guild_manager: Node = null) -> Array:
    var zones = []
    var cluster = [entity_name]
    if guild_manager != null and entity_type == "guild":
        if guild_manager.has_method("get_alliance_cluster"):
            cluster = guild_manager.get_alliance_cluster(entity_name)

    for zone_name in data["zones"].keys():
        var zone_data = data["zones"][zone_name]
        if zone_data.has("owner_type") and zone_data.has("owner_name"):
            if zone_data["owner_type"] == entity_type and zone_data["owner_name"] in cluster:
                zones.append(zone_name)
    return zones

func get_passive_buffs(entity_type: String, entity_name: String, guild_manager: Node = null) -> Dictionary:
    var buffs = {}
    var zones = get_controlled_zones(entity_type, entity_name, guild_manager)
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

func battle_for_zone(attacker_type: String, attacker_name: String, defender_type: String, defender_name: String, zone_name: String, attacker_score: int, defender_score: int, guild_manager: Node = null) -> bool:
    if guild_manager != null and attacker_type == "guild" and defender_type == "guild":
        if guild_manager.has_method("get_alliance_cluster"):
            var cluster = guild_manager.get_alliance_cluster(attacker_name)
            if defender_name in cluster:
                return false

    var owner_info = get_zone_owner(zone_name)
    var owner_type = owner_info["owner_type"]
    var owner_name = owner_info["owner_name"]

    if owner_name == null:
        if attacker_score > 0:
            return capture_zone(attacker_type, attacker_name, zone_name, guild_manager)
        return false

    if owner_type != defender_type or owner_name != defender_name:
        return false

    if attacker_score > defender_score:
        return capture_zone(attacker_type, attacker_name, zone_name, guild_manager)

    return false
