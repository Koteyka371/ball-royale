import math

class GhostCompanion:
    def __init__(self, owner_id, team, x, y):
        self.owner_id = owner_id
        self.team = team
        self.x = x
        self.y = y
        self.target_id = None
        self.speed = 150.0
        self.attach_radius = 30.0
        self.heal_rate = 5.0
        self.damage_rate = 5.0

    def update(self, delta, world):
        balls = getattr(world, 'balls', [])
        if not balls:
            return

        if self.target_id is not None:
            target = next((b for b in balls if getattr(b, 'id', -1) == self.target_id and getattr(b, 'alive', False)), None)
            if target:
                self.x = getattr(target, 'x', self.x)
                self.y = getattr(target, 'y', self.y)

                target_team = getattr(target, 'team', getattr(target, 'ball_type', ''))
                if target_team == self.team:
                    if hasattr(target, 'hp') and hasattr(target, 'max_hp'):
                        target.hp = min(getattr(target, 'max_hp', 100), getattr(target, 'hp', 0) + self.heal_rate * delta)
                else:
                    if hasattr(target, 'hp'):
                        target.hp -= self.damage_rate * delta
            else:
                self.target_id = None
        else:
            closest_dist = float('inf')
            closest_ball = None
            for b in balls:
                if not getattr(b, 'alive', False):
                    continue
                bx = getattr(b, 'x', 0)
                by = getattr(b, 'y', 0)
                dist = math.hypot(bx - self.x, by - self.y)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_ball = b

            if closest_ball:
                bx = getattr(closest_ball, 'x', 0)
                by = getattr(closest_ball, 'y', 0)
                if closest_dist <= self.attach_radius:
                    self.target_id = getattr(closest_ball, 'id', -1)
                else:
                    dx = bx - self.x
                    dy = by - self.y
                    length = math.hypot(dx, dy)
                    if length > 0:
                        self.x += (dx / length) * self.speed * delta
                        self.y += (dy / length) * self.speed * delta


    def to_dict(self):
        return {
            "type": "ghost_companion",
            "owner_id": self.owner_id,
            "team": self.team,
            "x": self.x,
            "y": self.y,
            "target_id": self.target_id,
            "radius": 15.0,
            "color": "white" if self.team == "blue" else "gray"
        }

class GhostCompanionManager:
    def __init__(self):
        self.ghosts = []
        self.processed_deaths = set()

    def update(self, delta, world):
        balls = getattr(world, 'balls', [])

        for b in balls:
            b_id = getattr(b, 'id', -1)
            is_alive = getattr(b, 'alive', True)
            if not is_alive and b_id not in self.processed_deaths:
                self.processed_deaths.add(b_id)
                team = getattr(b, 'team', getattr(b, 'ball_type', ''))
                x = getattr(b, 'x', 0)
                y = getattr(b, 'y', 0)
                ghost = GhostCompanion(b_id, team, x, y)
                self.ghosts.append(ghost)
                if not hasattr(world, 'entities'):
                    world.entities = []
                if hasattr(world, 'entities'):
                    world.entities.append(ghost)

        for ghost in self.ghosts:
            ghost.update(delta, world)
