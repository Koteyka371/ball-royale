import re

with open("src/ai/action.gd", "r") as f:
    content = f.read()

reflection_logic_gd = """func execute(strategy: String, delta: float):
\tif typeof(ball) == TYPE_OBJECT and "ball_type" in ball and ball.ball_type == "mirror" or (typeof(ball) == TYPE_DICTIONARY and ball.has("ball_type") and ball["ball_type"] == "mirror"):
\t\tvar negative_statuses = ["emp_timer", "poison_timer", "slow_timer", "burn_timer", "confusion_timer", "blindness_timer", "frozen_timer", "stun_timer", "silence_timer"]
\t\tvar has_status = false
\t\tfor stat in negative_statuses:
\t\t\tvar val = 0.0
\t\t\tif typeof(ball) == TYPE_OBJECT and stat in ball: val = ball[stat]
\t\t\telif typeof(ball) == TYPE_DICTIONARY and ball.has(stat): val = ball[stat]
\t\t\tif val > 0:
\t\t\t\thas_status = true
\t\t\t\tbreak
\t\tif has_status:
\t\t\tvar nearest_enemy = null
\t\t\tvar min_dist = 9999999.0
\t\t\tvar balls = []
\t\t\tif typeof(world) == TYPE_OBJECT and "balls" in world: balls = world.balls
\t\t\telif typeof(world) == TYPE_DICTIONARY and world.has("balls"): balls = world["balls"]
\t\t\tfor b in balls:
\t\t\t\tvar b_alive = true
\t\t\t\tvar b_id = -1
\t\t\t\tvar b_team = ""
\t\t\t\tvar self_id = -1
\t\t\t\tvar self_team = "mirror"
\t\t\t\tif typeof(b) == TYPE_OBJECT:
\t\t\t\t\tif "alive" in b: b_alive = b.alive
\t\t\t\t\tif "id" in b: b_id = b.id
\t\t\t\t\tif "team" in b: b_team = b.team
\t\t\t\t\telif "ball_type" in b: b_team = b.ball_type
\t\t\t\telif typeof(b) == TYPE_DICTIONARY:
\t\t\t\t\tb_alive = b.get("alive", true)
\t\t\t\t\tb_id = b.get("id", -1)
\t\t\t\t\tb_team = b.get("team", b.get("ball_type", ""))
\t\t\t\tif typeof(ball) == TYPE_OBJECT:
\t\t\t\t\tif "id" in ball: self_id = ball.id
\t\t\t\t\tif "team" in ball: self_team = ball.team
\t\t\t\telif typeof(ball) == TYPE_DICTIONARY:
\t\t\t\t\tself_id = ball.get("id", -1)
\t\t\t\t\tself_team = ball.get("team", "mirror")
\t\t\t\tif b_alive and b_id != self_id and b_team != self_team:
\t\t\t\t\tvar bx = 0.0
\t\t\t\t\tvar by = 0.0
\t\t\t\t\tvar sx = 0.0
\t\t\t\t\tvar sy = 0.0
\t\t\t\t\tif typeof(b) == TYPE_OBJECT:
\t\t\t\t\t\tbx = b.x
\t\t\t\t\t\tby = b.y
\t\t\t\t\telif typeof(b) == TYPE_DICTIONARY:
\t\t\t\t\t\tbx = b.get("x", 0.0)
\t\t\t\t\t\tby = b.get("y", 0.0)
\t\t\t\t\tif typeof(ball) == TYPE_OBJECT:
\t\t\t\t\t\tsx = ball.x
\t\t\t\t\t\tsy = ball.y
\t\t\t\t\telif typeof(ball) == TYPE_DICTIONARY:
\t\t\t\t\t\tsx = ball.get("x", 0.0)
\t\t\t\t\t\tsy = ball.get("y", 0.0)
\t\t\t\t\tvar dist = (bx - sx)*(bx - sx) + (by - sy)*(by - sy)
\t\t\t\t\tif dist < min_dist:
\t\t\t\t\t\tmin_dist = dist
\t\t\t\t\t\tnearest_enemy = b
\t\t\tif nearest_enemy != null:
\t\t\t\tfor stat in negative_statuses:
\t\t\t\t\tvar val = 0.0
\t\t\t\t\tif typeof(ball) == TYPE_OBJECT and stat in ball: val = ball[stat]
\t\t\t\t\telif typeof(ball) == TYPE_DICTIONARY and ball.has(stat): val = ball[stat]
\t\t\t\t\tif val > 0:
\t\t\t\t\t\tvar enemy_val = 0.0
\t\t\t\t\t\tif typeof(nearest_enemy) == TYPE_OBJECT and stat in nearest_enemy: enemy_val = nearest_enemy[stat]
\t\t\t\t\t\telif typeof(nearest_enemy) == TYPE_DICTIONARY and nearest_enemy.has(stat): enemy_val = nearest_enemy[stat]
\t\t\t\t\t\tif typeof(nearest_enemy) == TYPE_OBJECT: nearest_enemy[stat] = max(enemy_val, val)
\t\t\t\t\t\telif typeof(nearest_enemy) == TYPE_DICTIONARY: nearest_enemy[stat] = max(enemy_val, val)
\t\t\t\t\t\tif typeof(ball) == TYPE_OBJECT: ball[stat] = 0.0
\t\t\t\t\t\telif typeof(ball) == TYPE_DICTIONARY: ball[stat] = 0.0
\t\t\t\tvar is_emped = false
\t\t\t\tvar is_stunned = false
\t\t\t\tif typeof(ball) == TYPE_OBJECT:
\t\t\t\t\tif "is_emped" in ball: is_emped = ball.is_emped
\t\t\t\t\tif "is_stunned" in ball: is_stunned = ball.is_stunned
\t\t\t\telif typeof(ball) == TYPE_DICTIONARY:
\t\t\t\t\tis_emped = ball.get("is_emped", false)
\t\t\t\t\tis_stunned = ball.get("is_stunned", false)
\t\t\t\tif is_emped:
\t\t\t\t\tif typeof(nearest_enemy) == TYPE_OBJECT: nearest_enemy.is_emped = true
\t\t\t\t\telif typeof(nearest_enemy) == TYPE_DICTIONARY: nearest_enemy["is_emped"] = true
\t\t\t\t\tif typeof(ball) == TYPE_OBJECT: ball.is_emped = false
\t\t\t\t\telif typeof(ball) == TYPE_DICTIONARY: ball["is_emped"] = false
\t\t\t\tif is_stunned:
\t\t\t\t\tif typeof(nearest_enemy) == TYPE_OBJECT: nearest_enemy.is_stunned = true
\t\t\t\t\telif typeof(nearest_enemy) == TYPE_DICTIONARY: nearest_enemy["is_stunned"] = true
\t\t\t\t\tif typeof(ball) == TYPE_OBJECT: ball.is_stunned = false
\t\t\t\t\telif typeof(ball) == TYPE_DICTIONARY: ball["is_stunned"] = false"""

content = content.replace(
    'func execute(strategy: String, delta: float):',
    reflection_logic_gd
)

with open("src/ai/action.gd", "w") as f:
    f.write(content)
