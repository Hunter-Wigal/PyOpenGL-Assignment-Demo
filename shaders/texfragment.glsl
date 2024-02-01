#version 410 core

struct PointLight {
    vec3 position;
    vec3 color;
    float strength;
    float enabled;
};

in vec2 fragmentTexCoord;
in vec3 fragmentPosition;
in vec3 fragmentNormal;

uniform sampler2D imageTexture;
uniform PointLight Sun;
uniform PointLight[10] Lights;
uniform vec3 cameraPosition;

// Fog parameters, could make them uniforms and pass them into the fragment shader
// float fog_maxdist = 4.0;
// float fog_mindist = 0.1;
// vec4  fog_colour = vec4(0.4, 0.4, 0.4, 1.0);

out vec4 color;


void main()
{
    vec4 textColor = texture(imageTexture, fragmentTexCoord);

    struct PointLight currLight = Lights[0];
    float dist = distance(currLight.position, fragmentPosition);
    for(int i=1; i<3; i++){
        float newDist = distance(Lights[i].position, fragmentPosition);
        if(newDist < dist && Lights[i].enabled == 1){
            currLight = Lights[i];
            dist = newDist;
        }
    }

    float modifier = 1;
    if(currLight.enabled == 1){
        if(distance(currLight.position, fragmentPosition) < 10){
            modifier = 1/Sun.strength;
        }
    }


    color = textColor * Sun.strength * modifier;
}

