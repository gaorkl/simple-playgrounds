#version 330
uniform vec2 pos;
uniform float angle;
in vec2 in_vert;
    in vec2 in_uv;
    out vec3 uv;
    void main() {
	gl_Position = vec4(in_vert, 0.0, 1.0);
	mat3 trans = mat3(
	    1.0, 0.0, 0.0,
	    0.0, 1.0, 0.0,
	    pos.x, pos.y, 1.0
	);
	float s = 1;
	mat3 scale = mat3(
	    s, 0.0, 0.0,
	    0.0, s, 0.0,
	    0.0, 0.0, s
	);
	mat3 rot = mat3(
	    cos(angle), -sin(angle), 0.0,
	    sin(angle),  cos(angle), 0.0,
	    0.0, 0.0, 1.0
	);
// uv = trans * rot * scale * vec3(in_uv - vec2(0.5), 1.0) + vec3(0.5);
uv = scale* rot* trans * vec3(in_uv - vec2(0.5, 0.5), 1.0) + vec3(0.5, 0.5, 0) ;
}

