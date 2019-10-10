import pygame


class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)
        self.screenbackground = pygame.image.load('images/background.png')
        self.screenbackgroundrect = self.screenbackground.get_rect()

        # Game settings
        self.maxscores = 10
        self.number_of_rows = 6

        # Ship settings
        self.ship_limit = 3

        # Bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 5
        self.alien_bullet_color = (255, 175, 15)

        # Alien Bullet limits
        self.minimum_fire_interval = 500
        self.default_fire_interval = 2000
        # Random selects a number between 0 and this as its range, fires if equal to following variable
        self.maximum_fire_chance = 3
        # Fire a bullet if random number is the this number
        self.fire_chance_key = 1
        self.default_fire_chance = 25
        self.current_fire_interval = self.default_fire_interval
        self.current_fire_chance = self.default_fire_chance

        # Bunker settings
        self.explosionradius = 7

        # Alien settings
        self.fleet_drop_speed = 5

        # How quickly the game speeds up
        self.speedup_scale = 1.1
        # How quickly the alien point values increase
        self.score_scale = 1.5

        # Dynamic settings
        self.ship_speed = 1.5
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1
        self.fleet_direction = 1
        self.alien_points = 50
        self.max_aliens = 90

        # Dynamic settings boundaries
        self.maximum_ship_speed = 6.5
        self.maximum_bullet_speed = 9
        self.maximum_alien_speed = 4.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0

        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

        # Alien firing
        self.current_fire_interval = self.default_fire_interval
        self.current_fire_chance = self.default_fire_chance

    def increase_speed(self, level):
        """Increase speed settings and alien point values."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        """Increase variables related to alien bullets"""
        self.current_fire_interval = self.default_fire_interval - ((level - 1) * 30)

        if self.current_fire_interval < self.minimum_fire_interval:
            self.current_fire_interval = self.minimum_fire_interval

        self.current_fire_chance = self.default_fire_chance - int(level / 4)

        if self.current_fire_chance < self.maximum_fire_chance:
            self.current_fire_chance = self.maximum_fire_chance

        if self.ship_speed > self.maximum_ship_speed:
            self.ship_speed = self.maximum_ship_speed

        if self.bullet_speed > self.maximum_bullet_speed:
            self.bullet_speed = self.maximum_bullet_speed

        if self.alien_speed > self.maximum_alien_speed:
            self.alien_speed = self.maximum_alien_speed

        # self.alien_points = int(self.alien_points * self.score_scale)
        # TODO: handle inside each alien class individual
