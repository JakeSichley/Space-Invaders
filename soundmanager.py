import pygame
import threading
import sys
from pygame.locals import *


# Singleton class SoundManager
class SoundManager:
    __instance = None

    @staticmethod
    def getinstance():
        # Static access
        if SoundManager.__instance is None:
            SoundManager()
        return SoundManager.__instance

    def __init__(self):
        if SoundManager.__instance is not None:
            raise Exception("Instance already exists")
        else:
            SoundManager.__instance = self
            pygame.mixer.init(buffer=16)
            #self.__winningmusic = pygame.mixer.Sound('Resources\\winningmusic.wav')
            #self.__winningmusic.set_volume(0.15)
            self.__backgroundmusicfiles = ['sounds/backgroundmusic.mp3', 'sounds/backgroundmusic110.mp3',
                                           'sounds/backgroundmusic133.mp3', 'sounds/backgroundmusic150.mp3']
            self.backgroundmusicspeeds = [1, 1.1, 1.33, 1.5]
            self.musicindex = 0
            pygame.mixer.music.load(self.__backgroundmusicfiles[self.musicindex])
            self.__musicplaying = False
            self.__basemusicduration = 130
            self.__currentduration = 0

    def startgame(self):
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.1)
        self.__musicplaying = True

    def getmusicplaying(self):
        return self.__musicplaying

    def newlevel(self):
        # Implement logic to offset base music to feel less 'jumpy'?
        self.musicindex = 0
        pygame.mixer.music.load(self.__backgroundmusicfiles[self.musicindex])
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(0.1)
        self.__currentduration = 0

    @staticmethod
    def threadedsound(function):
        thread = threading.Thread(target=function, args=(), daemon=True)
        thread.start()

        # Threading the sound function to allow exiting of the game
        # Sound functions 'lock' the window with .wait()
        while thread.is_alive():
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

    @staticmethod
    def threadedfunction(function):
        thread = threading.Thread(target=function, args=(), daemon=True)
        thread.start()

    def increasemusicspeed(self):
        # Increase the current position offset by the real position of the song (duration * speed)
        self.__currentduration += pygame.mixer.music.get_pos() * self.backgroundmusicspeeds[self.musicindex] / 1000

        # Set background music to the next speed
        self.musicindex += 1
        if self.musicindex > len(self.__backgroundmusicfiles) - 1:
            self.musicindex = 0

        # Offset duration to be a position relevant to the next speed
        self.__currentduration %= self.__basemusicduration / self.backgroundmusicspeeds[self.musicindex]
        pygame.mixer.music.load(self.__backgroundmusicfiles[self.musicindex])
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_pos(self.__currentduration)
        pygame.mixer.music.set_volume(0.1)
