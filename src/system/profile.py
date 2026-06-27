import json

class ProfileManager:
    def __init__(self, filename="profile.json"):
        self.filename = filename
        self.data = self.load()

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
                }
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
