import re

# PATCH PYTHON FILE
py_file = "src/ai/game_modes.py"
with open(py_file, 'r') as f:
    py_content = f.read()

search_py = """                                if not hasattr(b, "elemental_auras"):
                                    b.elemental_auras = {"fire": 0, "water": 0, "earth": 0, "lightning": 0}
                                b.elemental_auras[element] = b.elemental_auras.get(element, 0) + 1
                                picked_up = True
                                break"""

replace_py = """                                if not hasattr(b, "elemental_auras"):
                                    b.elemental_auras = {"fire": 0, "water": 0, "earth": 0, "lightning": 0}
                                b.elemental_auras[element] = b.elemental_auras.get(element, 0) + 1
                                picked_up = True

                                # Disrupt random enemy aura
                                enemies = [eb for eb in balls if getattr(eb, "alive", False) and getattr(eb, "id", None) != getattr(b, "id", None) and getattr(eb, "team", "B") != getattr(b, "team", "A")]
                                random.shuffle(enemies)
                                for enemy in enemies:
                                    if hasattr(enemy, "elemental_auras"):
                                        has_auras = [k for k, v in enemy.elemental_auras.items() if v > 0]
                                        if has_auras:
                                            disrupted_element = random.choice(has_auras)
                                            enemy.elemental_auras[disrupted_element] -= 1
                                            if hasattr(world, "add_event"):
                                                world.add_event("aura_disrupted", {"id": enemy.id, "element": disrupted_element})
                                            break
                                break"""

py_content = py_content.replace(search_py, replace_py)

with open(py_file, 'w') as f:
    f.write(py_content)


# PATCH GD FILE
gd_file = "src/ai/game_modes.gd"
with open(gd_file, 'r') as f:
    gd_content = f.read()

search_gd = """								elif "elemental_auras" in b:
									auras = b.elemental_auras
									auras[element] = auras.get(element, 0) + 1
									b.elemental_auras = auras
								picked_up = true
								break"""

replace_gd = """								elif "elemental_auras" in b:
									auras = b.elemental_auras
									auras[element] = auras.get(element, 0) + 1
									b.elemental_auras = auras
								picked_up = true

								var b_team = "A"
								if typeof(b) != TYPE_DICTIONARY and b.has_method("has_meta") and b.has_meta("team"):
									b_team = b.get_meta("team")
								elif "team" in b:
									b_team = b.team
								var bid = b.get("id", "") if typeof(b) == TYPE_DICTIONARY else b.id

								var enemies_with_auras = []
								for eb in balls:
									var eb_alive = false
									if typeof(eb) != TYPE_DICTIONARY and eb.has_method("has_meta"):
										eb_alive = eb.get_meta("alive", true) if eb.has_meta("alive") else eb.alive
									elif "alive" in eb:
										eb_alive = eb.alive
									var ebid = eb.get("id", "") if typeof(eb) == TYPE_DICTIONARY else eb.id
									var eb_team = eb.get("team", "B") if typeof(eb) == TYPE_DICTIONARY else (eb.get_meta("team") if eb.has_method("has_meta") and eb.has_meta("team") else eb.team)
									if eb_alive and ebid != bid and eb_team != b_team:
										var e_auras = {}
										if typeof(eb) != TYPE_DICTIONARY and eb.has_method("has_meta") and eb.has_meta("elemental_auras"):
											e_auras = eb.get_meta("elemental_auras")
										elif "elemental_auras" in eb:
											e_auras = eb.elemental_auras
										var has_auras = []
										for k in e_auras.keys():
											if e_auras[k] > 0:
												has_auras.append(k)
										if has_auras.size() > 0:
											enemies_with_auras.append({"ball": eb, "has_auras": has_auras})

								if enemies_with_auras.size() > 0:
									var rng2 = RandomNumberGenerator.new()
									rng2.randomize()
									var target = enemies_with_auras[rng2.randi() % enemies_with_auras.size()]
									var e_ball = target["ball"]
									var disrupted_element = target["has_auras"][rng2.randi() % target["has_auras"].size()]

									var target_auras = {}
									if typeof(e_ball) != TYPE_DICTIONARY and e_ball.has_method("has_meta") and e_ball.has_meta("elemental_auras"):
										target_auras = e_ball.get_meta("elemental_auras")
									elif "elemental_auras" in e_ball:
										target_auras = e_ball.elemental_auras

									target_auras[disrupted_element] -= 1

									if typeof(e_ball) != TYPE_DICTIONARY and e_ball.has_method("has_meta"):
										e_ball.set_meta("elemental_auras", target_auras)
									elif "elemental_auras" in e_ball:
										e_ball.elemental_auras = target_auras

									if typeof(world) != TYPE_DICTIONARY and world.has_method("add_event"):
										var tid = e_ball.get("id", "") if typeof(e_ball) == TYPE_DICTIONARY else e_ball.id
										world.add_event("aura_disrupted", {"id": tid, "element": disrupted_element})

								break"""

gd_content = gd_content.replace(search_gd, replace_gd)

with open(gd_file, 'w') as f:
    f.write(gd_content)

print("Patched!")
