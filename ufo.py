import pygame
from pygame.sprite import Sprite


class UFO(Sprite):
    """A class to represent a UFO"""

    def __init__(self, ai_game, score):
        """Initialize the UFO and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the alien image and set its rect attribute.
        self.image = pygame.image.load('images/ufo.png')
        self.rect = self.image.get_rect()

        # Start each new UFO near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # Store the UFO's exact horizontal position.
        self.x = float(self.rect.x)

        # Store the UFO's score value
        self.score = score

    def check_edges(self):
        """Return True if alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Move the UFO right"""
        self.x += self.settings.ufo_speed
        self.rect.x = self.x

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
