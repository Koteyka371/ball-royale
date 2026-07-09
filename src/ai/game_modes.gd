class_name GameModes

class GameMode:
	var name: String = "Unknown"
	var description: String = "Base game mode"

	func _init() -> void:
		pass

	func setup(world, balls: Array) -> void:
		if not "dead_balls" in world:
			world.set_meta("dead_balls", []) if world.has_method("set_meta") else null
		for b in balls:
			var sponsor = ""
			if "sponsor" in b:
				sponsor = b.sponsor
			elif b.has_method("get_meta") and b.has_meta("sponsor"):
				sponsor = b.get_meta("sponsor")

			if sponsor == "aggressor":
				if "max_hp" in b:
					b.max_hp *= 0.8
					if "hp" in b: b.hp = min(b.hp, b.max_hp)
			elif sponsor == "juggernaut":
				if "speed" in b: b.speed *= 0.8
				if "base_speed" in b: b.base_speed *= 0.8
				elif b.has_method("set_meta") and b.has_meta("base_speed"):
					b.set_meta("base_speed", float(b.get_meta("base_speed")) * 0.8)
			elif sponsor == "vampiric":
				if "max_hp" in b:
					b.max_hp *= 0.9
					if "hp" in b: b.hp = min(b.hp, b.max_hp)

			var traits_arr = []
			if typeof(b) == TYPE_OBJECT and "traits" in b and typeof(b.traits) == TYPE_ARRAY:
				traits_arr = b.traits
			elif typeof(b) == TYPE_OBJECT and b.has_method("get_meta") and b.has_meta("traits"):
				var meta_tr = b.get_meta("traits")
				if typeof(meta_tr) == TYPE_ARRAY:
					traits_arr = meta_tr
			elif typeof(b) == TYPE_DICTIONARY and b.has("traits") and typeof(b["traits"]) == TYPE_ARRAY:
				traits_arr = b["traits"]

			for trait_name in traits_arr:
				if typeof(trait_name) != TYPE_STRING: continue
				if trait_name == "swift":
					if "speed" in b: b.speed *= 1.05
					if "base_speed" in b: b.base_speed *= 1.05
					elif b.has_method("set_meta") and b.has_meta("base_speed"):
						b.set_meta("base_speed", float(b.get_meta("base_speed")) * 1.05)
				elif trait_name == "slow":
					if "speed" in b: b.speed *= 0.95
					if "base_speed" in b: b.base_speed *= 0.95
					elif b.has_method("set_meta") and b.has_meta("base_speed"):
						b.set_meta("base_speed", float(b.get_meta("base_speed")) * 0.95)
				elif trait_name == "sturdy":
					if "max_hp" in b:
						b.max_hp *= 1.05
						if "hp" in b: b.hp = min(b.hp * 1.05, b.max_hp)
				elif trait_name == "fragile":
					if "max_hp" in b:
						b.max_hp *= 0.95
						if "hp" in b: b.hp = min(b.hp, b.max_hp)
				elif trait_name == "lethal":
					if "damage" in b: b.damage *= 1.05
					if "base_damage" in b: b.base_damage *= 1.05
					elif b.has_method("set_meta") and b.has_meta("base_damage"):
						b.set_meta("base_damage", float(b.get_meta("base_damage")) * 1.05)
				elif trait_name == "weak":
					if "damage" in b: b.damage *= 0.95
					if "base_damage" in b: b.base_damage *= 0.95
					elif b.has_method("set_meta") and b.has_meta("base_damage"):
						b.set_meta("base_damage", float(b.get_meta("base_damage")) * 0.95)

		var season_num = 1
		if "leaderboard_manager" in world and world.leaderboard_manager != null:
			season_num = world.leaderboard_manager.data.get("current_season", 1)
		elif "profile_manager" in world and world.profile_manager != null:
			if "leaderboard_manager" in world.profile_manager and world.profile_manager.leaderboard_manager != null:
				season_num = world.profile_manager.leaderboard_manager.data.get("current_season", 1)

		var modifiers = {
			1: {"type": "global_speed", "value": 1.2},
			2: {"type": "global_damage", "value": 0.9},
			3: {"type": "global_hp", "value": 1.15},
			4: {"type": "global_cooldown", "value": 0.8}
		}

		var mod_index = ((season_num - 1) % 4) + 1
		var mod = modifiers[mod_index]

		var current_week = int(Time.get_unix_time_from_system() / (7.0 * 24.0 * 3600.0))
		var weekly_mutators = {
			0: {"type": "low_gravity"},
			1: {"type": "double_damage"},
			2: {"type": "high_speed"},
			3: {"type": "vampirism"}
		}
		var week_index = current_week % weekly_mutators.size()
		var week_mod = weekly_mutators[week_index]
		if typeof(world) == TYPE_OBJECT or typeof(world) == TYPE_DICTIONARY:
			if world is Object and world.has_method("set"):
				world.set("weekly_mutator", week_mod["type"])
			elif typeof(world) == TYPE_DICTIONARY:
				world["weekly_mutator"] = week_mod["type"]


		for b in balls:
			if b.ball_type != "spectator":
				if not ("experience" in b): b.experience = 0.0
				if not ("level" in b): b.level = 1
				if mod["type"] == "global_speed":
					if "base_speed" in b:
						b.base_speed = b.base_speed * mod["value"]
					elif b.has_method("get_meta") and b.has_meta("base_speed"):
						b.set_meta("base_speed", b.get_meta("base_speed") * mod["value"])
					if "speed" in b:
						b.speed = b.speed * mod["value"]
				elif mod["type"] == "global_damage":
					if "base_damage" in b:
						b.base_damage = b.base_damage * mod["value"]
					elif b.has_method("get_meta") and b.has_meta("base_damage"):
						b.set_meta("base_damage", b.get_meta("base_damage") * mod["value"])
					if "damage" in b:
						b.damage = b.damage * mod["value"]
				elif mod["type"] == "global_hp":
					if "max_hp" in b:
						b.max_hp = b.max_hp * mod["value"]
					elif b.has_method("get_meta") and b.has_meta("max_hp"):
						b.set_meta("max_hp", b.get_meta("max_hp") * mod["value"])
					if "hp" in b:
						if "max_hp" in b:
							b.hp = b.max_hp
						elif b.has_method("get_meta") and b.has_meta("max_hp"):
							b.hp = b.get_meta("max_hp")
				elif mod["type"] == "global_cooldown":
					if "cooldown_multiplier" in b:
						b.cooldown_multiplier = b.cooldown_multiplier * mod["value"]

					elif b.has_method("get_meta") and b.has_meta("cooldown_multiplier"):
						b.set_meta("cooldown_multiplier", b.get_meta("cooldown_multiplier") * mod["value"])
					elif b.has_method("set_meta"):
						b.set_meta("cooldown_multiplier", mod["value"])

				if week_mod["type"] == "double_damage":
					if "base_damage" in b:
						b.base_damage = b.base_damage * 2.0
					elif b.has_method("get_meta") and b.has_meta("base_damage"):
						b.set_meta("base_damage", b.get_meta("base_damage") * 2.0)
					if "damage" in b:
						b.damage = b.damage * 2.0
				elif week_mod["type"] == "high_speed":
					if "base_speed" in b:
						b.base_speed = b.base_speed * 1.5
					elif b.has_method("get_meta") and b.has_meta("base_speed"):
						b.set_meta("base_speed", b.get_meta("base_speed") * 1.5)
					if "speed" in b:
						b.speed = b.speed * 1.5
				elif week_mod["type"] == "vampirism":
					if "lifesteal" in b:
						b.lifesteal = b.lifesteal + 0.5
					elif b.has_method("get_meta"):
						b.set_meta("lifesteal", b.get_meta("lifesteal", 0.0) + 0.5)
				elif week_mod["type"] == "low_gravity":
					if "mass" in b:
						b.mass = b.mass * 0.5
					elif b.has_method("get_meta"):
						b.set_meta("mass", b.get_meta("mass", 1.0) * 0.5)


	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		var ax = anomaly_center["x"]
		var ay = anomaly_center["y"]

		var entities_to_process = []
		for b in balls:
			entities_to_process.append(b)

		if typeof(world) == TYPE_OBJECT:
			if "projectiles" in world and typeof(world.projectiles) == TYPE_ARRAY:
				for p in world.projectiles:
					entities_to_process.append(p)
			if "entities" in world and typeof(world.entities) == TYPE_ARRAY:
				for e in world.entities:
					if not entities_to_process.has(e):
						entities_to_process.append(e)
		elif typeof(world) == TYPE_DICTIONARY:
			if world.has("projectiles") and typeof(world["projectiles"]) == TYPE_ARRAY:
				for p in world["projectiles"]:
					entities_to_process.append(p)
			if world.has("entities") and typeof(world["entities"]) == TYPE_ARRAY:
				for e in world["entities"]:
					if not entities_to_process.has(e):
						entities_to_process.append(e)

		for b in entities_to_process:
			var alive = true
			if typeof(b) == TYPE_DICTIONARY:
				alive = b.get("alive", true)
			else:
				if "alive" in b: alive = b.alive
				elif b.has_method("has_meta") and b.has_meta("alive"): alive = b.get_meta("alive")

			if not alive: continue

			var bx = 0.0
			var by = 0.0
			var bvx = 0.0
			var bvy = 0.0
			var bspeed = 100.0
			var has_base_speed = false
			var b_base_speed = 100.0

			if typeof(b) == TYPE_DICTIONARY:
				bx = b.get("x", 0.0)
				by = b.get("y", 0.0)
				bvx = b.get("vx", 0.0)
				bvy = b.get("vy", 0.0)
				bspeed = b.get("speed", 100.0)
				if b.has("base_speed"):
					has_base_speed = true
					b_base_speed = b.get("base_speed")
			else:
				if "x" in b: bx = b.x
				if "y" in b: by = b.y
				if "vx" in b: bvx = b.vx
				if "vy" in b: bvy = b.vy
				if "speed" in b: bspeed = b.speed
				if "base_speed" in b:
					has_base_speed = true
					b_base_speed = b.base_speed
				elif b.has_method("has_meta") and b.has_meta("base_speed"):
					has_base_speed = true
					b_base_speed = b.get_meta("base_speed")

			if not has_base_speed:
				b_base_speed = bspeed
				if typeof(b) == TYPE_DICTIONARY:
					b["base_speed"] = b_base_speed
				elif b.has_method("set_meta"):
					b.set_meta("base_speed", b_base_speed)

			var dx = ax - bx
			var dy = ay - by
			var dist = sqrt(dx*dx + dy*dy)

			if dist > 0 and dist < anomaly_radius:
				var nx = dx / dist
				var ny = dy / dist

				var v_mag = sqrt(bvx*bvx + bvy*bvy)
				if v_mag > 0.1:
					var dir_x = bvx / v_mag
					var dir_y = bvy / v_mag

					var dot_prod = dir_x * nx + dir_y * ny
					var speed_mult = 1.0 + (dot_prod * 0.5)

					if typeof(b) == TYPE_DICTIONARY:
						b["speed"] = b_base_speed * speed_mult
					elif "speed" in b:
						b.speed = b_base_speed * speed_mult

					var tx = -ny
					var ty = nx
					var curve_strength = 200.0 * delta
					var cross = dir_x * ty - dir_y * tx

					if cross > 0:
						bvx += tx * curve_strength
						bvy += ty * curve_strength
					else:
						bvx -= tx * curve_strength
						bvy -= ty * curve_strength

					if typeof(b) == TYPE_DICTIONARY:
						b["vx"] = bvx
						b["vy"] = bvy
					else:
						if "vx" in b: b.vx = bvx
						if "vy" in b: b.vy = bvy
			else:
				if typeof(b) == TYPE_DICTIONARY:
					b["speed"] = b_base_speed
				elif "speed" in b:
					b.speed = b_base_speed
