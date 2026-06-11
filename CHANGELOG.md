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
- Concurrency groups on ALL workflows (dispatcher, supervisor, agents, auto-merge, issue-to-task, auto-improve)
- GITHUB_TOKEN passed to all agent workflows + status_agents.py
- Atomic file writes via temp + fsync + os.replace
- verify_pushed() after commit (returns False on git error)
- Combined stale reset + assignments in one atomic_update
- Deep merge for agent_lock.json updates
- Rate-limit retry with bounded recursion (max 3)
- Day boundary cycle reset (all agents)
- Self-recovery for stale agents (>45 min timeout)
- Task deduplication via assigned_remote set
- Input validation/sanitization in issue-to-task.yml
- check_suite trigger on auto-merge.yml
- Pip caching on all Python workflows
- fetch-depth: 1 on checkout steps

### Changed
- Jules prompt now enforces self-evolution after each task
- Jules must run simulation and quality checks before creating PR
- PR polling increased from 2 min to 5 min
- Stale timeout increased from 20 min to 45 min
- auto-merge.yml now checks CI status before merging + has try/catch
- get_ci_status treats timed_out/cancelled/action_required as failures
- git reset --hard replaced with git checkout origin/main (safer)
- status_agents.py denominator fixed (180 → 210 for 7 agents)
- AREA_TO_AGENT includes all task areas including bugfix→meta
- CI skip automated commits (dispatcher/supervisor/auto)
- Lock file opened with a+ mode (not truncated)
- Lock file descriptors properly closed in finally blocks
- SUPERVISOR_ID constant instead of hardcoded "agent-7"

### Fixed
- supervisor.py: CI fix polling now refreshes SHA after each cycle
- supervisor.py: wait_for_ci uses correct range (max_minutes * 60)
- supervisor.py: get_ci_status scans ALL check-runs before returning pending
- supervisor.py: Removed non-existent commits/{sha}/pull-request endpoint
- supervisor.py: check_all_agents_idle returns False when any agent working
- supervisor.py: verify_pushed returns False on git error
- supervisor.py: get_open_prs filters dict responses
- supervisor.py: lock_data updated after stale reset computation
- supervisor.py: merge_pr checks merged field + return value checked
- launch_agent.py: Day boundary updates last_reset + includes in atomic_update
- launch_agent.py: Self-recovery for stale agents (>45 min)
- launch_agent.py: Rate limit retry bounded (max 3)
- launch_agent.py: Task deduplication via assigned_remote set
- launch_agent.py: git_fetch returns result.returncode
- launch_agent.py: PR polling uses owner:branch format
- launch_agent.py: Day boundary resets ALL agents
- dispatch_agents.py: Lock file opened with a+ (not truncated)
- dispatch_agents.py: git add return value checked
- dispatch_agents.py: Unparseable started_at resets agent
- dispatch_agents.py: AREA_TO_AGENT fallback returns None
- dispatch_agents.py: No in-place mutation before commit
- Workflows: Concurrency groups on all 6 agent workflows
- Workflows: auto-merge triggers on check_suite completion
- Workflows: auto-merge merge call wrapped in try/catch
- Workflows: issue-to-task top-level permissions: {}
- Workflows: All use checkout@v5 with pip caching
- Workflows: auto-merge per_page=100
- Workflows: ci.yml skips automated commits

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
