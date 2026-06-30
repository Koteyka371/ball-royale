with open("src/ai/game_modes.py", "r") as f:
    content = f.read()

replacement_tick = """            in_speed_zone = False
            in_damage_zone = False
            in_heal_zone = False
            in_debuff_zone = False

            for zone in self.zones:
                dx = b.x - zone["x"]
                dy = b.y - zone["y"]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist <= zone["radius"]:
                    if zone["type"] == "speed":
                        in_speed_zone = True
                    elif zone["type"] == "damage":
                        in_damage_zone = True
                    elif zone["type"] == "heal":
                        in_heal_zone = True
                    elif zone["type"] == "debuff":
                        in_debuff_zone = True

            if in_speed_zone:
                b.speed = b.base_speed * 1.5
                b.zone_modifier_speed = True
            else:
                if getattr(b, "zone_modifier_speed", False):
                    b.speed = b.base_speed
                    delattr(b, "zone_modifier_speed")

            if in_damage_zone:
                b.damage = b.base_damage * 1.5
                b.zone_modifier_damage = True
            else:
                if getattr(b, "zone_modifier_damage", False):
                    b.damage = b.base_damage
                    delattr(b, "zone_modifier_damage")

            if in_debuff_zone:
                if not hasattr(b, "base_max_hp"):
                    b.base_max_hp = getattr(b, "max_hp", 100.0)
                b.max_hp = b.base_max_hp * 0.5
                if hasattr(b, "hp") and b.hp > b.max_hp:
                    b.hp = b.max_hp
                b.zone_modifier_debuff = True
            else:
                if getattr(b, "zone_modifier_debuff", False):
                    if hasattr(b, "base_max_hp"):
                        b.max_hp = b.base_max_hp
                    delattr(b, "zone_modifier_debuff")

            if in_heal_zone:"""
content = content.replace("""            in_speed_zone = False
            in_damage_zone = False
            in_heal_zone = False

            for zone in self.zones:
                dx = b.x - zone["x"]
                dy = b.y - zone["y"]
                dist = math.sqrt(dx*dx + dy*dy)

                if dist <= zone["radius"]:
                    if zone["type"] == "speed":
                        in_speed_zone = True
                    elif zone["type"] == "damage":
                        in_damage_zone = True
                    elif zone["type"] == "heal":
                        in_heal_zone = True

            if in_speed_zone:
                b.speed = b.base_speed * 1.5
                b.zone_modifier_speed = True
            else:
                if getattr(b, "zone_modifier_speed", False):
                    b.speed = b.base_speed
                    delattr(b, "zone_modifier_speed")

            if in_damage_zone:
                b.damage = b.base_damage * 1.5
                b.zone_modifier_damage = True
            else:
                if getattr(b, "zone_modifier_damage", False):
                    b.damage = b.base_damage
                    delattr(b, "zone_modifier_damage")

            if in_heal_zone:""", replacement_tick)

with open("src/ai/game_modes.py", "w") as f:
    f.write(content)

with open("src/ai/game_modes.gd", "r") as f:
    content_gd = f.read()

replacement_tick_gd = """			var in_speed_zone = false
			var in_damage_zone = false
			var in_heal_zone = false
			var in_debuff_zone = false

			for zone in zones:
				var dx = b.x - zone["x"]
				var dy = b.y - zone["y"]
				var dist = sqrt(dx*dx + dy*dy)

				if dist <= zone["radius"]:
					if zone["type"] == "speed":
						in_speed_zone = true
					elif zone["type"] == "damage":
						in_damage_zone = true
					elif zone["type"] == "heal":
						in_heal_zone = true
					elif zone["type"] == "debuff":
						in_debuff_zone = true

			if in_speed_zone:
				b.speed = b.get_meta("base_speed") * 1.5
				b.set_meta("zone_modifier_speed", true)
			else:
				if b.has_meta("zone_modifier_speed"):
					b.speed = b.get_meta("base_speed")
					b.remove_meta("zone_modifier_speed")

			if in_damage_zone:
				b.damage = b.get_meta("base_damage") * 1.5
				b.set_meta("zone_modifier_damage", true)
			else:
				if b.has_meta("zone_modifier_damage"):
					b.damage = b.get_meta("base_damage")
					b.remove_meta("zone_modifier_damage")

			if in_debuff_zone:
				if not b.has_meta("base_max_hp"):
					b.set_meta("base_max_hp", b.get("max_hp", 100.0))
				b.max_hp = b.get_meta("base_max_hp") * 0.5
				if "hp" in b and b.hp > b.max_hp:
					b.hp = b.max_hp
				b.set_meta("zone_modifier_debuff", true)
			else:
				if b.has_meta("zone_modifier_debuff"):
					if b.has_meta("base_max_hp"):
						b.max_hp = b.get_meta("base_max_hp")
					b.remove_meta("zone_modifier_debuff")

			if in_heal_zone:"""
content_gd = content_gd.replace("""			var in_speed_zone = false
			var in_damage_zone = false
			var in_heal_zone = false

			for zone in zones:
				var dx = b.x - zone["x"]
				var dy = b.y - zone["y"]
				var dist = sqrt(dx*dx + dy*dy)

				if dist <= zone["radius"]:
					if zone["type"] == "speed":
						in_speed_zone = true
					elif zone["type"] == "damage":
						in_damage_zone = true
					elif zone["type"] == "heal":
						in_heal_zone = true

			if in_speed_zone:
				b.speed = b.get_meta("base_speed") * 1.5
				b.set_meta("zone_modifier_speed", true)
			else:
				if b.has_meta("zone_modifier_speed"):
					b.speed = b.get_meta("base_speed")
					b.remove_meta("zone_modifier_speed")

			if in_damage_zone:
				b.damage = b.get_meta("base_damage") * 1.5
				b.set_meta("zone_modifier_damage", true)
			else:
				if b.has_meta("zone_modifier_damage"):
					b.damage = b.get_meta("base_damage")
					b.remove_meta("zone_modifier_damage")

			if in_heal_zone:""", replacement_tick_gd)

with open("src/ai/game_modes.gd", "w") as f:
    f.write(content_gd)
