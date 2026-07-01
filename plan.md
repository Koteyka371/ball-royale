1. Fix issues in Boss Mutator logic:
   - Use `run_in_bash_session` to execute the following commands to update `src/ai/game_modes.py` and `src/ai/game_modes.gd`:
```bash
cat << 'PYEOF' > patch_py.py
import re
with open("src/ai/game_modes.py", "r") as f: content = f.read()
boss_logic_py = """
        if getattr(self, "mutators_active", False):
            if "boss" in self.mutators:
                if not hasattr(self, "boss_mutator_timer"):
                    self.boss_mutator_timer = 0.0

                # Check if there is already an active boss (even if dead)
                active_boss = None
                for b in balls:
                    if getattr(b, "_is_boss_mutator", False):
                        active_boss = b
                        break

                if active_boss:
                    # Decrement boss timer
                    if hasattr(active_boss, "_boss_mutator_duration"):
                        active_boss._boss_mutator_duration -= delta
                        if active_boss._boss_mutator_duration <= 0 or not getattr(active_boss, "alive", False):
                            # Revert boss
                            active_boss._is_boss_mutator = False
                            if hasattr(active_boss, "_original_radius"):
                                active_boss.radius = active_boss._original_radius
                            if hasattr(active_boss, "_original_max_hp"):
                                active_boss.max_hp = active_boss._original_max_hp
                            if hasattr(active_boss, "_original_damage"):
                                active_boss.damage = active_boss._original_damage
                            if hasattr(active_boss, "_original_base_damage"):
                                active_boss.base_damage = active_boss._original_base_damage
                            if hasattr(active_boss, "_original_team"):
                                active_boss.team = active_boss._original_team

                            # Restore hp proportionally if alive
                            if getattr(active_boss, "alive", False):
                                hp_pct = active_boss.hp / (active_boss.max_hp * 3) if active_boss.max_hp > 0 else 1.0
                                active_boss.hp = active_boss.max_hp * hp_pct

                            # Revert everyone else's team
                            for b in balls:
                                if getattr(b, "_original_team", None) is not None and b != active_boss:
                                    b.team = b._original_team
                            self.boss_mutator_timer = 0.0
                else:
                    self.boss_mutator_timer += delta
                    if self.boss_mutator_timer >= 10.0:
                        self.boss_mutator_timer = 0.0
                        import random
                        valid_bosses = [b for b in balls if getattr(b, "alive", False) and getattr(b, "ball_type", None) != "spectator"]
                        if valid_bosses:
                            new_boss = random.choice(valid_bosses)
                            new_boss._is_boss_mutator = True
                            new_boss._boss_mutator_duration = 15.0

                            new_boss._original_radius = getattr(new_boss, "radius", 15.0)
                            new_boss.radius = new_boss._original_radius * 2.0

                            new_boss._original_max_hp = getattr(new_boss, "max_hp", 100.0)
                            new_boss.max_hp = new_boss._original_max_hp * 3.0
                            hp_pct = getattr(new_boss, "hp", 100.0) / new_boss._original_max_hp if new_boss._original_max_hp > 0 else 1.0
                            new_boss.hp = new_boss.max_hp * hp_pct

                            new_boss._original_damage = getattr(new_boss, "damage", 10.0)
                            new_boss.damage = new_boss._original_damage * 2.0

                            if hasattr(new_boss, "base_damage"):
                                new_boss._original_base_damage = new_boss.base_damage
                                new_boss.base_damage = new_boss._original_base_damage * 2.0

                            new_boss._original_team = getattr(new_boss, "team", getattr(new_boss, "ball_type", "solo"))
                            new_boss.team = "Boss_Mutator"

                            # Everyone else teams up against the boss
                            for b in balls:
                                if b != new_boss and getattr(b, "ball_type", None) != "spectator":
                                    if not hasattr(b, "_original_team"):
                                        b._original_team = getattr(b, "team", getattr(b, "ball_type", "solo"))
                                    b.team = "Hunters"

                            if hasattr(world, "add_event"):
                                world.add_event("boss_mutator", {"message": f"{new_boss.ball_type.capitalize()} has become a Juggernaut Boss!"})

            trigger_reroll = False"""
content = re.sub(r'        if getattr\(self, "mutators_active", False\):\n            if "boss" in self\.mutators:.*?(?=            trigger_reroll = False)', boss_logic_py, content, flags=re.DOTALL)
with open("src/ai/game_modes.py", "w") as f: f.write(content)
PYEOF
python patch_py.py
cat << 'GDEOF' > patch_gd.py
import re
with open("src/ai/game_modes.gd", "r") as f: content = f.read()
boss_logic_gd = """
		if mutators_active:
			if mutators.has("boss"):
				if not has_meta("boss_mutator_timer"):
					set_meta("boss_mutator_timer", 0.0)

				var active_boss = null
				for b in balls:
					if b.has_meta("_is_boss_mutator") and b.get_meta("_is_boss_mutator"):
						active_boss = b
						break

				if active_boss != null:
					var b_dur = active_boss.get_meta("_boss_mutator_duration") - delta
					active_boss.set_meta("_boss_mutator_duration", b_dur)
					if b_dur <= 0 or not active_boss.alive:
						active_boss.set_meta("_is_boss_mutator", false)
						if active_boss.has_meta("_original_radius"):
							if "radius" in active_boss:
								active_boss.radius = active_boss.get_meta("_original_radius")
							else:
								active_boss.set_meta("radius", active_boss.get_meta("_original_radius"))
						if active_boss.has_meta("_original_max_hp"):
							active_boss.max_hp = active_boss.get_meta("_original_max_hp")
						if active_boss.has_meta("_original_damage"):
							active_boss.damage = active_boss.get_meta("_original_damage")
						if active_boss.has_meta("_original_base_damage"):
							active_boss.base_damage = active_boss.get_meta("_original_base_damage")
						if active_boss.has_meta("_original_team"):
							active_boss.team = active_boss.get_meta("_original_team")

						if active_boss.alive:
							var orig_hp = active_boss.get_meta("_original_max_hp") if active_boss.has_meta("_original_max_hp") else 100.0
							var hp_pct = active_boss.hp / (orig_hp * 3.0) if orig_hp > 0 else 1.0
							active_boss.hp = orig_hp * hp_pct

						for b in balls:
							if b != active_boss and b.has_meta("_original_team"):
								b.team = b.get_meta("_original_team")
						set_meta("boss_mutator_timer", 0.0)
				else:
					var b_timer = get_meta("boss_mutator_timer") + delta
					if b_timer >= 10.0:
						b_timer = 0.0
						var valid_bosses = []
						for b in balls:
							if b.alive and b.get("ball_type", "") != "spectator":
								valid_bosses.append(b)
						if valid_bosses.size() > 0:
							var new_boss = valid_bosses[randi() % valid_bosses.size()]
							new_boss.set_meta("_is_boss_mutator", true)
							new_boss.set_meta("_boss_mutator_duration", 15.0)

							var orig_rad = 15.0
							if "radius" in new_boss:
								orig_rad = new_boss.radius
								new_boss.radius = orig_rad * 2.0
							elif new_boss.has_meta("radius"):
								orig_rad = new_boss.get_meta("radius")
								new_boss.set_meta("radius", orig_rad * 2.0)
							new_boss.set_meta("_original_radius", orig_rad)

							var orig_max_hp = new_boss.get("max_hp", 100.0)
							new_boss.set_meta("_original_max_hp", orig_max_hp)
							new_boss.max_hp = orig_max_hp * 3.0

							var hp_pct = new_boss.get("hp", 100.0) / orig_max_hp if orig_max_hp > 0 else 1.0
							new_boss.hp = new_boss.max_hp * hp_pct

							var orig_dmg = new_boss.get("damage", 10.0)
							new_boss.set_meta("_original_damage", orig_dmg)
							new_boss.damage = orig_dmg * 2.0

							if "base_damage" in new_boss:
								new_boss.set_meta("_original_base_damage", new_boss.base_damage)
								new_boss.base_damage = new_boss.get_meta("_original_base_damage") * 2.0

							new_boss.set_meta("_original_team", new_boss.get("team", new_boss.get("ball_type", "solo")))
							new_boss.team = "Boss_Mutator"

							for b in balls:
								if b != new_boss and b.get("ball_type", "") != "spectator":
									if not b.has_meta("_original_team"):
										b.set_meta("_original_team", b.get("team", b.get("ball_type", "solo")))
									b.team = "Hunters"

							if world != null and world.has_method("add_event"):
								world.add_event("boss_mutator", {"message": "A player has become a Juggernaut Boss!"})

					set_meta("boss_mutator_timer", b_timer)

			var trigger_reroll = false"""
content = re.sub(r'\t\tif mutators_active:\n\t\t\tif mutators.has\("boss"\):.*?(?=\t\t\tvar trigger_reroll = false)', boss_logic_gd, content, flags=re.DOTALL)
with open("src/ai/game_modes.gd", "w") as f: f.write(content)
GDEOF
python patch_gd.py
```
2. Verify changes:
   - Use `run_in_bash_session` to execute `git diff` to ensure changes are correct.
