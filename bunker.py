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
    def validhit(self, bullet, alienbullet=False):
        image = ConvertImage.topil(self.image)

        # Crop the bullet inside the bunker to ensure coordinates are valid
        # Save the original rect to restore if there is not a collision
        originalrect = bullet.rect
        bullet.rect = bullet.rect.clip(self.rect)

        # Different coordinate offsets must be used depending on the bullet type
        # By default, game assumes that the bullet is a player bullet
        # [Player's bullet travels up, Alien's bullet travels down]
        if alienbullet:
            offset = tuple((bullet.rect.bottomleft[0] - self.rect.topleft[0],
                            bullet.rect.bottomleft[1] - self.rect.topleft[1]))
            y = offset[1] - bullet.rect.height
            y2 = offset[1]
        else:
            offset = tuple((bullet.rect.topleft[0] - self.rect.topleft[0],
                            bullet.rect.topleft[1] - self.rect.topleft[1]))
            y = offset[1]
            y2 = offset[1] + bullet.rect.height

        # Check the alpha of each of the coordinates in the bullet's rect area
        for x in range(offset[0], offset[0] + bullet.rect.width):
            for y in range(y, y2):
                pixel = image.getpixel((x, y))
                if pixel[3] != 0:
                    # If there is a collision, stop checking pixels, call collision functions, and return True
                    self.__hit(offset, self.settings.explosionradius)
                    return True

        # If there is not a collision, restore the bullet's rect and return False
        bullet.rect = originalrect
        return False

    """When a bunker is hit, destroy pixels in radius. This method returns a valid list of coordinates for a radius"""
    def __getradiuscoordinates(self, offset, radius):
        image = ConvertImage.topil(self.image)
        coordinates = []

        for x in range(image.size[0]):
            for y in range(image.size[1]):
                # Calculate if a point is inside (or on) the circle
                xdiff = x - offset[0]
                ydiff = y - offset[1]
                # Slightly increased performace over using ** operator; suttering for computations is less pronounced
                if xdiff * xdiff + ydiff * ydiff <= radius * radius:
                    coordinates.append((x, y))

        return coordinates

    """On a confirmed collision, destroy pixels in a radius around the hit"""
    def __hit(self, offset, radius):
        image = ConvertImage.topil(self.image)

        # 10% of destruction in outer most circle
        coordindates = self.__getradiuscoordinates(offset, radius + 10)
        for point in coordindates:
            if random.randint(0, 10) == 1:
                pixel = list(image.getpixel(point))
                # Set alpha of pixel to 0
                pixel[3] = 0
                image.putpixel(point, tuple(pixel))

        # 25% chance of destruction in second circle
        coordindates = self.__getradiuscoordinates(offset, radius + 5)
        for point in coordindates:
            if random.randint(0, 4) == 1:
                pixel = list(image.getpixel(point))
                # Set alpha of pixel to 0
                pixel[3] = 0
                image.putpixel(point, tuple(pixel))

        # 100% of destruction in base circle
        coordindates = self.__getradiuscoordinates(offset, radius)
        for point in coordindates:
            pixel = list(image.getpixel(point))
            # Set alpha of pixel to 0
            pixel[3] = 0
            image.putpixel(point, tuple(pixel))

        self.image = ConvertImage.topygame(image)
