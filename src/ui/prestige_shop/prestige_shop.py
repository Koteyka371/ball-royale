import random
class PrestigeShop:
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager

    def get_available_upgrades(self):
        return {
            "permanent_hp": {"cost": 5, "description": "Increases max HP permanently"},
            "permanent_speed": {"cost": 5, "description": "Increases base speed permanently"},
            "permanent_damage": {"cost": 5, "description": "Increases base damage permanently"},
            "mutator_unlocked": {"cost": 15, "description": "Unlocks custom match mutators (run mutators)"},
            "starting_artifact_shield": {"cost": 10, "description": "Start matches with a shield artifact"},
            "starting_artifact_dash": {"cost": 10, "description": "Start matches with a dash artifact"},
            "unlock_time_mage": {"cost": 25, "description": "Unlocks the Time-Mage ball archetype"},
            "shield_capacity_up": {"cost": 10, "description": "Increases reflect shield capacity by 20"},
            "shield_duration_up": {"cost": 10, "description": "Increases reflect shield duration by 1s"},
            "skin_neon": {"cost": 15, "description": "Unlock the Neon skin"},
            "skin_ninja": {"cost": 15, "description": "Unlock the Ninja skin"}
        }

    def buy_upgrade(self, upgrade_name):
        upgrades = self.get_available_upgrades()
        if upgrade_name not in upgrades:
            return False
        cost = upgrades[upgrade_name]["cost"]
        return self.profile_manager.buy_prestige_upgrade(upgrade_name, cost)


    def get_wheel_rewards(self):
        return {
            "skill_points_10": {"type": "skill_points", "amount": 10, "weight": 40},
            "skill_points_50": {"type": "skill_points", "amount": 50, "weight": 20},
            "prestige_token": {"type": "prestige_tokens", "amount": 1, "weight": 10},
            "cosmetic_spin_master": {"type": "cosmetics", "name": "spin_master", "weight": 5},
            "nothing": {"type": "nothing", "weight": 25}
        }

    def spin_wheel(self, cost=1):
        current_tokens = self.profile_manager.data.get("prestige_tokens", 0)
        if current_tokens < cost:
            return False, "Not enough tokens"

        self.profile_manager.data["prestige_tokens"] = current_tokens - cost
        self.profile_manager.save()

        rewards = self.get_wheel_rewards()
        total_weight = sum(r["weight"] for r in rewards.values())
        rand_val = random.uniform(0, total_weight)

        current_weight = 0
        selected_reward_key = None
        for key, reward in rewards.items():
            current_weight += reward["weight"]
            if rand_val <= current_weight:
                selected_reward_key = key
                break

        if not selected_reward_key:
            selected_reward_key = "nothing"

        reward = rewards[selected_reward_key]

        if reward["type"] == "skill_points":
            self.profile_manager.add_skill_points(reward["amount"])
            return True, f"Won {reward['amount']} Skill Points!"
        elif reward["type"] == "prestige_tokens":
            self.profile_manager.data["prestige_tokens"] = self.profile_manager.data.get("prestige_tokens", 0) + reward["amount"]
            self.profile_manager.save()
            return True, f"Won {reward['amount']} Prestige Token(s)!"
        elif reward["type"] == "cosmetics":
            self.profile_manager.add_cosmetic(reward["name"])
            return True, f"Won cosmetic: {reward['name']}!"
        else:
            return True, "Won nothing, better luck next time!"

    def get_roulette_color(self, number):
        if number == 0:
            return "green"
        return "red" if number % 2 != 0 else "black"

    def get_roulette_section(self, number):
        if number == 0:
            return "none"
        if 1 <= number <= 12:
            return "1st12"
        elif 13 <= number <= 24:
            return "2nd12"
        else:
            return "3rd12"

    def play_roulette(self, bet_amount, bet_type, bet_value):
        current_tokens = self.profile_manager.data.get("prestige_tokens", 0)
        if current_tokens < bet_amount:
            return False, "Not enough tokens"

        self.profile_manager.data["prestige_tokens"] = current_tokens - bet_amount
        self.profile_manager.save()

        # Spin the roulette (0 to 36)
        winning_number = random.randint(0, 36)
        winning_color = self.get_roulette_color(winning_number)
        winning_section = self.get_roulette_section(winning_number)

        payout = 0
        if bet_type == "color":
            if bet_value == winning_color:
                payout = bet_amount * (35 if bet_value == "green" else 2)
        elif bet_type == "section":
            if bet_value == winning_section:
                payout = bet_amount * 3
        elif bet_type == "number":
            try:
                if int(bet_value) == winning_number:
                    payout = bet_amount * 35
            except ValueError:
                pass

        msg = f"Roulette spun {winning_number} ({winning_color}). "
        if payout > 0:
            self.profile_manager.data["prestige_tokens"] = self.profile_manager.data.get("prestige_tokens", 0) + payout
            msg += f"You won {payout} tokens!"

            # Chance to unlock cosmetic on large wins
            if payout >= 50 and random.random() < 0.1:
                self.profile_manager.add_cosmetic("roulette_master")
                msg += " Also won exclusive cosmetic: roulette_master!"

            self.profile_manager.save()
            return True, msg
        else:
            msg += "You lost your bet."
            return True, msg

    def equip_skin(self, skin_name):
        return self.profile_manager.equip_skin(skin_name)

    def render_ui(self):
        # A simple terminal/text-based UI representation for the python mock environment
        output = ["--- Prestige Shop ---", "[Spin Wheel] - Cost 1 Token", "[Play Roulette] - High Stakes!"]
        upgrades = self.get_available_upgrades()
        current_tokens = self.profile_manager.data.get("prestige_tokens", 0)
        output.append(f"Tokens available: {current_tokens}")

        for name, data in upgrades.items():
            output.append(f"{name} - {data['description']} (Cost: {data['cost']})")
        return "\n".join(output)
