import pygame
import sys
import os
import random
from powerup import PowerUp
from player import Player
from obstacle import Obstacle

# -------- INITIALISATION --------
pygame.init()
pygame.mixer.init()
def get_asset(path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, 'assets', path)

WIDTH, HEIGHT = 1500, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Arena 2 Players")

# Charger le background
background = pygame.image.load(get_asset("background.jpg")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Charger le logo de l'entreprise (assurez-vous d'avoir ce fichier dans le dossier assets)

logo = pygame.image.load(get_asset("MHG11logo.png")).convert_alpha()
logo = pygame.transform.scale(logo, (200, 150))  # Ajustez la taille selon votre logo
has_logo = True

# Musique
pygame.mixer.music.load(get_asset("music.mp3.mp3"))
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)
music_on = True

clock = pygame.time.Clock()
FPS = 60

# Police pour l'UI
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# États du jeu
MENU = "menu"
GAME = "game"
state = MENU

# Variables du jeu
game_over = False
winner = ""
powerups = []
last_power_time = pygame.time.get_ticks()
POWER_DELAY = 15000  # 15 secondes

# -------- FONCTIONS D'INITIALISATION --------
def create_players():
    """Crée et retourne les deux joueurs"""
    player1 = Player(100, 100, 50, 50, (0, 100, 255), "ZQSD", "J1", get_asset("trank_1png.png"))
    player2 = Player(1440, 690, 50, 50, (255, 100, 0), "ARROWS", "J2", get_asset("trank_2.png.png"))
    return player1, player2

player1, player2 = create_players()

# -------- CRÉER OBSTACLES --------
wall_image = get_asset("wall.png")

obstacles = [
    # Murs extérieurs
    Obstacle(0, 0, WIDTH, 20, wall_image),          # Haut
    Obstacle(0, HEIGHT-20, WIDTH, 20, wall_image),  # Bas
    Obstacle(0, 0, 20, HEIGHT, wall_image),         # Gauche
    Obstacle(WIDTH-20, 0, 20, HEIGHT, wall_image),  # Droite
    
    # Structure principale
    Obstacle(750, 100, 20, 550, wall_image),        # Mur central
    
    # Sections gauches
    Obstacle(200, 100, 400, 20, wall_image),
    Obstacle(200, 100, 20, 200, wall_image),
    Obstacle(200, 300, 200, 20, wall_image),
    Obstacle(400, 300, 20, 200, wall_image),
    Obstacle(300, 500, 200, 20, wall_image),
    
    # Sections droites
    Obstacle(900, 100, 400, 20, wall_image),
    Obstacle(1300, 100, 20, 200, wall_image),
    Obstacle(1100, 300, 200, 20, wall_image),
    Obstacle(1090, 300, 20, 200, wall_image),
    Obstacle(1000, 500, 200, 20, wall_image),
    
    # Obstacles horizontaux
    Obstacle(100, 200, 300, 10, wall_image),
    Obstacle(100, 400, 300, 10, wall_image),
    Obstacle(1100, 200, 300, 10, wall_image),
    Obstacle(1100, 400, 300, 10, wall_image),
    
    # Barrières centrales
    Obstacle(600, 300, 100, 10, wall_image),
    Obstacle(800, 300, 100, 10, wall_image),
    Obstacle(700, 200, 10, 100, wall_image),
    Obstacle(700, 450, 10, 100, wall_image),
    
    # Cachettes
    Obstacle(100, 600, 200, 10, wall_image),
    Obstacle(100, 600, 10, 100, wall_image),
    Obstacle(1200, 600, 200, 10, wall_image),
    Obstacle(1390, 600, 10, 100, wall_image),
    
    # Passages
    Obstacle(500, 100, 10, 200, wall_image),
    Obstacle(500, 450, 10, 200, wall_image),
    Obstacle(990, 100, 10, 200, wall_image),
    Obstacle(990, 450, 10, 200, wall_image),
    
    # Zones centrales
    Obstacle(650, 500, 100, 10, wall_image),
    Obstacle(650, 150, 100, 10, wall_image),
]

def apply_power(player, enemy, ptype):
    """Applique l'effet d'un power-up"""
    if ptype == "rocket":
        if not enemy.shield:
            enemy.hp -= 30
    elif ptype == "heart":
        player.hp = min(100, player.hp + 50)
    elif ptype == "shield":
        player.shield = True
        player.shield_time = pygame.time.get_ticks()
    elif ptype == "laser":
        player.laser = True
        player.laser_time = pygame.time.get_ticks()

