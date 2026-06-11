# Changelog

All notable changes to Ball Royale will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Fixed
- dispatch_agents.py: Restore indentation in atomic_update (dispatcher was completely broken since Round 7)
- supervisor.py: Skip CI fix when agent_id cannot be extracted from branch
- supervisor.py: Reset agent status when Jules API fails to trigger fix
- supervisor.py: Add rate limit retry with backoff to github_api
- launch_agent.py: Keep 'working' status after Jules accepts (was immediately idle)
- launch_agent.py: Check PR before sleep in polling loop
- launch_agent.py: Handle unknown areas like dispatch_agents.py
- supervisor.py: Check pr_updates agents before saving
- auto-merge.yml: Add head filter to pulls.list for efficiency
- auto-improve.yml: Replace git add -A with targeted add
- status_agents.py: Count assigned agents as active
- status_agents.py: Safe access to task id with .get()
- jules-supervisor.yml: Remove redundant git pull step
- launch_agent.py: Remove unnecessary sleep(2)
- dispatch_agents.py: Safe setdefault for cycles_today
- ci.yml: Skip commits with auto: prefix

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
- auto-merge SHA fallback when check_suite.pull_requests empty
- auto-merge mergeable null handling (re-fetch after 30s)
- auto-merge empty check-runs retry after 30s
- issue-to-task graceful handling of missing/malformed agent_tasks.json
- status_agents.py try/except on load_json

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
- auto-improve.yml scripts use || true to prevent cascade failure
- dispatch_agents.py git reset scoped to LOCK_FILE only

### Fixed
- supervisor.py: CI fix polling now checks status BEFORE sleep (was sleeping first)
- supervisor.py: pr_updates populated after merges (agents were stuck working 45 min)
- supervisor.py: consecutive_failures reset on 'pending' status
- supervisor.py: get_ci_status distinguishes auth errors from pending
- supervisor.py: Agent ID extracted from PR branch for status updates
- supervisor.py: Area added to invoke_jules prompt
- launch_agent.py: atomic_update return checked on Jules success/failure paths
- launch_agent.py: Stale-reset atomic_update return checked
- launch_agent.py: Day-boundary atomic_update return checked
- launch_agent.py: Agent busy status check before task assignment
- launch_agent.py: 404 no longer retried 3 times (was wasting 30s)
- launch_agent.py: check_pr_created creates fresh request per retry
- dispatch_agents.py: git_reset_to_remote return checked on initial sync
- dispatch_agents.py: git reset scoped to LOCK_FILE (was unstaging ALL files)
- dispatch_agents.py: CONFLICT check case-insensitive
- dispatch_agents.py: Rollbacks batched in single atomic_update
- dispatch_agents.py: started_at uses batch timestamp
- dispatch_agents.py: New agents get default cycles_today=0
- dispatch_agents.py: Malformed TASK_FILE handled gracefully
- auto-merge.yml: check_suite fallback searches PRs by SHA
- auto-merge.yml: mergeable null handled with re-fetch
- auto-merge.yml: Empty check-runs triggers retry after 30s
- auto-merge.yml: Removed page >= 10 cap on check-runs pagination
- auto-improve.yml: Scripts use || true to prevent sequential failure
- issue-to-task.yml: Missing agent_tasks.json creates empty manifest
- status_agents.py: load_json wrapped in try/except
- status_agents.py: Division by zero prevented
- status_agents.py: Task status accessed safely with .get()

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
