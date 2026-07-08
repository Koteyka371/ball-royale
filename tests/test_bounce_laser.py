import unittest
from arena.procedural_arena import ProceduralArena, Hazard

class TestBounceLaser(unittest.TestCase):
    def test_bounce_laser_movement_and_bounce(self):
        arena = ProceduralArena(arena_size=2000.0)
        # Create a hazard near the top left boundary to test bounce quickly
        laser = Hazard(id=1, x=10.0, y=10.0, radius=20.0, kind="bounce_laser", damage=25.0)
        # Explicitly set velocity towards the boundaries
        laser.vx = -100.0
        laser.vy = -100.0
        arena.hazards.append(laser)

        # update_zone ticks hazards
        arena.update_zone(current_tick=0, delta=1.0)

        # x and y should be updated.
        # old x = 10, vx = -100, delta = 1
        # new x would be 10 - 100 = -90. This is < 0, so x should be bounded and vx reversed.
        # Since it bounded below radius, the logic is: if x - radius < 0 -> x = radius (20.0)
        self.assertEqual(laser.x, 20.0)
        self.assertEqual(laser.y, 20.0)

        # Velocity should be reversed due to abs() logic in bounding
        self.assertEqual(laser.vx, 100.0)
        self.assertEqual(laser.vy, 100.0)

        # Move forward, should now increase
        arena.update_zone(current_tick=1, delta=1.0)
        self.assertEqual(laser.x, 120.0)
        self.assertEqual(laser.y, 120.0)

if __name__ == '__main__':
    unittest.main()