var GAME_MODES = {
	"multiple_safe_zones": MultipleSafeZonesMode.new(),
	"entanglement_mutator": EntanglementMutatorMode.new(),
	"freeze_tag": FreezeTagMode.new(),
	"physics_anomaly_event": PhysicsAnomalyEventMode.new(),
	"spiked_walls": SpikedWallsMode.new(),
	"blackout_event": BlackoutEventMode.new(),
	"solar_flare": SolarFlareMode.new(),
	"center_black_hole": CenterBlackHoleMode.new(),
	"extreme_weather": ExtremeWeatherMode.new(),
	"invisible_decoys": InvisibleDecoysMode.new(),
	"reversed_input": ReversedInputMode.new(),
	"sweeping_paddles": SweepingPaddlesMode.new(),
	"artifact_upgrader": ArtifactUpgraderMode.new(),
	"meteor_shower": MeteorShowerMode.new(),
	"rolling_boulders": RollingBouldersMode.new(),
	"scrambler_drones": ScramblerDroneMode.new()
,
	"blizzard_mode": BlizzardMode.new(),

	"black_market": BlackMarketMode.new(),
	"floor_is_lava": FloorIsLavaMode.new(),


	"geometric_zone": GeometricZoneMode.new(),
	"daily_mutator": DailyMutatorMode.new(),
	"exploding_decoys": ExplodingDecoysMode.new(),
	"factory": FactoryMode.new(),
	"invisible_walls": InvisibleWallsMode.new(),
	"mirror_walls": MirrorWallsMode.new(),
	"stamina_regen": StaminaRegenMode.new(),
	"zero_gravity": ZeroGravityMode.new(),
	"magnetic_collisions": MagneticCollisionsMode.new(),
	"polarity_shift": PolarityShiftMode.new(),
	"day_night_mode": DayNightMode.new(),
	"shifting_maze": ShiftingMazeMode.new(),
	"maze_safe_zone": MazeSafeZoneMode.new(),
	"stamina_speed": StaminaSpeedMode.new(),

	"blackout": BlackoutMode.new(),
	"dual_payload": DualPayloadMode.new(),
	"tug_of_war": TugOfWarMode.new(),
	"ticking_payload": TickingPayloadMode.new(),
	"reverse_tug_of_war": ReverseTugOfWarMode.new(),
	"reverse_gravity_event": ReverseGravityEventMode.new(),
	"escort": EscortMode.new(),
	"windstorm": WindstormMode.new(),
	"modifier_zones": ModifierZonesMode.new(),
	"modifier_zones_safe_zone": ModifierZonesSafeZoneMode.new(),
	"draft_royale": DraftRoyaleMode.new(),
	"tournament": TournamentMode.new(),
	"pacifist_knockout": PacifistKnockoutMode.new(),
	"bumper_balls": BumperBallsMode.new(),
	"sumo_knockout": SumoKnockoutMode.new(),
	"bouncy_terrain": BouncyTerrainMode.new(),
	"pinball": PinballMode.new(),
	"portal_node": PortalNodeMode.new(),
	"memory_traps": MemoryTrapsMode.new(),
	"pitch_black": PitchBlackMode.new(),
	"vision_reduced": VisionReducedMode.new(),
	"emp_burst": EMPBurstMode.new(),
	"dynamic_hazards": DynamicHazardsMode.new(),
	"custom_match": CustomMatchMode.new(),
	"reverse_event": ReverseEventMode.new(),
	"unstable_portals_event": UnstablePortalsEventMode.new(),
	"minefield_event": MinefieldEventMode.new(),
	"meteor_crash_event": MeteorCrashEventMode.new(),
	"lightning_strike_event": LightningStrikeEventMode.new(),
	"chain_lightning_storm": ChainLightningStormMode.new(),
	"weather_chaos": WeatherChaosMode.new(),
	"lunar_eclipse_event": LunarEclipseEventMode.new(),
	"domination": DominationMode.new(),
	"black_hole": BlackHoleMode.new(),
	"sweeping_black_hole": SweepingBlackHoleMode.new(),
	"gravity_well": GravityWellMode.new(),
	"king_of_the_hill": KingOfTheHillMode.new(),
	"moving_zone": MovingZoneMode.new(),
	"vampire_royale": VampireRoyaleMode.new(),
	"battle_royale": BattleRoyaleMode.new(),
	"team_deathmatch": TeamDeathmatchMode.new(),
	"zombie_infection": ZombieInfectionMode.new(),
	"boss_fight": BossFightMode.new(),
	"juggernaut": JuggernautMode.new(),
	"guild_boss_fight": GuildBossFightMode.new(),
	"vip_defense": VIPDefenseMode.new(),
	"survival": SurvivalMode.new(),
	"toxic_environment": ToxicEnvironmentMode.new(),
	"capture_the_flag": CaptureTheFlagMode.new(),
	"evolutionary_simulation": EvolutionarySimulationMode.new(),
	"interactive_training": load("res://src/ai/interactive_training.gd").new(),
	"shrinking_danger_zone": ShrinkingDangerZoneMode.new(),
	"shrinking_boundary": ShrinkingBoundaryMode.new(),
	"inverse_safe_zone": InverseSafeZoneMode.new(),
	"safe_zone": SafeZoneMode.new(),
	"hex_grid_royale": HexGridRoyaleMode.new(),
	"minefield_safe_zone": MinefieldSafeZoneMode.new(),
	"dynamic_safe_zone": DynamicSafeZoneMode.new(),
	"moving_safe_zone": MovingSafeZoneMode.new(),
	"poison_gas_zone": PoisonGasZoneMode.new(),
	"bounty_hunt": BountyHuntMode.new(),
	"earthquake": EarthquakeMode.new(),
	"inverse_mirror_arena": InverseMirrorArenaMode.new(),
	"mirror_match": MirrorMatchMode.new(),
	"clone_trail": CloneTrailMode.new(),
	"clone_chaos": CloneChaosMode.new(),
	"volatile_clones": VolatileClonesMode.new(),
	"supernova": SupernovaMode.new(),
	"echolocation": EcholocationMode.new(),
	"body_swap": BodySwapMode.new(),
	"hazard_billiards": HazardBilliardsMode.new(),
	"time_rewind": TimeRewindMode.new(),
	"rhythm_panels": RhythmPanelsMode.new(),
	"cursed_buff_zone": CursedBuffZoneMode.new(),
	"weapon_collection": WeaponCollectionMode.new(),
	"soul_link": SoulLinkMode.new(),
	"clan_tournament": ClanTournamentMode.new(),
	"tag_team": TagTeamMode.new(),
	"rubber_band": RubberBandMode.new(),
	"rift_roulette": RiftRouletteMode.new(),
	"item_morph": ItemMorphMode.new(),
	"illusion_wall": IllusionWallMode.new(),

	"crossfire": CrossfireMode.new(),
	"reverse_friction": preload("res://src/ai/reverse_friction.gd").ReverseFrictionMode.new(),
	"underground_tunnels": UndergroundTunnelMode.new()
}


