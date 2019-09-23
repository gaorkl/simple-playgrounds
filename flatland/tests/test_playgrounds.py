import flatland.playgrounds.playground as playground

import matplotlib.pyplot as plt

from flatland.default_parameters.entities import *

def display(img):
    plt.imshow(img)
    plt.axis('off')
    plt.show()


####################################################
# Selecting different scene_layouts for a basic playground

pg = playground.PlaygroundGenerator.create('basic')
img = pg.generate_playground_image()
display(img)

pg_params = {
    'scene': {
        'shape': [600, 200],
        'scene_type': 'rooms_2'
    }
}

pg = playground.PlaygroundGenerator.create('basic', pg_params)
img = pg.generate_playground_image()
display(img)

####################################################
# Selecting different Playgrounds

pg = playground.PlaygroundGenerator.create('rooms_2_edible')
img = pg.generate_playground_image()
display(img)

# Changing default shape
pg_params = {
    'scene': {
        'shape': [600, 200],
    }
}
pg = playground.PlaygroundGenerator.create('rooms_2_edible', pg_params )
img = pg.generate_playground_image()
display(img)


#####################################################
# Adding entities

new_entity = basic_default.copy()
new_entity['position'] = [50, 50, 0]

pg_params = {
    'scene': {
        'shape': [600, 200]
    },
    'entities': [new_entity]
}
pg = playground.PlaygroundGenerator.create('rooms_2_edible', pg_params )
# img = pg.generate_playground_image()
# display(img)

new_entity = basic_default.copy()
new_entity['position'] = [50, 50, 0.2]
new_entity['physical_shape'] = 'box'
new_entity['size_box'] = [30, 60]

pg_params = {
    'scene': {
        'shape': [600, 200]
    },
    'entities': [new_entity]
}

pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
#img = pg.generate_playground_image()
#display(img)

new_entity = basic_default.copy()
new_entity['position'] = [50, 50, 0.2]
new_entity['physical_shape'] = 'triangle'
new_entity['radius'] = 30

pg_params = {
    'scene': {
        'shape': [600, 200]
    },
    'entities': [new_entity]
}

pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
img = pg.generate_playground_image()
display(img)

new_entity = edible_default.copy()
new_entity['position'] = [50, 50, 0.2]
new_entity['physical_shape'] = 'pentagon'
new_entity['radius'] = 30

pg_params = {
    'scene': {
        'shape': [600, 200]
    },
    'entities': [new_entity]
}

pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
img = pg.generate_playground_image()
display(img)


# Adding agent


