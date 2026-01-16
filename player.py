from bullet import Bullet
import pygame
import math

class Player:
    def __init__(self, x, y, width, height, color, controls, name, sprite_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 5
        self.hp = 100
        self.controls = controls
        self.name = name
        self.bullets = []
        self.shoot_cooldown = 0
        self.last_direction = (1, 0)  # direction initiale vers la droite
        self.shield = False
        self.shield_time = 0

        self.laser = False
        self.laser_time = 0

        # Contour du sprite (différent du rectangle de collision)
        self.contour_thickness = 3
        self.contour_color = (255, 255, 255)  # Blanc par défaut
        
        if sprite_path:
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
                # Redimensionner le sprite aux dimensions du joueur
                self.sprite = pygame.transform.scale(self.sprite, (width, height))
                # Créer une version avec contour pour l'affichage
                self.sprite_with_contour = self.add_contour_to_sprite(self.sprite, self.contour_color, self.contour_thickness)
            except:
                print(f"Erreur de chargement du sprite: {sprite_path}")
                self.sprite = None
                self.sprite_with_contour = None
        else:
            self.sprite = None
            self.sprite_with_contour = None
            
    def add_contour_to_sprite(self, sprite, color, thickness):
        """Ajoute un contour autour d'un sprite"""
        # Créer une surface légèrement plus grande pour le contour
        width, height = sprite.get_size()
        contour_surface = pygame.Surface((width + thickness*2, height + thickness*2), pygame.SRCALPHA)
        
        # Dessiner le contour sur la surface agrandie
        mask = pygame.mask.from_surface(sprite)
        for dx, dy in [(thickness + i, thickness + j) for i in (-thickness, 0, thickness) 
                      for j in (-thickness, 0, thickness) if not (i == 0 and j == 0)]:
            temp = sprite.copy()
            temp.fill(color, special_flags=pygame.BLEND_RGB_MAX)
            contour_surface.blit(temp, (dx, dy))
        
        # Dessiner le sprite original par dessus
        contour_surface.blit(sprite, (thickness, thickness))
        
        # Appliquer le masque alpha du sprite original au contour
        final_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        final_surface.blit(contour_surface, (-thickness, -thickness))
        
        return final_surface
            
    def move(self, keys, obstacles):
        dx, dy = 0, 0
        if self.controls == "ZQSD":
            if keys[pygame.K_z]: dy = -self.speed
            if keys[pygame.K_s]: dy = self.speed
            if keys[pygame.K_q]: dx = -self.speed
            if keys[pygame.K_d]: dx = self.speed
        elif self.controls == "ARROWS":
            if keys[pygame.K_UP]: dy = -self.speed
            if keys[pygame.K_DOWN]: dy = self.speed
            if keys[pygame.K_LEFT]: dx = -self.speed
            if keys[pygame.K_RIGHT]: dx = self.speed
        
        # Mémoriser la direction (pour les tirs)
        if dx != 0 or dy != 0:
            self.last_direction = [dx, dy]
        
        # Mouvement avec collision par axe
        self.rect.x += dx
        for obs in obstacles:
            if self.rect.colliderect(obs.rect):
                if dx > 0:
                    self.rect.right = obs.rect.left
                elif dx < 0:
                    self.rect.left = obs.rect.right
        
        self.rect.y += dy
        for obs in obstacles:
            if self.rect.colliderect(obs.rect):
                if dy > 0:
                    self.rect.bottom = obs.rect.top
                elif dy < 0:
                    self.rect.top = obs.rect.bottom
        
        # Garder dans l'écran (légèrement réduit pour la nouvelle taille)
        self.rect.clamp_ip(pygame.Rect(20, 20, 1460, 710))
    
    def handle_shooting(self, keys):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        shoot_key = pygame.K_LCTRL if self.controls == "ZQSD" else pygame.K_SPACE
        
        if keys[shoot_key] and self.shoot_cooldown == 0:
            # Tirs directionnels selon la dernière direction
            dx, dy = self.last_direction
            
            # Si le joueur ne bouge pas, tirer vers l'adversaire par défaut
            if dx == 0 and dy == 0:
                dx = 1 if self.controls == "ZQSD" else -1
            
            # Normaliser la direction
            if dx != 0 or dy != 0:
                # Si laser activé, tirer 3 balles
                if self.laser:
                    for offset in [-0.2, 0, 0.2]:
                        # Calculer la direction avec un petit offset
                        dir_dx = dx + offset * dy
                        dir_dy = dy - offset * dx
                        # Normaliser
                        length = math.sqrt(dir_dx*dir_dx + dir_dy*dir_dy)
                        if length > 0:
                            dir_dx /= length
                            dir_dy /= length
                        
                        bullet = Bullet(
                            self.rect.centerx,
                            self.rect.centery,
                            dir_dx,
                            dir_dy,
                            (255, 50, 50) if not self.laser else (255, 100, 100),  # Rouge plus clair pour laser
                            10 if self.laser else 7  # Vitesse augmentée pour laser
                        )
                        self.bullets.append(bullet)
                    self.shoot_cooldown = 10  # Cooldown réduit pour laser
                else:
                    # Tir normal
                    if dx != 0 and dy != 0:
                        dx *= 0.707  # 1/√2
                        dy *= 0.707
                    
                    bullet = Bullet(
                        self.rect.centerx,
                        self.rect.centery,
                        dx,
                        dy,
                        self.color
                    )
                    self.bullets.append(bullet)
                    self.shoot_cooldown = 15
    
    def update_bullets(self, screen, obstacles, opponent):
        current_time = pygame.time.get_ticks()

        # Vérifier la durée du shield
        if self.shield and current_time - self.shield_time > 10000:
            self.shield = False

        # Vérifier la durée du laser
        if self.laser and current_time - self.laser_time > 10000:
            self.laser = False

        for bullet in self.bullets[:]:
            bullet.update()
            
            # Collision avec obstacles
            for obs in obstacles:
                if bullet.rect.colliderect(obs.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
            
            # Collision avec adversaire
            if bullet.rect.colliderect(opponent.rect):
                # Si l'adversaire a un shield, le tir est bloqué
                if opponent.shield:
                    # Effet visuel quand un tir est bloqué
                    pygame.draw.circle(screen, (100, 200, 255), 
                                     (bullet.rect.centerx, bullet.rect.centery), 15, 2)
                else:
                    opponent.hp -= 10
                    # Feedback visuel - changer la couleur du contour temporairement
                    opponent.contour_color = (255, 50, 50)  # Rouge flash
                    pygame.time.set_timer(pygame.USEREVENT, 100)  # Réinitialiser après 100ms
                
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue
            
            # Hors écran
            if (bullet.rect.x < -50 or bullet.rect.x > 1550 or 
                bullet.rect.y < -50 or bullet.rect.y > 800):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                continue
            
            bullet.draw(screen)
            
    def draw(self, screen):
        # Si sprite existe
        if hasattr(self, "sprite") and self.sprite:
            # Calculer l'angle selon last_direction
            dx, dy = self.last_direction
            if dx != 0 or dy != 0:
                angle = math.degrees(math.atan2(-dy, dx))  # -dy car y augmente vers le bas
                rotated_sprite = pygame.transform.rotate(self.sprite, angle)
                # Ajuster la position pour centrer
                new_rect = rotated_sprite.get_rect(center=self.rect.center)
                screen.blit(rotated_sprite, new_rect.topleft)
            else:
                screen.blit(self.sprite, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        # Dessiner le shield si activé
        if self.shield:
            pygame.draw.circle(screen, (100, 200, 255), 
                             (self.rect.centerx, self.rect.centery), 
                             self.rect.width//2 + 5, 3)
        
        # Indicateur de direction
        dx, dy = self.last_direction
        if dx != 0 or dy != 0:
            length = (dx**2 + dy**2) ** 0.5
            dx /= length
            dy /= length
        dir_x = self.rect.centerx + dx * 25
        dir_y = self.rect.centery + dy * 25
        
        # Changer la couleur de l'indicateur si laser est activé
        indicator_color = (255, 100, 100) if self.laser else (255, 255, 0)
        pygame.draw.circle(screen, indicator_color, (int(dir_x), int(dir_y)), 5)