import pygame
import random
import os, sys

def get_asset(path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'assets', path)

POWER_TYPES = ["rocket", "heart", "shield", "laser"]

class PowerUp:
    def __init__(self, x, y):
        self.type = random.choice(POWER_TYPES)
        self.rect = pygame.Rect(x, y, 40, 40)

        self.images = {
            "rocket": pygame.image.load(get_asset("rocket.png")).convert_alpha(),
            "heart": pygame.image.load(get_asset("heart.png")).convert_alpha(),
            "shield": pygame.image.load(get_asset("shield.png")).convert_alpha(),
            "laser": pygame.image.load(get_asset("laser.png")).convert_alpha(),
        }

        self.image = pygame.transform.scale(self.images[self.type], (40, 40))

    def draw(self, screen):
        screen.blit(self.image, self.rect)