class CrossfireMode extends GameMode:
	func _init().():
		name = "Crossfire"
		description = "Balls are divided into two teams on opposite sides of a center line. Players cannot cross the line but can throw hazards and boosters."

	func setup(world, balls: Array) -> void:
		.setup(world, balls)
		var arena_width = 1000.0
		if typeof(world) == TYPE_OBJECT and world.get("arena"):
			arena_width = float(world.arena.get("width"))
		elif typeof(world) == TYPE_DICTIONARY and world.has("arena"):
			arena_width = float(world["arena"].get("width") if typeof(world["arena"]) == TYPE_OBJECT else world["arena"]["width"])

		var alive_balls = []
		for b in balls:
			var is_spec = false
			if typeof(b) == TYPE_OBJECT and b.get("ball_type") == "spectator":
				is_spec = true
			elif typeof(b) == TYPE_DICTIONARY and b.has("ball_type") and b["ball_type"] == "spectator":
				is_spec = true
			if not is_spec:
				alive_balls.append(b)

		alive_balls.shuffle()
		var midpoint = alive_balls.size() / 2

		for i in range(alive_balls.size()):
			var b = alive_balls[i]
			var is_left = (i < midpoint)
			var team_name = "team_left" if is_left else "team_right"
			var pos_x = 0.0

			if is_left:
				pos_x = rand_range(50.0, arena_width / 2.0 - 50.0)
			else:
				pos_x = rand_range(arena_width / 2.0 + 50.0, arena_width - 50.0)

			if typeof(b) == TYPE_OBJECT:
				b.set("team", team_name)
				b.set("x", pos_x)
			elif typeof(b) == TYPE_DICTIONARY:
				b["team"] = team_name
				b["x"] = pos_x

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)
		var arena_width = 1000.0
		if typeof(world) == TYPE_OBJECT and world.get("arena"):
			arena_width = float(world.arena.get("width"))
		elif typeof(world) == TYPE_DICTIONARY and world.has("arena"):
			arena_width = float(world["arena"].get("width") if typeof(world["arena"]) == TYPE_OBJECT else world["arena"]["width"])

		var center_line = arena_width / 2.0

		for b in balls:
			var is_alive = false
			if typeof(b) == TYPE_OBJECT and b.get("alive"):
				is_alive = true
			elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"]:
				is_alive = true

			if not is_alive:
				continue

			var team = null
			var radius = 15.0
			var b_x = 0.0
			var vx = 0.0

			if typeof(b) == TYPE_OBJECT:
				team = b.get("team")
				radius = b.get("radius")
				b_x = b.get("x")
				vx = b.get("vx") if b.get("vx") != null else 0.0
			elif typeof(b) == TYPE_DICTIONARY:
				team = b.get("team")
				radius = b.get("radius")
				b_x = b.get("x")
				vx = b.get("vx") if b.has("vx") else 0.0

			if team == "team_left":
				if b_x + radius > center_line:
					var new_x = center_line - radius
					var new_vx = -abs(vx) * 0.5
					if typeof(b) == TYPE_OBJECT:
						b.set("x", new_x)
						b.set("vx", new_vx)
					elif typeof(b) == TYPE_DICTIONARY:
						b["x"] = new_x
						b["vx"] = new_vx
			elif team == "team_right":
				if b_x - radius < center_line:
					var new_x = center_line + radius
					var new_vx = abs(vx) * 0.5
					if typeof(b) == TYPE_OBJECT:
						b.set("x", new_x)
						b.set("vx", new_vx)
					elif typeof(b) == TYPE_DICTIONARY:
						b["x"] = new_x
						b["vx"] = new_vx


