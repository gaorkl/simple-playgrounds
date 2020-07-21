import matplotlib.pyplot as plt


def display_plt(self, img ):
    """
    Plot the Environment using pyplot.

    """
    img = self.generate_sensor_image(self, agent, width_sensor, height_sensor)

    plt.axis('off')
    plt.imshow(img)
