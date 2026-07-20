If the Godot layer implements `world._collect_booster`, then changing boosters' effects requires modifying that, which we can't do if it's in the root or outside `src`.
Wait, IS there a file outside `src`? We shouldn't modify files outside `src`.
If we can't modify `world.gd` (or wherever it is), we CAN intercept the `_collect_booster` call inside `src/ai/action.py` and `src/ai/action.gd`.

But implementing inverse effects for ALL boosters inside `action.py`/`action.gd` right before skipping the `world._collect_booster()` call is tedious.
However, look at how `ItemMorphMode` works. It literally changes the `kind` of boosters!
```python
        self.booster_kinds = ["tracker_booster", "tornado_booster", "cursed_relic", "vampiric_aura_booster", ... ]
```
Is there a booster kind that applies debuffs? We saw `cursed_booster` and `debuff_booster`.
If we just convert any collected booster into a debuff right before it's collected?
Wait, if `CursedBoosterMode` is active, what if in `GameMode.tick()` we iterate over `balls` and dynamically track their `hp` and `speed`? No, because if they pick up an `hp_booster`, they get +HP.

Wait, is there a way to monkey patch `world._collect_booster` dynamically from `GameMode.tick()`?
```python
class CursedBoosterMode(GameMode):
    def __init__(self):
        super().__init__()
        self.name = "Cursed Boosters"
        self.description = "All boosters collected have the opposite of their intended effect, forcing players to avoid items they usually collect."
        self.patched = False

    def tick(self, world, balls, delta=0.016):
        super().tick(world, balls, delta)
        # In Python simulations, we can patch world._collect_booster
        if not self.patched and hasattr(world, "_collect_booster"):
            self.orig_collect = world._collect_booster
            def cursed_collect(ball, booster):
                # How do we inverse it?
                pre_hp = getattr(ball, "hp", 100)
                pre_speed = getattr(ball, "speed", 100)

                self.orig_collect(ball, booster)

                # Inverse
                diff_hp = getattr(ball, "hp", 100) - pre_hp
                if diff_hp > 0:
                    ball.hp = pre_hp - diff_hp

                diff_speed = getattr(ball, "speed", 100) - pre_speed
                if diff_speed > 0:
                    ball.speed = pre_speed - diff_speed

            world._collect_booster = cursed_collect
            self.patched = True
```
But this ONLY works in Python! It wouldn't work in Godot because Godot executes GDScript and does not call the Python `GameMode.tick()` to patch Godot objects! Godot calls GDScript `GameMode.tick()`.
Wait, if it's GDScript, we need to modify `game_modes.gd` as well.
In `game_modes.gd`, there is a dictionary of game modes.

What if we modify `action.py` and `action.gd`'s `_collect_booster`?
In `action.py`:
```python
        if dist <= ball_radius + 10:
            # We are about to collect `nearest`
            is_cursed_mode = hasattr(self.world, "mode") and getattr(self.world.mode, "name", "") == "Cursed Boosters"
            if is_cursed_mode:
                # We can't easily inverse. What if we just swap the booster's `kind` before collection?
                kind = getattr(nearest, "kind", "")
                if "speed" in kind:
                    nearest.kind = "slow_booster" # does this exist?
```

Wait, what if we define a method `apply_cursed_booster(ball, booster)` and call that INSTEAD of `self.world._collect_booster` if the mode is "Cursed Boosters"?
Or, we just deal damage to the ball and apply slow, regardless of the booster type, to simulate "opposite effect" generically?
"All boosters collected have the opposite of their intended effect..."
If it's an HP booster, it damages you. If it's a speed booster, it slows you down. If it's a shield booster, it breaks your shield.
There are a LOT of boosters!
