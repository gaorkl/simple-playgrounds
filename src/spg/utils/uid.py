def id_to_pixel(uid):

    id_0 = uid & 255
    id_1 = (uid >> 8) & 255
    id_2 = (uid >> 16) & 255

    return id_0, id_1, id_2
