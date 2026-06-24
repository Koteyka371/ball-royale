# Ball Royale — Agent Changelog

Tracked history of successful tasks completed by autonomous agents.

## [idea-128] Black Hole Arena — *2026-06-24 23:22:19 UTC*

An arena featuring a massive, slow-moving black hole in the center that gradually pulls all balls and boosters towards it. The gravitational pull gets stronger closer to the center, forcing balls to use their movement skills creatively to avoid being crushed while trying to push enemies in.

---

## [idea-127] Zombie Infection Mode — *2026-06-24 21:21:54 UTC*

A mode where one powerful 'Zombie' ball starts against a large number of regular balls. When a regular ball is killed by a Zombie, it resurrects as a Zombie. The regular balls win if they survive until the timer runs out, while the Zombies win if they infect everyone.

---

## [idea-126] Threat Heatmap Pathfinding — *2026-06-24 19:32:03 UTC*

Enhance A* navigation by overlaying a dynamic threat heatmap based on enemy DPS and attack ranges. Instead of finding the shortest path, A* will minimize a 'danger cost' function. Technical implementation involves creating a new helper method `_find_path` or modifying obstacle avoidance in `src/ai/action.py` to evaluate nodes using a new `danger_coefficient` grid maintained by the Arena state.

---

## [auto-implement-**neural-ball**-—-a-ball-controlled-by-a] Implement **Neural Ball** — A ball controlled by a simple neural network skill — *2026-06-24 17:38:31 UTC*

Create **Neural Ball** — A ball controlled by a simple neural network skill: numpy, no external libs

---

## [auto-implement-**kite**-—-держит-дистанцию,-атакует-при] Implement **Kite** — держит дистанцию, атакует при приближении skill — *2026-06-24 15:39:09 UTC*

Create **Kite** — держит дистанцию, атакует при приближении skill: для Sniper

---

## [idea-arena-119] Create Neural Ball arena — *2026-06-22 19:06:19 UTC*

Implement Create Neural Ball arena as described in game_design.md

---

## [idea-arena-099] Create Flee arena — *2026-06-22 15:00:05 UTC*

Implement Create Flee arena as described in game_design.md

---

## [idea-arena-118] Create Ball Genetics arena — *2026-06-22 09:00:38 UTC*

Implement Create Ball Genetics arena as described in game_design.md

---

## [idea-arena-094] Create Target Strong arena — *2026-06-22 02:20:32 UTC*

Implement Create Target Strong arena as described in game_design.md

---

## [idea-arena-114] Create Funny fails arena — *2026-06-21 23:29:06 UTC*

Implement Create Funny fails arena as described in game_design.md

---

## [idea-arena-122] Create AI Commentary arena — *2026-06-21 22:22:49 UTC*

Implement Create AI Commentary arena as described in game_design.md

---

## [idea-arena-104] Create Heal Ally arena — *2026-06-21 22:16:40 UTC*

Implement Create Heal Ally arena as described in game_design.md

---

## [idea-arena-107] Create Escort arena — *2026-06-21 22:12:33 UTC*

Implement Create Escort arena as described in game_design.md

---

## [idea-arena-111] Create Wait and Watch arena — *2026-06-21 20:29:32 UTC*

Implement Create Wait and Watch arena as described in game_design.md

---

## [auto-implement-**target-strong**-—-атакует-самого-сильн] Implement **Target Strong** — атакует самого сильного skill — *2026-06-21 20:28:16 UTC*

Create **Target Strong** — атакует самого сильного skill: для Tank

---

## [idea-arena-093] Create Target Weak arena — *2026-06-21 18:29:57 UTC*

Implement Create Target Weak arena as described in game_design.md

---

## [idea-arena-126] Create Battle Royale Shrinking Zone arena — *2026-06-21 18:20:56 UTC*

Implement Create Battle Royale Shrinking Zone arena as described in game_design.md

---

## [idea-arena-121] Create Emotional Contagion arena — *2026-06-21 16:28:42 UTC*

Implement Create Emotional Contagion arena as described in game_design.md

---

## [idea-arena-125] Create Physics Chain Reactions arena — *2026-06-21 14:21:11 UTC*

Implement Create Physics Chain Reactions arena as described in game_design.md

---

