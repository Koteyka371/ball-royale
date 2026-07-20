Actually, what if we let the `world._collect_booster` run normally, and then inside `action.py` right AFTER it runs, if `Cursed Boosters` is active, we just apply generic debuffs?
Wait! The task asks for a GAME MODE where all boosters collected have the opposite of their intended effect.
If we can't patch Godot from Python, and we can't edit `world.gd`, maybe `world.gd` DOES NOT handle all logic? Maybe `_collect_booster` is implemented somewhere we CAN access? Let's check `tests/test_homing_missile_booster.py` which had `def _collect_booster`. That was just a mock. Where is the REAL `_collect_booster`?
Wait! `action.gd` checks `if self.world != null and self.world.has_method("_collect_booster"): self.world._collect_booster(self.ball, nearest)`
It means `world` must implement it. Since we can't edit `world.gd` because it's not in `src/`, we MUST put the reverse logic in `action.py` and `action.gd` or the game mode.

Let's look at how we can reverse effects. In `action.py`, before `world._collect_booster`, we can record state:
```python
is_cursed = hasattr(self.world, "mode") and getattr(self.world.mode, "name", "") == "Cursed Boosters"
pre_stats = {}
if is_cursed:
    pre_stats = {
        "hp": getattr(self.ball, "hp", 100.0),
        "speed": getattr(self.ball, "speed", 100.0),
        "damage": getattr(self.ball, "damage", 10.0),
        "stamina": getattr(self.ball, "stamina", 100.0)
    }

if hasattr(self.world, "_collect_booster"):
    self.world._collect_booster(self.ball, nearest)

if is_cursed:
    # Reverse HP changes
    post_hp = getattr(self.ball, "hp", 100.0)
    if post_hp > pre_stats["hp"]:
        self.ball.hp = pre_stats["hp"] - (post_hp - pre_stats["hp"])

    # Reverse Speed changes
    post_speed = getattr(self.ball, "speed", 100.0)
    if post_speed > pre_stats["speed"]:
        self.ball.speed = pre_stats["speed"] - (post_speed - pre_stats["speed"])
        self.ball.slow_timer = 5.0 # also apply a slow timer so the speed decrease lasts

    # Reverse damage changes
    post_damage = getattr(self.ball, "damage", 10.0)
    if post_damage > pre_stats["damage"]:
        self.ball.damage = pre_stats["damage"] - (post_damage - pre_stats["damage"])

    # Reverse stamina changes
    post_stamina = getattr(self.ball, "stamina", 100.0)
    if post_stamina > pre_stats["stamina"]:
        self.ball.stamina = pre_stats["stamina"] - (post_stamina - pre_stats["stamina"])
```
This is a very clean and general way to "reverse" the effects! And it scales to ANY booster that increases these stats.

For GDScript:
```gdscript
var is_cursed = false
if self.world != null and "mode" in self.world and typeof(self.world.mode) == TYPE_OBJECT and "name" in self.world.mode and self.world.mode.name == "Cursed Boosters":
    is_cursed = true
elif self.world != null and "mode" in self.world and typeof(self.world.mode) == TYPE_DICTIONARY and self.world.mode.has("name") and self.world.mode["name"] == "Cursed Boosters":
    is_cursed = true

var pre_stats = {}
if is_cursed:
    pre_stats["hp"] = _get_prop(self.ball, "hp", 100.0)
    pre_stats["speed"] = _get_prop(self.ball, "speed", 100.0)
    pre_stats["damage"] = _get_prop(self.ball, "damage", 10.0)
    pre_stats["stamina"] = _get_prop(self.ball, "stamina", 100.0)

if self.world != null and self.world.has_method("_collect_booster"):
    self.world._collect_booster(self.ball, nearest)

if is_cursed:
    var post_hp = _get_prop(self.ball, "hp", 100.0)
    if post_hp > pre_stats["hp"]:
        _set_prop(self.ball, "hp", pre_stats["hp"] - (post_hp - pre_stats["hp"]))

    var post_speed = _get_prop(self.ball, "speed", 100.0)
    if post_speed > pre_stats["speed"]:
        _set_prop(self.ball, "speed", pre_stats["speed"] - (post_speed - pre_stats["speed"]))
        _set_prop(self.ball, "slow_timer", 5.0)

    var post_damage = _get_prop(self.ball, "damage", 10.0)
    if post_damage > pre_stats["damage"]:
        _set_prop(self.ball, "damage", pre_stats["damage"] - (post_damage - pre_stats["damage"]))

    var post_stamina = _get_prop(self.ball, "stamina", 100.0)
    if post_stamina > pre_stats["stamina"]:
        _set_prop(self.ball, "stamina", pre_stats["stamina"] - (post_stamina - pre_stats["stamina"]))
```
Wait, we need to handle dictionaries and objects properly in GDScript, but `_get_prop` and `_set_prop` handles that! Wait, `_get_prop` might not be in scope in `action.gd`. Let's check if `_get_prop` exists in `action.gd`.
