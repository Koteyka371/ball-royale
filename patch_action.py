import re

with open('src/ai/action.py', 'r') as f:
    content = f.read()

content = content.replace('                                cloud = Hazard(id=h_id, x=target_minion.x, y=target_minion.y, radius=cloud_radius, kind="poison_cloud", damage=cloud_damage)\n                                setattr(cloud, "duration", 5.0)\n                                self.world.arena.hazards.append(cloud)\n                            except Exception:\n                                pass', '                                cloud = Hazard(id=h_id, x=target_minion.x, y=target_minion.y, radius=cloud_radius, kind="poison_cloud", damage=cloud_damage)\n                                setattr(cloud, "duration", 5.0)\n                                self.world.arena.hazards.append(cloud)\n                            except Exception:\n                                pass\n\n                        # Apply heal and shield to Necromancer\n                        heal_amount = 40.0 if is_elite else 20.0\n                        self.ball.hp = min(getattr(self.ball, "hp", 100.0) + heal_amount, getattr(self.ball, "max_hp", 100.0))\n                        \n                        if is_elite:\n                            self.ball.energy_shield_active = True\n                            self.ball.energy_shield_hp = getattr(self.ball, "energy_shield_hp", 0) + 30.0')

with open('src/ai/action.py', 'w') as f:
    f.write(content)
