1. **Modify `simulate_battle.py`**:
   - Add an optional `use_neural_network` or `eval_neural` boolean flag to the command-line arguments and `BattleSimulation.__init__`.
   - Update `__main__` so that it supports `--eval-neural` flag. When the flag is used, it should run 500 battles to evaluate learning efficiency (standard BallBrain vs NeuralNetworkBrain). Or maybe just add a mode to evaluate it. Wait, the task says: "Run the NeuralNetworkBrain (Phase 2) alongside the standard BallBrain in simulate_battle.py to evaluate learning efficiency over 500 battles."
   - Let's create an evaluation mode in `simulate_battle.py` by adding a `--eval-neural` flag. When given, it will run 500 battles, where in each battle, half the balls use `NeuralNetworkBrain` and half use `BallBrain`.
   - In `_spawn_balls`, or rather right after creating the brains, check if `eval_neural` is enabled. If it is, for half of the balls (maybe even ID/index based), assign `NeuralNetworkBrain` instead of `BallBrain`.
   - After the 500 battles, print a summary comparing the stats (e.g. win rate, total kills, avg duration) of Neural vs Standard brains.

Let's check the wording again: "Run the NeuralNetworkBrain (Phase 2) alongside the standard BallBrain in simulate_battle.py to evaluate learning efficiency over 500 battles."

I'll add:
- A new argument `--eval-neural`
- When `--eval-neural` is set, `__main__` loops 500 times. In each loop, it creates a `BattleSimulation(use_neural=True)`.
- Inside `BattleSimulation`, if `use_neural` is true:
  - Assign `NeuralNetworkBrain` to 50% of the balls.
  - Tag the `ball.brain_type = "neural"` vs `"standard"` so we can track stats.
- Aggregate stats over the 500 battles:
  - Total standard wins vs neural wins.
  - Total standard kills vs neural kills.
  - Total standard survivals vs neural survivals.
- Output a clear summary report.

Let me test if this is a good plan.