def draw_ui():
    """Dessine l'interface utilisateur"""
    bar_width = 250
    bar_height = 25
    
    # Vie joueur 1
    pygame.draw.rect(screen, (100, 100, 100), (30, 30, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (30, 30, player1.hp * 2.5, bar_height))
    
    # Vie joueur 2
    pygame.draw.rect(screen, (100, 100, 100), (WIDTH - bar_width - 30, 30, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 255, 0), (WIDTH - bar_width - 30 + (250 - player2.hp * 2.5), 30, player2.hp * 2.5, bar_height))
    
    # Texte des HP
    hp1_text = font.render(f"{player1.hp} HP", True, (255, 255, 255))
    hp2_text = font.render(f"{player2.hp} HP", True, (255, 255, 255))
    screen.blit(hp1_text, (40, 60))
    screen.blit(hp2_text, (WIDTH - 120, 60))
    
    # Noms des joueurs
    name1_text = font.render(f"{player1.name}", True, (200, 200, 255))
    name2_text = font.render(f"{player2.name}", True, (255, 200, 200))
    screen.blit(name1_text, (30, 5))
    screen.blit(name2_text, (WIDTH - 150, 5))
    
    # Contrôles
    controls1 = font.render("", True, (200, 200, 255))
    controls2 = font.render("", True, (255, 200, 200))
    screen.blit(controls1, (20, HEIGHT - 40))
    screen.blit(controls2, (WIDTH - 300, HEIGHT - 40))

def draw_powerup_info():
    """Affiche les informations sur les power-ups actifs"""
    y_offset = 100
    
    # Joueur 1
    if player1.shield:
        shield_text = font.render("SHIELD ACTIF", True, (100, 200, 255))
        screen.blit(shield_text, (30, y_offset))
        y_offset += 30
    
    if player1.laser:
        laser_text = font.render("LASER ACTIF", True, (255, 100, 100))
        screen.blit(laser_text, (30, y_offset))
        y_offset += 30
    
    # Joueur 2
    y_offset = 100
    if player2.shield:
        shield_text = font.render("SHIELD ACTIF", True, (100, 200, 255))
        screen.blit(shield_text, (WIDTH - 150, y_offset))
        y_offset += 30
    
    if player2.laser:
        laser_text = font.render("LASER ACTIF", True, (255, 100, 100))
        screen.blit(laser_text, (WIDTH - 150, y_offset))
        y_offset += 30
    
    # Timer pour power-ups
    current_time = pygame.time.get_ticks()
    
    # Shield timer joueur 1
    if player1.shield:
        time_left = max(0, 10000 - (current_time - player1.shield_time))
        timer_text = font.render(f"Shield: {time_left//1000}.{(time_left%1000)//100}s", 
                               True, (100, 200, 255))
        screen.blit(timer_text, (30, HEIGHT - 80))
    
    # Laser timer joueur 1
    if player1.laser:
        time_left = max(0, 10000 - (current_time - player1.laser_time))
        timer_text = font.render(f"Laser: {time_left//1000}.{(time_left%1000)//100}s", 
                               True, (255, 100, 100))
        screen.blit(timer_text, (30, HEIGHT - 110))
    
    # Shield timer joueur 2
    if player2.shield:
        time_left = max(0, 10000 - (current_time - player2.shield_time))
        timer_text = font.render(f"Shield: {time_left//1000}.{(time_left%1000)//100}s", 
                               True, (100, 200, 255))
        screen.blit(timer_text, (WIDTH - 150, HEIGHT - 80))
    
    # Laser timer joueur 2
    if player2.laser:
        time_left = max(0, 10000 - (current_time - player2.laser_time))
        timer_text = font.render(f"Laser: {time_left//1000}.{(time_left%1000)//100}s", 
                               True, (255, 100, 100))
        screen.blit(timer_text, (WIDTH - 150, HEIGHT - 110))

def show_winner(winner):
    """Affiche l'écran de fin de jeu"""
    screen.fill((0, 0, 0))
    winner_text = big_font.render(f"{winner} GAGNE!", True, (255, 255, 0))
    restart_text = font.render("Appuyez sur R pour rejouer", True, (255, 255, 255))
    
    # Afficher le logo sur l'écran de fin
    if has_logo:
        logo_rect = logo.get_rect(center=(WIDTH//2, HEIGHT//2 - 150))
        screen.blit(logo, logo_rect)
    
    screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
        clock.tick(FPS)

def draw_menu():
    """Dessine le menu principal avec le logo"""
    screen.blit(background, (0, 0))
    
    # Afficher le logo en haut au centre
    if has_logo:
        logo_rect = logo.get_rect(center=(WIDTH//2, 100))
        # Ajouter un fond au logo
    
        screen.blit(logo, logo_rect)

    title = big_font.render("BATTLE TANK ARENA", True, (255, 200, 0))
    play_text = font.render("PLAY", True, (255, 255, 255))
    music_text = font.render("MUSIC : ON" if music_on else "MUSIC : OFF", True, (255, 255, 255))

    controls1 = font.render("J1 : Z Q S D + CTRL", True, (200, 200, 255))
    controls2 = font.render("J2 : ↑ ↓ ← → + SPACE", True, (255, 200, 200))

    screen.blit(title, (WIDTH//2 - title.get_width()//2, 200 if has_logo else 120))

    # Bouton PLAY
    play_rect = pygame.Rect(WIDTH//2 - 120, 300 if has_logo else 300, 240, 60)
    pygame.draw.rect(screen, (50, 200, 50), play_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), play_rect, 3, border_radius=10)  # Bordure
    screen.blit(play_text, (play_rect.centerx - play_text.get_width()//2,
                            play_rect.centery - play_text.get_height()//2))

    # Bouton MUSIC
    music_rect = pygame.Rect(WIDTH//2 - 120, 380 if has_logo else 380, 240, 50)
    pygame.draw.rect(screen, (70, 70, 200), music_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), music_rect, 3, border_radius=10)  # Bordure
    screen.blit(music_text, (music_rect.centerx - music_text.get_width()//2,
                             music_rect.centery - music_text.get_height()//2))

    screen.blit(controls1, (WIDTH//2 - 150, 480 if has_logo else 480))
    screen.blit(controls2, (WIDTH//2 - 150, 520 if has_logo else 520))
    
    # Copyright ou nom de l'entreprise en bas
    copyright_text = font.render("", True, (150, 150, 150))
    screen.blit(copyright_text, (WIDTH//2 - copyright_text.get_width()//2, HEIGHT - 40))

    return play_rect, music_rect

def draw_game_ui():
    """Dessine l'UI pendant le jeu avec le logo en petit"""
    draw_ui()
    draw_powerup_info()
    
    # Afficher un petit logo en bas au centre pendant le jeu
    if has_logo:
        small_logo = pygame.transform.scale(logo, (80, 60))
        screen.blit(small_logo, (WIDTH//2 - 40, HEIGHT - 70))

# -------- BOUCLE PRINCIPALE --------
running = True
while running:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()
    
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if play_rect.collidepoint(mouse_pos):
                state = GAME
                # Réinitialiser le jeu
                player1, player2 = create_players()
                powerups.clear()
                game_over = False
                winner = ""
            elif music_rect.collidepoint(mouse_pos):
                music_on = not music_on
                if music_on:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.stop()
    
    # Affichage selon l'état
    if state == MENU:
        play_rect, music_rect = draw_menu()
    
    elif state == GAME:
        screen.blit(background, (0, 0))
        
        if not game_over:
            keys = pygame.key.get_pressed()
            
            # Mouvement des joueurs
            player1.move(keys, obstacles)
            player2.move(keys, obstacles)
            
            # Gestion des tirs
            player1.handle_shooting(keys)
            player2.handle_shooting(keys)
            
            # Gestion des power-ups
            if current_time - last_power_time > POWER_DELAY and len(powerups) == 0:
                x = random.randint(50, WIDTH-90)
                y = random.randint(50, HEIGHT-90)
                powerups.append(PowerUp(x, y))
                last_power_time = current_time
            
            # Collision avec les power-ups
            for powerup in powerups[:]:
                if player1.rect.colliderect(powerup.rect):
                    apply_power(player1, player2, powerup.type)
                    powerups.remove(powerup)
                elif player2.rect.colliderect(powerup.rect):
                    apply_power(player2, player1, powerup.type)
                    powerups.remove(powerup)
            
            # Dessin des obstacles
            for obs in obstacles:
                obs.draw(screen)
            
            # Dessin des power-ups
            for powerup in powerups:
                powerup.draw(screen)
            
            # Mise à jour et dessin des balles
            player1.update_bullets(screen, obstacles, player2)
            player2.update_bullets(screen, obstacles, player1)
            
            # Dessin des joueurs
            player1.draw(screen)
            player2.draw(screen)
            
            # UI avec logo
            draw_game_ui()
            
            # Vérifier fin de jeu
            if player1.hp <= 0:
                game_over = True
                winner = "JOUEUR 2"
                player1.hp = 0
            elif player2.hp <= 0:
                game_over = True
                winner = "JOUEUR 1"
                player2.hp = 0
        
        else:
            # Écran de fin de jeu
            if show_winner(winner):
                # Réinitialiser le jeu
                player1, player2 = create_players()
                powerups.clear()
                game_over = False
                winner = ""
    
    pygame.display.flip()

pygame.quit()