class TagTeamMode extends GameMode:
	var swap_timer: float = 0.0
	var swap_interval: float = 10.0
	var team_counter: int = 1

	func _init().():
		name = "Tag Team"
		description = "Players queue as a team of two balls but only one is active at a time. The active ball swaps with their teammate on a cooldown."

	func setup(world, balls: Array) -> void:
		.setup(world, balls)
		swap_timer = 0.0

		var alive_balls = []
		for b in balls:
			var b_type = b.ball_type if "ball_type" in b else ""
			if b_type != "spectator":
				alive_balls.append(b)

		alive_balls.shuffle()
		team_counter = 1

		var i = 0
		while i < alive_balls.size() - 1:
			var b1 = alive_balls[i]
			var b2 = alive_balls[i+1]

			if typeof(b1) == TYPE_OBJECT:
				b1.set_meta("tag_team_id", team_counter)
				b1.set_meta("tag_original_ball_type", b1.get("ball_type") if "ball_type" in b1 else "player")
				b1.set_meta("tag_original_team", b1.get("team") if "team" in b1 else "players")
			elif typeof(b1) == TYPE_DICTIONARY:
				b1["tag_team_id"] = team_counter
				b1["tag_original_ball_type"] = b1["ball_type"] if b1.has("ball_type") else "player"
				b1["tag_original_team"] = b1["team"] if b1.has("team") else "players"

			if typeof(b2) == TYPE_OBJECT:
				b2.set_meta("tag_team_id", team_counter)
				b2.set_meta("tag_original_ball_type", b2.get("ball_type") if "ball_type" in b2 else "player")
				b2.set_meta("tag_original_team", b2.get("team") if "team" in b2 else "players")

				b2.set("ball_type", "spectator")
				b2.set("team", "spectator")
				b2.set("x", -1000.0)
				b2.set("y", -1000.0)
			elif typeof(b2) == TYPE_DICTIONARY:
				b2["tag_team_id"] = team_counter
				b2["tag_original_ball_type"] = b2["ball_type"] if b2.has("ball_type") else "player"
				b2["tag_original_team"] = b2["team"] if b2.has("team") else "players"

				b2["ball_type"] = "spectator"
				b2["team"] = "spectator"
				b2["x"] = -1000.0
				b2["y"] = -1000.0

			team_counter += 1
			i += 2

		if alive_balls.size() % 2 != 0:
			var last_ball = alive_balls[alive_balls.size() - 1]
			if typeof(last_ball) == TYPE_OBJECT:
				last_ball.set_meta("tag_team_id", team_counter)
			elif typeof(last_ball) == TYPE_DICTIONARY:
				last_ball["tag_team_id"] = team_counter

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)

		swap_timer += delta
		if swap_timer >= swap_interval:
			swap_timer = 0.0

			var teams = {}
			for b in balls:
				var is_alive = false
				if typeof(b) == TYPE_OBJECT and b.get("alive"):
					is_alive = true
				elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"]:
					is_alive = true

				if not is_alive:
					continue

				var tid = null
				if typeof(b) == TYPE_OBJECT and b.has_meta("tag_team_id"):
					tid = b.get_meta("tag_team_id")
				elif typeof(b) == TYPE_DICTIONARY and b.has("tag_team_id"):
					tid = b["tag_team_id"]

				if tid != null:
					if not teams.has(tid):
						teams[tid] = []
					teams[tid].append(b)

			for tid in teams:
				var members = teams[tid]
				if members.size() == 2:
					var b1 = members[0]
					var b2 = members[1]

					var b1_is_spec = false
					if typeof(b1) == TYPE_OBJECT and b1.get("ball_type") == "spectator":
						b1_is_spec = true
					elif typeof(b1) == TYPE_DICTIONARY and b1.has("ball_type") and b1["ball_type"] == "spectator":
						b1_is_spec = true

					var b2_is_spec = false
					if typeof(b2) == TYPE_OBJECT and b2.get("ball_type") == "spectator":
						b2_is_spec = true
					elif typeof(b2) == TYPE_DICTIONARY and b2.has("ball_type") and b2["ball_type"] == "spectator":
						b2_is_spec = true

					var inactive = null
					var active = null

					if b1_is_spec and not b2_is_spec:
						inactive = b1
						active = b2
					elif b2_is_spec and not b1_is_spec:
						inactive = b2
						active = b1
					else:
						continue

					var a_x = 0.0
					var a_y = 0.0
					var a_vx = 0.0
					var a_vy = 0.0

					if typeof(active) == TYPE_OBJECT:
						a_x = active.get("x") if "x" in active else 0.0
						a_y = active.get("y") if "y" in active else 0.0
						a_vx = active.get("vx") if "vx" in active else 0.0
						a_vy = active.get("vy") if "vy" in active else 0.0

						active.set("ball_type", "spectator")
						active.set("team", "spectator")
						active.set("x", -1000.0)
						active.set("y", -1000.0)
					elif typeof(active) == TYPE_DICTIONARY:
						a_x = active["x"] if active.has("x") else 0.0
						a_y = active["y"] if active.has("y") else 0.0
						a_vx = active["vx"] if active.has("vx") else 0.0
						a_vy = active["vy"] if active.has("vy") else 0.0

						active["ball_type"] = "spectator"
						active["team"] = "spectator"
						active["x"] = -1000.0
						active["y"] = -1000.0

					if typeof(inactive) == TYPE_OBJECT:
						var orig_type = inactive.get_meta("tag_original_ball_type") if inactive.has_meta("tag_original_ball_type") else "player"
						var orig_team = inactive.get_meta("tag_original_team") if inactive.has_meta("tag_original_team") else "players"
						inactive.set("ball_type", orig_type)
						inactive.set("team", orig_team)
						inactive.set("x", a_x)
						inactive.set("y", a_y)
						inactive.set("vx", a_vx)
						inactive.set("vy", a_vy)
					elif typeof(inactive) == TYPE_DICTIONARY:
						var orig_type = inactive["tag_original_ball_type"] if inactive.has("tag_original_ball_type") else "player"
						var orig_team = inactive["tag_original_team"] if inactive.has("tag_original_team") else "players"
						inactive["ball_type"] = orig_type
						inactive["team"] = orig_team
						inactive["x"] = a_x
						inactive["y"] = a_y
						inactive["vx"] = a_vx
						inactive["vy"] = a_vy



