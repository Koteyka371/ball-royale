import json

class GuildManager:
    def __init__(self, filename="guilds.json"):
        self.filename = filename
        self.data = self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if "guilds" not in data:
                    data["guilds"] = {}
                if "territories" not in data:
                    data["territories"] = {}
                for guild in data["guilds"].values():
                    if "hq" not in guild:
                        guild["hq"] = {
                            "statues": [],
                            "banners": [],
                            "cosmetics": [],
                            "flags": [],
                            "backgrounds": [],
                            "announcer_voices": [],
                            "mini_games": {},
                            "training_arena_unlocked": False
                        }
                    elif "mini_games" not in guild["hq"]:
                        guild["hq"]["mini_games"] = {}

                    if "guild_xp" not in guild:
                        guild["guild_xp"] = 0
                    if "perks" not in guild:
                        guild["perks"] = []
                    if "active_abilities" not in guild:
                        guild["active_abilities"] = []
                    if "active_bounties" not in guild:
                        guild["active_bounties"] = {}
                    if "prestige_pool" not in guild:
                        guild["prestige_pool"] = 0
                    if "titles" not in guild:
                        guild["titles"] = []
                    if "cosmetic_auras" not in guild:
                        guild["cosmetic_auras"] = []
                    if "emblem" not in guild:
                        guild["emblem"] = {"shape": "circle", "color": "white", "symbol": "none"}
                    if "unlocked_emblem_parts" not in guild:
                        guild["unlocked_emblem_parts"] = {"shapes": ["circle"], "colors": ["white"], "symbols": ["none"]}
                    if "allies" not in guild:
                        guild["allies"] = []
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {"guilds": {}, "territories": {}}

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)


    def pool_mutator_tokens(self, guild_name, amount, profile):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if profile.data.get("mutator_tokens", 0) >= amount:
                profile.data["mutator_tokens"] -= amount
                profile.save()

                if "mutator_token_pool" not in guild:
                    guild["mutator_token_pool"] = 0
                guild["mutator_token_pool"] += amount
                self.save()
                return True
        return False

    def cast_gvg_mutator_vote(self, guild_name, mutator, tokens_to_spend):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild.get("mutator_token_pool", 0) >= tokens_to_spend:
                guild["mutator_token_pool"] -= tokens_to_spend

                if "gvg_mutator_votes" not in guild:
                    guild["gvg_mutator_votes"] = {}

                current_votes = guild["gvg_mutator_votes"].get(mutator, 0)
                guild["gvg_mutator_votes"][mutator] = current_votes + tokens_to_spend
                self.save()
                return True
        return False

    def get_gvg_match_mutator(self, guild1_name, guild2_name):
        import random
        votes = {}

        for g_name in [guild1_name, guild2_name]:
            if g_name in self.data["guilds"]:
                g_votes = self.data["guilds"][g_name].get("gvg_mutator_votes", {})
                for mutator, count in g_votes.items():
                    votes[mutator] = votes.get(mutator, 0) + count

        if not votes:
            options = ["low_gravity", "double_damage", "high_speed", "vampirism", "global_hp", "global_cooldown", "invisible_hazards", "kinetic_ghost"]
            return random.choice(options)

        winning_mutator = max(votes.items(), key=lambda x: x[1])[0]
        return winning_mutator

    def create_guild(self, guild_name, creator_id):
        if guild_name in self.data["guilds"]:
            return False

        self.data["guilds"][guild_name] = {
            "members": [creator_id],
            "level": 1,
            "resources": 0,
            "prestige_pool": 0,
            "titles": [],
            "cosmetic_auras": [],
            "buffs": {
                "bonus_hp": 0,
                "bonus_speed": 0,
                "bonus_damage": 0
            },
            "gvg_points": 0,
            "guild_xp": 0,
            "perks": [],
            "active_abilities": [],
            "active_bounties": {},
            "chat_history": [],
            "vault": [],
            "boss_progress": {},
            "hq": {
                "statues": [],
                "banners": [],
                "cosmetics": [],
                "mini_games": {},
                "training_arena_unlocked": False
            },
            "emblem": {"shape": "circle", "color": "white", "symbol": "none"},
            "unlocked_emblem_parts": {"shapes": ["circle"], "colors": ["white"], "symbols": ["none"]},
            "allies": []
        }
        self.save()
        return True

    def join_guild(self, guild_name, player_id):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if player_id not in guild["members"]:
                guild["members"].append(player_id)
                self.save()
                return True
        return False

    def leave_guild(self, guild_name, player_id):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if player_id in guild["members"]:
                guild["members"].remove(player_id)
                if len(guild["members"]) == 0:
                    del self.data["guilds"][guild_name]
                self.save()
                return True
        return False

    def donate_prestige(self, guild_name, amount):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            guild["prestige_pool"] = guild.get("prestige_pool", 0) + amount
            self.save()
            return True
        return False

    def unlock_global_cosmetic(self, guild_name, cosmetic_id, cost):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild.get("prestige_pool", 0) >= cost:
                if "cosmetic_auras" not in guild:
                    guild["cosmetic_auras"] = []
                if cosmetic_id not in guild["cosmetic_auras"]:
                    guild["prestige_pool"] -= cost
                    guild["cosmetic_auras"].append(cosmetic_id)
                    self.save()
                    return True
        return False

    def unlock_global_title(self, guild_name, title_id, cost):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild.get("prestige_pool", 0) >= cost:
                if "titles" not in guild:
                    guild["titles"] = []
                if title_id not in guild["titles"]:
                    guild["prestige_pool"] -= cost
                    guild["titles"].append(title_id)
                    self.save()
                    return True
        return False

    def get_unlocked_cosmetics(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("cosmetic_auras", [])
        return []

    def get_unlocked_titles(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("titles", [])
        return []

    def donate_resources(self, guild_name, amount):
        if guild_name in self.data["guilds"]:
            self.data["guilds"][guild_name]["resources"] += amount
            self.save()
            return True
        return False


    def upgrade_guild_level(self, guild_name, cost):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild.get("gvg_points", 0) >= cost:
                guild["gvg_points"] -= cost
                guild["level"] = guild.get("level", 1) + 1
                self.save()
                return True
        return False

    def unlock_buff(self, guild_name, buff_name, cost, required_level=1):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild["resources"] >= cost and buff_name in guild["buffs"] and guild.get("level", 1) >= required_level:
                guild["resources"] -= cost
                guild["buffs"][buff_name] += 1
                self.save()
                return True
        return False


    def place_bounty(self, guild_name, target_guild_name, reward_points):
        if guild_name in self.data["guilds"] and target_guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild.get("resources", 0) >= reward_points:
                guild["resources"] -= reward_points
                target_guild = self.data["guilds"][target_guild_name]
                if "active_bounties" not in target_guild:
                    target_guild["active_bounties"] = {}

                if guild_name not in target_guild["active_bounties"]:
                    target_guild["active_bounties"][guild_name] = 0
                target_guild["active_bounties"][guild_name] += reward_points
                self.save()
                return True
        return False

    def get_bounties_on_guild(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("active_bounties", {})
        return {}

    def claim_bounty(self, target_guild_name, claiming_guild_name):
        if target_guild_name in self.data["guilds"] and claiming_guild_name in self.data["guilds"]:
            target_guild = self.data["guilds"][target_guild_name]
            claiming_guild = self.data["guilds"][claiming_guild_name]

            bounties = target_guild.get("active_bounties", {})
            if claiming_guild_name in bounties and bounties[claiming_guild_name] > 0:
                reward = bounties[claiming_guild_name]
                claiming_guild["resources"] = claiming_guild.get("resources", 0) + reward
                bounties[claiming_guild_name] = 0
                self.save()
                return reward
        return 0


    def register_for_tournament(self, guild_name, tournament_id):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if "tournaments" not in guild:
                guild["tournaments"] = []
            if tournament_id not in guild["tournaments"]:
                guild["tournaments"].append(tournament_id)
                self.save()
                return True
        return False

    def process_tournament_results(self, tournament_id, rankings):
        # rankings: list of dicts [{"guild_name": str, "rank": int}]
        for entry in rankings:
            guild_name = entry["guild_name"]
            rank = entry["rank"]
            if guild_name in self.data["guilds"]:
                guild = self.data["guilds"][guild_name]
                if "tournaments" in guild and tournament_id in guild["tournaments"]:
                    if rank == 1:
                        guild.setdefault("titles", []).append("Tournament Champion")
                        guild.setdefault("cosmetic_auras", []).append("Champion Aura")
                        guild["prestige_pool"] = guild.get("prestige_pool", 0) + 10000
                    elif rank <= 3:
                        guild.setdefault("titles", []).append("Tournament Finalist")
                        guild["prestige_pool"] = guild.get("prestige_pool", 0) + 5000
                    elif rank <= 10:
                        guild["prestige_pool"] = guild.get("prestige_pool", 0) + 1000
        self.save()
        return True

    def get_guild_buffs(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name]["buffs"]
        return {"bonus_hp": 0, "bonus_speed": 0, "bonus_damage": 0}

    def record_gvg_match(self, guild1_name, guild2_name, winner_name):
        if guild1_name in self.data["guilds"] and guild2_name in self.data["guilds"]:
            if winner_name == guild1_name:
                self.data["guilds"][guild1_name]["gvg_points"] += 10
                self.data["guilds"][guild1_name]["guild_xp"] += 50
                self.data["guilds"][guild2_name]["gvg_points"] = max(0, self.data["guilds"][guild2_name]["gvg_points"] - 5)
                self.data["guilds"][guild2_name]["guild_xp"] += 10
            elif winner_name == guild2_name:
                self.data["guilds"][guild2_name]["gvg_points"] += 10
                self.data["guilds"][guild2_name]["guild_xp"] += 50
                self.data["guilds"][guild1_name]["gvg_points"] = max(0, self.data["guilds"][guild1_name]["gvg_points"] - 5)
                self.data["guilds"][guild1_name]["guild_xp"] += 10
            self.save()
            return True
        return False

    def unlock_perk(self, guild_name, perk_name, cost, required_perk=None):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild["guild_xp"] >= cost:
                if perk_name not in guild.get("perks", []):
                    if required_perk is None or required_perk in guild.get("perks", []):
                        guild["guild_xp"] -= cost
                        guild.setdefault("perks", []).append(perk_name)
                        self.save()
                        return True
        return False

    def buy_active_ability(self, guild_name, ability_name, cost, currency="resources"):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if currency in guild and guild[currency] >= cost:
                if ability_name not in guild.get("active_abilities", []):
                    guild[currency] -= cost
                    guild.setdefault("active_abilities", []).append(ability_name)
                    self.save()
                    return True
        return False

    def get_active_abilities(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("active_abilities", [])
        return []

    def deploy_active_ability(self, guild_name, ability_name):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if ability_name in guild.get("active_abilities", []):
                guild["active_abilities"].remove(ability_name)
                self.save()
                return True
        return False

    def get_guild_perks(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("perks", [])
        return []

    def get_guild(self, guild_name):
        return self.data["guilds"].get(guild_name)

    def send_chat_message(self, guild_name, sender_id, message):
        if guild_name in self.data["guilds"]:
            self.data["guilds"][guild_name].setdefault("chat_history", []).append({
                "sender": sender_id,
                "message": message
            })
            self.save()
            return True
        return False

    def get_chat_history(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("chat_history", [])
        return []

    def get_guild_leaderboard(self):
        guilds = []
        for name, info in self.data["guilds"].items():
            guilds.append({
                "name": name,
                "gvg_points": info.get("gvg_points", 0)
            })
        guilds.sort(key=lambda x: x["gvg_points"], reverse=True)
        return guilds

    def deposit_item(self, guild_name, item):
        if guild_name in self.data["guilds"]:
            self.data["guilds"][guild_name].setdefault("vault", []).append(item)
            self.save()
            return True
        return False

    def withdraw_item(self, guild_name, item):
        if guild_name in self.data["guilds"]:
            vault = self.data["guilds"][guild_name].setdefault("vault", [])
            if item in vault:
                vault.remove(item)
                self.save()
                return True
        return False

    def capture_territory(self, guild_name, territory_name):
        if guild_name in self.data["guilds"]:
            if "territories" not in self.data:
                self.data["territories"] = {}
            self.data["territories"][territory_name] = guild_name
            self.save()
            return True
        return False

    def get_territories(self, guild_name):
        if "territories" not in self.data:
            return []
        return [t for t, owner in self.data["territories"].items() if owner == guild_name]

    def collect_passive_resources(self):
        if "territories" not in self.data:
            return

        incomes = {}
        for territory, owner in self.data["territories"].items():
            if owner in self.data["guilds"]:
                incomes[owner] = incomes.get(owner, 0) + 5

                allies = self.data["guilds"][owner].get("allies", [])
                for ally in allies:
                    if ally in self.data["guilds"]:
                        incomes[ally] = incomes.get(ally, 0) + 2

        for guild_name, amount in incomes.items():
            guild = self.data["guilds"][guild_name]
            pay_taxes_to = guild.get("pay_taxes_to", [])

            if pay_taxes_to:
                tax_rate = 0.5
                tax_amount = int(amount * tax_rate)
                amount -= tax_amount

                tax_per_winner = tax_amount // len(pay_taxes_to)
                for winner in pay_taxes_to:
                    if winner in self.data["guilds"]:
                        self.data["guilds"][winner]["resources"] += tax_per_winner

            self.data["guilds"][guild_name]["resources"] += amount

        self.save()

    def declare_war(self, guild1_name, guild2_name):
        if guild1_name in self.data["guilds"] and guild2_name in self.data["guilds"] and guild1_name != guild2_name:
            self.break_alliance(guild1_name, guild2_name)

            guild1 = self.data["guilds"][guild1_name]
            guild2 = self.data["guilds"][guild2_name]

            if "wars" not in guild1: guild1["wars"] = []
            if "wars" not in guild2: guild2["wars"] = []

            if guild2_name not in guild1["wars"] and guild1_name not in guild2["wars"]:
                guild1["wars"].append(guild2_name)
                guild2["wars"].append(guild1_name)
                self.save()
                return True
        return False

    def end_war(self, winner_name, loser_name):
        if winner_name in self.data["guilds"] and loser_name in self.data["guilds"]:
            winner = self.data["guilds"][winner_name]
            loser = self.data["guilds"][loser_name]

            modified = False
            if "wars" in winner and loser_name in winner["wars"]:
                winner["wars"].remove(loser_name)
                modified = True
            if "wars" in loser and winner_name in loser["wars"]:
                loser["wars"].remove(winner_name)
                modified = True

            if modified:
                territories_to_transfer = self.get_territories(loser_name)
                for t in territories_to_transfer:
                    self.capture_territory(winner_name, t)

                if "pay_taxes_to" not in loser:
                    loser["pay_taxes_to"] = []
                if winner_name not in loser["pay_taxes_to"]:
                    loser["pay_taxes_to"].append(winner_name)

                self.save()
                return True
        return False

    def form_alliance(self, guild1_name, guild2_name):
        if guild1_name in self.data["guilds"] and guild2_name in self.data["guilds"] and guild1_name != guild2_name:
            guild1 = self.data["guilds"][guild1_name]
            guild2 = self.data["guilds"][guild2_name]

            if "allies" not in guild1:
                guild1["allies"] = []
            if "allies" not in guild2:
                guild2["allies"] = []

            if guild2_name not in guild1["allies"] and guild1_name not in guild2["allies"]:
                guild1["allies"].append(guild2_name)
                guild2["allies"].append(guild1_name)
                self.save()
                return True
        return False

    def break_alliance(self, guild1_name, guild2_name):
        if guild1_name in self.data["guilds"] and guild2_name in self.data["guilds"]:
            guild1 = self.data["guilds"][guild1_name]
            guild2 = self.data["guilds"][guild2_name]

            modified = False
            if "allies" in guild1 and guild2_name in guild1["allies"]:
                guild1["allies"].remove(guild2_name)
                modified = True
            if "allies" in guild2 and guild1_name in guild2["allies"]:
                guild2["allies"].remove(guild1_name)
                modified = True

            if modified:
                self.save()
                return True
        return False

    def _get_alliance_boss_damage(self, guild_name, week_id, tier_str):
        total_damage = 0.0

        def get_damage_for_guild(g_name):
            if g_name in self.data["guilds"]:
                guild = self.data["guilds"][g_name]
                if "boss_progress" in guild and week_id in guild["boss_progress"]:
                    progress = guild["boss_progress"][week_id]
                    if "damage_dealt" in progress:
                        progress = {"1": progress}
                    if tier_str in progress:
                        return progress[tier_str]["damage_dealt"]
            return 0.0

        total_damage += get_damage_for_guild(guild_name)

        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            for ally_name in guild.get("allies", []):
                total_damage += get_damage_for_guild(ally_name)

        return total_damage

    def record_boss_damage(self, guild_name, damage, week_id, tier=1):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if "boss_progress" not in guild:
                guild["boss_progress"] = {}
            if week_id not in guild["boss_progress"]:
                guild["boss_progress"][week_id] = {}
            if "damage_dealt" in guild["boss_progress"][week_id]:
                old = guild["boss_progress"][week_id]
                guild["boss_progress"][week_id] = {"1": old}
            tier_str = str(tier)
            if tier_str not in guild["boss_progress"][week_id]:
                guild["boss_progress"][week_id][tier_str] = {"damage_dealt": 0.0, "claimed_by": []}
            guild["boss_progress"][week_id][tier_str]["damage_dealt"] += damage
            self.save()
            return True
        return False

    def check_boss_defeated(self, guild_name, week_id, required_damage, tier=1):
        if guild_name in self.data["guilds"]:
            tier_str = str(tier)
            total_damage = self._get_alliance_boss_damage(guild_name, week_id, tier_str)
            return total_damage >= required_damage
        return False

    def claim_boss_reward(self, guild_name, player_id, week_id, required_damage, tier=1):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            tier_str = str(tier)

            # Check if defeated using pooled damage
            total_damage = self._get_alliance_boss_damage(guild_name, week_id, tier_str)
            if total_damage >= required_damage:
                # Ensure the local progress structure exists so we can record who claimed it
                if "boss_progress" not in guild:
                    guild["boss_progress"] = {}
                if week_id not in guild["boss_progress"]:
                    guild["boss_progress"][week_id] = {}

                progress = guild["boss_progress"][week_id]
                if "damage_dealt" in progress:
                    progress = {"1": progress}
                    guild["boss_progress"][week_id] = progress

                if tier_str not in progress:
                    progress[tier_str] = {"damage_dealt": 0.0, "claimed_by": []}

                tier_prog = progress[tier_str]
                if player_id not in tier_prog["claimed_by"]:
                    tier_prog["claimed_by"].append(player_id)
                    reward_amount = 100 * int(tier)
                    if "resources" not in guild:
                        guild["resources"] = 0
                    guild["resources"] += reward_amount
                    self.save()
                    return True
        return False

    def unlock_hq_feature(self, guild_name, feature_type, feature_id, cost, required_level=1, currency="resources"):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if currency not in ["resources", "guild_xp"]:
                return False

            if guild.get(currency, 0) >= cost and guild.get("level", 1) >= required_level:
                if feature_type == "training_arena":
                    if not guild.get("hq", {}).get("training_arena_unlocked", False):
                        guild[currency] -= cost
                        guild.setdefault("hq", {})["training_arena_unlocked"] = True
                        self.save()
                        return True
                elif feature_type in ["statues", "banners", "cosmetics", "flags", "backgrounds", "announcer_voices"]:
                    if feature_id not in guild.setdefault("hq", {}).setdefault(feature_type, []):
                        guild[currency] -= cost
                        guild["hq"][feature_type].append(feature_id)
                        self.save()
                        return True
                elif feature_type == "mini_games":
                    hq = guild.setdefault("hq", {})
                    mini_games = hq.setdefault("mini_games", {})
                    if feature_id not in mini_games:
                        guild[currency] -= cost
                        mini_games[feature_id] = {"high_scores": {}}
                        self.save()
                        return True
        return False

    def record_mini_game_score(self, guild_name, mini_game_id, player_id, score):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            hq = guild.get("hq", {})
            mini_games = hq.get("mini_games", {})
            if mini_game_id in mini_games:
                high_scores = mini_games[mini_game_id].setdefault("high_scores", {})
                current_score = high_scores.get(player_id, 0)
                if score > current_score:
                    high_scores[player_id] = score
                    self.save()
                    return True
        return False

    def get_mini_game_leaderboard(self, guild_name, mini_game_id):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            hq = guild.get("hq", {})
            mini_games = hq.get("mini_games", {})
            if mini_game_id in mini_games:
                high_scores = mini_games[mini_game_id].get("high_scores", {})
                scores = [{"player_id": player, "score": score} for player, score in high_scores.items()]
                scores.sort(key=lambda x: x["score"], reverse=True)
                return scores
        return []

    def build_hq_defense(self, guild_name, defense_type, cost, amount=1):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild.get("resources", 0) >= cost:
                guild["resources"] -= cost
                hq = guild.setdefault("hq", {})
                defenses = hq.setdefault("defenses", {})
                defenses[defense_type] = defenses.get(defense_type, 0) + amount
                self.save()
                return True
        return False

    def get_hq_defenses(self, guild_name):
        if guild_name in self.data["guilds"]:
            return self.data["guilds"][guild_name].get("hq", {}).get("defenses", {})
        return {}

    def record_siege_defense_broken(self, attacker_name, defender_name, stolen_amount):
        if attacker_name in self.data["guilds"] and defender_name in self.data["guilds"]:
            defender = self.data["guilds"][defender_name]
            attacker = self.data["guilds"][attacker_name]

            actual_stolen = min(defender.get("resources", 0), stolen_amount)
            if actual_stolen > 0:
                defender["resources"] -= actual_stolen
                attacker["resources"] = attacker.get("resources", 0) + actual_stolen
                self.save()
            return actual_stolen
        return 0

    def record_siege_held(self, defender_name, xp_reward):
        if defender_name in self.data["guilds"]:
            defender = self.data["guilds"][defender_name]
            defender["guild_xp"] = defender.get("guild_xp", 0) + xp_reward
            self.save()
            return True
        return False

    def get_hq_status(self, guild_name):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            hq = guild.get("hq", {})
            return {
                "statues": hq.get("statues", []),
                "banners": hq.get("banners", []),
                "cosmetics": hq.get("cosmetics", []),
                "flags": hq.get("flags", []),
                "backgrounds": hq.get("backgrounds", []),
                "announcer_voices": hq.get("announcer_voices", []),
                "mini_games": hq.get("mini_games", {}),
                "defenses": hq.get("defenses", {}),
                "training_arena_unlocked": hq.get("training_arena_unlocked", False)
            }
        return None

    def unlock_emblem_part(self, guild_name, part_type, part_id, cost):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            if guild.get("resources", 0) >= cost:
                unlocked_parts = guild.get("unlocked_emblem_parts", {"shapes": [], "colors": [], "symbols": []})
                if part_type in unlocked_parts:
                    if part_id not in unlocked_parts[part_type]:
                        guild["resources"] -= cost
                        unlocked_parts[part_type].append(part_id)
                        guild["unlocked_emblem_parts"] = unlocked_parts
                        self.save()
                        return True
        return False

    def update_emblem(self, guild_name, shape, color, symbol):
        if guild_name in self.data["guilds"]:
            guild = self.data["guilds"][guild_name]
            unlocked = guild.get("unlocked_emblem_parts", {"shapes": [], "colors": [], "symbols": []})
            if shape in unlocked.get("shapes", []) and color in unlocked.get("colors", []) and symbol in unlocked.get("symbols", []):
                guild["emblem"] = {"shape": shape, "color": color, "symbol": symbol}
                self.save()
                return True
        return False
