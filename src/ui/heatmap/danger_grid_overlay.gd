extends ColorRect

var danger_grid: Dictionary = {}

func update_danger_grid(grid: Dictionary):
    danger_grid = grid

    if material and material is ShaderMaterial:
        var positions = PackedVector2Array()
        var values = PackedFloat32Array()

        var i = 0
        var max_danger = 1.0
        for key in danger_grid:
            if i >= 400: # shader array limit
                break
            var val = danger_grid[key]
            if val > 0.0:
                if val > max_danger:
                    max_danger = val

                var vx = 0.0
                var vy = 0.0
                if typeof(key) == TYPE_STRING:
                    var parts = key.split(",")
                    if parts.size() == 2:
                        vx = float(parts[0])
                        vy = float(parts[1])
                elif typeof(key) == TYPE_VECTOR2:
                    vx = key.x
                    vy = key.y
                elif typeof(key) == TYPE_ARRAY and key.size() >= 2:
                    vx = key[0]
                    vy = key[1]

                # Grid indices are scaled by 100 to world coordinates
                positions.append(Vector2(vx, vy) * 100.0 + Vector2(50.0, 50.0))
                values.append(val)
                i += 1

        material.set_shader_parameter("point_count", positions.size())
        material.set_shader_parameter("points", positions)
        material.set_shader_parameter("danger_values", values)
        material.set_shader_parameter("max_danger", max_danger)

func _ready():
    var shader = Shader.new()
    shader.code = """
    shader_type canvas_item;

    uniform int point_count = 0;
    uniform vec2 points[400];
    uniform float danger_values[400];
    uniform float max_danger = 1.0;

    void fragment() {
        vec2 uv_pos = UV * vec2(1920.0, 1080.0);

        float local_danger = 0.0;

        for (int i = 0; i < min(point_count, 400); i++) {
            float dist = distance(uv_pos, points[i]);
            if (dist < 150.0) {
                float intensity = 1.0 - (dist / 150.0);
                local_danger += danger_values[i] * intensity;
            }
        }

        if (local_danger <= 0.01) {
            // Safe zone: slight green tint
            COLOR = vec4(0.0, 1.0, 0.0, 0.1);
        } else {
            float normalized = clamp(local_danger / max_danger, 0.0, 1.0);
            float pulse = (sin(TIME * 5.0) * 0.3) + 0.7; // Pulse between 0.4 and 1.0
            vec4 danger_color = vec4(1.0, 0.0, 0.0, 0.6 * pulse); // Red
            vec4 intermediate_color = vec4(1.0, 1.0, 0.0, 0.3); // Yellow for mid danger

            if (normalized < 0.5) {
                COLOR = mix(vec4(0.0, 1.0, 0.0, 0.1), intermediate_color, normalized * 2.0);
            } else {
                COLOR = mix(intermediate_color, danger_color, (normalized - 0.5) * 2.0);
            }
        }
    }
    """
    var mat = ShaderMaterial.new()
    mat.shader = shader
    self.material = mat
