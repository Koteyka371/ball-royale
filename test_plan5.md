There's an `invert_booster` or `debuff_booster` in `booster_kinds`?
Wait, there's `debuff_booster`, `cursed_booster`!
If the game mode simply renames all boosters that spawn to `debuff_booster` or `cursed_booster`?
Wait, the prompt says: "A game mode where all boosters collected have the opposite of their intended effect, forcing players to avoid items they usually collect."
If we just change their kinds to `debuff_booster`, they might look like debuff boosters instead of their original intended types. The prompt implies players see the item they *usually* collect, but it has the opposite effect! So they have to "avoid items they usually collect".
If we just transform `health_pack` to `damage_pack`, how does it work?

Let's see if we can intercept the collection itself. In `game_modes.py`, we can intercept booster collection if we do it in the Godot engine... wait, we only have access to Python files and GDScript files under `src/ai`.
Wait, we CAN modify `action.py` and `action.gd`! In `action.py`, inside `_collect_booster`, right before `self.world._collect_booster(self.ball, nearest)`, we can check if `getattr(self.world, "mode", None)` is our new mode, and if so, instead of calling `self.world._collect_booster()`, we can apply the inverse effect and remove the booster!
Wait, is `_collect_booster` in Godot accessible? No, but wait, `action.gd` also calls `self.world._collect_booster(self.ball, nearest)`.

Is there a way to do it inside `GameMode.tick()` without touching `action.py`/`action.gd`?
What if `CursedBoosterMode` wraps the `world._collect_booster` function?
```python
class CursedBoosterMode(GameMode):
    def setup(self, world, balls):
        super().setup(world, balls)
        self.original_collect = getattr(world, "_collect_booster", None)
        if self.original_collect:
            def cursed_collect(ball, booster):
                self.apply_inverse_effect(world, ball, booster)
            world._collect_booster = cursed_collect
```
But wait, `world` in Godot is a C++ or GDScript object! In `game_modes.gd`, we can't easily redefine a method of `world`.
Wait, can we just set a flag `world.cursed_boosters = True` and then modify `_collect_booster` inside Godot's `world.gd`? But we CANNOT modify files outside `src/`! `world.gd` is likely outside `src/`.
Let's see if we can apply the inverse effect within `action.py` and `action.gd`. Yes, we can modify `action.py` and `action.gd` because they are in `src/ai/`.
