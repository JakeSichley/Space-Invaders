import pygame
from pygame.sprite import Sprite


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
        self.rect.y = int(self.settings.screen_height * 0.75)

        # Store the bunker's exact horizontal position.
        self.x = float(self.rect.x)
