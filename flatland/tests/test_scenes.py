import flatland.playgrounds.playground as playground

import matplotlib.pyplot as plt


def display(img):
    plt.imshow(img)
    plt.axis('off')
    plt.show()

#
# ####################################################
# # Basic Empty playgound with different layouts
#
# ### Empty Squared
# pg_params = {
#     'playground_type': 'basic_empty',
#     'scene': {
#         'scene_type': 'room',
#         'scene_shape': [200, 200]
#     }
# }
#
#
# pg = playground.PlaygroundGenerator.create(pg_params)
# img = pg.generate_playground_image()
# display(img)
#
# ### Empty Rect
#
# pg_params = {
#     'playground_type': 'basic_empty',
#     'scene': {
#         'room_shape': [200, 400]
#     }
# }
#
#
# pg = playground.PlaygroundGenerator.create(pg_params)
# img = pg.generate_playground_image()
# display(img)
#
# ### Empty Linear rooms
#
# pg_params = {
#     'playground_type': 'basic_empty',
#     'scene': {
#         'scene_type': 'linear_rooms',
#         'doorstep_type' : 'random',
#         'doorstep_size' : 50,
#         'number_rooms' : 10,
#         'room_shape': [200, 100]
#     }
# }
#

# pg = playground.PlaygroundGenerator.create(pg_params)
# img = pg.generate_playground_image()
# display(img)


pg_params = {
    'playground_type': 'basic_empty',
    'scene': {
        'scene_type': 'sketch_scene',
        'doorstep_size' : 30,
        'unit_size' : 100,
        'layout':"""
        ##########
        #        #
        #    #   #
        ##########
        """

    }
}
pg = playground.PlaygroundGenerator.create(pg_params)
img = pg.generate_playground_image()
display(img)

