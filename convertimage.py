import pygame
from PIL import Image


class ConvertImage:
    @staticmethod
    def topygame(image):
        mode = image.mode
        size = image.size
        data = image.tobytes()

        return pygame.image.fromstring(data, size, mode)

    @staticmethod
    def topil(image):
        strformat = "RGBA"
        raw_str = pygame.image.tostring(image, strformat, False)
        return Image.frombytes(strformat, image.get_size(), raw_str)

    @staticmethod
    def changepixelrgba(coordinates, rgba, image):
        image.putpixel((coordinates[0], coordinates[1]), rgba)

    """ temp = ConvertImage.topil(playerImage)
                pixels = temp.getdata()

                for i in range(temp.size[0]):
                    for j in range(temp.size[1]):
                        if random.randint(0, 10) == 6:
                            temp.putpixel((i, j), (0, 0, 255, 255))

                playerImage = ConvertImage.topygame(temp)"""