class TeleporterHubMode extends GameMode:
	var hub_x: float = 400.0
	var hub_y: float = 300.0
	var shift_timer: float = 0.0
	var shift_interval: float = 5.0
	var peripheral_zones: Array = []
	var portals: Array = []

	func _init().():
		name = "Teleporter Hub"
		description = "A central teleporter hub that randomly connects to various peripheral zones, shifting its destinations every few seconds."

	func setup(world, balls: Array) -> void:
		.setup(world, balls)
		shift_timer = 0.0

		var arena_w = 800.0
		var arena_h = 600.0
		if world and "arena" in world and world.arena:
			arena_w = world.arena.width if "width" in world.arena else 800.0
			arena_h = world.arena.height if "height" in world.arena else 600.0

		hub_x = arena_w / 2.0
		hub_y = arena_h / 2.0

		peripheral_zones = [
			[100.0, 100.0],
			[arena_w - 100.0, 100.0],
			[100.0, arena_h - 100.0],
			[arena_w - 100.0, arena_h - 100.0],
			[arena_w / 2.0, 100.0],
			[arena_w / 2.0, arena_h - 100.0],
			[100.0, arena_h / 2.0],
			[arena_w - 100.0, arena_h / 2.0]
		]

		_spawn_portals(world)

	func _spawn_portals(world) -> void:
		if not world or not "arena" in world or not "hazards" in world.arena:
			return

		# Remove existing
		var new_hazards = []
		for h in world.arena.hazards:
			if not (typeof(h) == TYPE_OBJECT and h.has_method("get_meta") and h.get_meta("mode_teleporter")):
				if not (typeof(h) == TYPE_DICTIONARY and h.has("mode_teleporter")):
					if not ("mode_teleporter" in h and h.mode_teleporter):
						new_hazards.append(h)
		world.arena.hazards = new_hazards
		portals = []

		var num_destinations = randi() % 2 + 3 # 3 or 4
		var dests = []
		var available_zones = peripheral_zones.duplicate()
		for i in range(num_destinations):
			var idx = randi() % available_zones.size()
			dests.append(available_zones[idx])
			available_zones.remove(idx)

		var HazardObj = load("res://src/arena/procedural_arena.gd").Hazard

		for i in range(dests.size()):
			var dx = dests[i][0]
			var dy = dests[i][1]

			var p_out
			if typeof(world.arena.hazards) == TYPE_ARRAY:
				p_out = HazardObj.new("hub_dest_in_" + str(i), dx, dy, 30.0, "teleporter", 0.0)
				p_out.set_meta("mode_teleporter", true)
				p_out.set_meta("target_x", hub_x + randf_range(-10, 10))
				p_out.set_meta("target_y", hub_y + randf_range(-10, 10))
				# Compatibility fallback
				p_out.target_x = hub_x + randf_range(-10, 10)
				p_out.target_y = hub_y + randf_range(-10, 10)
				p_out.mode_teleporter = true

			world.arena.hazards.append(p_out)
			portals.append(p_out)

			var angle = (float(i) / float(num_destinations)) * 2.0 * PI
			var cx = hub_x + cos(angle) * 30.0
			var cy = hub_y + sin(angle) * 30.0

			var p_in
			if typeof(world.arena.hazards) == TYPE_ARRAY:
				p_in = HazardObj.new("hub_dest_out_" + str(i), cx, cy, 30.0, "teleporter", 0.0)
				p_in.set_meta("mode_teleporter", true)
				p_in.set_meta("target_x", dx + randf_range(-10, 10))
				p_in.set_meta("target_y", dy + randf_range(-10, 10))
				p_in.target_x = dx + randf_range(-10, 10)
				p_in.target_y = dy + randf_range(-10, 10)
				p_in.mode_teleporter = true

			world.arena.hazards.append(p_in)
			portals.append(p_in)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)

		shift_timer += delta
		if shift_timer >= shift_interval:
			shift_timer = 0.0
			_spawn_portals(world)
			if world.has_method("add_event"):
				world.add_event("portal_shift", {"type": "portal_shift", "message": "Teleporter Hub destinations shifted!"})

class RubberBandMode extends GameMode:
	var max_distance: float = 300.0
	var snap_force: float = 1500.0
	var damage: float = 50.0

	func _init().():
		name = "Rubber Band"
		description = "Teams are tethered by invisible rubber bands. If they move too far apart, they snap back together with massive force, dealing damage to anything in their path."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)

		var teams = {}
		for b in balls:
			var is_alive = false
			if typeof(b) == TYPE_OBJECT and b.get("alive"):
				is_alive = true
			elif typeof(b) == TYPE_DICTIONARY and b.has("alive") and b["alive"]:
				is_alive = true

			if not is_alive:
				continue

			var team = null
			if typeof(b) == TYPE_OBJECT and "team" in b:
				team = b.get("team")
			elif typeof(b) == TYPE_DICTIONARY and b.has("team"):
				team = b["team"]

			if team != null:
				if not teams.has(team):
					teams[team] = []
				teams[team].append(b)

		for team in teams.keys():
			var tballs = teams[team]
			var size = tballs.size()
			if size < 2:
				continue

			for i in range(size):
				for j in range(i + 1, size):
					var b1 = tballs[i]
					var b2 = tballs[j]

					var b1_x = 0.0
					var b1_y = 0.0
					if typeof(b1) == TYPE_OBJECT:
						b1_x = b1.get("x") if "x" in b1 else 0.0
						b1_y = b1.get("y") if "y" in b1 else 0.0
					else:
						b1_x = b1["x"] if b1.has("x") else 0.0
						b1_y = b1["y"] if b1.has("y") else 0.0

					var b2_x = 0.0
					var b2_y = 0.0
					if typeof(b2) == TYPE_OBJECT:
						b2_x = b2.get("x") if "x" in b2 else 0.0
						b2_y = b2.get("y") if "y" in b2 else 0.0
					else:
						b2_x = b2["x"] if b2.has("x") else 0.0
						b2_y = b2["y"] if b2.has("y") else 0.0

					var dx = b2_x - b1_x
					var dy = b2_y - b1_y
					var dist = sqrt(dx * dx + dy * dy)

					if dist > max_distance:
						var excess = dist - max_distance
						var pull = (excess / max_distance) * snap_force

						var nx = dx / dist
						var ny = dy / dist

						var b1_vx = 0.0
						var b1_vy = 0.0
						if typeof(b1) == TYPE_OBJECT:
							b1_vx = b1.get("vx") if "vx" in b1 else 0.0
							b1_vy = b1.get("vy") if "vy" in b1 else 0.0
							b1.set("vx", b1_vx + nx * pull * delta)
							b1.set("vy", b1_vy + ny * pull * delta)
						else:
							b1_vx = b1["vx"] if b1.has("vx") else 0.0
							b1_vy = b1["vy"] if b1.has("vy") else 0.0
							b1["vx"] = b1_vx + nx * pull * delta
							b1["vy"] = b1_vy + ny * pull * delta

						var b2_vx = 0.0
						var b2_vy = 0.0
						if typeof(b2) == TYPE_OBJECT:
							b2_vx = b2.get("vx") if "vx" in b2 else 0.0
							b2_vy = b2.get("vy") if "vy" in b2 else 0.0
							b2.set("vx", b2_vx - nx * pull * delta)
							b2.set("vy", b2_vy - ny * pull * delta)
						else:
							b2_vx = b2["vx"] if b2.has("vx") else 0.0
							b2_vy = b2["vy"] if b2.has("vy") else 0.0
							b2["vx"] = b2_vx - nx * pull * delta
							b2["vy"] = b2_vy - ny * pull * delta

						for other in balls:
							var other_alive = false
							if typeof(other) == TYPE_OBJECT and other.get("alive"):
								other_alive = true
							elif typeof(other) == TYPE_DICTIONARY and other.has("alive") and other["alive"]:
								other_alive = true

							if not other_alive or other == b1 or other == b2:
								continue

							var other_x = 0.0
							var other_y = 0.0
							var other_radius = 15.0

							if typeof(other) == TYPE_OBJECT:
								other_x = other.get("x") if "x" in other else 0.0
								other_y = other.get("y") if "y" in other else 0.0
								other_radius = other.get("radius") if "radius" in other else 15.0
							else:
								other_x = other["x"] if other.has("x") else 0.0
								other_y = other["y"] if other.has("y") else 0.0
								other_radius = other["radius"] if other.has("radius") else 15.0

							var px = other_x - b1_x
							var py = other_y - b1_y

							var dot = px * nx + py * ny
							if dot >= 0 and dot <= dist:
								var cx = b1_x + dot * nx
								var cy = b1_y + dot * ny

								var cdx = other_x - cx
								var cdy = other_y - cy
								var cdist = sqrt(cdx * cdx + cdy * cdy)

								if cdist <= other_radius + 5.0:
									var damage_val = damage * delta * 60.0
									if world and world.has_method("_deal_damage"):
										world._deal_damage(b1, other, damage_val)
									else:
										if typeof(other) == TYPE_OBJECT:
											var hp = other.get("hp") if "hp" in other else 100.0
											other.set("hp", hp - damage_val)
										else:
											var hp = other["hp"] if other.has("hp") else 100.0
											other["hp"] = hp - damage_val
