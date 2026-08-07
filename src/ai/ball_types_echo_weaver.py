class EchoWeaver:
    """
    Echo Weaver ball uses the echo_rewind skill to record its state and rewind back to it.
    """
    SKILL = "echo_rewind"
    SKILL_COOLDOWN = 12.0

    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.base_speed = 3.5
        self.max_hp = 100.0
        self.hp = self.max_hp
        self.damage = 10.0
        self.radius = 15.0

        self.team = "echo_weaver"
        self.kind = "player"
        self.alive = True

        self.color = "light_blue"
        self.skill = self.SKILL
        self.skill_timer = 0.0

        # Skill specific state
        self.is_echo_recording = False
        self.echo_rewind_timer = 0.0
        self.echo_rewind_state = {}

    def tick(self, world, balls, delta):
        if self.skill_timer > 0:
            self.skill_timer -= delta

    def use_skill(self) -> bool:
        if self.skill_timer <= 0:
            if not self.is_echo_recording:
                # Start recording, small cooldown before we can activate again
                self.skill_timer = 0.5
            else:
                # Used rewind, go on full cooldown
                self.skill_timer = self.SKILL_COOLDOWN
            return True
        return False
