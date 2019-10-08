import sys
from time import sleep
import pygame
from alien import Alien
from bullet import Bullet
from button import Button
from game_stats import GameStats
from scoreboard import Scoreboard
from settings import Settings
from ship import Ship
from bunker import Bunker
from soundmanager import SoundManager
from alienexplosion import AlienExplosion


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self.settings)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()

        self._create_fleet()
        self._create_bunker_wall()

        self._soundmananger = SoundManager()

        self._update_frame_event = pygame.USEREVENT + 1
        self._update_explosion_frame_event = pygame.USEREVENT + 2
        pygame.time.set_timer(self._update_frame_event, 1000)
        pygame.time.set_timer(self._update_explosion_frame_event, 200)

        # Make the Play button.
        self.play_button = Button(self, "Play", (0, -50))
        self.score_button = Button(self, "High Scores", (0, 50))

    def run_game(self):
        """Start the main loop for the game."""
        # Game stats == false is here
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == self._update_frame_event:
                self._update_frames()
            elif event.type == self._update_explosion_frame_event:
                self._update_explosion_frames()

    # Game start function
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats(self.settings)
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self._create_bunker_wall()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

            # Start background music
            self._soundmananger.getinstance().startgame()

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self.ship.moving_left = True
        elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            SoundManager.threadedfunction(self._soundmananger.getinstance().increasemusicspeed)

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, False)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)

                for alien in aliens:
                    explosion = AlienExplosion(self, alien)
                    self.explosions.add(explosion)
                    alien.kill()

            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # New level created here
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self._create_bunker_wall()
            self.settings.increase_speed()
            self._soundmananger.getinstance().newlevel()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

        # Get a list of collisions between all bunkers and bullets
        # Don't kill bullets, as we need the coordinates for bunker pixel destruction
        collisions = pygame.sprite.groupcollide(self.bunkers, self.bullets, False, False)

        if collisions:
            for bunker in collisions:
                for bullet in collisions[bunker]:
                    if bunker.validhit(bullet):
                        bullet.kill()

    def _update_aliens(self):
        """
        Check if the fleet is at an edge,
          then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()
        self.explosions.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

        # Check how many aliens are left
        remaining = len(self.aliens)
        speeds = [0.75, 0.5, 0.25]

        # As more aliens are killed, increase the speed of the music
        for index in range(len(speeds)):
            if remaining < int(self.settings.max_aliens * speeds[index])\
                    and self._soundmananger.getinstance().musicindex < index + 1:
                self._soundmananger.getinstance().increasemusicspeed()

    def _update_frames(self):
        for alien in self.aliens:
            alien.nextframe()

    def _update_explosion_frames(self):
        for explosion in self.explosions:
            explosion.nextframe()

            if explosion.finished:
                explosion.kill()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self._create_bunker_wall()
            self.ship.center_ship()
            
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self, ['images/alien1frame1.png', 'images/alien1frame2.png'])
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        # Available rows
        available_space_y = (self.settings.screen_height - (5 * alien_height) - ship_height)
        #number_rows = available_space_y // (2 * alien_height)
        number_rows = 6

        alienimages = [
            ['images/alien1frame1.png', 'images/alien1frame2.png'],
            ['images/alien2frame1.png', 'images/alien2frame2.png'],
            ['images/alien3frame1.png', 'images/alien3frame2.png']
        ]

        alienimageindex = 0

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            if row_number % 2 == 0 and row_number is not 0:
                alienimageindex += 1
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number, alienimages[alienimageindex])

        self.settings.max_aliens = len(self.aliens)

    # Pass in images to this function
    def _create_alien(self, alien_number, row_number, images):
        """Create an alien and place it in the row."""
        alien = Alien(self, images)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _create_bunker_wall(self):
        """Create the row of bunkers."""
        # Create an bunker and find the number of bunkers in a row.
        # Spacing between each bunker is equal to one alien width.
        bunker = Bunker(self)
        bunker_width, bunker_height = bunker.rect.size
        available_space_x = self.settings.screen_width
        number_bunkers_x = (available_space_x // bunker_width) // 2

        # Create the full wall of bunkers.
        for bunker_number in range(number_bunkers_x):
            self._create_bunker(bunker_number)

    def _create_bunker(self, bunker_number):
        """Create an bunker and place it in the row."""
        bunker = Bunker(self)
        bunker_width, bunker_height = bunker.rect.size
        bunker.x = (bunker_width // 2) + 2 * bunker_width * bunker_number
        bunker.rect.x = bunker.x
        bunker.rect.y = int(self.settings.screen_height * 0.80)
        self.bunkers.add(bunker)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                return

        for explosion in self.explosions.sprites():
            if explosion.check_edges():
                self._change_fleet_direction()
                return

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        # Space update: fleet no longer drops down
        # for alien in self.aliens.sprites():
        #    alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(self.settings.screenbackground, self.settings.screenbackgroundrect)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        # Draw the aliens
        self.aliens.draw(self.screen)
        # Draw the bunkers
        self.bunkers.draw(self.screen)
        # Draw the explosions
        self.explosions.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        # Control goes here after a game ends2
        if not self.stats.game_active:
            self.stats.writehighscores()
            self.play_button.draw_button()
            self.score_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