## [idea-arena-106] Create Body Block arena — *2026-06-21 12:04:51 UTC*

Implement Create Body Block arena as described in game_design.md

---

## [idea-arena-124] Create Meta Evolution arena — *2026-06-21 11:55:20 UTC*

Implement Create Meta Evolution arena as described in game_design.md

---

## [idea-arena-098] Create Ambush arena — *2026-06-21 09:06:37 UTC*

Implement Create Ambush arena as described in game_design.md

---

## [idea-arena-117] Create Team wipes arena — *2026-06-21 08:55:14 UTC*

Implement Create Team wipes arena as described in game_design.md

---

## [idea-ball_type-085] Implement Scout ball — *2026-06-21 04:28:25 UTC*

Implement Implement Scout ball as described in game_design.md

---

## [idea-arena-120] Create Swarm Intelligence arena — *2026-06-21 04:21:25 UTC*

Implement Create Swarm Intelligence arena as described in game_design.md

---

## [idea-arena-116] Create 1v1 Finals arena — *2026-06-21 04:17:33 UTC*

Implement Create 1v1 Finals arena as described in game_design.md

---

## [idea-arena-112] Create Clutch plays arena — *2026-06-20 23:53:39 UTC*

Implement Create Clutch plays arena as described in game_design.md

---

## [idea-arena-108] Create Collect Booster arena — *2026-06-20 22:15:36 UTC*

Implement Create Collect Booster arena as described in game_design.md

---

## [idea-arena-123] Create Ball Relationships arena — *2026-06-20 21:01:24 UTC*

Implement Create Ball Relationships arena as described in game_design.md

---

## [idea-arena-110] Create Reposition arena — *2026-06-20 19:38:29 UTC*

Implement Create Reposition arena as described in game_design.md

---

## [idea-ball_type-088] Implement Sniper ball — *2026-06-20 18:30:16 UTC*

Implement Implement Sniper ball as described in game_design.md

---

## [idea-arena-115] Create Epic kills arena — *2026-06-20 18:19:29 UTC*

Implement Create Epic kills arena as described in game_design.md

---

## [idea-arena-097] Create Group Attack arena — *2026-06-20 18:13:52 UTC*

Implement Create Group Attack arena as described in game_design.md

---

## [idea-arena-109] Create Avoid Trap arena — *2026-06-20 18:05:45 UTC*

Implement Create Avoid Trap arena as described in game_design.md

---

## [idea-arena-095] Create Kite arena — *2026-06-20 17:06:56 UTC*

Implement Create Kite arena as described in game_design.md

---

## [idea-arena-100] Create Circle Strafe arena — *2026-06-20 16:37:59 UTC*

Implement Create Circle Strafe arena as described in game_design.md

---

## [idea-arena-103] Create Hide Behind arena — *2026-06-20 15:15:30 UTC*

Implement Create Hide Behind arena as described in game_design.md

---

## [idea-ball_type-091] Implement King ball — *2026-06-20 15:12:37 UTC*

Implement Implement King ball as described in game_design.md

---

## [idea-ball_type-082] Implement Hard ball — *2026-06-20 15:02:59 UTC*

Implement Implement Hard ball as described in game_design.md

---

## [idea-arena-113] Create Comebacks arena — *2026-06-20 14:59:06 UTC*

Implement Create Comebacks arena as described in game_design.md

---

## [idea-feature-072] 12+ ball types — *2026-06-20 12:56:27 UTC*

Implement 12+ ball types as described in game_design.md

---

## [idea-ball_type-087] Implement Healer ball — *2026-06-20 12:54:41 UTC*

Implement Implement Healer ball as described in game_design.md

---

## [idea-arena-092] Create Aggressive Chase arena — *2026-06-20 12:51:51 UTC*

Implement Create Aggressive Chase arena as described in game_design.md

---

## [idea-arena-105] Create Buff Ally arena — *2026-06-20 12:39:16 UTC*

Implement Create Buff Ally arena as described in game_design.md

---

## [idea-ball_type-083] Implement Chaos ball — *2026-06-20 11:21:25 UTC*

Implement Implement Chaos ball as described in game_design.md

---

## [idea-arena-102] Create Retreat to Ally arena — *2026-06-20 11:09:33 UTC*

