from flatland import playgrounds
import matplotlib.pyplot as plt


def display(img):
    plt.imshow(img)
    plt.axis('off')
    plt.show()


####################################################
# Selecting different scenes for a basic playground

pg = playgrounds.PlaygroundGenerator.create('basic')
img = pg.generate_playground_image()
display(img)

pg_params = {
    'scene': {
        'shape': [600, 200],
        'scene_type': 'rooms_2'
    }
}

pg = playgrounds.PlaygroundGenerator.create('basic', pg_params)
img = pg.generate_playground_image()
display(img)

####################################################
# Selecting different Playgrounds

pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible')
img = pg.generate_playground_image()
display(img)

# Changing default shape
pg_params = {
    'scene': {
        'shape': [600, 200],
    }
}
pg = playgrounds.PlaygroundGenerator.create('rooms_2_edible', pg_params )
img = pg.generate_playground_image()
display(img)

# Adding entity

# Adding agent

