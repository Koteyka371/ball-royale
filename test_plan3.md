Wait, if `self.world._collect_booster(self.ball, nearest)` is called, where is `_collect_booster` defined on `world`? Is it in `system/`? Let's check `src/system/world.py` or similar. Oh, I don't see `src/ai/world.py`. I can look for `class World` or `def _collect_booster`.
Wait, in `src/ai/action.py`, it uses `hasattr(self.world, "_collect_booster")`. So it's dynamic. Let's find `class World` or check the main simulation loop.
The task says: "A game mode where all boosters collected have the opposite of their intended effect...".
If I create a new game mode, how does the game apply booster effects? Usually, it's defined in the game modes themselves? No, `_collect_booster` might be defined in the main Godot code (`world.gd`?), and the Python side is for AI and some headless simulations?
Let's search for `_collect_booster` in `src/` again, including `.gd` files.
