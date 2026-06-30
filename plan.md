1. Verify the functionality using Python test framework. We already ran `pytest`, and all tests passed.
2. Ensure we met the requirements: A new hazard type that links two balls together. If one takes damage or gets a status effect, the other receives a fraction of it. It requires coordination to break the link by moving far enough apart or finding a cleanser item.
    - We added `damage_link` hazard logic in `src/ai/action.py` and `src/ai/action.gd` that sets `damage_link_target` when a ball touches the hazard.
    - If a ball takes damage, stuns, or silences, half of it is dealt to the linked target.
    - Link is broken if they are > 300 distance apart (`90000.0` squared distance).
    - Link is broken if one of them picks up a `cleanser` item.
3. Write 2 ideas in the `ideas/` folder.
4. Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
5. Submit the changes.
