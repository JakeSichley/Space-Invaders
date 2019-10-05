import pygame
from pygame.sprite import Sprite
from convertimage import ConvertImage
import random


class Bunker(Sprite):
    """A class to represent a single bunker."""

    def __init__(self, ai_game):
        """Initialize the bunker and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the bunker image and set its rect attribute.
        self.image = pygame.image.load('images/bunker.png')
        self.rect = self.image.get_rect()

        # Start each new bunker near the bottom left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = int(self.settings.screen_height * 0.90)

        # Store the bunker's exact horizontal position.
        self.x = float(self.rect.x)

    """When a collision occurs, check to see if see if pixels are valid (Alpha != 0)"""
    def validhit(self, bullet):
        image = ConvertImage.topil(self.image)

        # back to clip
        # compute top left offset then use width + height
        originalrect = bullet.rect
        bullet.rect = bullet.rect.clip(self.rect)

        offset = tuple((bullet.rect.topleft[0] - self.rect.topleft[0],
                        bullet.rect.topleft[1] - self.rect.topleft[1]))

        for x in range(offset[0], offset[0] + bullet.rect.width):
            for y in range(offset[1], offset[1] + bullet.rect.height):
                pixel = image.getpixel((x, y))
                if pixel[3] != 0:
                    self.__hit(bullet, self.settings.explosionradius)
                    return True

        bullet.rect = originalrect
        return False

    """When a bunker is hit, destroy pixels in radius. This method supplies a valid list of coordinates for a radius"""
    def __getradiuscoordinates(self, bullet, radius):
        image = ConvertImage.topil(self.image)
        # Compute offset of rectangle to use in localized image coordinates
        offset = tuple((bullet.rect.topleft[0] - self.rect.topleft[0],
                        bullet.rect.topleft[1] - self.rect.topleft[1]))

        coordinates = []

        for x in range(image.size[0]):
            for y in range(image.size[1]):
                # Calculate if a point is inside (or on) the circle
                if (x - offset[0])**2 + (y - offset[1])**2 <= radius**2:
                    coordinates.append((x, y))

        return coordinates

    """On a confirmed collision, destroy pixels in a radius around the hit"""
    def __hit(self, bullet, radius):
        image = ConvertImage.topil(self.image)

        # 10% of destruction in outer most circle
        coordindates = self.__getradiuscoordinates(bullet, radius + 10)
        for point in coordindates:
            if random.randint(0, 10) == 1:
                pixel = list(image.getpixel(point))
                # Set alpha of pixel to 0
                pixel[3] = 0
                image.putpixel(point, tuple(pixel))

        # 25% chance of destruction in second circle
        coordindates = self.__getradiuscoordinates(bullet, radius + 5)
        for point in coordindates:
            if random.randint(0, 4) == 1:
                pixel = list(image.getpixel(point))
                # Set alpha of pixel to 0
                pixel[3] = 0
                image.putpixel(point, tuple(pixel))

        # 100% of destruction in base circle
        coordindates = self.__getradiuscoordinates(bullet, radius)
        for point in coordindates:
            pixel = list(image.getpixel(point))
            # Set alpha of pixel to 0
            pixel[3] = 0
            image.putpixel(point, tuple(pixel))

        self.image = ConvertImage.topygame(image)
