class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, settings):
        """Initialize statistics."""
        self.ships_left = 0
        self.score = 0
        self.level = 1
        self.reset_stats(settings)

        # Start game in an inactive state.
        self.game_active = False

        # High score should never be reset.
        self.high_score = 0
        
    def reset_stats(self, settings):
        """Initialize statistics that can change during the game."""
        self.ships_left = settings.ship_limit
        self.score = 0
        self.level = 1
