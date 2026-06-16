# Ball Royale — Agent Changelog

Tracked history of successful tasks completed by autonomous agents.

## [ai-behavior-collect-booster] Implement Collect Booster behavior — *2026-06-16 22:24:14 UTC*

Ball moves towards nearest booster. Ignores enemies when collecting (greed). Can be interrupted if enemy gets too close.

---

## [ai-ball-scout-ai] Implement Scout AI profile — *2026-06-16 19:35:48 UTC*

Scout AI: curious personality, seeks boosters, attacks weak enemies, flees from strong ones, uses Dash to escape or chase.

---

## [ai-swarm-boids] Create Swarm intelligence boid rules — *2026-06-16 19:31:28 UTC*

Implement boid rules (separation, alignment, cohesion) for the swarm ball type. This will make swarm balls group together and move dynamically like a flock of birds.

---

## [balance-buff-rogue] Balance: Buff underpowered 'rogue' — *2026-06-16 19:26:33 UTC*

The 'rogue' class is winning only 0.0% of the time (expected ~8.3%). It is severely underpowered. Please increase its survivability, damage, speed, or decrease skill cooldown.

---

## [ai-behavior-group-attack] Implement Group Attack behavior — *2026-06-16 19:24:36 UTC*

Multiple balls coordinate to attack same target. Balls signal intent and converge. Tank takes aggro, damage dealers attack, healer supports.

---

## [balance-buff-swarm] Balance: Buff underpowered 'swarm' — *2026-06-16 19:22:55 UTC*

The 'swarm' class is winning only 0.0% of the time (expected ~8.3%). It is severely underpowered. Please increase its survivability, damage, speed, or decrease skill cooldown.

---

## [ai-behavior-attack] Implement Attack behavior — *2026-06-16 16:24:22 UTC*

Ball attacks when in range. Timing varies by ball type (fast for Scout, slow for Tank). Can chain attacks. Uses skill when available and optimal.

---

## [auto-implement-decision-skill] Implement DECISION skill — *2026-06-16 16:07:30 UTC*

Create DECISION skill: Решение

---

## [balance-buff-assassin] Balance: Buff underpowered 'assassin' — *2026-06-16 16:04:21 UTC*

The 'assassin' class is winning only 0.0% of the time (expected ~8.3%). It is severely underpowered. Please increase its survivability, damage, speed, or decrease skill cooldown.

---

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

