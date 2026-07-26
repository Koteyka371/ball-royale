import json
import os

class ClanEmissary:
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager
        self.quests = [
            {"id": "q1", "desc": "Have 5 clan members achieve a triple kill", "reward": 10},
            {"id": "q2", "desc": "Win 10 matches as a clan", "reward": 15},
            {"id": "q3", "desc": "Deal 10000 damage combined", "reward": 5}
        ]
        self.shop_items = [
            {"id": "item1", "name": "Clan Banner", "cost": 10},
            {"id": "item2", "name": "Clan Icon", "cost": 5},
            {"id": "item3", "name": "XP Booster", "cost": 20}
        ]

    def render_ui(self):
        tokens = self.profile_manager.data.get("emissary_tokens", 0)
        return {
            "quests": self.quests,
            "shop_items": self.shop_items,
            "emissary_tokens": tokens
        }

    def complete_quest(self, quest_id):
        for quest in self.quests:
            if quest["id"] == quest_id:
                completed = self.profile_manager.data.get("completed_clan_quests", [])
                if quest_id not in completed:
                    tokens = self.profile_manager.data.get("emissary_tokens", 0)
                    self.profile_manager.data["emissary_tokens"] = tokens + quest["reward"]
                    completed.append(quest_id)
                    self.profile_manager.data["completed_clan_quests"] = completed
                    self.profile_manager.save()
                    return True
        return False

    def buy_item(self, item_id):
        tokens = self.profile_manager.data.get("emissary_tokens", 0)
        for item in self.shop_items:
            if item["id"] == item_id and tokens >= item["cost"]:
                self.profile_manager.data["emissary_tokens"] = tokens - item["cost"]
                inventory = self.profile_manager.data.get("clan_inventory", [])
                inventory.append(item_id)
                self.profile_manager.data["clan_inventory"] = inventory
                self.profile_manager.save()
                return True
        return False
