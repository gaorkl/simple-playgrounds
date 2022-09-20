
def id_to_pixel(id):

    id_0 = id & 255
    id_1 = (id >> 8) & 255
    id_2 = (id >> 16) & 255

    return id_0, id_1, id_2
