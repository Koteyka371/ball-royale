1. **Understand Task**: Create zones with different modifiers (e.g. speed boost, damage boost, healing) that balls can fight over.
2. **Implementation Strategy**:
    - We will create a new game mode `ZoneControlMode` or similar in `src/ai/game_modes.py` and `src/ai/game_modes.gd`.
    - However, looking at the existing modes, there is already `DominationMode`, `KingOfTheHillMode`, `MovingZoneMode`. Let's create a new mode `ModifierZonesMode` that explicitly matches the description "zones with different modifiers (e.g. speed boost, damage boost, healing) that balls can fight over."
    - In this new mode:
        - Setup: define several zones with different types (speed, damage, heal).
        - Tick: for balls inside a zone, apply the specific buff (modify speed, damage, or add hp over time).
    - We will also need to reset modifiers when a ball leaves a zone (similar to weather resetting them to `base_speed` or `base_damage`).
    - Let's create this mode in both python and gdscript.
    - We will register it in the `GAME_MODES` dict.
    - We will add a test file `test_modifier_zones.py`.
    - We will verify our changes.
