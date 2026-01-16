import pygame

class Obstacle:
    def __init__(self, x, y, width, height, sprite_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (80, 80, 80)
        self.border_color = (120, 120, 120)

        # Charger l'image si fournie
        if sprite_path:
            self.sprite = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (width, height))
        else:
            self.sprite = None

    def draw(self, screen):
        for i in range(0, self.rect.width, 20):
            for j in range(0, self.rect.height, 20):
                pygame.draw.rect(screen, (100, 100, 100),
                                (self.rect.x + i, self.rect.y + j, 18, 18))
