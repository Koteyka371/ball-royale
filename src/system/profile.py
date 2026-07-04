import time
import json
import datetime
import base64
import zlib
from system.leaderboard import LeaderboardManager

class ProfileManager:
    TOTAL_BALLS = 34
    MAX_BONUS_LEVEL = 10

    def __init__(self, filename="profile.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "inventory" not in data:
                    data["inventory"] = {"materials": {}, "crafted_items": {}}
                if "loadouts" not in data:
                    data["loadouts"] = {}
                if "quests" not in data:
                    data["quests"] = []
                if "cosmetics" not in data:
                    data["cosmetics"] = []
                if "titles" not in data:
                    data["titles"] = []
                if "status_effects" not in data:
                    data["status_effects"] = []
                if "nemeses" not in data:
                    data["nemeses"] = {}
                if "login_streak" not in data:
                    data["login_streak"] = 0
                if "last_login_date" not in data:
                    data["last_login_date"] = ""
                if "guild_name" not in data:
                    data["guild_name"] = ""
                if "clan_name" not in data:
                    data["clan_name"] = ""
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "skill_points": 0,
                "inventory": {"materials": {}, "crafted_items": {}},
                "unlocked_balls": ["basic"],
                "bonuses": {
                    "bonus_hp": 0,
                    "bonus_speed": 0,
                    "bonus_damage": 0
                },
                "loadouts": {},
                "prestige_level": 0,
                "prestige_tokens": 0,
                "prestige_upgrades": {},
                "quests": [],
                "cosmetics": [],
                "titles": [],
                "status_effects": [],
                "nemeses": {},
                "login_streak": 0,
                "last_login_date": "",
                "guild_name": "",
                "clan_name": ""
            }

    def add_quest(self, quest_description, reward):
        if "quests" not in self.data:
            self.data["quests"] = []
        self.data["quests"].append({
            "description": quest_description,
            "reward": reward,
            "completed": False
        })
        self.save()

    def get_quests(self):
        return self.data.get("quests", [])

    def complete_quest(self, quest_index):
        if "quests" in self.data and 0 <= quest_index < len(self.data["quests"]):
            quest = self.data["quests"][quest_index]
            if not quest.get("completed", False):
                quest["completed"] = True
                self.add_skill_points(quest["reward"])
                return True
        return False

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)


    def _get_catchup_multiplier(self):
        try:
            filename = "test_leaderboard_catchup.json" if "test" in self.filename else "leaderboard.json"
            with open(filename, 'r') as f:
                import json
                data = json.load(f)
                start_time = data.get("season_start_time", time.time())
                elapsed = time.time() - start_time
                duration = 30 * 24 * 60 * 60
                if elapsed > duration * 0.75:
                    return 1.5
                elif elapsed > duration * 0.5:
                    return 1.25
        except Exception:
            pass
        return 1.0

    def add_skill_points(self, points):
        points = int(points * self._get_catchup_multiplier())
        self.data["skill_points"] += points
        self.save()


    def get_unlocked_balls(self):
        unlocked = list(self.data.get("unlocked_balls", []))
        if self.data.get("prestige_upgrades", {}).get("unlock_time_mage", 0) > 0:
            if "time_mage" not in unlocked:
                unlocked.append("time_mage")
        return unlocked

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

    def are_mutators_unlocked(self):
        return self.data.get("prestige_level", 0) >= 5 or self.data.get("prestige_upgrades", {}).get("mutator_unlocked", 0) > 0

    def can_prestige(self):
        unlocked_all_balls = len(self.get_unlocked_balls()) >= self.TOTAL_BALLS
        maxed_hp = self.data.get("bonuses", {}).get("bonus_hp", 0) >= self.MAX_BONUS_LEVEL
        maxed_speed = self.data.get("bonuses", {}).get("bonus_speed", 0) >= self.MAX_BONUS_LEVEL
        maxed_damage = self.data.get("bonuses", {}).get("bonus_damage", 0) >= self.MAX_BONUS_LEVEL
        return unlocked_all_balls and maxed_hp and maxed_speed and maxed_damage


    def _to_roman(self, num):
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num

    def do_prestige(self):
        if self.can_prestige():
            prestige_level = self.data.get("prestige_level", 0) + 1
            # Calculate prestige tokens based on past stats (skill points, current prestige, maxed bonuses)
            tokens_earned = 5 + prestige_level + (self.data.get("skill_points", 0) // 100)
            tokens_earned = int(tokens_earned * self._get_catchup_multiplier())
            current_tokens = self.data.get("prestige_tokens", 0)
            current_upgrades = self.data.get("prestige_upgrades", {})

            self.data = {
                "skill_points": 0,
                "inventory": {"materials": {}, "crafted_items": {}},
                "unlocked_balls": ["basic"],
                "bonuses": {
                    "bonus_hp": 0,
                    "bonus_speed": 0,
                    "bonus_damage": 0
                },
                "loadouts": self.data.get("loadouts", {}),
                                "prestige_level": prestige_level,
                "prestige_tokens": current_tokens + tokens_earned,
                "prestige_upgrades": current_upgrades,
                "quests": [],
                "cosmetics": self.data.get("cosmetics", []),
                "titles": self.data.get("titles", []),
                "badges": self.data.get("badges", []),
                "status_effects": self.data.get("status_effects", []),
                "nemeses": self.data.get("nemeses", {}),
                "login_streak": self.data.get("login_streak", 0),
                "last_login_date": self.data.get("last_login_date", ""),
                "guild_name": self.data.get("guild_name", ""),
                "clan_name": self.data.get("clan_name", "")
            }

            for level in range(5, prestige_level + 1, 5):
                if level == 5:
                    if "Prestige V Champion" not in self.data["titles"]:
                        self.data["titles"].append("Prestige V Champion")
                    if "prestige_aura_gold" not in self.data["cosmetics"]:
                        self.data["cosmetics"].append("prestige_aura_gold")
                    if "prestige_master" not in self.data["unlocked_balls"]:
                        self.data["unlocked_balls"].append("prestige_master")
                elif level == 10:
                    if "Prestige X Grandmaster" not in self.data["titles"]:
                        self.data["titles"].append("Prestige X Grandmaster")
                    if "prestige_aura_diamond" not in self.data["cosmetics"]:
                        self.data["cosmetics"].append("prestige_aura_diamond")
                    if "prestige_grandmaster" not in self.data["unlocked_balls"]:
                        self.data["unlocked_balls"].append("prestige_grandmaster")
                else:
                    roman = self._to_roman(level)
                    title = f"Prestige {roman} Legend"
                    aura = f"prestige_aura_tier_{level}"
                    skin = f"prestige_skin_{level}"

                    if title not in self.data["titles"]:
                        self.data["titles"].append(title)
                    if aura not in self.data["cosmetics"]:
                        self.data["cosmetics"].append(aura)
                    if skin not in self.data["unlocked_balls"]:
                        self.data["unlocked_balls"].append(skin)

            self.save()
            lm = LeaderboardManager("leaderboard.json", profile_manager=self)
            lm.update_prestige("local_player", prestige_level)
            lm.check_season()
            return True
        return False


    def buy_prestige_upgrade(self, upgrade_name, cost):
        current_tokens = self.data.get("prestige_tokens", 0)
        upgrades = self.data.get("prestige_upgrades", {})

        if current_tokens >= cost:
            self.data["prestige_tokens"] = current_tokens - cost
            upgrades[upgrade_name] = upgrades.get(upgrade_name, 0) + 1
            self.data["prestige_upgrades"] = upgrades
            self.save()
            return True
        return False

    def add_cosmetic(self, cosmetic_name):
        if "cosmetics" not in self.data:
            self.data["cosmetics"] = []
        if cosmetic_name not in self.data["cosmetics"]:
            self.data["cosmetics"].append(cosmetic_name)
            self.save()

    def add_title(self, title_name):
        if "titles" not in self.data:
            self.data["titles"] = []
        if title_name not in self.data["titles"]:
            self.data["titles"].append(title_name)
            self.save()

    def add_badge(self, badge_name):
        if "badges" not in self.data:
            self.data["badges"] = []
        if badge_name not in self.data["badges"]:
            self.data["badges"].append(badge_name)
            self.save()

    def save_loadout(self, loadout_name, ball_type, trap_variant, preferred_bonuses=None, cosmetic=None, title=None, badge=None):
        if "loadouts" not in self.data:
            self.data["loadouts"] = {}
        if preferred_bonuses is None:
            preferred_bonuses = {}
        self.data["loadouts"][loadout_name] = {
            "ball_type": ball_type,
            "trap_variant": trap_variant,
            "preferred_bonuses": preferred_bonuses,
            "cosmetic": cosmetic,
            "title": title,
            "badge": badge
        }
        self.save()

    def set_default_loadout(self, loadout_name):
        if "loadouts" in self.data and loadout_name in self.data["loadouts"]:
            self.data["default_loadout"] = loadout_name
            self.save()
            return True
        return False

    def get_default_loadout(self):
        return self.data.get("default_loadout")

    def get_loadout(self, loadout_name):
        return self.data.get("loadouts", {}).get(loadout_name)

    def get_all_loadouts(self):
        return self.data.get("loadouts", {})

    def delete_loadout(self, loadout_name):
        if "loadouts" in self.data and loadout_name in self.data["loadouts"]:
            del self.data["loadouts"][loadout_name]
            self.save()
            return True
        return False


    def generate_loadout_code(self, loadout_name):
        loadout = self.get_loadout(loadout_name)
        if not loadout:
            return None
        try:
            json_str = json.dumps(loadout)
            compressed = zlib.compress(json_str.encode('utf-8'))
            b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')
            return b64.rstrip('=')
        except Exception:
            return None

    def import_loadout_code(self, loadout_name, code):
        try:
            padding = '=' * ((4 - len(code) % 4) % 4)
            b64_bytes = base64.urlsafe_b64decode(code + padding)
            decompressed = zlib.decompress(b64_bytes)
            loadout = json.loads(decompressed.decode('utf-8'))

            # Simple validation to ensure it's a valid loadout dict
            if isinstance(loadout, dict) and "ball_type" in loadout and "trap_variant" in loadout:
                if "loadouts" not in self.data:
                    self.data["loadouts"] = {}
                self.data["loadouts"][loadout_name] = loadout
                self.save()
                return True
            return False
        except Exception:
            return False

    def add_status_effect(self, effect_name):
        if "status_effects" not in self.data:
            self.data["status_effects"] = []
        if effect_name not in self.data["status_effects"]:
            self.data["status_effects"].append(effect_name)
            self.save()

    def add_kill(self, killer_type, victim_type):
        if "nemeses" not in self.data:
            self.data["nemeses"] = {}
        if killer_type not in self.data["nemeses"]:
            self.data["nemeses"][killer_type] = {}
        self.data["nemeses"][killer_type][victim_type] = self.data["nemeses"][killer_type].get(victim_type, 0) + 1
        self.save()

    def is_nemesis(self, killer_type, victim_type):
        if "nemeses" not in self.data:
            return False
        return self.data["nemeses"].get(killer_type, {}).get(victim_type, 0) >= 2

    def process_daily_login(self, current_date_str: str):
        last_date_str = self.data.get("last_login_date", "")
        if last_date_str == current_date_str:
            return {}

        streak = self.data.get("login_streak", 0)

        try:
            current_date = datetime.date.fromisoformat(current_date_str)
            if last_date_str:
                last_date = datetime.date.fromisoformat(last_date_str)
                if (current_date - last_date).days == 1:
                    streak += 1
                else:
                    streak = 1
            else:
                streak = 1
        except Exception:
            streak = 1

        self.data["login_streak"] = streak
        self.data["last_login_date"] = current_date_str

        # Rewards
        sp_reward = 10 * min(streak, 10)
        self.add_skill_points(sp_reward)
        rewards = {"skill_points": sp_reward}

        if streak > 0 and streak % 7 == 0:
            self.data["prestige_tokens"] = self.data.get("prestige_tokens", 0) + 1
            rewards["prestige_tokens"] = 1
            cosmetic_name = f"streak_master_{streak}"
            self.add_cosmetic(cosmetic_name)
            rewards["cosmetics"] = cosmetic_name

        self.save()
        return rewards

    def add_ancient_fragment(self):
        """Adds an ancient loadout fragment. Collect 3 to unlock ancient items."""
        count = self.data.get("ancient_fragments", 0) + 1
        self.data["ancient_fragments"] = count
        if count >= 3:
            self.data["ancient_fragments"] -= 3
            unlocked = False
            if "ancient_aura" not in self.data.get("cosmetics", []):
                self.add_cosmetic("ancient_aura")
                unlocked = True
            if "ancient_guardian" not in self.data.get("unlocked_balls", []):
                if "unlocked_balls" not in self.data:
                    self.data["unlocked_balls"] = []
                self.data["unlocked_balls"].append("ancient_guardian")
                unlocked = True
            if unlocked:
                self.save()
            return True
        self.save()
        return False

    def add_material(self, material_name, amount):
        if "inventory" not in self.data:
            self.data["inventory"] = {"materials": {}, "crafted_items": {}}
        mats = self.data["inventory"]["materials"]
        mats[material_name] = mats.get(material_name, 0) + amount
        self.save()

    def craft_item(self, recipe_id):
        recipes = {
            "health_potion": {"materials": {"Iron Ore": 1, "Magic Dust": 1}, "yields": 1},
            "speed_boost": {"materials": {"Magic Dust": 2}, "yields": 1},
            "artifact": {"materials": {"Void Shard": 3}, "crafted_items": {"health_potion": 1}, "yields": 1}
        }
        if recipe_id not in recipes: return False
        if "inventory" not in self.data: self.data["inventory"] = {"materials": {}, "crafted_items": {}}
        inv = self.data["inventory"]
        req = recipes[recipe_id]
        for m, c in req.get("materials", {}).items():
            if inv["materials"].get(m, 0) < c: return False
        for c_item, c in req.get("crafted_items", {}).items():
            if inv["crafted_items"].get(c_item, 0) < c: return False
        for m, c in req.get("materials", {}).items():
            inv["materials"][m] -= c
        for c_item, c in req.get("crafted_items", {}).items():
            inv["crafted_items"][c_item] -= c
        inv["crafted_items"][recipe_id] = inv["crafted_items"].get(recipe_id, 0) + req["yields"]
        self.save()
        return True
