import pygame
import random

POWER_TYPES = ["rocket", "heart", "shield", "laser"]

class PowerUp:
    def __init__(self, x, y):
        self.type = random.choice(POWER_TYPES)
        self.rect = pygame.Rect(x, y, 40, 40)

        self.images = {
            "rocket": pygame.image.load("assets/rocket.png").convert_alpha(),
            "heart": pygame.image.load("assets/heart.png").convert_alpha(),
            "shield": pygame.image.load("assets/shield.png").convert_alpha(),
            "laser": pygame.image.load("assets/laser.png").convert_alpha(),
        }

        self.image = pygame.transform.scale(self.images[self.type], (40, 40))

    def draw(self, screen):
        screen.blit(self.image, self.rect)