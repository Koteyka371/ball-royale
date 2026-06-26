extends ColorRect

var death_coordinates: Array = []
var max_deaths_per_pixel: float = 1.0

func update_heatmap(coords: Array):
    death_coordinates = coords
    max_deaths_per_pixel = max(1.0, float(coords.size()) * 0.1) # Simple normalization

    if material and material is ShaderMaterial:
        # Pass coordinates to shader.
        # In Godot 4, we usually use uniform arrays, but for unlimited size,
        # drawing to a texture or passing a packed vector array is better.
        # Since this is a mock representation according to task constraints,
        # we can just set an array or a point count.
        var positions = PackedVector2Array()
        for c in coords:
            positions.append(Vector2(c.get("x", 0), c.get("y", 0)))

        # Shader needs to be set up to handle this data.
        # For simplicity, we just set a property that our mock shader would use.
        material.set_shader_parameter("point_count", positions.size())
        material.set_shader_parameter("points", positions)
        material.set_shader_parameter("max_density", max_deaths_per_pixel)

func _ready():
    # Setup shader
    var shader = Shader.new()
    shader.code = """
    shader_type canvas_item;

    uniform int point_count = 0;
    uniform vec2 points[100]; // Fixed size for simplicity in this example
    uniform float max_density = 1.0;

    void fragment() {
        float density = 0.0;
        vec2 uv_pos = UV * vec2(1920.0, 1080.0); // Assuming screen size

        for (int i = 0; i < min(point_count, 100); i++) {
            float dist = distance(uv_pos, points[i]);
            if (dist < 50.0) {
                density += 1.0 - (dist / 50.0);
            }
        }

        float normalized_density = clamp(density / max_density, 0.0, 1.0);

        // Heatmap colors: Blue -> Green -> Red
        vec4 color = vec4(0.0, 0.0, 0.0, 0.0);
        if (normalized_density > 0.0) {
            if (normalized_density < 0.5) {
                color = mix(vec4(0,0,1,0.5), vec4(0,1,0,0.5), normalized_density * 2.0);
            } else {
                color = mix(vec4(0,1,0,0.5), vec4(1,0,0,0.8), (normalized_density - 0.5) * 2.0);
            }
        }

        COLOR = color;
    }
    """

    var mat = ShaderMaterial.new()
    mat.shader = shader
    self.material = mat
