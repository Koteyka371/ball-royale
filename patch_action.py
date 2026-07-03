import re

with open('src/ai/action.py', 'r') as f:
    text = f.read()

search_quicksand = """                            # Occasional slow debuff that lingers
                            if getattr(self.ball, "quicksand_debuff_timer", 0.0) <= 0:
                                if random.random() < 0.1:  # 10% chance per tick to apply debuff
                                    self.ball.quicksand_debuff_timer = 2.0

                            if getattr(self.ball, "quicksand_debuff_timer", 0.0) > 0:
                                self.ball.speed = getattr(self.ball, 'base_speed', 100.0) * 0.3
                                self.ball.quicksand_debuff_timer -= delta

                            self.ball.is_in_quicksand = True"""

replace_quicksand = """                            # Occasional slow debuff that lingers
                            b_type = str(getattr(self.ball, "ball_type", "")).lower()
                            traits = getattr(self.ball, "traits", [])
                            has_water_trait = "water" in b_type or "swamp" in b_type or any("water" in str(t).lower() or "swamp" in str(t).lower() for t in traits)

                            if not has_water_trait:
                                if getattr(self.ball, "quicksand_debuff_timer", 0.0) <= 0:
                                    if random.random() < 0.1:  # 10% chance per tick to apply debuff
                                        self.ball.quicksand_debuff_timer = 2.0

                                if getattr(self.ball, "quicksand_debuff_timer", 0.0) > 0:
                                    self.ball.speed = getattr(self.ball, 'base_speed', 100.0) * 0.3
                                    self.ball.quicksand_debuff_timer -= delta

                            self.ball.is_in_quicksand = True"""

if search_quicksand in text:
    text = text.replace(search_quicksand, replace_quicksand)
    print("Replaced quicksand blocks")
else:
    print("Could not find quicksand block")

with open('src/ai/action.py', 'w') as f:
    f.write(text)