class RiftRouletteMode extends GameMode:
	var cycle_timer: float = 0.0
	var cycle_interval: float = 8.0
	var portals: Array = []

	func _init().():
		name = "Rift Roulette"
		description = "Two pairs of interconnected portals periodically spawn and swap positions, allowing players to instantly traverse the map but also throwing unexpected hazards through the rifts."

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)

		cycle_timer -= delta
		if cycle_timer <= 0:
			cycle_timer = cycle_interval

			if world and "arena" in world and "hazards" in world.arena:
				var new_hazards = []
				for h in world.arena.hazards:
					var keep = true
					if typeof(h) == TYPE_OBJECT:
						if h.has_method("get_meta") and (h.get_meta("is_rift_portal") or h.get_meta("is_rift_hazard")):
							keep = false
						elif "is_rift_portal" in h and h.is_rift_portal:
							keep = false
						elif "is_rift_hazard" in h and h.is_rift_hazard:
							keep = false
					elif typeof(h) == TYPE_DICTIONARY:
						if h.has("is_rift_portal") and h["is_rift_portal"]:
							keep = false
						if h.has("is_rift_hazard") and h["is_rift_hazard"]:
							keep = false
					if keep:
						new_hazards.append(h)
				world.arena.hazards = new_hazards

				var arena_w = world.arena.width if "width" in world.arena else 800.0
				var arena_h = world.arena.height if "height" in world.arena else 600.0

				portals = []
				var HazardObj = load("res://src/arena/procedural_arena.gd").Hazard

				for i in range(2):
					var p1_id = "rift_" + str(i) + "_a"
					var p2_id = "rift_" + str(i) + "_b"

					var x1 = randf_range(100, arena_w - 100)
					var y1 = randf_range(100, arena_h - 100)
					var x2 = randf_range(100, arena_w - 100)
					var y2 = randf_range(100, arena_h - 100)

					var p1 = HazardObj.new(p1_id, x1, y1, 30.0, "teleporter", 0.0)
					p1.set_meta("target_x", x2)
					p1.set_meta("target_y", y2)
					p1.set_meta("is_rift_portal", true)

					var p2 = HazardObj.new(p2_id, x2, y2, 30.0, "teleporter", 0.0)
					p2.set_meta("target_x", x1)
					p2.set_meta("target_y", y1)
					p2.set_meta("is_rift_portal", true)

					world.arena.hazards.append(p1)
					world.arena.hazards.append(p2)
					portals.append(p1)
					portals.append(p2)

				if world.has_method("add_event"):
					world.add_event("rifts_shifted", {"message": "Rifts have shifted positions!"})

				for p in portals:
					if randf() < 0.5:
						var h_types = ["meteor", "tornado", "black_hole", "poison_cloud"]
						var h_type = h_types[randi() % h_types.size()]
						var h = HazardObj.new("rift_hazard_" + str(randi() % 10000), p.x, p.y, 20.0, h_type, 10.0)
						h.set_meta("is_rift_hazard", true)
						h.duration = 5.0
						world.arena.hazards.append(h)


class ItemMorphMode extends GameMode:
	var morph_timer: float = 0.0
	var morph_interval: float = 10.0
	var rng = RandomNumberGenerator.new()
	var booster_kinds = ["damage_link_booster", "speed_booster", "hologram_booster", "damage_booster", "hp_booster", "vision_booster", "stamina_booster", "pull_booster", "nemesis_booster", "nemesis_compass_item", "shadow_booster", "stealth_booster", "weather_scanner_item", "aura_booster", "emp_immunity_booster", "cleanse_booster", "fake_booster", "cursed_booster", "grapple_booster", "time_rewind_booster", "time_stop_booster", "instant_rewind_booster", "half_reflect_shield_booster", "projectile_reflect_booster", "rearm_token"]

	func _init().():
		name = "Item Morph"
		description = "Periodically, all active items and boosters in the arena randomly transform into different item types, keeping players constantly adapting."
		rng.randomize()

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		.tick(world, balls, delta)
		morph_timer += delta
		while morph_timer >= morph_interval:
			morph_timer -= morph_interval
			if typeof(world) == TYPE_DICTIONARY and world.has("boosters") and typeof(world.boosters) == TYPE_ARRAY and world.boosters.size() > 0:
				var morphed = false
				for b in world.boosters:
					var active = true
					if typeof(b) == TYPE_DICTIONARY:
						if b.has("active"): active = b["active"]
					elif typeof(b) == TYPE_OBJECT:
						if "active" in b: active = b.get("active")

					if active:
						var new_kind = booster_kinds[rng.randi() % booster_kinds.size()]
						if typeof(b) == TYPE_DICTIONARY:
							b["kind"] = new_kind
						elif typeof(b) == TYPE_OBJECT:
							b.set("kind", new_kind)
						morphed = true

				if morphed and world.has("add_event"):
					if typeof(world.add_event) == TYPE_OBJECT and world.add_event.has_method("call"):
						world.add_event.call("items_morphed", {"message": "All items have morphed!"})
					elif world.has_method("add_event"):
						world.add_event("items_morphed", {"message": "All items have morphed!"})
			elif typeof(world) == TYPE_OBJECT and "boosters" in world and typeof(world.boosters) == TYPE_ARRAY and world.boosters.size() > 0:
				var morphed = false
				for b in world.boosters:
					var active = true
					if typeof(b) == TYPE_DICTIONARY:
						if b.has("active"): active = b["active"]
					elif typeof(b) == TYPE_OBJECT:
						if "active" in b: active = b.get("active")

					if active:
						var new_kind = booster_kinds[rng.randi() % booster_kinds.size()]
						if typeof(b) == TYPE_DICTIONARY:
							b["kind"] = new_kind
						elif typeof(b) == TYPE_OBJECT:
							b.set("kind", new_kind)
						morphed = true

				if morphed and world.has_method("add_event"):
					world.add_event("items_morphed", {"message": "All items have morphed!"})


