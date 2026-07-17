class_name FrictionlessModifierMode
extends GameModes.GameMode

var frictionless_active: bool = false
var timer: float = 0.0
var event_message_sent: bool = false
var rng: RandomNumberGenerator

func _init() -> void:
    super()
    name = "Frictionless Arena Modifier"
    description = "Introduces an arena modifier that completely removes friction for a random duration, forcing players to perfectly balance their momentum and making collisions much more impactful and chaotic."
    rng = RandomNumberGenerator.new()
    rng.randomize()
    frictionless_active = false
    timer = rng.randf_range(10.0, 30.0)
    event_message_sent = false

func setup(world, balls: Array) -> void:
    super.setup(world, balls)
    frictionless_active = false
    timer = rng.randf_range(10.0, 30.0)
    event_message_sent = true

func tick(world, balls: Array, delta: float = 0.016) -> void:
    super.tick(world, balls, delta)
    timer -= delta

    if timer <= 0:
        frictionless_active = not frictionless_active
        event_message_sent = false
        if frictionless_active:
            timer = rng.randf_range(5.0, 15.0)
        else:
            timer = rng.randf_range(10.0, 30.0)

    if frictionless_active:
        if not event_message_sent:
            if world.has_method("add_event"):
                world.add_event("frictionless_modifier", {"message": "The arena is now completely frictionless! Balance your momentum!"})
            event_message_sent = true

        for b in balls:
            var is_alive = false
            if typeof(b) == TYPE_DICTIONARY:
                is_alive = b.get("alive", false)
            else:
                is_alive = b.get("alive") if "alive" in b else false

            if is_alive:
                if typeof(b) == TYPE_DICTIONARY:
                    b["is_frictionless"] = true
                elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
                    b.set_meta("is_frictionless", true)
                    if "is_frictionless" in b:
                        b.is_frictionless = true
    else:
        if not event_message_sent:
            if world.has_method("add_event"):
                world.add_event("frictionless_modifier", {"message": "Friction has returned to normal."})
            event_message_sent = true

        for b in balls:
            var is_alive = false
            if typeof(b) == TYPE_DICTIONARY:
                is_alive = b.get("alive", false)
            else:
                is_alive = b.get("alive") if "alive" in b else false

            if is_alive:
                if typeof(b) == TYPE_DICTIONARY:
                    b["is_frictionless"] = false
                elif typeof(b) == TYPE_OBJECT and b.has_method("set_meta"):
                    b.set_meta("is_frictionless", false)
                    if "is_frictionless" in b:
                        b.is_frictionless = false