Implement Create Retreat to Ally arena as described in game_design.md

---

## [auto-implement-**flank**-—-обходит-сзади-для-удара-skil] Implement **Flank** — обходит сзади для удара skill — *2026-06-20 08:43:30 UTC*

Create **Flank** — обходит сзади для удара skill: для Ninja

---

## [idea-feature-036] Battle Royale mode with 20 balls — *2026-06-20 08:36:55 UTC*

Implement Battle Royale mode with 20 balls as described in game_design.md

---

## [idea-arena-101] Create Use Shield arena — *2026-06-20 08:33:13 UTC*

Implement Create Use Shield arena as described in game_design.md

---

## [idea-ball_type-084] Implement Warrior ball — *2026-06-20 05:16:07 UTC*

Implement Implement Warrior ball as described in game_design.md

---

## [idea-ball_type-089] Implement Bomber ball — *2026-06-20 05:05:01 UTC*

Implement Implement Bomber ball as described in game_design.md

---

## [idea-arena-096] Create Flank arena — *2026-06-20 05:02:12 UTC*

Implement Create Flank arena as described in game_design.md

---

## [idea-feature-079] Stats overlay — *2026-06-20 00:36:19 UTC*

Implement Stats overlay as described in game_design.md

---

## [idea-ball_type-081] Implement Medium ball — *2026-06-20 00:31:35 UTC*

Implement Implement Medium ball as described in game_design.md

---

## [idea-feature-076] Camera system — *2026-06-20 00:29:49 UTC*

Implement Camera system as described in game_design.md

---

## [idea-ball_type-090] Implement Ninja ball — *2026-06-20 00:21:54 UTC*

Implement Implement Ninja ball as described in game_design.md

---

## [idea-ball_type-080] Implement Easy ball — *2026-06-19 22:52:26 UTC*

Implement Implement Easy ball as described in game_design.md

---

## [idea-ball_type-086] Implement Tank ball — *2026-06-19 22:43:32 UTC*

Implement Implement Tank ball as described in game_design.md

---

## [idea-feature-077] Highlight detection — *2026-06-19 21:35:30 UTC*

Implement Highlight detection as described in game_design.md

---

## [idea-feature-074] 10+ arenas — *2026-06-19 21:33:52 UTC*

Implement 10+ arenas as described in game_design.md

---

## [idea-feature-078] Replay system — *2026-06-19 21:29:56 UTC*

Implement Replay system as described in game_design.md

---

## [idea-feature-075] AI difficulty levels — *2026-06-19 20:16:06 UTC*

Implement AI difficulty levels as described in game_design.md

---

## [idea-feature-073] 6 game modes — *2026-06-19 20:11:54 UTC*

Implement 6 game modes as described in game_design.md

---

## [idea-feature-061] Skill usage AI — *2026-06-19 16:19:23 UTC*

Implement Skill usage AI as described in game_design.md

---

## [auto-implement-**ball-genetics**-—-balls-reproduce-afte] Implement **Ball Genetics** — Balls reproduce after surviving N battles. Offspring inherit traits skill — *2026-06-19 12:29:23 UTC*

Create **Ball Genetics** — Balls reproduce after surviving N battles. Offspring inherit traits skill: speed, damage, color

---

## [idea-feature-063] 8 ball types — *2026-06-19 02:53:36 UTC*

Implement 8 ball types as described in game_design.md

---

## [idea-feature-059] Advanced behaviors (kite, flank, group attack) — *2026-06-19 02:48:38 UTC*

Implement Advanced behaviors (kite, flank, group attack) as described in game_design.md

---

## [sync-gd-perception-calc-dist] Sync GDScript: Implement 'calc_dist' in perception.gd — *2026-06-19 02:33:29 UTC*

The Python class in perception.py implements 'calc_dist', but the GDScript counterpart perception.gd is missing it. Please implement the same logic in GDScript.

---

## [visualizer-interactive-spectator] Add interactive inspection mode to Visualizer — *2026-06-18 23:48:07 UTC*

Allow clicking on any ball during playback to highlight it, display its active state, current health, target enemy, and emotional level in a detailed inspector panel on the page.

---

## [idea-feature-062] Team coordination — *2026-06-18 23:39:35 UTC*

