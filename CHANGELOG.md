# Changelog

All notable changes to Ball Royale will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- Battle simulation engine (50-1000 balls) — `tests/simulate_battle.py`
- AI performance benchmark — `tests/benchmark_ai.py`
- Ball type configs — `configs/ball_types.json`
- Content generator from JSON — `scripts/generate_content.py`
- Code quality metrics — `scripts/quality_metrics.py`
- Concurrency groups for dispatcher/supervisor workflows
- GITHUB_TOKEN passed to all agent workflows
- Atomic file writes via temp + fsync + os.replace
- verify_pushed() after commit
- Combined stale reset + assignments in one atomic_update
- Deep merge for agent_lock.json updates
- Rate-limit retry with 60s sleep
- Day boundary cycle reset

### Changed
- Jules prompt now enforces self-evolution after each task
- Jules must run simulation and quality checks before creating PR
- PR polling increased from 2 min to 5 min
- Stale timeout increased from 20 min to 45 min
- auto-merge.yml now checks CI status before merging
- get_ci_status treats timed_out/cancelled/action_required as failures
- git reset --hard replaced with git checkout origin/main (safer)
- status_agents.py denominator fixed (180 → 210 for 7 agents)
- AREA_TO_AGENT includes all task areas including bugfix→meta

### Fixed
- C1: git_reset_to_remote uses checkout instead of reset --hard
- C2: atomic_update deep-merges agents (not full replacement)
- C3: File descriptor leak fixed (lock_fd in finally)
- C4: get_ci_status handles all failure states
- C5: auto-merge.yml checks CI before merge
- H3: Cycles_today reset at day boundaries
- H4: verify_pushed checks origin/main exists
- H5: Stale in-progress detection (no task = reset)
- H7: Stale lock_data snapshot overwrites remote
- H8: File descriptor leak on lock contention
- M1-M10: 10 medium-severity bugs across all scripts
- L1-L12: 12 low-severity issues including encoding, Windows compat

## [0.1.0] - 2026-06-05

### Added
- BallBrain architecture (Perception → Emotion → Decision → Action)
- GDScript implementation — `src/ai/ball_brain.gd`
- Python implementation — `src/ai/ball_brain.py`
- Unit tests for BallBrain — `tests/test_ball_brain.py`
- GitHub Actions CI pipeline
- Jules infinite loop workflow with self-improvement
- Auto-merge for Jules PRs
- 37 initial tasks in `agent_tasks.json`