3. Update tests:
   - Use `run_in_bash_session` to write updated test cases to `src/ai/test_boss_mutator.py`:
```bash
cat << 'PYEOF' > src/ai/test_boss_mutator.py
import pytest
from ai.game_modes import CustomMatchMode

class MockWorld:
    def __init__(self):
        self.events = []
    def add_event(self, type, data):
        self.events.append((type, data))

class MockBall:
    def __init__(self, id, ball_type):
        self.id = id
        self.ball_type = ball_type
        self.alive = True
        self.team = ball_type
        self.radius = 15.0
        self.max_hp = 100.0
        self.hp = 100.0
        self.damage = 10.0
        self.base_damage = 10.0

def test_boss_mutator():
    mode = CustomMatchMode()
    mode.mutators = ["boss"]
    world = MockWorld()
    world.profile_manager = type('MockProfileManager', (), {'are_mutators_unlocked': lambda self: True})()

    balls = [
        MockBall(id=1, ball_type="tank"),
        MockBall(id=2, ball_type="sniper"),
        MockBall(id=3, ball_type="healer")
    ]

    mode.setup(world, balls)
    assert mode.mutators_active == True

    # Tick past 10 seconds to trigger boss
    mode.tick(world, balls, delta=10.1)

    # Verify one ball is boss
    bosses = [b for b in balls if getattr(b, "_is_boss_mutator", False)]
    assert len(bosses) == 1
    boss = bosses[0]

    assert boss.team == "Boss_Mutator"

    # Tick past 15 seconds to end boss mutator
    mode.tick(world, balls, delta=15.1)

    # Verify reverted
    assert not getattr(boss, "_is_boss_mutator", False)
    assert boss.team == boss._original_team

def test_boss_mutator_early_death():
    mode = CustomMatchMode()
    mode.mutators = ["boss"]
    world = MockWorld()
    world.profile_manager = type('MockProfileManager', (), {'are_mutators_unlocked': lambda self: True})()

    balls = [
        MockBall(id=1, ball_type="tank"),
        MockBall(id=2, ball_type="sniper"),
        MockBall(id=3, ball_type="healer")
    ]

    mode.setup(world, balls)

    # Tick past 10 seconds to trigger boss
    mode.tick(world, balls, delta=10.1)

    bosses = [b for b in balls if getattr(b, "_is_boss_mutator", False)]
    boss = bosses[0]

    # Kill the boss early
    boss.hp = 0
    boss.alive = False

    # Tick to process death and revert
    mode.tick(world, balls, delta=0.1)

    # Verify everyone reverts
    assert not getattr(boss, "_is_boss_mutator", False)
    assert boss.team == boss._original_team
    hunters = [b for b in balls if b != boss]
    for h in hunters:
        assert h.team == h._original_team

    # Verify timer resets and ticks again
    assert getattr(mode, "boss_mutator_timer", 0) > 0
    mode.tick(world, balls, delta=10.0)
    new_bosses = [b for b in balls if getattr(b, "_is_boss_mutator", False)]
    assert len(new_bosses) == 1
PYEOF
```
4. Verify tests pass:
   - Use `run_in_bash_session` to run `PYTHONPATH=src pytest src/` to run all tests and verify the changes didn't introduce regressions.
5. Pre-commit check:
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
6. Submit PR:
   - Call the `submit` tool to create the PR.
