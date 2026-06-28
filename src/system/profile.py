import json

class ProfileManager:
    def __init__(self, filename="profile.json"):
        self.filename = filename
        self.data = self.load()
        self.get_daily_quests()  # Ensure quests are updated on load

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
                        return {
                "skill_points": 0,
                "unlocked_balls": ["basic"],
                "bonuses": {
                    "bonus_hp": 0,
                    "bonus_speed": 0,
                    "bonus_damage": 0
                },
                "daily_quests": [],
                "last_login_date": ""
            }

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_skill_points(self, points):
        self.data["skill_points"] += points
        self.save()

    def unlock_ball(self, ball_name, cost):
        if self.data["skill_points"] >= cost and ball_name not in self.data["unlocked_balls"]:
            self.data["skill_points"] -= cost
            self.data["unlocked_balls"].append(ball_name)
            self.save()
            return True
        return False

    def upgrade_bonus(self, bonus_name, cost):
        if bonus_name in self.data["bonuses"] and self.data["skill_points"] >= cost:
            self.data["skill_points"] -= cost
            self.data["bonuses"][bonus_name] += 1
            self.save()
            return True
        return False

    def get_daily_quests(self):
        import datetime
        import random

        today = datetime.date.today().isoformat()

        # Initialize if missing
        if "daily_quests" not in self.data:
            self.data["daily_quests"] = []
        if "last_login_date" not in self.data:
            self.data["last_login_date"] = ""

        if self.data["last_login_date"] != today:
            # Generate new daily quests
            possible_quests = [
                {"id": "survive_5_min", "description": "Survive for 5 minutes", "type": "survive_time", "target": 300, "progress": 0, "reward": 50, "completed": False},
                {"id": "defeat_10_sniper", "description": "Defeat 10 enemies with sniper ball", "type": "kill_with_sniper", "target": 10, "progress": 0, "reward": 50, "completed": False},
                {"id": "play_3_matches", "description": "Play 3 matches", "type": "play_matches", "target": 3, "progress": 0, "reward": 30, "completed": False},
                {"id": "win_1_match", "description": "Win 1 match", "type": "win_match", "target": 1, "progress": 0, "reward": 100, "completed": False},
                {"id": "deal_1000_damage", "description": "Deal 1000 damage", "type": "deal_damage", "target": 1000, "progress": 0, "reward": 40, "completed": False}
            ]
            self.data["daily_quests"] = random.sample(possible_quests, 3)
            self.data["last_login_date"] = today
            self.save()

        return self.data["daily_quests"]

    def update_quest_progress(self, quest_type, amount=1):
        if "daily_quests" not in self.data:
            return

        updated = False
        for quest in self.data["daily_quests"]:
            if quest["type"] == quest_type and not quest["completed"]:
                quest["progress"] = min(quest["progress"] + amount, quest["target"])
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
                    self.add_skill_points(quest["reward"])
                updated = True

        if updated:
            self.save()
