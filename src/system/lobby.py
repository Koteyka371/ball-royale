class PreGameLobby:
    def __init__(self):
        self.selections = {}
        self.banned_ball_types = []
        self.team_picks = {}
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
        if variant in ["normal", "poison", "stun", "ricochet", "emp"]:
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
            return True
        return False

    def ban_ball_type(self, team_id: str, ball_type: str) -> bool:
        if ball_type not in self.banned_ball_types:
            self.banned_ball_types.append(ball_type)
            return True
        return False

    def pick_ball_type(self, team_id: str, ball_type: str) -> bool:
        if ball_type in self.banned_ball_types:
            return False

        for picks in self.team_picks.values():
            if ball_type in picks:
                return False

        if team_id not in self.team_picks:
            self.team_picks[team_id] = []

        self.team_picks[team_id].append(ball_type)
        return True

lobby = PreGameLobby()
