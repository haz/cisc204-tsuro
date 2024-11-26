

#     1   2
#   +-------+
# 8 |       | 3
#   |       |
# 7 |       | 4
#   +-------+
#     6   5


from PIL import Image, ImageDraw

# Define image size and corner extent
image_size = 300  # Image will be 300x300 pixels
corner_extent = 100  # 100 pixels extent from each corner


def draw_border(draw):
    # Draw a thick black border around the entire image
    border_thickness = 5
    for i in range(border_thickness):
        draw.rectangle([i, i, image_size - i - 1, image_size - i - 1], outline="black")

# Draw straight lines
def draw_16(draw, col="black", width=3):
    draw.line([corner_extent, 0, corner_extent, image_size], fill=col, width=width)
def draw_25(draw, col="black", width=3):
    draw.line([image_size-corner_extent, 0, image_size-corner_extent, image_size], fill=col, width=width)
def draw_38(draw, col="black", width=3):
    draw.line([0, corner_extent, image_size, corner_extent], fill=col, width=width)
def draw_47(draw, col="black", width=3):
    draw.line([0, image_size-corner_extent, image_size, image_size-corner_extent], fill=col, width=width)

# Self-loops
def draw_12(draw, col="black", width=3):
    draw.arc([corner_extent, -0.5*corner_extent, 2*corner_extent, 0.5*corner_extent], start=0, end=180, fill=col, width=width)
def draw_34(draw, col="black", width=3):
    draw.arc([image_size-0.5*corner_extent, corner_extent, image_size+0.5*corner_extent, 2*corner_extent], start=90, end=270, fill=col, width=width)
def draw_56(draw, col="black", width=3):
    draw.arc([corner_extent, image_size-0.5*corner_extent, 2*corner_extent, image_size+0.5*corner_extent], start=180, end=360, fill=col, width=width)
def draw_78(draw, col="black", width=3):
    draw.arc([-0.5*corner_extent, corner_extent, 0.5*corner_extent, 2*corner_extent], start=270, end=90, fill=col, width=width)

# Small corner loops
def draw_18(draw, col="black", width=3):
    draw.arc([-corner_extent, -corner_extent, corner_extent, corner_extent], start=0, end=90, fill=col, width=width)
def draw_23(draw, col="black", width=3):
    draw.arc([image_size-corner_extent, -corner_extent, image_size+corner_extent, corner_extent], start=90, end=180, fill=col, width=width)
def draw_45(draw, col="black", width=3):
    draw.arc([image_size-corner_extent, image_size-corner_extent, image_size+corner_extent, image_size+corner_extent], start=180, end=270, fill=col, width=width)
def draw_67(draw, col="black", width=3):
    draw.arc([-corner_extent, image_size-corner_extent, corner_extent, image_size+corner_extent], start=270, end=360, fill=col, width=width)

# Large corner loops
def draw_14(draw, col="black", width=3):
    draw.arc([corner_extent, -2*corner_extent, image_size+2*corner_extent, image_size-corner_extent], start=0, end=360, fill=col, width=width)
def draw_27(draw, col="black", width=3):
    draw.arc([-2*corner_extent, -2*corner_extent, image_size-corner_extent, image_size-corner_extent], start=0, end=360, fill=col, width=width)
def draw_36(draw, col="black", width=3):
    draw.arc([corner_extent, corner_extent, image_size+2*corner_extent, image_size+2*corner_extent], start=0, end=360, fill=col, width=width)
def draw_58(draw, col="black", width=3):
    draw.arc([-2*corner_extent, corner_extent, image_size-corner_extent, image_size+2*corner_extent], start=0, end=360, fill=col, width=width)


# Large skewed corner loops
def draw_13(draw, col="black", width=3):
    draw.arc([corner_extent, -corner_extent, image_size+2*corner_extent, corner_extent], start=0, end=180, fill=col, width=width)
def draw_17(draw, col="black", width=3):
    draw.arc([-corner_extent, -2*corner_extent, corner_extent, image_size-corner_extent], start=270, end=90, fill=col, width=width)
def draw_24(draw, col="black", width=3):
    draw.arc([image_size-corner_extent, -2*corner_extent, image_size+corner_extent, image_size-corner_extent], start=90, end=270, fill=col, width=width)
def draw_28(draw, col="black", width=3):
    draw.arc([-2*corner_extent, -corner_extent, image_size-corner_extent, corner_extent], start=0, end=180, fill=col, width=width)
def draw_35(draw, col="black", width=3):
    draw.arc([image_size-corner_extent, corner_extent, image_size+corner_extent, image_size+2*corner_extent], start=90, end=270, fill=col, width=width)
def draw_46(draw, col="black", width=3):
    draw.arc([corner_extent, image_size-corner_extent, image_size+2*corner_extent, image_size+corner_extent], start=180, end=360, fill=col, width=width)
def draw_57(draw, col="black", width=3):
    draw.arc([-2*corner_extent, image_size-corner_extent, image_size-corner_extent, image_size+corner_extent], start=270, end=90, fill=col, width=width)
