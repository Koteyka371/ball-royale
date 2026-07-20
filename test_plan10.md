Ah, memory says "In the GDScript implementation (`action.gd`), use the built-in helper functions `_get_prop(entity, "property_name", default_value)`". But grep shows it only in `game_modes.gd`. Wait, what if we define those helper functions inline inside `action.gd`'s `_collect_booster` function?

```gdscript
var is_cursed = false
if self.world != null and "mode" in self.world:
    if typeof(self.world.mode) == TYPE_OBJECT and "name" in self.world.mode and self.world.mode.name == "Cursed Boosters":
        is_cursed = true
    elif typeof(self.world.mode) == TYPE_DICTIONARY and self.world.mode.has("name") and self.world.mode["name"] == "Cursed Boosters":
        is_cursed = true

var pre_hp = 100.0
var pre_speed = 100.0
var pre_damage = 10.0
var pre_stamina = 100.0

if is_cursed:
    if typeof(self.ball) == TYPE_OBJECT:
        if "hp" in self.ball: pre_hp = self.ball.hp
        if "speed" in self.ball: pre_speed = self.ball.speed
        if "damage" in self.ball: pre_damage = self.ball.damage
        if "stamina" in self.ball: pre_stamina = self.ball.stamina
    elif typeof(self.ball) == TYPE_DICTIONARY:
        if self.ball.has("hp"): pre_hp = self.ball["hp"]
        if self.ball.has("speed"): pre_speed = self.ball["speed"]
        if self.ball.has("damage"): pre_damage = self.ball["damage"]
        if self.ball.has("stamina"): pre_stamina = self.ball["stamina"]
```

Then we call `self.world._collect_booster(self.ball, nearest)`

Then we do:
```gdscript
if is_cursed:
    var post_hp = 100.0
    var post_speed = 100.0
    var post_damage = 10.0
    var post_stamina = 100.0
    if typeof(self.ball) == TYPE_OBJECT:
        if "hp" in self.ball: post_hp = self.ball.hp
        if "speed" in self.ball: post_speed = self.ball.speed
        if "damage" in self.ball: post_damage = self.ball.damage
        if "stamina" in self.ball: post_stamina = self.ball.stamina
    elif typeof(self.ball) == TYPE_DICTIONARY:
        if self.ball.has("hp"): post_hp = self.ball["hp"]
        if self.ball.has("speed"): post_speed = self.ball["speed"]
        if self.ball.has("damage"): post_damage = self.ball["damage"]
        if self.ball.has("stamina"): post_stamina = self.ball["stamina"]

    if post_hp > pre_hp:
        var diff = post_hp - pre_hp
        if typeof(self.ball) == TYPE_OBJECT: self.ball.hp = pre_hp - diff
        else: self.ball["hp"] = pre_hp - diff

    if post_speed > pre_speed:
        var diff = post_speed - pre_speed
        if typeof(self.ball) == TYPE_OBJECT:
            self.ball.speed = pre_speed - diff
            if "slow_timer" in self.ball: self.ball.slow_timer = 5.0
            else: self.ball.set_meta("slow_timer", 5.0)
        else:
            self.ball["speed"] = pre_speed - diff
            self.ball["slow_timer"] = 5.0

    if post_damage > pre_damage:
        var diff = post_damage - pre_damage
        if typeof(self.ball) == TYPE_OBJECT: self.ball.damage = pre_damage - diff
        else: self.ball["damage"] = pre_damage - diff

    if post_stamina > pre_stamina:
        var diff = post_stamina - pre_stamina
        if typeof(self.ball) == TYPE_OBJECT: self.ball.stamina = pre_stamina - diff
        else: self.ball["stamina"] = pre_stamina - diff
```

This logic accurately reverses the stat buffs from the booster.
We'll do the same in `action.py`.
And we'll create `CursedBoosterMode` in `game_modes.py` and `game_modes.gd`.
