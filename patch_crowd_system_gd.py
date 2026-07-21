import re

with open("src/system/crowd_system.gd", "r") as f:
    content = f.read()

# 1. Update variables
init_replacement = """var active_vote = null
var votes = {}
var vote_bids = {}
var vote_auction_timer = 0
var vote_auction_active = false"""
content = re.sub(r"var active_vote = null\nvar votes = \{\}", init_replacement, content)

# 2. Update player_bribe_vote
new_player_bribe_vote = """func player_bribe_vote(player_id: String, action: String, option: String = "") -> bool:
    if active_vote == null or votes.is_empty():
        return false

    if action != "cancel" and (action != "skew" or not votes.has(option)):
        return false

    var pm = null
    if world != null and world.has_method("get_profile_manager"):
        pm = world.get_profile_manager()
    elif typeof(world) == TYPE_OBJECT and "profile_manager" in world:
        pm = world.profile_manager
    elif typeof(world) == TYPE_DICTIONARY and world.has("profile_manager"):
        pm = world["profile_manager"]

    if pm == null:
        return false

    var pm_data = null
    if typeof(pm) == TYPE_OBJECT and pm.has_method("get"):
        pm_data = pm.get("data")
    elif typeof(pm) == TYPE_DICTIONARY and pm.has("data"):
        pm_data = pm["data"]
    elif typeof(pm) == TYPE_DICTIONARY:
        pm_data = pm

    if pm_data == null:
        return false

    var currency_type = "skill_points"
    var currency_cost = int(max(10, 50 * (2.0 - corruptibility_level * 1.5)))
    var bid_power = currency_cost

    var current_sp = pm_data.get("skill_points", 0)
    var current_pt = pm_data.get("prestige_tokens", 0)

    if current_sp >= currency_cost:
        pm_data["skill_points"] = current_sp - currency_cost
    elif current_pt >= 1:
        pm_data["prestige_tokens"] = current_pt - 1
        bid_power = 100
        currency_type = "prestige_tokens"
    else:
        return false

    if vote_bids.has(player_id):
        vote_bids[player_id]["amount"] += bid_power
        vote_bids[player_id]["action"] = action
        if option != "":
            vote_bids[player_id]["option"] = option
    else:
        vote_bids[player_id] = {"amount": bid_power, "action": action, "option": option}

    if vote_bids.size() == 1:
        vote_auction_timer = 300
        if world != null and world.has_method("add_event"):
            world.add_event("bribe_attempt", {"message": "Player " + player_id + " is attempting to bribe the vote! 5 seconds to counter-bid!"})
    elif vote_bids.size() >= 2 and not vote_auction_active:
        vote_auction_active = true
        vote_auction_timer = 300
        if world != null and world.has_method("add_event"):
            world.add_event("auction_started", {"message": "Multiple players are bribing! A short auction has started!"})

    return true"""

old_player_bribe_vote = re.search(r"func player_bribe_vote.*?func _process_external_commands", content, re.DOTALL).group(0)
content = content.replace(old_player_bribe_vote, new_player_bribe_vote + "\n\nfunc _process_external_commands")

# 3. Update _process_votes
new_process_votes = """func _process_votes(balls: Array, current_tick: int):
    if vote_cooldown > 0:
        vote_cooldown -= 1

    if active_vote == null:
        if vote_cooldown == 0 and excitement_level >= 30.0 and randf() < 0.001:
            _start_vote(balls)
        return

    if not vote_bids.is_empty():
        vote_auction_timer -= 1
        if vote_auction_timer <= 0:
            _resolve_vote_auction(balls)
    else:
        vote_timer -= 1

        if not has_real_spectators:
            if randf() < 0.05:
                _simulate_spectator_vote()

        if vote_timer <= 0:
            _resolve_vote(balls)

func _resolve_vote_auction(balls: Array):
    if vote_bids.is_empty():
        return

    var winner_id = ""
    var highest_bid = -1

    for pid in vote_bids.keys():
        if vote_bids[pid]["amount"] > highest_bid:
            highest_bid = vote_bids[pid]["amount"]
            winner_id = pid

    var bid_info = vote_bids[winner_id]

    if world != null and world.has_method("add_event"):
        world.add_event("auction_ended", {"message": "Player " + winner_id + " won the bribe auction and secured the decision!"})

    var action = bid_info["action"]
    var option = bid_info["option"]

    if action == "cancel":
        if world != null and world.has_method("add_event"):
            world.add_event("vote_cancelled", {"message": "Player " + winner_id + " bribed the crowd to cancel the vote!"})
        active_vote = null
        votes.clear()
        vote_cooldown = 1000
    elif action == "skew":
        if votes.has(option):
            votes[option] += 9999
            if world != null and world.has_method("add_event"):
                world.add_event("crowd_cheer", {"message": "Player " + winner_id + " bribed the crowd to favor " + option + "!"})
            vote_timer = 0

    vote_bids.clear()
    vote_auction_active = false"""

old_process_votes = re.search(r"func _process_votes.*?func _process_spectator_signs", content, re.DOTALL).group(0)
content = content.replace(old_process_votes, new_process_votes + "\n\nfunc _process_spectator_signs")

with open("src/system/crowd_system.gd", "w") as f:
    f.write(content)
