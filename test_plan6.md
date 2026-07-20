Wait, `world._collect_booster` doesn't just do one thing, it handles ALL boosters! If I skip calling `world._collect_booster`, I have to manually implement the inverse effect for *every single booster type*!
Is there an easier way?
What if the game mode just intercepts the booster's properties when they spawn, or dynamically modifies the ball's stats after collection?
Wait, the `world._collect_booster` function in Godot applies the booster. What if my game mode observes the ball's stats before and after calling it, and reverses the difference?
In `action.py`:
```python
if hasattr(self.world, "_collect_booster"):
    is_cursed = hasattr(self.world, "mode") and getattr(self.world.mode, "id", "") == "cursed_boosters"
    if is_cursed:
        pre_hp = getattr(self.ball, "hp", 100)
        pre_speed = getattr(self.ball, "speed", 100)
        pre_damage = getattr(self.ball, "damage", 10)
        # ...

    self.world._collect_booster(self.ball, nearest)

    if is_cursed:
        post_hp = getattr(self.ball, "hp", 100)
        # reverse the diff!
```
Is this robust enough? Timers for buffs (like `speed_booster_timer`) would be increased, so we'd have to unset them and set debuff timers instead? That's messy.

Another option: rename the booster `kind` to something that natively applies debuffs?
If a booster spawns as `hp_booster`, we keep it looking like `hp_booster`. But its `kind` dictates its appearance *and* effect in the engine. Can we decouple appearance from `kind`?
Wait, if a GameMode changes the effect...
Let's see if there's a mutator or flag in Godot that already does this.
