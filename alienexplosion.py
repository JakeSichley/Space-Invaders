import pygame
from pygame.sprite import Sprite


class AlienExplosion(Sprite):
    """A class to represent a single explosion of a dead alien in the fleet."""

    def __init__(self, ai_game, alien):
        """Initialize the explosion and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the explosion images and set its rect attribute.
        self.imageindex = 0
        self.explosions = ['images/explosionframe1.png', 'images/explosionframe2.png',
                           'images/explosionframe3.png', 'images/explosionframe4.png']
        self.image = pygame.image.load(self.explosions[0])
        self.rect = self.image.get_rect()

        # Start each new explosion where the alien died
        self.rect.x = alien.rect.x
        self.rect.y = alien.rect.y

        # Store the explosions's exact horizontal position.
        self.x = float(self.rect.x)

        self.finished = False

    def check_edges(self):
        """Return True if explosion is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Move the explosion right or left."""
        self.x += (self.settings.alien_speed * self.settings.fleet_direction)
        self.rect.x = self.x

    def nextframe(self):
        self.imageindex += 1

        if self.imageindex > len(self.explosions) - 1:
            self.finished = True
            return

        self.image = pygame.image.load(self.explosions[self.imageindex])
