TASK: A game mode where all boosters collected have the opposite of their intended effect, forcing players to avoid items they usually collect.

Plan:
1. Create a new `GameMode` subclass `CursedBoosterMode` in `src/ai/game_modes.py`.
   - Name: "Cursed Boosters"
   - Description: "All boosters collected have the opposite of their intended effect, forcing players to avoid items they usually collect."
   - In `tick()`, intercept booster collection effects before normal processing or apply a global mutator that reverses stats when a booster is collected. We need to look at how boosters are processed (or maybe the opposite effect is applied on the world level if the mode modifies `apply_dynamic_traits` or alters booster contents). Wait, boosters are collected in `action.py` `_collect_booster`, or `action.gd`. `action.py` usually calls `_collect_booster` where it applies stats. However, modifying `action.py` and `action.gd` for all booster types would be massive.
   Is there a central place where booster effects are defined? Let's check `_collect_booster` logic again.
