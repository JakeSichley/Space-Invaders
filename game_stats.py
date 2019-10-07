import os
import pygame


class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, settings):
        """Initialize statistics."""
        self.ships_left = 0
        self.score = 0
        self.level = 1
        self.settings = settings
        self.reset_stats(settings)
        self.highscorelist = []

        # Start game in an inactive state.
        self.game_active = False

        # High score should never be reset.
        self.loadhighscores()
        self.high_score = self.highscorelist[0][1]

        #self.score = 11
        #self.checkfornewhighscore()
        #self.debugscores()
        
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
                name = ''
                while len(name) < 3:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            character = pygame.key.name(event.key)
                            if character.isalpha():
                                name += character

                self.highscorelist.insert(index, tuple((name.upper(), self.score)))
                self.highscorelist = self.highscorelist[:self.settings.maxscores]
                return

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
