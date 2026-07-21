import re

with open("src/system/crowd_system.py", "r") as f:
    content = f.read()

# 1. Update __init__
init_replacement = """        self.active_vote = None
        self.votes = {}
        self.vote_bids = {}
        self.vote_auction_timer = 0
        self.vote_auction_active = False"""
content = re.sub(r"        self\.active_vote = None\n        self\.votes = {}", init_replacement, content)

# 2. Update player_bribe_vote
new_player_bribe_vote = """    def player_bribe_vote(self, player_id: str, action: str, option: str = None) -> bool:
        if not self.active_vote or not self.votes:
            return False

        if action != "cancel" and (action != "skew" or option not in self.votes):
            return False

        pm = None
        if hasattr(self.world, "get_profile_manager"):
            pm = self.world.get_profile_manager()
        elif hasattr(self.world, "profile_manager"):
            pm = self.world.profile_manager

        if not pm or not hasattr(pm, "data"):
            return False

        currency_type = "skill_points"
        currency_cost = max(10, int(50 * (2.0 - self.corruptibility_level * 1.5)))
        bid_power = currency_cost

        if pm.data.get("skill_points", 0) >= currency_cost:
            pm.data["skill_points"] -= currency_cost
        elif pm.data.get("prestige_tokens", 0) >= 1:
            pm.data["prestige_tokens"] -= 1
            bid_power = 100
            currency_type = "prestige_tokens"
        else:
            return False

        if not hasattr(self, 'vote_bids'):
            self.vote_bids = {}
            self.vote_auction_timer = 0
            self.vote_auction_active = False

        if player_id in self.vote_bids:
            self.vote_bids[player_id]["amount"] += bid_power
            self.vote_bids[player_id]["action"] = action
            if option:
                self.vote_bids[player_id]["option"] = option
        else:
            self.vote_bids[player_id] = {"amount": bid_power, "action": action, "option": option}

        if len(self.vote_bids) == 1:
            self.vote_auction_timer = 300
            if hasattr(self.world, 'add_event'):
                self.world.add_event("bribe_attempt", {"message": f"Player {player_id} is attempting to bribe the vote! 5 seconds to counter-bid!"})
        elif len(self.vote_bids) >= 2 and not self.vote_auction_active:
            self.vote_auction_active = True
            self.vote_auction_timer = 300
            if hasattr(self.world, 'add_event'):
                self.world.add_event("auction_started", {"message": "Multiple players are bribing! A short auction has started!"})

        return True"""

old_player_bribe_vote = re.search(r"    def player_bribe_vote.*?return False", content, re.DOTALL).group(0)
# we actually want to match up to the end of the original function.
# so we match up to "def _process_external_commands"
old_player_bribe_vote = re.search(r"    def player_bribe_vote.*?def _process_external_commands", content, re.DOTALL).group(0)
content = content.replace(old_player_bribe_vote, new_player_bribe_vote + "\n\n    def _process_external_commands")


# 3. Update _process_votes
new_process_votes = """    def _process_votes(self, balls: List[Any], tick: int):
        if self.vote_cooldown > 0:
            self.vote_cooldown -= 1

        if self.active_vote is None:
            # 1 in 1000 chance per tick to start a vote if excitement is decent
            if self.vote_cooldown == 0 and self.excitement_level >= 30.0 and random.random() < 0.001:
                self._start_vote(balls)
            return

        if hasattr(self, 'vote_bids') and self.vote_bids:
            self.vote_auction_timer -= 1
            if self.vote_auction_timer <= 0:
                self._resolve_vote_auction(balls)
        else:
            # Handle active vote
            self.vote_timer -= 1

            # Simulate spectators casting votes
            if not self.has_real_spectators:
                if random.random() < 0.05:  # Random spectator votes
                    self._simulate_spectator_vote()

            if self.vote_timer <= 0:
                self._resolve_vote(balls)

    def _resolve_vote_auction(self, balls: List[Any]):
        if not self.vote_bids:
            return

        highest_bidder = max(self.vote_bids.items(), key=lambda x: x[1]["amount"])
        winner_id = highest_bidder[0]
        bid_info = highest_bidder[1]

        if hasattr(self.world, 'add_event'):
            self.world.add_event("auction_ended", {"message": f"Player {winner_id} won the bribe auction and secured the decision!"})

        action = bid_info["action"]
        option = bid_info["option"]

        if action == "cancel":
            if hasattr(self.world, 'add_event'):
                self.world.add_event("vote_cancelled", {"message": f"Player {winner_id} bribed the crowd to cancel the vote!"})
            self.active_vote = None
            self.votes = {}
            self.vote_cooldown = 1000
        elif action == "skew":
            if option in self.votes:
                self.votes[option] += 9999
                if hasattr(self.world, 'add_event'):
                    self.world.add_event("crowd_cheer", {"message": f"Player {winner_id} bribed the crowd to favor {option}!"})
                self.vote_timer = 0

        self.vote_bids = {}
        self.vote_auction_active = False"""

old_process_votes = re.search(r"    def _process_votes.*?def _process_spectator_signs", content, re.DOTALL).group(0)
content = content.replace(old_process_votes, new_process_votes + "\n\n    def _process_spectator_signs")

with open("src/system/crowd_system.py", "w") as f:
    f.write(content)