Implement Team coordination as described in game_design.md

---

## [procedural-hazards] Add procedural hazards to arena — *2026-06-18 21:42:40 UTC*

Generate random hazards (spikes, lava) in the arena that damage balls when they collide.

---

## [idea-feature-060] Emotion system (fear, rage, greed) — *2026-06-18 21:23:23 UTC*

Implement Emotion system (fear, rage, greed) as described in game_design.md

---

## [idea-feature-037] Basic arena — *2026-06-18 21:20:08 UTC*

Implement Basic arena as described in game_design.md

---

## [add-particle-effects] Add particle effects for skills — *2026-06-18 19:13:14 UTC*

Create basic particle effects in Godot for when balls use their skills like Wave Attack or Explosion.

---

## [visualizer-skills-effects] Implement visual effects for all ball skills in HTML5 Canvas — *2026-06-18 18:46:54 UTC*

Enhance visualizer/index.html to draw unique particle animations and visual elements when balls trigger specific skills (e.g. Shield draws a glowing cyan circle around the tank, Wave Attack draws red shockwaves, Dash leaves ghost trail particles).

---

## [arena-procedural-generation-rooms] Add procedural multi-room arenas — *2026-06-18 18:36:57 UTC*

Expand the arena generation algorithm to create multi-room maps connected by corridors, rather than a single large open space.

---

## [arena-shrinking-zone] Add shrinking battle zone logic — *2026-06-18 15:57:35 UTC*

Implement a battle royale shrinking zone (like in PUBG/Fortnite). The safe area should decrease over time, and any ball outside the zone takes continuous damage.

---

## [add-skill-effects-vfx] Add Particle VFX for Ball Skills — *2026-06-18 15:43:26 UTC*

Implement Godot Particle2D nodes that trigger when a ball uses its special skill, such as wave attack or explosion.

---

## [innovate-perceptron-ai] Innovation: Implement Neural Network Perceptron AI — *2026-06-18 12:09:09 UTC*

Replace the hardcoded if-else logic in src/ai/decision.py and src/ai/decision.gd with a simple Perceptron/Weights Matrix. Create a file ai_weights.json to store the weights. The decision layer should calculate the score for each action by multiplying perception inputs with the weights.

---

## [implement-kill-feed-ui] Implement Kill Feed UI — *2026-06-18 12:00:03 UTC*

Create a UI kill feed that logs which ball killed which, using the battle simulation kill_log data.

---

## [idea-feature-035] 4 ball types with unique AI — *2026-06-18 07:54:38 UTC*

Implement 4 ball types with unique AI as described in game_design.md

---

## [ai-meta-evolution-phase] Implement Meta Evolution phase between battles — *2026-06-18 07:39:45 UTC*

Create a system where balls have a development phase between battles to upgrade stats (speed, damage, max hp) based on their survival and kills.

---

## [auto-implement-coach-mode-(тренер)-game-mode] Implement Coach Mode (Тренер) game mode — *2026-06-18 02:33:50 UTC*

Create Coach Mode (Тренер) with full rules and mechanics

---

## [auto-create-procedural-arenas-arena] Create Procedural Arenas arena — *2026-06-18 02:29:44 UTC*

Implement Procedural Arenas with unique mechanics

---

## [ai-neural-network-brain-phase3] Evaluate NeuralNetworkBrain performance — *2026-06-17 23:26:52 UTC*

Run the NeuralNetworkBrain (Phase 2) alongside the standard BallBrain in simulate_battle.py to evaluate learning efficiency over 500 battles.

---

## [ai-emotional-contagion-logic] Implement Emotional Contagion Logic — *2026-06-17 21:54:12 UTC*

Update Emotion layer so fear and aggression spread like a virus. If a ball flees, nearby balls have a chance to enter cowardice/fear state.

---

## [ai-behavior-flank] Implement Flank behavior — *2026-06-17 21:34:57 UTC*

Ball moves behind enemy for bonus damage. Uses stealth (Ninja) or speed (Scout) to get behind. Attacks from behind for critical hit.

---

## [ai-physics-chain-reactions] Add Physics Chain Reactions — *2026-06-17 19:53:23 UTC*

Make it so balls bouncing off walls or enemies can trigger a ripple effect, pushing other balls into hazards or causing extra damage based on speed.

