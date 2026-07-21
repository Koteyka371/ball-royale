extends Node

class_name BountyIndicatorUI

var screen_width: float
var screen_height: float
var active_indicators: Array = []

func _init(w: float = 800.0, h: float = 600.0):
    screen_width = w
    screen_height = h

func update(events: Array, local_player_id = null) -> void:
    active_indicators.clear()

    for event in events:
        if typeof(event) == TYPE_DICTIONARY and event.has("type") and event["type"] == "minimap_ping":
            var data = event.get("data", {})
            active_indicators.append({
                "target_x": float(data.get("x", 0.0)),
                "target_y": float(data.get("y", 0.0)),
                "radius": float(data.get("radius", 0.0)),
                "is_minimap_ping": true,
                "color": "yellow" if data.get("type") == "safe_zone" else "white"
            })
        elif typeof(event) == TYPE_DICTIONARY and event.has("type") and (event["type"] == "bounty_compass" or event["type"] == "nemesis_compass"):
            var data = event.get("data", {})
            var owner_id = data.get("owner_id")

            if local_player_id == null or owner_id == local_player_id:
                active_indicators.append({
                    "target_x": float(data.get("target_x", 0.0)),
                    "target_y": float(data.get("target_y", 0.0)),
                    "owner_id": owner_id,
                    "is_nemesis": event["type"] == "nemesis_compass"
                })

func get_render_data(camera_x: float, camera_y: float, zoom: float) -> Array:
    var render_data = []
    var center_x = screen_width / 2.0
    var center_y = screen_height / 2.0

    for indicator in active_indicators:
        var dx = indicator["target_x"] - camera_x
        var dy = indicator["target_y"] - camera_y

        var dist_sq = dx * dx + dy * dy

        var half_w = (screen_width / 2.0) / zoom
        var half_h = (screen_height / 2.0) / zoom

        if abs(dx) > half_w or abs(dy) > half_h:
            var dist = sqrt(dist_sq)
            if dist > 0:
                var nx = dx / dist
                var ny = dy / dist

                var margin = 30.0

                var screen_dx = center_x - margin
                var screen_dy = center_y - margin

                var t_x = INF if nx == 0 else abs(screen_dx / nx)
                var t_y = INF if ny == 0 else abs(screen_dy / ny)

                var t = min(t_x, t_y)

                var indicator_x = center_x + nx * t
                var indicator_y = center_y + ny * t

                var angle = atan2(ny, nx)

                if indicator.get("is_nemesis", false):
                    render_data.append({
                        "type": "nemesis_pointer",
                        "x": indicator_x,
                        "y": indicator_y,
                        "angle": angle,
                        "color": "purple"
                    })
                elif indicator.get("is_minimap_ping", false):
                    render_data.append({
                        "type": "minimap_ping",
                        "x": indicator["target_x"],
                        "y": indicator["target_y"],
                        "radius": indicator.get("radius", 50.0),
                        "color": indicator.get("color", "yellow")
                    })
                else:
                    render_data.append({
                        "type": "bounty_pointer",
                        "x": indicator_x,
                        "y": indicator_y,
                        "angle": angle,
                        "color": "orange"
                    })
        elif indicator.get("is_minimap_ping", false):
            render_data.append({
                "type": "minimap_ping",
                "x": indicator["target_x"],
                "y": indicator["target_y"],
                "radius": indicator.get("radius", 50.0),
                "color": indicator.get("color", "yellow")
            })

    return render_data
