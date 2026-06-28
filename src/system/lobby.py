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
        if variant in ["normal", "poison", "stun", "ricochet"]:
            self.selections[ball_id] = variant

    def get_trap_variant(self, ball_id):
        return self.selections.get(ball_id, "normal")

lobby = PreGameLobby()
