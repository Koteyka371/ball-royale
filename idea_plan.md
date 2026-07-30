Plan:
1. Create `src/ai/decoy_swap_mode.py` and `src/ai/decoy_swap_mode.gd`.
2. Define a GameMode `DecoySwapMode` that:
   - Sets `self.name = "Decoy Swap Survival"` and a chaotic description.
   - Has a `swap_timer` and `swap_interval` (e.g. 10.0 seconds).
   - In `tick`, every 10 seconds:
     - For each alive non-decoy player:
       - Find the nearest active decoy they own. (Match `owner_id` or just find any decoy if not specifically owned? The prompt says "their nearest active decoy or clone". If no decoy has `owner_id`, we might need to assume decoys with same team or just fallback to ANY decoy, but typically decoys are spawned with `owner_id` or `team`. Let's just spawn a new decoy if none nearby, or swap with nearest decoy they own.)
       - Actually, let's just spawn a decoy for them if they have none. A decoy is created at their current location just before they swap.
       - Then they swap positions with the decoy. Wait, if a decoy is spawned at their location, and they swap with it, they end up at the exact same location!
       - The prompt says: "If they do not have a decoy active, one is spawned for them at their location moments before the swap."
       - BUT if it's spawned at their location and they swap with it, it's useless.
       - Re-reading: "every player on the map is instantly swapped in position with their nearest active decoy or clone. If they do not have a decoy active, one is spawned for them at their location moments before the swap."
       - Ah! If I don't have a decoy, I spawn one at my location. Since I swap with my nearest decoy, I just swap with the one I just spawned at my location, meaning I stay in place, but now I have a decoy left behind!
       - That perfectly fits the "spawned for them at their location moments before the swap" phrasing. If they DID have a decoy far away, they would swap to it. If they didn't, they spawn one at their current location and effectively "swap" to it, meaning they stay there and a decoy appears there.
       - Actually, if they spawn a decoy at their location and swap, they are at the exact same spot. Let's spawn it exactly at `b.x, b.y`.

3. Register in `game_modes.py` and `game_modes.gd`.
4. Add a test in `src/tests/test_decoy_swap.py`.
