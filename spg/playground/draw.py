import matplotlib.pyplot as plt
import pymunk


def plt_draw(playground, plt_width=10, center=None, size=None):

    if not center:
        center = (0, 0)

    if not size:
        size = playground.size

    fig_size = (plt_width, plt_width / size[0] * size[1])

    fig = plt.figure(figsize=fig_size)

    ax = plt.axes(
        xlim=(center[0] - size[0] / 2, center[0] + size[0] / 2),
        ylim=(center[1] - size[1] / 2, center[1] + size[1] / 2),
    )
    ax.set_aspect("equal")

    options = pymunk.matplotlib_util.DrawOptions(ax)
    options.collision_point_color = (10, 20, 30, 40)
    playground.space.debug_draw(options)
    # ax.invert_yaxis()
    plt.show()
    del fig
