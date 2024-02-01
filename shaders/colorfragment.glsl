#version 330 core

// in vec2 fragmentTexCoord;

in vec3 fragmentColor;

//uniform sampler2D imageTexture;

out vec4 color;

void main()
{
    color = vec4(fragmentColor, 1.0);
}