def draw_68(draw, col="black", width=3):
    draw.arc([-corner_extent, corner_extent, corner_extent, image_size+2*corner_extent], start=180, end=360, fill=col, width=width)

# S-curves
def draw_15(draw, col="black", width=3):
    draw.arc([corner_extent, -(image_size // 2), image_size-corner_extent, image_size//2], start=90, end=180, fill=col, width=width)
    draw.arc([corner_extent, (image_size // 2), image_size-corner_extent, 1.5 * image_size], start=270, end=360, fill=col, width=width)
def draw_26(draw, col="black", width=3):
    draw.arc([corner_extent, -(image_size // 2), image_size-corner_extent, image_size // 2], start=0, end=90, fill=col, width=width)
    draw.arc([corner_extent, image_size // 2, image_size-corner_extent, 1.5 * image_size], start=180, end=270, fill=col, width=width)
def draw_37(draw, col="black", width=3):
    draw.arc([-(image_size // 2), corner_extent, image_size // 2, image_size - corner_extent], start=0, end=90, fill=col, width=width)
    draw.arc([image_size // 2, corner_extent, 1.5*image_size, image_size-corner_extent], start=180, end=270, fill=col, width=width)
def draw_48(draw, col="black", width=3):
    draw.arc([-(image_size // 2), corner_extent, image_size // 2, image_size - corner_extent], start=270, end=360, fill=col, width=width)
    draw.arc([image_size // 2, corner_extent, 1.5*image_size, image_size-corner_extent], start=90, end=180, fill=col, width=width)



draw_method = {
    (1,2): draw_12,
    (1,3): draw_13,
    (1,4): draw_14,
    (1,5): draw_15,
    (1,6): draw_16,
    (1,7): draw_17,
    (1,8): draw_18,
    (2,3): draw_23,
    (2,4): draw_24,
    (2,5): draw_25,
    (2,6): draw_26,
    (2,7): draw_27,
    (2,8): draw_28,
    (3,4): draw_34,
    (3,5): draw_35,
    (3,6): draw_36,
    (3,7): draw_37,
    (3,8): draw_38,
    (4,5): draw_45,
    (4,6): draw_46,
    (4,7): draw_47,
    (4,8): draw_48,
    (5,6): draw_56,
    (5,7): draw_57,
    (5,8): draw_58,
    (6,7): draw_67,
    (6,8): draw_68,
    (7,8): draw_78,
}

def draw_tile(connections):
    # Create a blank square image with a white background
    image = Image.new("RGB", (image_size, image_size), "white")
    draw = ImageDraw.Draw(image)
    draw_border(draw)

    for u,v in connections:
        if u > v:
            u,v = v,u
        draw_method[(u,v)](draw)

    return (image, draw)

def draw_2by2_tiles(tiles, path=None):
    image = Image.new("RGB", (2*image_size, 2*image_size), "white")
    for i in range(2):
        for j in range(2):
            (image_ij, dr_ij) = draw_tile(tiles[i][j])
            if path is not None:
                for u,v in path[i][j]:
                    if u > v:
                        u,v = v,u
                    draw_method[(u,v)](dr_ij, col="red", width=5)
            image.paste(image_ij, (j*image_size, i*image_size))

    return image


if __name__ == '__main__':

    # draw_tile([(1,2), (3,4), (5,6), (7,8)])[0].show()
    # draw_tile([(2,3), (4,5), (6,7), (8,1)])[0].show()
    # draw_tile([(1,4), (2,7), (3,6), (5,8)])[0].show()
    # draw_tile([(1,3), (1,7), (2,4), (2,8), (3,5), (4,6), (5,7), (6,8)])[0].show()
    # draw_tile([(6, 1), (7, 2), (4,5), (8, 3)])[0].show()

    # Test cases to draw every line that starts with a particular edge location
    # draw_tile([(1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8)])[0].show()
    # draw_tile([(2,1), (2,3), (2,4), (2,5), (2,6), (2,7), (2,8)])[0].show()
    # draw_tile([(3,1), (3,2), (3,4), (3,5), (3,6), (3,7), (3,8)])[0].show()
    # draw_tile([(4,1), (4,2), (4,3), (4,5), (4,6), (4,7), (4,8)])[0].show()
    # draw_tile([(5,1), (5,2), (5,3), (5,4), (5,6), (5,7), (5,8)])[0].show()
    # draw_tile([(6,1), (6,2), (6,3), (6,4), (6,5), (6,7), (6,8)])[0].show()
    # draw_tile([(7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,8)])[0].show()
    # draw_tile([(8,1), (8,2), (8,3), (8,4), (8,5), (8,6), (8,7)])[0].show()

    # exit()

    from examples import example1

    tiles = [
        [example1["tiles"][0], example1["tiles"][1]],
        [example1["tiles"][2], []]
    ]

    path = [
        [[(1,4), (3,8), (5,6)], [(7,8)]],
        [[(1,8), (2,5)], []]
    ]
    # path=None

    # draw_2by2_tiles(tiles, path=path).save('tile.png')
    draw_2by2_tiles(tiles, path=path).show()
