import sys
import random
from time import sleep
import threading
import pygame
import pygame.font
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
from alienbullet import AlienBullet
from ufo import UFO


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
        self.stats = GameStats(self, self.settings)
        self.sb = Scoreboard(self)

        # Sprites
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.bunkers = pygame.sprite.Group()
        self.alienbullets = pygame.sprite.Group()
        # UFO variables
        self.ufo = None
        self.display_ufo_score = False
        self.ufo_score = None
        self.ufo_rect = None

        self._create_fleet()
        self._create_bunker_wall()

        self._soundmananger = SoundManager()

        # TODO: Use wait function to display ufo value on screen

        """
        DEFINITION OF EVENTS:
        a) '_update_frame_event': EVENTID=25, how often alien animations should be updated
        b) '_update_explosion_frame_event': EVENTID=26, how often explosion animations should be updated
        c) '_alien_shoot_event': EVENTID=27, how often the aliens have an opportunity to shoot
        d) '_ufo_summon_event': EVENTID=28, how often the ufo has an opportunity to spawn
        """
        self._update_frame_event = pygame.USEREVENT + 1
        self._update_explosion_frame_event = pygame.USEREVENT + 2
        self._alien_shoot_event = pygame.USEREVENT + 3
        self._ufo_summon_event = pygame.USEREVENT + 4
        pygame.time.set_timer(self._update_frame_event, 1000)
        pygame.time.set_timer(self._update_explosion_frame_event, 200)
        pygame.time.set_timer(self._alien_shoot_event, self.settings.current_fire_interval)
        pygame.time.set_timer(self._ufo_summon_event, 10000)

        # Make the Play button.
        self.play_button = Button(self, "Play", (0, -50))
        self.score_button = Button(self, "High Scores", (0, 50))
        self.back_button = Button(self, "Main Menu", (0, 50))

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
            else:
                self._draw_main_menu()

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
                self._check_score_button(mouse_pos)
            elif event.type == self._update_frame_event:
                self._update_frames()
            elif event.type == self._update_explosion_frame_event:
                self._update_explosion_frames()
            elif event.type == self._alien_shoot_event:
                self._alien_shoot()
            elif event.type == self._ufo_summon_event:
                self._create_ufo()

    # Game start function
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Make sure all sprites are destroyed if there was a previous game
            self.bullets.empty()
            self.bunkers.empty()
            self.alienbullets.empty()
            self.aliens.empty()
            if self.ufo is not None:
                self.ufo.kill()
                if self._soundmananger.getinstance().getufosoundactive:
                    self._soundmananger.getinstance().stopufosound()
                self.ufo = None

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

            # Update events
            pygame.time.set_timer(self._alien_shoot_event, self.settings.current_fire_interval)

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

            # Start background music
            self._soundmananger.getinstance().startgame()

    def _check_score_button(self, mouse_pos):
        button_clicked = self.score_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.screen.fill(self.settings.bg_color)
            self.screen.blit(self.settings.screenbackground, self.settings.screenbackgroundrect)
            self.stats.display_scores()
            self.back_button.rect = self.score_button.rect
            self.back_button.prep_msg()
            self.back_button.draw_button()
            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        button_clicked = self.score_button.rect.collidepoint(mouse_pos)
                        if button_clicked:
                            return

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

    def _alien_shoot(self):
        for alien in self.aliens:
            if random.randint(0, self.settings.current_fire_chance) == self.settings.fire_chance_key:
                self._alien_fire_bullet(alien)

    def _alien_fire_bullet(self, alien):
        new_bullet = AlienBullet(self, alien)
        self.alienbullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        # Update alien bullet positions
        self.alienbullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        for bullet in self.alienbullets.copy():
            if bullet.rect.bottom >= self.settings.screen_height:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()
        self._check_alienbullet_collisions()

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-UFO collisions."""
        if self.ufo is not None:
            collisions = pygame.sprite.spritecollide(self.ufo, self.bullets, False)

            if collisions:
                self.stats.score += self.ufo.score
                self.sb.prep_score()
                self.sb.check_high_score()
                score_str = "{:,}".format(self.ufo.score)
                font = pygame.font.SysFont(None, 36)
                self.ufo_score = font.render(score_str, True, (255, 255, 0), self.settings.bg_color)
                self.ufo_rect = self.ufo_score.get_rect()
                self.ufo_rect.center = self.ufo.rect.center
                self.display_ufo_score = True
                thread = threading.Thread(target=self._ufo_score_duration, args=[3000], daemon=True)
                thread.start()
                self.ufo.kill()
                if self._soundmananger.getinstance().getufosoundactive():
                    self._soundmananger.getinstance().stopufosound()
                self.ufo = None

        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, False)

        if collisions:
            for aliens in collisions.values():
                for alien in aliens:
                    self.stats.score += alien.score
                    explosion = AlienExplosion(self, alien)
                    self.explosions.add(explosion)
                    alien.kill()

            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # New level created here
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self.bunkers.empty()
            self.alienbullets.empty()
            if self.ufo is not None:
                self.ufo.kill()
                if self._soundmananger.getinstance().getufosoundactive:
                    self._soundmananger.getinstance().stopufosound()
                self.ufo = None
            # Create new objects
            self._create_fleet()
            self._create_bunker_wall()
            # Adjust stats & increase level
            self.stats.level += 1
            self.settings.increase_speed(self.stats.level)
            pygame.time.set_timer(self._alien_shoot_event, self.settings.current_fire_interval)

            self._soundmananger.getinstance().newlevel()

            self.sb.prep_level()

        # Get a list of collisions between all bunkers and bullets
        # Don't kill bullets, as we need the coordinates for bunker pixel destruction
        collisions = pygame.sprite.groupcollide(self.bunkers, self.bullets, False, False)

        if collisions:
            for bunker in collisions:
                for bullet in collisions[bunker]:
                    if bunker.validhit(bullet):
                        bullet.kill()

    def _check_alienbullet_collisions(self):
        """Check to see if ship was hit by a bullet"""
        collisions = pygame.sprite.spritecollide(self.ship, self.alienbullets, False)

        if collisions:
            self._ship_hit()

        collisions = pygame.sprite.groupcollide(self.bunkers, self.alienbullets, False, False)

        if collisions:
            for bunker in collisions:
                for bullet in collisions[bunker]:
                    if bunker.validhit(bullet, True):
                        bullet.kill()

    def _update_aliens(self):
        """
        Check if the fleet is at an edge,
          then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()
        self.explosions.update()

        if self.ufo is not None:
            self.ufo.update()

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

        """Also check for bunker collisions"""
        collisions = pygame.sprite.groupcollide(self.bunkers, self.aliens, False, False)

        if collisions:
            for bunker in collisions:
                for alien in collisions[bunker]:
                    alien.kill()
                    bunker.kill()
                    break

    def _ship_explosion(self):
        for image in self.ship.explosion_frames:
            self.ship.setexplosionframe(image)
            self._update_screen()
            pygame.time.wait(175)

        self.ship.resetimage()
        self._update_screen()
        pygame.time.wait(500)

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        thread = threading.Thread(target=self._ship_explosion, args=(), daemon=True)
        thread.start()

        # Threading the explosion function to allow exiting of the game
        # pygame.time.wait() locks the window, preventing exiting
        while thread.is_alive():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # Get rid of any remaining aliens, bunkers, and all bullets
            self.aliens.empty()
            self.bullets.empty()
            self.bunkers.empty()
            self.alienbullets.empty()
            if self.ufo is not None:
                self.ufo.kill()
                if self._soundmananger.getinstance().getufosoundactive:
                    self._soundmananger.getinstance().stopufosound()
                self.ufo = None
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self._create_bunker_wall()
            self.ship.center_ship()
            self._soundmananger.getinstance().newlevel()
            
            # Pause.
            sleep(0.5)
        # Game ending control goes here
        else:
            self.stats.game_active = False
            if self._soundmananger.getinstance().getmusicplaying():
                self._soundmananger.getinstance().stopmusic()
            pygame.mouse.set_visible(True)

            if self.stats.checkfornewhighscore():
                self._check_score_button(self.score_button.rect.center)

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self, ['images/alien1frame1.png', 'images/alien1frame2.png'], 0)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        # ship_height = self.ship.rect.height
        # Available rows
        # available_space_y = (self.settings.screen_height - (5 * alien_height) - ship_height)
        # number_rows = available_space_y // (2 * alien_height)
        number_rows = self.settings.number_of_rows

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
                self._create_alien(alien_number, row_number, alienimages[alienimageindex],
                                   self.settings.score_values[alienimageindex], alien_number % 2)

        self.settings.max_aliens = len(self.aliens)

    def _create_alien(self, alien_number, row_number, images, score, offset):
        """Create an alien and place it in the row."""
        alien = Alien(self, images, score, offset)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 1.25 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _create_ufo(self):
        if not self.stats.game_active:
            return

        if self.ufo is None and random.randint(0, 5) == 2:
            self.ufo = UFO(self, int(self.settings.score_values[2] * random.randint(3, 9) / 1.5))
            self.ufo.rect.y = int(self.settings.screen_height * random.randint(15, 75) / 100)
            if not self._soundmananger.getinstance().getufosoundactive():
                self._soundmananger.getinstance().playufosound()

    def _ufo_score_duration(self, duration):
        pygame.time.wait(duration)
        self.display_ufo_score = False

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

        if self.ufo is not None:
            if self.ufo.check_edges():
                self.ufo.kill()
                if self._soundmananger.getinstance().getufosoundactive:
                    self._soundmananger.getinstance().stopufosound()
                self.ufo = None

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        # They do drop down
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _draw_main_menu(self):
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(self.settings.screenbackground, self.settings.screenbackgroundrect)
        height = self.sb.show_main_menu()
        self.play_button.rect.bottom = self.play_button.rect.height + height + 75
        self.score_button.rect.top = self.play_button.rect.bottom + 50
        self.play_button.prep_msg()
        self.score_button.prep_msg()
        self.play_button.draw_button()
        self.score_button.draw_button()
        pygame.display.flip()

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(self.settings.screenbackground, self.settings.screenbackgroundrect)
        self.ship.blitme()
        if self.ufo is not None:
            self.ufo.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        for bullet in self.alienbullets.sprites():
            bullet.draw_bullet()

        # Draw the aliens
        self.aliens.draw(self.screen)
        # Draw the bunkers
        self.bunkers.draw(self.screen)
        # Draw the explosions
        self.explosions.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        if self.display_ufo_score:
            self.screen.blit(self.ufo_score, self.ufo_rect)

        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
