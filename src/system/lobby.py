class PreGameLobby:
    def __init__(self):
        self.selections = {}
        self.daily_quests = [
            {"description": "Survive for 5 minutes", "reward": {"skill_points": 50, "material": "Iron Ore", "material_amount": 2}},
            {"description": "Defeat 10 enemies with sniper ball", "reward": 100},
            {"description": "Heal allies for 500 HP", "reward": 75},
            {"description": "Win a Battle Royale match", "reward": {"skill_points": 200, "cosmetic": "winner_crown"}},
            {"description": "Deal 1000 damage in a single match", "reward": 150},
            {"description": "Deal 10,000 damage", "reward": {"skill_points": 300, "prestige_tokens": 1}},
            {"description": "Play 3 matches in the current weekly mutator mode", "reward": {"skill_points": 250, "cosmetic": "mutator_badge"}},
            {"description": "Get 50 kills in a single match", "reward": {"mutator_tokens": 1}},
        ]

    def get_daily_quests(self):
        import random
        return random.sample(self.daily_quests, min(3, len(self.daily_quests)))

    def assign_daily_quests_to_profile(self, profile):
        quests = self.get_daily_quests()
        for quest in quests:
            profile.add_quest(quest["description"], quest["reward"])

    def select_trap_variant(self, ball_id, variant):
        if variant in ["normal", "poison", "stun", "ricochet", "emp", "hologram", "blindness", "decoy", "mine", "elemental_mine", "warp", "clone", "tar", "link"]:
            self.selections[ball_id] = variant

    def get_trap_variant(self, ball_id):
        return self.selections.get(ball_id, "normal")

    def get_trap_level(self, ball_id):
        return self.selections.get(f"{ball_id}_trap_level", 1)

    def select_perk(self, ball_id, perk):
        key = f"{ball_id}_perks"
        if key not in self.selections:
            self.selections[key] = []
        if len(self.selections[key]) < 2 and perk not in self.selections[key]:
            self.selections[key].append(perk)

    def select_perks(self, ball_id, perks):
        key = f"{ball_id}_perks"
        self.selections[key] = []
        for perk in perks:
            self.select_perk(ball_id, perk)


    def select_traits(self, ball_id, traits):
        key = f"{ball_id}_traits"
        self.selections[key] = []
        for trait in traits:
            if trait in ["swift", "slow", "sturdy", "fragile", "lethal", "weak", "soul_dropper"]:
                self.selections[key].append(trait)

    def get_traits(self, ball_id):
        key = f"{ball_id}_traits"
        return self.selections.get(key, [])

    def get_perks(self, ball_id):
        key = f"{ball_id}_perks"
        return self.selections.get(key, [])



    def get_mutator_options(self):
        return ["low_gravity", "double_damage", "high_speed", "vampirism", "global_hp", "global_cooldown", "invisible_hazards", "kinetic_ghost", "bouncy_walls"]

    def cast_mutator_vote(self, player_id, mutator, profile, spend_currency=False, currency_type="skill_points"):
        if "mutator_votes" not in self.selections:
            self.selections["mutator_votes"] = {}

        if "player_voted_mutators" not in self.selections:
            self.selections["player_voted_mutators"] = []

        if player_id in self.selections["player_voted_mutators"]:
            return False

        if mutator not in self.get_mutator_options():
            return False

        vote_weight = 1

        if spend_currency:
            if currency_type == "skill_points":
                if profile.data.get("skill_points", 0) >= 50:
                    profile.add_skill_points(-50)
                    vote_weight = 3
                else:
                    return False
            elif currency_type == "mutator_tokens":
                if profile.data.get("mutator_tokens", 0) >= 1:
                    profile.data["mutator_tokens"] -= 1
                    profile.save()
                    vote_weight = 5
                else:
                    return False
            else:
                return False

        current_votes = self.selections["mutator_votes"].get(mutator, 0)
        self.selections["mutator_votes"][mutator] = current_votes + vote_weight
        self.selections["player_voted_mutators"].append(player_id)
        return True

    def get_winning_mutator(self):
        votes = self.selections.get("mutator_votes", {})
        if not votes:
            import random
            return random.choice(self.get_mutator_options())

        sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_votes) >= 2:
            top1 = sorted_votes[0][0]
            top2 = sorted_votes[1][0]
            if {top1, top2} == {"high_speed", "bouncy_walls"}:
                return "pinball_mutator"

        winning_mutator = sorted_votes[0][0]
        return winning_mutator

    def apply_loadout_to_ball(self, ball_id, profile, loadout_name):
        loadout = profile.get_loadout(loadout_name)
        if loadout:
            trap = loadout.get("trap_variant", "normal")
            self.select_trap_variant(ball_id, trap)
            self.selections[f"{ball_id}_trap_level"] = profile.get_trap_level(trap) if hasattr(profile, "get_trap_level") else 1
            # Store ball_type and preferred_bonuses in selections if needed by the system
            if "ball_type" in loadout:
                self.selections[f"{ball_id}_ball_type"] = loadout["ball_type"]
            if "preferred_bonuses" in loadout:
                self.selections[f"{ball_id}_preferred_bonuses"] = loadout["preferred_bonuses"]
            if loadout.get("cosmetic"):
                self.selections[f"{ball_id}_cosmetic"] = loadout["cosmetic"]
            if loadout.get("title"):
                self.selections[f"{ball_id}_title"] = loadout["title"]
            if loadout.get("badge"):
                self.selections[f"{ball_id}_badge"] = loadout["badge"]
            if "perks" in loadout:
                self.select_perks(ball_id, loadout["perks"])
            if "traits" in loadout:
                self.select_traits(ball_id, loadout["traits"])
            return True
        return False

    def apply_random_loadout(self, ball_id, profile):
        import random
        unlocked_balls = profile.data.get("unlocked_balls", ["basic"])
        if not unlocked_balls:
            unlocked_balls = ["basic"]

        ball_type = random.choice(unlocked_balls)
        trap_variants = ["normal", "poison", "stun", "ricochet", "emp", "hologram", "blindness", "chain_lightning", "decoy", "mine", "elemental_mine", "warp", "siphon", "clone", "tar", "link"]
        trap_variant = random.choice(trap_variants)

        self.select_trap_variant(ball_id, trap_variant)
        self.selections[f"{ball_id}_trap_level"] = profile.get_trap_level(trap_variant) if hasattr(profile, "get_trap_level") else 1
        self.selections[f"{ball_id}_ball_type"] = ball_type

        # Add random loadout challenge quest
        profile.add_quest("Win a match using a Random Loadout", 300)

        return True

    def apply_default_loadout(self, ball_id, profile):
        default_loadout = profile.get_default_loadout()
        if default_loadout:
            return self.apply_loadout_to_ball(ball_id, profile, default_loadout)
        return False


    def join_spectator_queue(self, player_id, target_match_id=None):
        if "spectator_queue" not in self.selections:
            self.selections["spectator_queue"] = []
        self.selections["spectator_queue"].append({"player_id": player_id, "match_id": target_match_id})
        return True

    def get_spectators_for_match(self, match_id):
        if "spectator_queue" not in self.selections:
            return []
        return [s["player_id"] for s in self.selections["spectator_queue"] if s["match_id"] == match_id or s["match_id"] is None]

lobby = PreGameLobby()
