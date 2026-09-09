import re

with open("src/ai/action.py", "r") as f:
    code = f.read()

# I want to add elemental_resonance right after resonance is computed.
target = """
                            if resonance:
                                if hasattr(self.world, "events"):
                                    self.world.events.append({"type": "visual_effect", "data": {"type": "resonance_chain_explosion", "x": b.x, "y": b.y, "radius": 400.0}})
"""

replacement = """
                            decoy_element = getattr(b, "element", None)
                            elemental_resonance = False

                            if resonance:
                                if decoy_element:
                                    same_element_decoys = [sib for sib in nearby_exploding if getattr(sib, "element", None) == decoy_element]
                                    if len(same_element_decoys) >= 3:
                                        elemental_resonance = True

                                if elemental_resonance:
                                    if hasattr(self.world, "events"):
                                        self.world.events.append({"type": "visual_effect", "data": {"type": f"{decoy_element}_storm_creation", "x": b.x, "y": b.y, "radius": 450.0}})
                                else:
                                    if hasattr(self.world, "events"):
                                        self.world.events.append({"type": "visual_effect", "data": {"type": "resonance_chain_explosion", "x": b.x, "y": b.y, "radius": 400.0}})
"""
code = code.replace(target, replacement)

target2 = """
                            decoy_element = getattr(b, "element", None)

                            # Extreme weather decoy interactions
"""
replacement2 = """
                            # Extreme weather decoy interactions
"""
code = code.replace(target2, replacement2)

target3 = """
                            if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                                if resonance:
                                    import random
"""

replacement3 = """
                            if hasattr(self.world, "arena") and hasattr(self.world.arena, "hazards"):
                                if elemental_resonance:
                                    import random
                                    h_id = getattr(self.world, "next_id", random.randint(10000, 99999))
                                    if hasattr(self.world, "next_id"):
                                        self.world.next_id += 1

                                    storm_type = "storm"
                                    if decoy_element == "fire":
                                        storm_type = "firenado"
                                    elif decoy_element == "ice":
                                        storm_type = "blizzard_zone"
                                    elif decoy_element == "lightning":
                                        storm_type = "lightning_storm"
                                    elif decoy_element == "water":
                                        storm_type = "whirlpool"
                                    else:
                                        storm_type = f"{decoy_element}_storm"

                                    try:
                                        from arena.arena_types import Hazard
                                        hz = Hazard(h_id, b.x, b.y, 450.0, storm_type, 0.0)
                                        hz.duration = 10.0
                                        hz.owner_id = getattr(b, "owner_id", None)
                                        self.world.arena.hazards.append(hz)
                                    except ImportError:
                                        try:
                                            from arena.procedural_arena import Hazard
                                            hz = Hazard(id=h_id, x=b.x, y=b.y, radius=450.0, kind=storm_type, damage=0.0)
                                            setattr(hz, "duration", 10.0)
                                            hz.owner_id = getattr(b, "owner_id", None)
                                            self.world.arena.hazards.append(hz)
                                        except ImportError:
                                            class MockHz: pass
                                            hz = MockHz()
                                            hz.id = h_id
                                            hz.x = b.x
                                            hz.y = b.y
                                            hz.radius = 450.0
                                            hz.kind = storm_type
                                            hz.damage = 0.0
                                            hz.duration = 10.0
                                            hz.owner_id = getattr(b, "owner_id", None)
                                            self.world.arena.hazards.append(hz)
                                elif resonance:
                                    import random
"""

code = code.replace(target3, replacement3)

with open("src/ai/action.py", "w") as f:
    f.write(code)
