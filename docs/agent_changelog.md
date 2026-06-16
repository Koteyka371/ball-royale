# Ball Royale — Agent Changelog

Tracked history of successful tasks completed by autonomous agents.

## [ai-personality-system] Implement Personality system — *2026-06-16 15:41:18 UTC*

Create Personality class that defines ball's character: aggressive, cautious, supportive, reckless, cunning. Each ball type has default personality. Personality influences decision weights.

---

## [balance-buff-healer] Balance: Buff underpowered 'healer' — *2026-06-16 15:35:37 UTC*

The 'healer' class is winning only 0.0% of the time (expected ~8.3%). It is severely underpowered. Please increase its survivability, damage, speed, or decrease skill cooldown.

---

## [ai-action-system] Implement Action execution system — *2026-06-16 15:27:31 UTC*

Create Action class that executes chosen behavior: move to target, attack, use skill, flee, collect booster. Handles pathfinding, timing, and cooldowns.

---

## [ai-behavior-chase] Implement Chase behavior — *2026-06-16 15:27:27 UTC*

Ball moves towards nearest enemy. Uses pathfinding to avoid obstacles. Stops when in attack range. Can be modified by fear (runs away) or greed (chases booster instead).

---

## [ai-team-coordination] Implement Team coordination AI — *2026-06-16 12:47:06 UTC*

Balls in same team share information: call out targets, request help, coordinate attacks. Tank signals to hold position, Healer calls for wounded, Sniper calls out threats.

---

## [ai-behavior-flee] Implement Flee behavior — *2026-06-16 12:46:57 UTC*

Ball moves away from nearest threat. Prioritizes moving towards allies or safe zones. Speed boost when fleeing. Can stop when safe.

---

## [ai-difficulty-system] Implement AI difficulty levels — *2026-06-16 12:46:18 UTC*

Create difficulty system: Easy (slow reactions, simple decisions), Medium (normal), Hard (fast, optimal), Chaos (random, funny). Affects reaction time, decision quality, skill usage.

---

