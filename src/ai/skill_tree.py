import random
from typing import Any, List, Dict

class SkillTreeNode:
    def __init__(self, name: str, description: str, level_req: int, stat_multipliers: Dict[str, float] = None, special_effects: List[str] = None):
        self.name = name
        self.description = description
        self.level_req = level_req
        self.stat_multipliers = stat_multipliers or {}
        self.special_effects = special_effects or []

class SkillTree:
    def __init__(self):
        self.nodes = [
            # Level 2 Passives
            SkillTreeNode("Thick Skin", "Increases Max HP by 20%", 2, {"max_hp": 1.2}),
            SkillTreeNode("Sprinter", "Increases Speed by 20%", 2, {"speed": 1.2}),
            SkillTreeNode("Sharp Edges", "Increases Damage by 20%", 2, {"damage": 1.2}),

            # Level 4 Passives
            SkillTreeNode("Regeneration", "Grants health regeneration", 4, special_effects=["regen"]),
            SkillTreeNode("Vampirism", "Grants lifesteal on hits", 4, special_effects=["lifesteal"]),
            SkillTreeNode("Quick Cooldowns", "Reduces skill cooldowns", 4, {"skill_cooldown": 0.8}),

            # Level 6 Passives
            SkillTreeNode("Juggernaut", "Massive HP but slower", 6, {"max_hp": 1.5, "speed": 0.9}),
            SkillTreeNode("Assassin", "Massive Damage but less HP", 6, {"damage": 1.5, "max_hp": 0.8}),
                        SkillTreeNode("Speedster", "Massive Speed but less Damage", 6, {"speed": 1.5, "damage": 0.9}),

            # Level 8 Passives
            SkillTreeNode("Decoy Mimic", "Decoys occasionally mimic casting harmless visual versions of your active skill", 8, special_effects=["decoy_mimic_cast"])
        ]

    def get_available_upgrades(self, level: int) -> List[SkillTreeNode]:
        return [n for n in self.nodes if n.level_req == level]

    def apply_upgrade(self, ball: Any, upgrade: SkillTreeNode):
        if not hasattr(ball, "passives"):
            ball.passives = []
        ball.passives.append(upgrade.name)

        for stat, multi in upgrade.stat_multipliers.items():
            current = getattr(ball, stat, 1.0)
            setattr(ball, stat, current * multi)
            if stat == "max_hp" and getattr(ball, "alive", False):
                # Heal proportionally
                ball.hp = getattr(ball, "hp", current) * multi

        for effect in upgrade.special_effects:
            if effect == "regen":
                ball.health_regen = getattr(ball, "health_regen", 0.0) + 5.0
            elif effect == "lifesteal":
                ball.lifesteal = getattr(ball, "lifesteal", 0.0) + 0.2
            elif effect == "decoy_mimic_cast":
                if not hasattr(ball, "traits"):
                    ball.traits = []
                if "decoy_mimic_cast" not in ball.traits:
                    ball.traits.append("decoy_mimic_cast")
