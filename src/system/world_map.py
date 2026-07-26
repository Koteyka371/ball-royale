import json

class WorldMapManager:
    def __init__(self, filename="world_map.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "zones" not in data:
                    data["zones"] = {}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"zones": {}}

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def register_zone(self, zone_name, buff_type, buff_value):
        if zone_name not in self.data["zones"]:
            self.data["zones"][zone_name] = {
                "buff_type": buff_type,
                "buff_value": buff_value,
                "owner_type": None,  # 'clan' or 'guild'
                "owner_name": None
            }
            self.save()
            return True
        return False

    def capture_zone(self, entity_type, entity_name, zone_name, guild_manager=None):
        if entity_type not in ["clan", "guild"]:
            return False

        if zone_name in self.data["zones"]:
            self.data["zones"][zone_name]["owner_type"] = entity_type
            self.data["zones"][zone_name]["owner_name"] = entity_name
            self.save()

            if guild_manager and entity_type == "guild":
                self.check_alliance_break(guild_manager)

            return True
        return False

    def check_alliance_break(self, guild_manager):
        visited_clusters = []

        for guild_name in guild_manager.data.get("guilds", {}):
            guild_data = guild_manager.data["guilds"][guild_name]
            if "allies" in guild_data and guild_data["allies"]:
                cluster = guild_manager.get_alliance_cluster(guild_name)

                if cluster in visited_clusters:
                    continue
                visited_clusters.append(cluster)

                allied_zones = 0
                total_zones = len(self.data["zones"])

                if total_zones == 0:
                    continue

                for z in self.data["zones"].values():
                    if z.get("owner_type") == "guild" and z.get("owner_name") in cluster:
                        allied_zones += 1

                if allied_zones == total_zones:
                    members = list(cluster)
                    for i in range(len(members)):
                        for j in range(i + 1, len(members)):
                            guild_manager.break_alliance(members[i], members[j])

    def get_zone_owner(self, zone_name):
        if zone_name in self.data["zones"]:
            return self.data["zones"][zone_name].get("owner_type"), self.data["zones"][zone_name].get("owner_name")
        return None, None

    def get_controlled_zones(self, entity_type, entity_name, guild_manager=None):
        zones = []
        cluster = {entity_name}
        if guild_manager and entity_type == "guild":
            cluster = guild_manager.get_alliance_cluster(entity_name)

        for zone_name, zone_data in self.data["zones"].items():
            if zone_data.get("owner_type") == entity_type and zone_data.get("owner_name") in cluster:
                zones.append(zone_name)
        return zones

    def get_passive_buffs(self, entity_type, entity_name, guild_manager=None):
        buffs = {}
        for zone_name in self.get_controlled_zones(entity_type, entity_name, guild_manager):
            zone_data = self.data["zones"][zone_name]
            b_type = zone_data.get("buff_type")
            b_val = zone_data.get("buff_value", 0)
            if b_type:
                buffs[b_type] = buffs.get(b_type, 0) + b_val
        return buffs

    def battle_for_zone(self, attacker_type, attacker_name, defender_type, defender_name, zone_name, attacker_score, defender_score, guild_manager=None):
        if guild_manager and attacker_type == "guild" and defender_type == "guild":
            cluster = guild_manager.get_alliance_cluster(attacker_name)
            if defender_name in cluster:
                return False

        # A simple method to resolve a battle for a zone
        owner_type, owner_name = self.get_zone_owner(zone_name)

        # If unowned, attacker takes it automatically if score > 0
        if owner_name is None:
            if attacker_score > 0:
                self.capture_zone(attacker_type, attacker_name, zone_name, guild_manager)
                return True
            return False

        # If owned, but wrong defender passed, fail
        if owner_type != defender_type or owner_name != defender_name:
            return False

        # Attacker wins if strictly greater score
        if attacker_score > defender_score:
            self.capture_zone(attacker_type, attacker_name, zone_name, guild_manager)
            return True

        return False
