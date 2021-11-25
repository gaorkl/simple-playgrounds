from simple_playgrounds.common.contour import Contour


def test_circle_contour():

    contour = Contour(shape='circle', radius=10)
    mask = contour.mask

    assert mask[10, 10] == 1
    assert mask[2, 2] == 0


def test_rectangle_contour():

    # size is width-length
    contour = Contour(shape='rectangle', size=(11, 3))
    mask = contour.mask

    # but numpy coordinate systems is row, col
    assert mask.shape == (11, 11)
    assert mask[5, 3] == 0