---

## [idea-feature-034] Basic AI behaviors (chase, flee, attack) — *2026-06-17 17:20:51 UTC*

Implement Basic AI behaviors (chase, flee, attack) as described in game_design.md

---

## [auto-implement-spectator-mode-(наблюдатель)-game-mode] Implement Spectator Mode (Наблюдатель) game mode — *2026-06-17 17:14:27 UTC*

Create Spectator Mode (Наблюдатель) with full rules and mechanics

---

## [ai-ball-tank-ai] Implement Tank AI profile — *2026-06-17 17:14:05 UTC*

Tank AI: brave personality, protects allies, uses Shield when taking damage, body blocks for healers, draws aggro.

---

## [ai-ball-ninja-ai] Implement Ninja AI profile — *2026-06-17 17:08:06 UTC*

Ninja AI: cunning personality, uses Stealth to approach, attacks from behind for critical, flees after attack, hit-and-run tactics.

---

## [ai-neural-network-brain-wrapper] Implement NeuralNetworkBrain wrapper — *2026-06-17 13:31:07 UTC*

Create a wrapper for Neural Network that plugs directly into BallBrain architecture (replacing Decision layer) to evaluate its performance against the standard Decision logic.

---

## [auto-implement-action-skill] Implement ACTION skill — *2026-06-17 13:25:23 UTC*

Create ACTION skill: Действие

---

## [ai-ball-bomber-ai] Implement Bomber AI profile — *2026-06-17 13:23:00 UTC*

Bomber AI: reckless personality, seeks crowded enemy groups, uses Bomb when 3+ enemies nearby, suicide attacks.

---

## [ai-ball-healer-ai] Implement Healer AI profile — *2026-06-17 09:37:16 UTC*

Healer AI: caring personality, follows wounded allies, heals them, avoids combat, uses heal on cooldown.

---

## [ai-battle-commentator-text] Add AI Battle Commentator — *2026-06-17 09:33:57 UTC*

Create a module that parses the kill_log and actions performed during a simulation to produce exciting, dynamic text commentary of the battle.

---

## [ai-ball-sniper-ai] Implement Sniper AI profile — *2026-06-17 04:32:15 UTC*

Sniper AI: cautious personality, maintains distance, uses Snipe from max range, kites enemies, avoids melee.

---

## [ai-ball-king-ai] Implement King AI profile — *2026-06-17 04:31:51 UTC*

King AI: leader personality, stays behind allies, uses Command to buff team, targets low HP allies to boost, avoids direct combat.

---

## [ai-neural-network-learning] Implement Neural Network module for learning — *2026-06-17 04:23:57 UTC*

Create a simple neural network that allows balls to learn from their successes (kills, survival time) and failures over multiple rounds. The weights should adjust dynamically to improve decision making.

---

## [web-visualizer-improvements] Improve Web Visualizer (index.html) — *2026-06-17 04:16:57 UTC*

The user requested improvements to visualizer/index.html. We need to add better UI controls (pause/play, timeline slider, speed control), show the winner clearly, fix any bugs, improve the rendering quality (e.g. better shadows, text showing ball HP or class), and make it fully responsive. Ensure all JS is clean and robust.

---

## [balance-buff-guardian] Balance: Buff underpowered 'guardian' — *2026-06-17 01:37:56 UTC*

The 'guardian' class is winning only 0.0% of the time (expected ~8.3%). It is severely underpowered. Please increase its survivability, damage, speed, or decrease skill cooldown.

---

## [ai-neural-network-learning-v2] Implement Neural Network learning logic (Phase 2) — *2026-06-17 00:09:56 UTC*

Refine the previously designed neural network learning module for balls by testing with actual battle simulation data over multiple generations.

---

## [ai-ball-warrior-ai] Implement Warrior AI profile — *2026-06-17 00:05:33 UTC*

Warrior AI: aggressive personality, high attack priority, never flees, uses Wave Attack when 2+ enemies in front, charges into battle.

---

## [ai-behavior-kite] Implement Kite behavior — *2026-06-16 22:26:31 UTC*

Ball maintains distance from enemy while attacking. Moves back when enemy approaches, attacks when enemy retreats. Used by Sniper and ranged types.

---

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

