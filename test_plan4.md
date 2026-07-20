It seems that booster effects are processed on the C++/Godot side when `_collect_booster` is called, but we don't have access to the main `world.gd` file here in `src/`.
Wait, looking at `action.py`, it literally says `self.world._collect_booster(self.ball, nearest)`! Where is `world._collect_booster` defined?
Maybe it is injected from Godot, and the Python mock testing is just for the AI logic.
If we want a GameMode that reverses boosters... how can a GameMode in Python intercept it?
Wait, boosters are stored in `world.boosters`. If a GameMode changes the `kind` of all boosters to reversed versions? E.g., `speed_booster` becomes `slow_booster`. But then we'd have to implement 20+ new booster types.

Another approach: What if the `CursedBoosterMode` intercepts when a ball's stats have changed? Or what if it sets a flag on the `world` (like `world.cursed_boosters = True`) and we modify `action.py` and `action.gd` to reverse the effects of standard boosters if that flag is set?
No, the Godot side's `world._collect_booster` actually applies the effect, not `action.py`. Wait, in `action.py` `_collect_booster`, there's a huge block checking `getattr(nearest, "kind", None) == "anvil_piece"` etc... is that where booster effects are?
Let's see: `sed -n '12180,12230p' src/ai/action.py`. It explicitly delegates to `self.world._collect_booster(self.ball, nearest)`.

Wait, in `game_modes.py`, there is a `GameMode` `tick(self, world, balls, delta)` method.
We could intercept `world._collect_booster`?
Wait! In Python, we can dynamically monkey-patch or wrap `world._collect_booster` when the mode is active!
