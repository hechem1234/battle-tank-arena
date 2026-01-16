import pygame
import math

class Bullet:
    def __init__(self, x, y, dx, dy, color=(255, 255, 0), speed=7):
        self.rect = pygame.Rect(x - 5, y - 2, 10, 4)  # Centré
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.color = color
        self.lifetime = 120 # Disparaît après 2 secondes à 60 FPS
        self.is_laser = (color == (255, 100, 100) or color == (255, 50, 50))  # Détecter si c'est une balle laser
        
        # Normaliser la direction pour vitesse constante
        if dx != 0 or dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            self.dx = dx / length
            self.dy = dy / length
    
    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        self.lifetime -= 1
    
    def draw(self, screen):
        # Dessiner la balle avec un effet différent pour laser
        if self.is_laser:
            # Balle laser plus grande et plus lumineuse
            pygame.draw.rect(screen, (255, 100, 100), self.rect)
            # Effet de lumière
            pygame.draw.rect(screen, (255, 200, 200), 
                            (self.rect.x+1, self.rect.y+1, 8, 2))
            # Contour
            pygame.draw.rect(screen, (255, 50, 50), self.rect, 1)
        else:
            # Balle normale
            pygame.draw.rect(screen, self.color, self.rect)
            # Ajouter un effet lumineux
            pygame.draw.rect(screen, (255, 255, 200), 
                            (self.rect.x+2, self.rect.y+1, 6, 2))