class IllusionWallMode extends GameMode:
	var decoy_id_counter = 800000

	func _init():
		name = "Illusion Wall"
		description = "Hazard objects that look like solid walls but are actually reflective illusions. Passing through them creates a temporary fake decoy of the ball that moves in the opposite direction."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		if world == null or not ("arena" in world) or world.arena == null:
			return

		if not ("hazards" in world.arena):
			return

		var arena_w = 800.0
		if "width" in world.arena:
			arena_w = world.arena.width
		var arena_h = 600.0
		if "height" in world.arena:
			arena_h = world.arena.height

		for i in range(5):
			var h_id = 95000 + world.arena.hazards.size() + i
			var x = 200.0 + randf() * (arena_w - 400.0)
			var y = 200.0 + randf() * (arena_h - 400.0)

			var wall = {
				"id": h_id,
				"x": x,
				"y": y,
				"radius": 80.0,
				"target_radius": 80.0,
				"kind": "illusion_wall",
				"damage": 0.0,
				"active": true
			}
			world.arena.hazards.append(wall)

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		if world != null and "arena" in world and world.arena != null and "hazards" in world.arena:
			for h in world.arena.hazards:
				var kind = ""
				if typeof(h) == TYPE_DICTIONARY:
					kind = h.get("kind", "")
				else:
					kind = h.get("kind")

				if kind == "illusion_wall":
					for b in balls:
						if typeof(b) == TYPE_DICTIONARY:
							if not b.get("alive", false) or b.get("is_decoy", false) or b.get("ball_type", "") == "spectator":
								continue
						else:
							if not b.get("alive") or b.get("is_decoy") or b.get("ball_type") == "spectator":
								continue

						var h_id = -1
						var h_x = 0.0
						var h_y = 0.0
						var h_radius = 80.0
						if typeof(h) == TYPE_DICTIONARY:
							h_id = h.get("id", -1)
							h_x = h.get("x", 0.0)
							h_y = h.get("y", 0.0)
							h_radius = h.get("radius", 80.0)
						else:
							h_id = h.get("id")
							h_x = h.get("x")
							h_y = h.get("y")
							h_radius = h.get("radius")

						var interacted = []
						if typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("interacted_illusion_walls"):
							interacted = b.get_meta("interacted_illusion_walls")
						elif typeof(b) == TYPE_DICTIONARY and b.has("interacted_illusion_walls"):
							interacted = b.get("interacted_illusion_walls")

						if h_id in interacted:
							continue

						var b_x = 0.0
						var b_y = 0.0
						var b_vx = 0.0
						var b_vy = 0.0
						var b_type = "mimic_decoy"
						var b_team = "neutral"
						if typeof(b) == TYPE_DICTIONARY:
							b_x = b.get("x", 0.0)
							b_y = b.get("y", 0.0)
							b_vx = b.get("vx", 0.0)
							b_vy = b.get("vy", 0.0)
							b_type = b.get("ball_type", "mimic_decoy")
							b_team = b.get("team", "neutral")
						else:
							b_x = b.get("x")
							b_y = b.get("y")
							b_vx = b.get("vx")
							b_vy = b.get("vy")
							if "ball_type" in b: b_type = b.get("ball_type")
							if "team" in b: b_team = b.get("team")

						var dx = b_x - h_x
						var dy = b_y - h_y
						var dist = sqrt(dx*dx + dy*dy)

						var b_radius = 15.0
						if typeof(b) == TYPE_DICTIONARY:
							b_radius = b.get("radius", 15.0)
						else:
							if "radius" in b: b_radius = b.get("radius")

						if dist < h_radius + b_radius:
							if typeof(b) == TYPE_OBJECT and b.has_method("has_meta"):
								var inter_arr = []
								if b.has_meta("interacted_illusion_walls"):
									inter_arr = b.get_meta("interacted_illusion_walls")
								inter_arr.append(h_id)
								b.set_meta("interacted_illusion_walls", inter_arr)
							elif typeof(b) == TYPE_DICTIONARY:
								var inter_arr = []
								if b.has("interacted_illusion_walls"):
									inter_arr = b.get("interacted_illusion_walls")
								inter_arr.append(h_id)
								b["interacted_illusion_walls"] = inter_arr

							decoy_id_counter += 1

							var new_decoy = {}
							new_decoy["id"] = decoy_id_counter
							new_decoy["x"] = b_x
							new_decoy["y"] = b_y
							new_decoy["vx"] = -b_vx
							new_decoy["vy"] = -b_vy
							new_decoy["radius"] = b_radius
							new_decoy["hp"] = 1.0
							new_decoy["max_hp"] = 1.0
							new_decoy["alive"] = true
							new_decoy["ball_type"] = b_type
							new_decoy["team"] = b_team
							new_decoy["is_decoy"] = true
							new_decoy["lifespan"] = 5.0

							# Give dummy methods to avoid client crashes
							new_decoy["has_method"] = func(name): return false

							if "balls" in world:
								world.balls.append(new_decoy)
							if "entities" in world and world.balls != world.entities:
								world.entities.append(new_decoy)

		# Handle decoy lifecycle
		for b in balls.duplicate():
			if typeof(b) == TYPE_DICTIONARY and b.get("is_decoy", false) and b.has("lifespan"):
				b["lifespan"] -= delta
				if b["lifespan"] <= 0:
					b["alive"] = false
					continue
				b["x"] += b.get("vx", 0.0) * delta
				b["y"] += b.get("vy", 0.0) * delta

		# Reset interaction logic if ball moves far away
		if world != null and "arena" in world and world.arena != null and "hazards" in world.arena:
			for b in balls:
				var interacted = []
				if typeof(b) == TYPE_OBJECT and b.has_method("has_meta") and b.has_meta("interacted_illusion_walls"):
					interacted = b.get_meta("interacted_illusion_walls")
				elif typeof(b) == TYPE_DICTIONARY and b.has("interacted_illusion_walls"):
					interacted = b.get("interacted_illusion_walls")

				if interacted.size() > 0:
					var new_interacted = []
					for h_id in interacted:
						var h_found = null
						for hz in world.arena.hazards:
							var hz_id = -1
							if typeof(hz) == TYPE_DICTIONARY:
								hz_id = hz.get("id", -1)
							else:
								hz_id = hz.get("id")
							if hz_id == h_id:
								h_found = hz
								break

						if h_found != null:
							var h_x = 0.0
							var h_y = 0.0
							var h_radius = 80.0
							if typeof(h_found) == TYPE_DICTIONARY:
								h_x = h_found.get("x", 0.0)
								h_y = h_found.get("y", 0.0)
								h_radius = h_found.get("radius", 80.0)
							else:
								h_x = h_found.get("x")
								h_y = h_found.get("y")
								h_radius = h_found.get("radius")

							var b_x = 0.0
							var b_y = 0.0
							var b_radius = 15.0
							if typeof(b) == TYPE_DICTIONARY:
								b_x = b.get("x", 0.0)
								b_y = b.get("y", 0.0)
								b_radius = b.get("radius", 15.0)
							else:
								b_x = b.get("x")
								b_y = b.get("y")
								if "radius" in b: b_radius = b.get("radius")

							var dx = b_x - h_x
							var dy = b_y - h_y
							var dist = sqrt(dx*dx + dy*dy)

							if dist < h_radius + b_radius + 10.0:
								new_interacted.append(h_id)

						if typeof(b) == TYPE_OBJECT and b.has_method("has_meta"):
							b.set_meta("interacted_illusion_walls", new_interacted)
						elif typeof(b) == TYPE_DICTIONARY:
							b["interacted_illusion_walls"] = new_interacted


