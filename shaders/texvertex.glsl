#version 410 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec2 vertexTexCoord;
layout (location=2) in vec3 vertexNormal;
layout (location=3) in vec3 objectPos;

uniform mat4 model;
// uniform mat4 view;
uniform mat4 projection;

out vec2 fragmentTexCoord;
out vec3 fragmentPosition;
out vec3 fragmentNormal;

void main()
{
    gl_Position = projection * model * vec4(vertexPos, 1.0);
    fragmentTexCoord = vertexTexCoord;
    fragmentPosition = (model * vec4(vertexPos, 1.0)).xyz;
    // fragmentPosition = objectPos;
    fragmentNormal = mat3(model) * vertexNormal;
}