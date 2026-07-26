class_name ClanEmissary
extends Control

var profile_manager: ProfileManager

var quests: Array = [
    {"id": "q1", "desc": "Have 5 clan members achieve a triple kill", "reward": 10},
    {"id": "q2", "desc": "Win 10 matches as a clan", "reward": 15},
    {"id": "q3", "desc": "Deal 10000 damage combined", "reward": 5}
]

var shop_items: Array = [
    {"id": "item1", "name": "Clan Banner", "cost": 10},
    {"id": "item2", "name": "Clan Icon", "cost": 5},
    {"id": "item3", "name": "XP Booster", "cost": 20}
]

var tokens_label: Label
var items_list: ItemList
var quests_list: ItemList

func _init(pm: ProfileManager):
    profile_manager = pm

    var vbox = VBoxContainer.new()
    add_child(vbox)

    tokens_label = Label.new()
    vbox.add_child(tokens_label)

    var quests_label = Label.new()
    quests_label.text = "Clan Quests:"
    vbox.add_child(quests_label)

    quests_list = ItemList.new()
    quests_list.custom_minimum_size = Vector2(300, 100)
    vbox.add_child(quests_list)

    var shop_label = Label.new()
    shop_label.text = "Emissary Shop:"
    vbox.add_child(shop_label)

    items_list = ItemList.new()
    items_list.custom_minimum_size = Vector2(300, 100)
    vbox.add_child(items_list)

    _refresh_ui()

func _refresh_ui():
    var tokens = profile_manager.data.get("emissary_tokens", 0)
    tokens_label.text = "Emissary Tokens: " + str(tokens)

    quests_list.clear()
    for q in quests:
        quests_list.add_item(q["desc"] + " (Reward: " + str(q["reward"]) + ")")

    items_list.clear()
    for item in shop_items:
        items_list.add_item(item["name"] + " (Cost: " + str(item["cost"]) + ")")

func complete_quest(quest_id: String) -> bool:
    for q in quests:
        if q["id"] == quest_id:
            var completed = profile_manager.data.get("completed_clan_quests", [])
            if not completed.has(quest_id):
                var tokens = profile_manager.data.get("emissary_tokens", 0)
                profile_manager.data["emissary_tokens"] = tokens + q["reward"]
                completed.append(quest_id)
                profile_manager.data["completed_clan_quests"] = completed
                profile_manager.save()
                _refresh_ui()
                return true
    return false

func buy_item(item_id: String) -> bool:
    var tokens = profile_manager.data.get("emissary_tokens", 0)
    for item in shop_items:
        if item["id"] == item_id and tokens >= item["cost"]:
            profile_manager.data["emissary_tokens"] = tokens - item["cost"]
            var inventory = profile_manager.data.get("clan_inventory", [])
            inventory.append(item_id)
            profile_manager.data["clan_inventory"] = inventory
            profile_manager.save()
            _refresh_ui()
            return true
    return false