class UndergroundTunnelMode extends GameMode:
	var tunnels = []
	var tunnel_radius = 40.0
	var travel_speed = 300.0
	var tunnel_class = null

	class Tunnel:
		var x1: float
		var y1: float
		var x2: float
		var y2: float
		func _init(a, b, c, d):
			x1 = a
			y1 = b
			x2 = c
			y2 = d

	func _init():
		name = "Underground Tunnels"
		description = "Procedural arenas can spawn underground tunnels, allowing balls to temporarily travel underneath obstacles. While underground, balls are invisible and cannot be targeted, but can only emerge at specific tunnel exits."

	func setup(world, balls: Array) -> void:
		super.setup(world, balls)
		tunnels = []
		for i in range(3):
			var x1 = randf_range(200, 800)
			var y1 = randf_range(200, 800)
			var x2 = randf_range(200, 800)
			var y2 = randf_range(200, 800)
			tunnels.append(Tunnel.new(x1, y1, x2, y2))

		if typeof(world) == TYPE_OBJECT and "arena" in world and world.arena != null:
			if not "hazards" in world.arena:
				world.arena.hazards = []

			for i in range(tunnels.size()):
				var t = tunnels[i]
				# Entrance A
				world.arena.hazards.append({
					"id": "tunnel_" + str(i) + "_a",
					"x": t.x1, "y": t.y1,
					"radius": tunnel_radius,
					"kind": "tunnel_entrance"
				})
				# Entrance B
				world.arena.hazards.append({
					"id": "tunnel_" + str(i) + "_b",
					"x": t.x2, "y": t.y2,
					"radius": tunnel_radius,
					"kind": "tunnel_entrance"
				})

	func tick(world, balls: Array, delta: float = 0.016) -> void:
		super.tick(world, balls, delta)

		for b in balls:
			var b_alive = true
			if "alive" in b: b_alive = b.alive
			elif b.has_method("has_meta") and b.has_meta("alive"): b_alive = b.get_meta("alive")
			if not b_alive: continue

			var is_underground = false
			if "underground" in b: is_underground = b.underground
			elif b.has_method("has_meta") and b.has_meta("underground"): is_underground = b.get_meta("underground")

			if is_underground:
				var tx = b.x
				var ty = b.y
				if "tunnel_target_x" in b: tx = b.tunnel_target_x
				elif b.has_method("has_meta") and b.has_meta("tunnel_target_x"): tx = b.get_meta("tunnel_target_x")
				if "tunnel_target_y" in b: ty = b.tunnel_target_y
				elif b.has_method("has_meta") and b.has_meta("tunnel_target_y"): ty = b.get_meta("tunnel_target_y")

				var dx = tx - b.x
				var dy = ty - b.y
				var dist = sqrt(dx*dx + dy*dy)

				if dist <= travel_speed * delta:
					b.x = tx
					b.y = ty
					if "underground" in b: b.underground = false
					elif b.has_method("set_meta"): b.set_meta("underground", false)

					if "is_invisible" in b: b.is_invisible = false
					elif b.has_method("set_meta"): b.set_meta("is_invisible", false)

					if "tunnel_cooldown" in b: b.tunnel_cooldown = 1.0
					elif b.has_method("set_meta"): b.set_meta("tunnel_cooldown", 1.0)
				else:
					b.x += (dx / dist) * travel_speed * delta
					b.y += (dy / dist) * travel_speed * delta

				continue

			var cd = 0.0
			if "tunnel_cooldown" in b: cd = b.tunnel_cooldown
			elif b.has_method("has_meta") and b.has_meta("tunnel_cooldown"): cd = b.get_meta("tunnel_cooldown")

			if cd > 0:
				var new_cd = max(0.0, cd - delta)
				if "tunnel_cooldown" in b: b.tunnel_cooldown = new_cd
				elif b.has_method("set_meta"): b.set_meta("tunnel_cooldown", new_cd)
				continue

			for t in tunnels:
				var dist_a = sqrt(pow(b.x - t.x1, 2) + pow(b.y - t.y1, 2))
				if dist_a < tunnel_radius:
					if "underground" in b: b.underground = true
					elif b.has_method("set_meta"): b.set_meta("underground", true)

					if "is_invisible" in b: b.is_invisible = true
					elif b.has_method("set_meta"): b.set_meta("is_invisible", true)

					if "tunnel_target_x" in b: b.tunnel_target_x = t.x2
					elif b.has_method("set_meta"): b.set_meta("tunnel_target_x", t.x2)

					if "tunnel_target_y" in b: b.tunnel_target_y = t.y2
					elif b.has_method("set_meta"): b.set_meta("tunnel_target_y", t.y2)

					if "vx" in b: b.vx = 0.0
					elif b.has_method("set_meta"): b.set_meta("vx", 0.0)
					if "vy" in b: b.vy = 0.0
					elif b.has_method("set_meta"): b.set_meta("vy", 0.0)
					break

				var dist_b = sqrt(pow(b.x - t.x2, 2) + pow(b.y - t.y2, 2))
				if dist_b < tunnel_radius:
					if "underground" in b: b.underground = true
					elif b.has_method("set_meta"): b.set_meta("underground", true)

					if "is_invisible" in b: b.is_invisible = true
					elif b.has_method("set_meta"): b.set_meta("is_invisible", true)

					if "tunnel_target_x" in b: b.tunnel_target_x = t.x1
					elif b.has_method("set_meta"): b.set_meta("tunnel_target_x", t.x1)

					if "tunnel_target_y" in b: b.tunnel_target_y = t.y1
					elif b.has_method("set_meta"): b.set_meta("tunnel_target_y", t.y1)

					if "vx" in b: b.vx = 0.0
					elif b.has_method("set_meta"): b.set_meta("vx", 0.0)
					if "vy" in b: b.vy = 0.0
					elif b.has_method("set_meta"): b.set_meta("vy", 0.0)
					break
