
class ConcaveMovable(PhysicalEntity):

    def __init__(self, playground, initial_coordinates, radius, width, **kwargs):

        img = np.zeros((2*radius + 2*width +1, 2*radius + 2*width+1, 4))
        rr, cc = circle_perimeter(radius+width, radius+width, radius)
        img[rr, cc] = 1.0

        rr, cc = polygon( np.array([0, 0, radius+width]), np.array([0, 2*radius+2*width, radius+width]) )
        img[rr, cc] = 0.0

        for _ in range(int((width)/2)):
            img = binary_dilation(img)
        
        pil_img = Image.fromarray(np.uint8(img*255)).convert('RGBA')
        texture = arcade.Texture(name='U_'+ str(radius), image=pil_img)

        super().__init__(playground, initial_coordinates, mass=10, radius = radius,
                         texture=texture, **kwargs)
        
    def _set_pm_collision_type(self):
        pass


class Cross(PhysicalEntity):

    def __init__(self, playground, initial_coordinates, radius, width, **kwargs):

        img = np.zeros((2*radius + 2*width +1, 2*radius + 2*width+1, 4))
       
        rr, cc = line_nd( (width, radius+width), (2*radius+width, radius+width))
        img[rr, cc, :] = 1

        rr, cc = line_nd( (radius+width, width), (radius+width, 2*radius + width))
        img[rr, cc, :] = 1

        for _ in range(int((width)/2)):
            img = binary_dilation(img)

        pil_img = Image.fromarray(np.uint8(img*255)).convert('RGBA')
        texture = arcade.Texture(name='U_'+ str(radius), image=pil_img, hit_box_algorithm='Detailed', hit_box_detail=0.2)

        super().__init__(playground, initial_coordinates, mass=10, radius = radius,
                         texture=texture, **kwargs)
        
    def _set_pm_collision_type(self):
        pass


