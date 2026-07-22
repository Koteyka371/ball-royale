import pytest
from system.guild import GuildManager
from system.profile import ProfileManager

@pytest.fixture
def temp_guild_file(tmp_path):
    file_path = tmp_path / "test_guilds.json"
    yield str(file_path)

@pytest.fixture
def temp_profile_file(tmp_path):
    file_path = tmp_path / "test_profile.json"
    yield str(file_path)

def test_create_guild(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    assert gm.create_guild("TestGuild", "player1") == True
    assert gm.create_guild("TestGuild", "player2") == False # Already exists

    guild = gm.get_guild("TestGuild")
    assert guild is not None
    assert "player1" in guild["members"]
    assert guild["resources"] == 0

def test_join_and_leave_guild(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("TestGuild", "player1")

    assert gm.join_guild("TestGuild", "player2") == True
    assert gm.join_guild("NonExistent", "player3") == False

    guild = gm.get_guild("TestGuild")
    assert "player2" in guild["members"]

    assert gm.leave_guild("TestGuild", "player2") == True
    guild = gm.get_guild("TestGuild")
    assert "player2" not in guild["members"]

def test_guild_disbands_when_empty(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("SoloGuild", "player1")
    assert gm.leave_guild("SoloGuild", "player1") == True
    assert gm.get_guild("SoloGuild") is None

def test_donate_and_unlock_buffs(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("BuffGuild", "player1")

    assert gm.donate_resources("BuffGuild", 100) == True
    guild = gm.get_guild("BuffGuild")
    assert guild["resources"] == 100

    assert gm.unlock_buff("BuffGuild", "bonus_hp", 50) == True
    guild = gm.get_guild("BuffGuild")
    assert guild["resources"] == 50
    assert guild["buffs"]["bonus_hp"] == 1

    assert gm.unlock_buff("BuffGuild", "bonus_hp", 100) == False # Not enough resources

def test_gvg_match_recording(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("GuildA", "player1")
    gm.create_guild("GuildB", "player2")

    assert gm.record_gvg_match("GuildA", "GuildB", "GuildA") == True

    assert gm.get_guild("GuildA")["gvg_points"] == 10
    assert gm.get_guild("GuildB")["gvg_points"] == 0

    gm.record_gvg_match("GuildA", "GuildB", "GuildB")
    assert gm.get_guild("GuildA")["gvg_points"] == 5
    assert gm.get_guild("GuildB")["gvg_points"] == 10

def test_profile_guild_integration(temp_profile_file):
    pm = ProfileManager(temp_profile_file)
    assert pm.data["guild_name"] == ""

    pm.data["guild_name"] = "MyGuild"
    pm.save()

    pm2 = ProfileManager(temp_profile_file)
    assert pm2.data["guild_name"] == "MyGuild"

    pm2.do_prestige()
    assert pm2.data["guild_name"] == "MyGuild"

def test_guild_chat(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("ChatGuild", "player1")
    assert gm.send_chat_message("ChatGuild", "player1", "Hello World!") == True
    history = gm.get_chat_history("ChatGuild")
    assert len(history) == 1
    assert history[0]["sender"] == "player1"
    assert history[0]["message"] == "Hello World!"

def test_guild_vault(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("VaultGuild", "player1")
    assert gm.deposit_item("VaultGuild", "sword") == True
    guild = gm.get_guild("VaultGuild")
    assert "sword" in guild["vault"]
    assert gm.withdraw_item("VaultGuild", "shield") == False
    assert gm.withdraw_item("VaultGuild", "sword") == True
    guild = gm.get_guild("VaultGuild")
    assert "sword" not in guild["vault"]

def test_guild_territories(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("Conquerors", "player1")
    assert gm.capture_territory("Conquerors", "Castle") == True
    territories = gm.get_territories("Conquerors")
    assert "Castle" in territories
    assert gm.get_territories("NoGuild") == []

    # test passive resources
    guild = gm.get_guild("Conquerors")
    initial_resources = guild["resources"]
    gm.collect_passive_resources()
    guild = gm.get_guild("Conquerors")
    assert guild["resources"] == initial_resources + 5

def test_guild_leaderboard(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("Guild1", "p1")
    gm.create_guild("Guild2", "p2")
    gm.record_gvg_match("Guild1", "Guild2", "Guild2") # Guild2 wins, gets 10 points

    leaderboard = gm.get_guild_leaderboard()
    assert leaderboard[0]["name"] == "Guild2"
    assert leaderboard[0]["gvg_points"] == 10
    assert leaderboard[1]["name"] == "Guild1"
    assert leaderboard[1]["gvg_points"] == 0

def test_boss_progress(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("BossKillers", "player1")

    week_id = "week_1"
    required_damage = 1000.0

    # Check defeated before damage
    assert not gm.check_boss_defeated("BossKillers", week_id, required_damage)

    # Deal damage
    assert gm.record_boss_damage("BossKillers", 400.0, week_id)
    assert not gm.check_boss_defeated("BossKillers", week_id, required_damage)

    assert gm.record_boss_damage("BossKillers", 700.0, week_id)
    assert gm.check_boss_defeated("BossKillers", week_id, required_damage)

    # Claim rewards
    assert gm.claim_boss_reward("BossKillers", "player1", week_id, required_damage)
    # Should not be able to claim twice
    assert not gm.claim_boss_reward("BossKillers", "player1", week_id, required_damage)
    # Different player can claim
    assert gm.claim_boss_reward("BossKillers", "player2", week_id, required_damage)

def test_hq_customization(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("HQGuild", "player1")

    # Needs resources
    assert gm.unlock_hq_feature("HQGuild", "statues", "golden_ball", 500) == False

    gm.donate_resources("HQGuild", 1000)

    # Unlock statue
    assert gm.unlock_hq_feature("HQGuild", "statues", "golden_ball", 500) == True
    # Can't unlock same statue
    assert gm.unlock_hq_feature("HQGuild", "statues", "golden_ball", 500) == False

    # Unlock training arena
    assert gm.unlock_hq_feature("HQGuild", "training_arena", "", 500) == True
    assert gm.unlock_hq_feature("HQGuild", "training_arena", "", 500) == False # Already unlocked

    hq_status = gm.get_hq_status("HQGuild")
    assert hq_status is not None
    assert "golden_ball" in hq_status["statues"]
    assert hq_status["training_arena_unlocked"] == True

def test_hq_mini_games(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("MiniGameGuild", "player1")

    # Need resources
    assert gm.unlock_hq_feature("MiniGameGuild", "mini_games", "obstacle_course", 100) == False

    gm.donate_resources("MiniGameGuild", 500)

    # Unlock mini game
    assert gm.unlock_hq_feature("MiniGameGuild", "mini_games", "obstacle_course", 100) == True
    # Already unlocked
    assert gm.unlock_hq_feature("MiniGameGuild", "mini_games", "obstacle_course", 100) == False

    hq_status = gm.get_hq_status("MiniGameGuild")
    assert "obstacle_course" in hq_status["mini_games"]
    assert hq_status["mini_games"]["obstacle_course"] == {"high_scores": {}}

    # Record scores
    assert gm.record_mini_game_score("MiniGameGuild", "obstacle_course", "player1", 1500) == True
    assert gm.record_mini_game_score("MiniGameGuild", "obstacle_course", "player2", 2000) == True

    # Try updating with a lower score
    assert gm.record_mini_game_score("MiniGameGuild", "obstacle_course", "player1", 1000) == False

    # Get leaderboard
    leaderboard = gm.get_mini_game_leaderboard("MiniGameGuild", "obstacle_course")
    assert len(leaderboard) == 2
    assert leaderboard[0] == {"player_id": "player2", "score": 2000}
    assert leaderboard[1] == {"player_id": "player1", "score": 1500}

    # Unknown mini game
    assert gm.record_mini_game_score("MiniGameGuild", "unknown_game", "player1", 100) == False
    assert gm.get_mini_game_leaderboard("MiniGameGuild", "unknown_game") == []

def test_guild_active_abilities(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("AbilityGuild", "p1")
    gm.donate_resources("AbilityGuild", 200)

    assert gm.buy_active_ability("AbilityGuild", "Mass Heal", 100) == True
    assert gm.buy_active_ability("AbilityGuild", "Global Speed Boost", 100) == True
    assert gm.buy_active_ability("AbilityGuild", "Mass Heal", 100) == False

    abilities = gm.get_active_abilities("AbilityGuild")
    assert "Mass Heal" in abilities
    assert "Global Speed Boost" in abilities

    assert gm.deploy_active_ability("AbilityGuild", "Mass Heal") == True
    assert gm.deploy_active_ability("AbilityGuild", "Mass Heal") == False

    abilities = gm.get_active_abilities("AbilityGuild")
    assert "Mass Heal" not in abilities
    assert "Global Speed Boost" in abilities

def test_guild_perk_progression(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("PerkGuild", "p1")
    gm.create_guild("OtherGuild", "p2")

    # Give some XP via GvG
    gm.record_gvg_match("PerkGuild", "OtherGuild", "PerkGuild") # PerkGuild +50 XP
    gm.record_gvg_match("PerkGuild", "OtherGuild", "PerkGuild") # PerkGuild +50 XP, total 100

    guild = gm.get_guild("PerkGuild")
    assert guild["guild_xp"] == 100

    # Try unlocking a perk
    assert gm.unlock_perk("PerkGuild", "hp_5_percent", 50) == True
    assert guild["guild_xp"] == 50
    assert "hp_5_percent" in gm.get_guild_perks("PerkGuild")

    # Try unlocking same perk again
    assert gm.unlock_perk("PerkGuild", "hp_5_percent", 10) == False

    # Try unlocking with insufficient XP
    assert gm.unlock_perk("PerkGuild", "hp_10_percent", 100) == False

    # Try unlocking with missing dependency
    # Let's say hp_10_percent requires hp_5_percent, but damage_10_percent requires damage_5_percent
    assert gm.unlock_perk("PerkGuild", "damage_10_percent", 50, required_perk="damage_5_percent") == False

    # Get more XP
    gm.record_gvg_match("PerkGuild", "OtherGuild", "PerkGuild") # +50 XP, total 100
    assert gm.unlock_perk("PerkGuild", "hp_10_percent", 100, required_perk="hp_5_percent") == True
    assert "hp_10_percent" in gm.get_guild_perks("PerkGuild")

def test_guild_level_up(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("LevelGuild", "player1")
    gm.create_guild("OtherGuild", "player2")

    # Needs points
    assert gm.upgrade_guild_level("LevelGuild", 10) == False

    gm.record_gvg_match("LevelGuild", "OtherGuild", "LevelGuild") # +10 points

    # Try unlock buff requiring level 2
    gm.donate_resources("LevelGuild", 100)
    assert gm.unlock_buff("LevelGuild", "bonus_hp", 50, required_level=2) == False

    # Try unlock HQ cosmetic requiring level 2
    assert gm.unlock_hq_feature("LevelGuild", "cosmetics", "gold_trim", 50, required_level=2) == False

    # Upgrade level
    assert gm.upgrade_guild_level("LevelGuild", 10) == True

    guild = gm.get_guild("LevelGuild")
    assert guild["level"] == 2

    # Now unlock should work
    assert gm.unlock_buff("LevelGuild", "bonus_hp", 50, required_level=2) == True
    assert gm.unlock_hq_feature("LevelGuild", "cosmetics", "gold_trim", 50, required_level=2) == True

    hq_status = gm.get_hq_status("LevelGuild")
    assert "gold_trim" in hq_status["cosmetics"]

def test_guild_emblem(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("EmblemGuild", "player1")

    guild = gm.get_guild("EmblemGuild")
    # Verify initial emblem and parts
    assert guild["emblem"] == {"shape": "circle", "color": "white", "symbol": "none"}
    assert guild["unlocked_emblem_parts"] == {"shapes": ["circle"], "colors": ["white"], "symbols": ["none"]}

    # Give resources
    gm.donate_resources("EmblemGuild", 1000)

    # Unlock some parts
    assert gm.unlock_emblem_part("EmblemGuild", "shapes", "shield", 100) == True
    assert gm.unlock_emblem_part("EmblemGuild", "colors", "red", 50) == True
    assert gm.unlock_emblem_part("EmblemGuild", "symbols", "sword", 150) == True

    # Try unlocking the same part
    assert gm.unlock_emblem_part("EmblemGuild", "shapes", "shield", 100) == False

    # Try unlocking with insufficient resources
    gm.get_guild("EmblemGuild")["resources"] = 0
    assert gm.unlock_emblem_part("EmblemGuild", "colors", "blue", 50) == False

    # Try updating with unowned parts
    assert gm.update_emblem("EmblemGuild", "shield", "blue", "sword") == False

    # Try updating with owned parts
    assert gm.update_emblem("EmblemGuild", "shield", "red", "sword") == True

    # Verify updated emblem
    guild = gm.get_guild("EmblemGuild")
    assert guild["emblem"] == {"shape": "shield", "color": "red", "symbol": "sword"}


def test_guild_tournament(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("ChampGuild", "p1")
    gm.create_guild("RunnerUpGuild", "p2")
    gm.create_guild("Top10Guild", "p3")
    gm.create_guild("LoserGuild", "p4")

    assert gm.register_for_tournament("ChampGuild", "tourney_1") == True
    assert gm.register_for_tournament("RunnerUpGuild", "tourney_1") == True
    assert gm.register_for_tournament("Top10Guild", "tourney_1") == True
    assert gm.register_for_tournament("LoserGuild", "tourney_1") == True

    rankings = [
        {"guild_name": "ChampGuild", "rank": 1},
        {"guild_name": "RunnerUpGuild", "rank": 2},
        {"guild_name": "Top10Guild", "rank": 5},
        {"guild_name": "LoserGuild", "rank": 20}
    ]

    assert gm.process_tournament_results("tourney_1", rankings) == True

    champ = gm.get_guild("ChampGuild")
    assert "Tournament Champion" in champ["titles"]
    assert "Champion Aura" in champ["cosmetic_auras"]
    assert champ["prestige_pool"] == 10000

    runner = gm.get_guild("RunnerUpGuild")
    assert "Tournament Finalist" in runner["titles"]
    assert runner["prestige_pool"] == 5000

    top10 = gm.get_guild("Top10Guild")
    assert top10["prestige_pool"] == 1000

    loser = gm.get_guild("LoserGuild")
    assert loser.get("prestige_pool", 0) == 0

def test_hq_currency(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("CurrencyGuild", "player1")

    # Give resources and guild_xp
    gm.donate_resources("CurrencyGuild", 500)

    gm.create_guild("OtherGuild", "player2")
    # Try unlocking with guild_xp (should fail due to 0 xp)
    assert gm.unlock_hq_feature("CurrencyGuild", "flags", "jolly_roger", 100, currency="guild_xp") == False

    # Give guild XP
    gm.record_gvg_match("CurrencyGuild", "OtherGuild", "CurrencyGuild") # +50 XP
    gm.record_gvg_match("CurrencyGuild", "OtherGuild", "CurrencyGuild") # +50 XP

    assert gm.get_guild("CurrencyGuild")["guild_xp"] == 100

    # Unlock with guild_xp
    assert gm.unlock_hq_feature("CurrencyGuild", "flags", "jolly_roger", 100, currency="guild_xp") == True

    # XP should be 0 now
    assert gm.get_guild("CurrencyGuild")["guild_xp"] == 0

    # Resources should still be 500
    assert gm.get_guild("CurrencyGuild")["resources"] == 500

    # HQ status should have flag
    hq_status = gm.get_hq_status("CurrencyGuild")
    assert "jolly_roger" in hq_status["flags"]

def test_hq_defenses(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("DefenseGuild", "p1")

    # Add resources
    guild = gm.get_guild("DefenseGuild")
    guild["resources"] = 1000
    gm.save()

    assert gm.build_hq_defense("DefenseGuild", "turret", 200, 2) == True
    assert gm.build_hq_defense("DefenseGuild", "barricade", 100, 5) == True

    # Check resources
    guild = gm.get_guild("DefenseGuild")
    assert guild["resources"] == 700

    defenses = gm.get_hq_defenses("DefenseGuild")
    assert defenses["turret"] == 2
    assert defenses["barricade"] == 5

    hq_status = gm.get_hq_status("DefenseGuild")
    assert "turret" in hq_status["defenses"]

def test_siege_mechanics(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("AttackerGuild", "p1")
    gm.create_guild("DefenderGuild", "p2")

    attacker = gm.get_guild("AttackerGuild")
    defender = gm.get_guild("DefenderGuild")

    attacker["resources"] = 100
    defender["resources"] = 500
    defender["guild_xp"] = 100
    gm.save()

    # Break defense
    stolen = gm.record_siege_defense_broken("AttackerGuild", "DefenderGuild", 200)
    assert stolen == 200

    attacker = gm.get_guild("AttackerGuild")
    defender = gm.get_guild("DefenderGuild")
    assert attacker["resources"] == 300
    assert defender["resources"] == 300

    # Break again, more than available
    stolen2 = gm.record_siege_defense_broken("AttackerGuild", "DefenderGuild", 400)
    assert stolen2 == 300

    attacker = gm.get_guild("AttackerGuild")
    defender = gm.get_guild("DefenderGuild")
    assert attacker["resources"] == 600
    assert defender["resources"] == 0

    # Hold siege
    assert gm.record_siege_held("DefenderGuild", 50) == True
    defender = gm.get_guild("DefenderGuild")
    assert defender["guild_xp"] == 150

def test_guild_perk_currency_and_level(temp_guild_file):
    gm = GuildManager(temp_guild_file)
    gm.create_guild("AdvancedGuild", "p1")
    guild = gm.get_guild("AdvancedGuild")
    guild["gvg_points"] = 100
    guild["guild_xp"] = 100
    guild["resources"] = 500

    # Try unlocking with level requirement (fails, currently level 1)
    assert gm.unlock_perk("AdvancedGuild", "hp_5_percent", 50, required_level=2) == False

    # Upgrade level
    gm.upgrade_guild_level("AdvancedGuild", 0) # cost=0 for gvg_points to save points for perk test
    assert guild["level"] == 2

    # Try unlocking again (success)
    assert gm.unlock_perk("AdvancedGuild", "hp_5_percent", 50, required_level=2) == True
    assert guild["guild_xp"] == 50

    # Unlock with gvg_points
    assert gm.unlock_perk("AdvancedGuild", "hp_10_percent", 50, required_perk="hp_5_percent", required_level=2, currency="gvg_points") == True
    assert guild["gvg_points"] == 50
    assert "hp_10_percent" in gm.get_guild_perks("AdvancedGuild")
