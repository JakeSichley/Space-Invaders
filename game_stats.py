import os
import pygame
import pygame.font


class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, ai_game, settings):
        """Initialize statistics."""
        self.ships_left = 0
        self.score = 0
        self.level = 1
        self.settings = settings
        self.reset_stats(settings)
        self.highscorelist = []
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings

        # Start game in an inactive state.
        self.game_active = False

        # High score should never be reset.
        self.loadhighscores()
        self.high_score = self.highscorelist[0][1]

    def reset_stats(self, settings):
        """Initialize statistics that can change during the game."""
        self.ships_left = settings.ship_limit
        self.score = 0
        self.level = 1

    def debugscores(self):
        for score in self.highscorelist:
            print(score[0] + ' ' + str(score[1]))

    def checkfornewhighscore(self):
        # Needs prompt but otherwise works
        for index in range(len(self.highscorelist)):
            if self.score > self.highscorelist[index][1]:
                self.newhighscore(index)
                self.writehighscores()
                return True

        return False

    def newhighscore(self, index):
        self.screen.fill(self.settings.bg_color)
        self.screen.blit(self.settings.screenbackground, self.settings.screenbackgroundrect)
        font = pygame.font.SysFont(None, 150)
        title = font.render("NEW HIGH SCORE!", True, (51, 255, 51), (0, 0, 0))
        # Center the title at the top of the screen.
        title_rect = title.get_rect()
        title_rect.centerx = self.screen_rect.centerx
        title_rect.top = 100
        self.screen.blit(title, title_rect)

        font = pygame.font.SysFont(None, 75)
        score = font.render(str(round(self.score, -1)) + ' POINTS', True, (255, 0, 0), (0, 0, 0))
        score_rect = score.get_rect()
        score_rect.centerx = self.screen_rect.centerx
        score_rect.top = title_rect.bottom + 100
        self.screen.blit(score, score_rect)

        font = pygame.font.SysFont(None, 75)
        initial_text = font.render("Enter Your Initials:", True, (255, 255, 51), (0, 0, 0))
        initial_rect = initial_text.get_rect()
        initial_rect.centerx = self.screen_rect.centerx
        initial_rect.top = score_rect.bottom + 100
        self.screen.blit(initial_text, initial_rect)

        pygame.display.flip()

        initials_str = ''

        while len(initials_str) < 3:
            self.screen.blit(title, title_rect)
            self.screen.blit(initial_text, initial_rect)
            self.screen.blit(score, score_rect)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    character = pygame.key.name(event.key)
                    if character.isalpha():
                        initials_str += character.upper()

            font = pygame.font.SysFont(None, 75)
            initials_text = font.render(initials_str, True, (255, 255, 51), (0, 0, 0))
            initials_rect = initials_text.get_rect()
            initials_rect.centerx = self.screen_rect.centerx
            initials_rect.top = initial_rect.bottom + 100
            self.screen.blit(initials_text, initials_rect)
            pygame.display.flip()

        initials_str = initials_str[:3]
        self.highscorelist.insert(index, tuple((initials_str.upper(), self.score)))
        self.highscorelist = self.highscorelist[:self.settings.maxscores]

    def loadhighscores(self):
        filepath = 'highscores.txt'

        if not os.path.isfile(filepath):
            file = open(filepath, 'x+')
        else:
            file = open(filepath, 'r')

        try:
            for line in file:
                scorepair = line.rpartition(' ')
                self.highscorelist.append(tuple((scorepair[0], int(scorepair[2]))))

            length = len(self.highscorelist)

            # If there are too many scores, resize to max number of high scores
            if length > self.settings.maxscores:
                self.highscorelist = self.highscorelist[:(self.settings.maxscores - length)]

            # If there are not enough scores, append filler scores to the list
            elif length < self.settings.maxscores:
                for blank in range(self.settings.maxscores - length):
                    self.highscorelist.append(tuple(('---', 0)))
        finally:
            file.close()

    def writehighscores(self):
        file = open('highscores.txt', 'w')

        try:
            for score in self.highscorelist:
                file.write(score[0] + ' ' + str(score[1]) + '\n')

        finally:
            file.close()

    def display_scores(self):
        font = pygame.font.SysFont(None, 150)
        title = font.render("HIGH SCORES", True, (51, 255, 51), (0, 0, 0))
        # Center the title at the top of the screen.
        title_rect = title.get_rect()
        title_rect.centerx = self.screen_rect.centerx
        title_rect.top = 100
        self.screen.blit(title, title_rect)

        height = title_rect.bottom
        height_offset = 60
        font = pygame.font.SysFont(None, 50)
        for index in range(len(self.highscorelist)):
            string_list = [str(index + 1) + ':', self.highscorelist[index][0], str(self.highscorelist[index][1])]

            text = font.render(string_list[0], True, (51, 255, 51), (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.x = self.screen_rect.centerx - 200
            text_rect.top = height + height_offset
            self.screen.blit(text, text_rect)

            text = font.render(string_list[1], True, (255, 255, 51), (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.x = self.screen_rect.centerx - 50
            text_rect.top = height + height_offset
            self.screen.blit(text, text_rect)

            text = font.render(string_list[2], True, (255, 255, 51), (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.x = self.screen_rect.centerx + 150
            text_rect.top = height + height_offset
            self.screen.blit(text, text_rect)

            height += height_offset
