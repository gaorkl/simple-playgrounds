            # version 440

            layout(local_size_x=MAX_N_RAYS) in;

            struct HitPoint
            {
                // Position of hitpoint on view
                float view_pos_x;
                float view_pos_y;

                // Position of hitpoint in env
                float env_pos_x;
                float env_pos_y;

                // Position of hitpoint relative to sensor
                float rel_pos_x;
                float rel_pos_y;

                // Position of sensor on view
                float sensor_x_on_view;
                float sensor_y_on_view;

                float id;
                float dist;

                float r;
                float g;
                float b;
            };

            uniform sampler2D color_texture;

            layout(std430, binding = 4) buffer hit_points
            {
                HitPoint hpts[];
            } In;

            void main() {

                int i_ray = int(gl_LocalInvocationIndex);
                int i_sensor = int(gl_WorkGroupID);


                HitPoint hit_pt = In.hpts[i_ray + i_sensor*MAX_N_RAYS] ;

                float x = hit_pt.view_pos_x;
                float y = hit_pt.view_pos_y;

                ivec2 pos = ivec2(x, y);

                float id = int(hit_pt.id);

                vec4 color_out = vec4(0,0,0,0);
                if (id != 0)
                {
                color_out = texelFetch(color_texture, pos, 0);
                }

                hit_pt.r = color_out.x*255;
                hit_pt.g = color_out.y*255;
                hit_pt.b = color_out.z*255;

                In.hpts[i_ray + i_sensor*MAX_N_RAYS] = hit_pt;

            }

