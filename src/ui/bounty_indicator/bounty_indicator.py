from typing import List, Dict, Any, Optional

class BountyIndicatorUI:
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active_indicators: List[Dict[str, Any]] = []

    def update(self, events: List[Dict[str, Any]], local_player_id: Optional[int] = None) -> None:
        self.active_indicators.clear()

        for event in events:
            if event.get("type") == "minimap_ping":
                data = event.get("data", {})
                self.active_indicators.append({
                    "target_x": float(data.get("x", 0.0)),
                    "target_y": float(data.get("y", 0.0)),
                    "radius": float(data.get("radius", 0.0)),
                    "is_minimap_ping": True,
                    "color": "yellow" if data.get("type") == "safe_zone" else "white"
                })
            elif event.get("type") in ("bounty_compass", "nemesis_compass"):
                data = event.get("data", {})
                owner_id = data.get("owner_id")

                # Only show indicator if the current player is the bounty hunter,
                # or if we're spectating (no local player)
                if local_player_id is None or owner_id == local_player_id:
                    self.active_indicators.append({
                        "target_x": data.get("target_x", 0.0),
                        "target_y": data.get("target_y", 0.0),
                        "owner_id": owner_id,
                        "is_nemesis": event.get("type") == "nemesis_compass"
                    })

            elif event.get("type") == "sniper_nest_indicator":
                data = event.get("data", {})
                self.active_indicators.append({
                    "target_x": data.get("target_x", 0.0),
                    "target_y": data.get("target_y", 0.0),
                    "owner_id": None, # Always show
                    "is_sniper": True
                })



    def get_render_data(self, camera_x: float, camera_y: float, zoom: float) -> List[Dict[str, Any]]:
        render_data = []
        center_x = self.screen_width / 2
        center_y = self.screen_height / 2

        for indicator in self.active_indicators:
            # Calculate vector from camera to target
            dx = indicator["target_x"] - camera_x
            dy = indicator["target_y"] - camera_y

            # Distance squared
            dist_sq = dx * dx + dy * dy

            # If within screen bounds (roughly), we don't need a border indicator
            # We'll use a simple bounding box check
            half_w = (self.screen_width / 2) / zoom
            half_h = (self.screen_height / 2) / zoom

            # Check if target is outside current camera view
            if abs(dx) > half_w or abs(dy) > half_h:
                # Calculate intersection with screen border
                # We need to find the point on the screen edge pointing towards the target

                # Normalize vector
                import math
                dist = math.sqrt(dist_sq)
                if dist > 0:
                    nx = dx / dist
                    ny = dy / dist

                    # We want to place the indicator on the edge of the screen, slightly inset
                    margin = 30

                    # Find which edge it intersects
                    # t_x is the multiplier to reach left/right edge
                    # t_y is the multiplier to reach top/bottom edge

                    screen_dx = center_x - margin
                    screen_dy = center_y - margin

                    t_x = float('inf') if nx == 0 else abs(screen_dx / nx)
                    t_y = float('inf') if ny == 0 else abs(screen_dy / ny)

                    t = min(t_x, t_y)

                    # Calculate final screen position
                    indicator_x = center_x + nx * t
                    indicator_y = center_y + ny * t

                    # Calculate angle for rotation (pointing towards target)
                    angle = math.atan2(ny, nx)

                    if indicator.get("is_sniper"):
                        render_data.append({
                            "type": "sniper_indicator",
                            "x": indicator_x,
                            "y": indicator_y,
                            "angle": angle,
                            "color": "red"
                        })
                    elif indicator.get("is_nemesis"):
                        render_data.append({
                            "type": "nemesis_pointer",
                            "x": indicator_x,
                            "y": indicator_y,
                            "angle": angle,
                            "color": "purple"
                        })
                    elif indicator.get("is_minimap_ping"):
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
            elif indicator.get("is_minimap_ping"):
                render_data.append({
                    "type": "minimap_ping",
                    "x": indicator["target_x"],
                    "y": indicator["target_y"],
                    "radius": indicator.get("radius", 50.0),
                    "color": indicator.get("color", "yellow")
                })

        return render_data
