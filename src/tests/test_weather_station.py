def test_weather_station_capture_and_effects():
    from ai.game_modes import CaptureableWeatherStation

    mode = CaptureableWeatherStation()
    world = type('World', (), {'balls': [], 'arena': type('Arena', (), {'width': 1000, 'height': 1000}), 'weather_stations': [], 'next_id': 9999, 'hazards': []})()
    ball1 = type('Ball', (), {'id': 1, 'x': 250, 'y': 250, 'team': 'red', 'hp': 100, 'max_hp': 100, 'base_speed': 100, 'speed': 100, 'base_damage_multiplier': 1.0, 'damage_multiplier': 1.0, 'alive': True, 'ball_type': 'basic', 'vx': 0.0, 'vy': 0.0, 'radius': 10.0, 'suspended_projectiles': [], 'state_history': [], 'last_teleport_tick': -100})()
    ball2 = type('Ball', (), {'id': 2, 'x': 250, 'y': 250, 'team': 'blue', 'hp': 100, 'max_hp': 100, 'base_speed': 100, 'speed': 100, 'base_damage_multiplier': 1.0, 'damage_multiplier': 1.0, 'alive': True, 'ball_type': 'basic', 'vx': 0.0, 'vy': 0.0, 'radius': 10.0, 'suspended_projectiles': [], 'state_history': [], 'last_teleport_tick': -100})()
    world.balls = [ball1, ball2]

    mode.setup(world, world.balls)
    assert len(world.weather_stations) == 4

    # Move station 0 to balls
    world.weather_stations[0].x = 250
    world.weather_stations[0].y = 250

    # tick to capture by red
    ball2.x = 900 # Move away
    for _ in range(100):
        mode.tick(world, world.balls, 0.1)

    assert world.weather_stations[0].owner_team == 'red'
    assert world.weather_stations[0].capture_progress == 100.0

    # Check effects
    ball2.x = 250 # move back
    for _ in range(10):
        mode.tick(world, world.balls, 0.1)

    assert ball1.speed > 100 # buff
    assert ball2.speed < 100 # debuff
