class PreGameLobby:
    def __init__(self):
        self.selections = {}
        self.daily_quests = [
            {"description": "Survive for 5 minutes", "reward": 50},
            {"description": "Defeat 10 enemies with sniper ball", "reward": 100},
            {"description": "Heal allies for 500 HP", "reward": 75},
            {"description": "Win a Battle Royale match", "reward": 200},
            {"description": "Deal 1000 damage in a single match", "reward": 150}
        ]

    def get_daily_quests(self):
        import random
        return random.sample(self.daily_quests, min(3, len(self.daily_quests)))

    def assign_daily_quests_to_profile(self, profile):
        quests = self.get_daily_quests()
        for quest in quests:
            profile.add_quest(quest["description"], quest["reward"])

    def select_trap_variant(self, ball_id, variant):
        if variant in ["normal", "poison", "stun", "ricochet", "emp", "hologram", "blindness"]:
            self.selections[ball_id] = variant

    def get_trap_variant(self, ball_id):
        return self.selections.get(ball_id, "normal")


    def apply_loadout_to_ball(self, ball_id, profile, loadout_name):
        loadout = profile.get_loadout(loadout_name)
        if loadout:
            trap = loadout.get("trap_variant", "normal")
            self.select_trap_variant(ball_id, trap)
            # Store ball_type and preferred_bonuses in selections if needed by the system
            if "ball_type" in loadout:
                self.selections[f"{ball_id}_ball_type"] = loadout["ball_type"]
            if "preferred_bonuses" in loadout:
                self.selections[f"{ball_id}_preferred_bonuses"] = loadout["preferred_bonuses"]
            if loadout.get("cosmetic"):
                self.selections[f"{ball_id}_cosmetic"] = loadout["cosmetic"]
            if loadout.get("title"):
                self.selections[f"{ball_id}_title"] = loadout["title"]
            return True
        return False

    def apply_random_loadout(self, ball_id, profile):
        import random
        unlocked_balls = profile.data.get("unlocked_balls", ["basic"])
        if not unlocked_balls:
            unlocked_balls = ["basic"]

        ball_type = random.choice(unlocked_balls)
        trap_variants = ["normal", "poison", "stun", "ricochet", "emp", "hologram", "blindness"]
        trap_variant = random.choice(trap_variants)

        self.select_trap_variant(ball_id, trap_variant)
        self.selections[f"{ball_id}_ball_type"] = ball_type

        # Add random loadout challenge quest
        profile.add_quest("Win a match using a Random Loadout", 300)

        return True

    def apply_default_loadout(self, ball_id, profile):
        default_loadout = profile.get_default_loadout()
        if default_loadout:
            return self.apply_loadout_to_ball(ball_id, profile, default_loadout)
        return False

lobby = PreGameLobby()
