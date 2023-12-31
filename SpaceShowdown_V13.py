import pygame
import sys
import random
import os
import pickle

# Initialize pygame
pygame.init()

# Set display mode to be resizable
screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)

# Get the current display info
screen_info = pygame.display.Info()

# Calculate the dimensions for the windowed full screen
target_width = screen_info.current_w
target_height = screen_info.current_h
aspect_ratio = target_width / target_height

# Set initial screen dimensions to be the calculated size
screen_width = target_width
screen_height = target_height

# Load images
background_image = pygame.image.load("background.jpg")
ship_image = pygame.image.load("ship.png")
enemy_image = pygame.image.load("enemy.png")
projectile_image = pygame.image.load("projectile.png")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
orange = (255, 165, 0)

# Define fonts
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 72)

# Initialize clock
clock = pygame.time.Clock()

# Define game states
START_SCREEN = 0
GAME_RUNNING = 1
GAME_OVER = 2
LEADERBOARD = 3
game_state = START_SCREEN

# Load high scores from file if it exists
scores_file = "high_scores.pkl"
high_scores = {}
if os.path.exists(scores_file):
    with open(scores_file, "rb") as f:
        high_scores = pickle.load(f)

def save_high_scores():
    with open(scores_file, "wb") as f:
        pickle.dump(high_scores, f)

def generate_enemies(round_num):
    new_enemies = []
    for _ in range(num_enemies):
        enemy_speed = random.uniform(1, 3) + (round_num * 0.2)
        enemy_x = random.randint(0, screen_width - enemy_width)
        enemy_y = random.randint(-600, -enemy_height)
        enemy_movement_speed = random.uniform(0.5, 1.5)
        new_enemies.append([enemy_x, enemy_y, enemy_speed, enemy_movement_speed])
    return new_enemies

def display_text(text, x, y, color=white, font=None):
    if font is None:
        font = pygame.font.Font(None, 36)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Player ship dimensions and initial position
player_width = 50
player_height = 50
player_x = (screen_width - player_width) // 2
player_y = screen_height - player_height - 10
player_speed = 5

# Number of enemies and their dimensions
num_enemies = 25
enemy_width = 50
enemy_height = 50

# Initialize enemy projectiles
enemy_projectiles = []
enemy_projectile_speed = 7

# Initialize other game variables
enemies = generate_enemies(1)
running = True
score = 0
streak = 0
round_bonus = 0
current_round = 1
lives = 3
new_life_ship_x = -100
new_life_ship_y = -100
player_invincible = False
invincible_frames = 0
invincible_duration = 60
projectile_speed = 10
projectile = None
projectile_fired = False
initials_text = ""

# Initialize variables for enemy movement patterns
movement_direction = 1  # 1 for right, -1 for left
movement_amplitude = 20

# New variables for spinning animation and ship visibility
player_spinning = False
player_visible = True
spin_angle = 0
spin_direction = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # Update screen dimensions when window is resized
            screen_width = event.w
            screen_height = event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    
    keys = pygame.key.get_pressed()

    if game_state == START_SCREEN:
        screen.fill(black)
        title_text = title_font.render("Space Showdown", True, white)
        start_text = font.render("Press Enter to Start", True, white)
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, screen_height // 2 - title_text.get_height() // 2))
        screen.blit(start_text, (screen_width // 2 - start_text.get_width() // 2, screen_height // 2 + title_text.get_height() // 2))
        
        if keys[pygame.K_RETURN]:
            score = 0
            streak = 0
            round_bonus = 0
            game_state = GAME_RUNNING
            enemies = generate_enemies(1)
            player_x = (screen_width - player_width) // 2
            player_y = screen_height - player_height - 10
            current_round = 1
            projectiles = []

    elif game_state == GAME_RUNNING:
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed

        player_x = max(0, min(screen_width - player_width, player_x))

        if keys[pygame.K_SPACE] and not projectile_fired:
            projectile = [player_x + player_width // 2, player_y]
            projectile_fired = True

        if projectile:
            projectile[1] -= projectile_speed
            if projectile[1] < 0:
                projectile = None
                projectile_fired = False

        enemies_to_remove = []
        for enemy in enemies:
            enemy_speed = enemy[2]
            enemy[1] += enemy_speed
            enemy_movement_speed = enemy[3]
            enemy[0] += movement_direction * enemy_movement_speed
            
            if projectile:
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_width, enemy_height)
                projectile_rect = pygame.Rect(projectile[0], projectile[1], 1, 1)
                if enemy_rect.colliderect(projectile_rect):
                    enemies_to_remove.append(enemy)
                    projectile = None
                    projectile_fired = False
                    streak += 1
                    score += streak * 10

                    if streak % 5 == 0:
                        round_bonus += 500 * streak // 5

            if enemy[1] >= screen_height:
                enemy[1] = -enemy_height
                enemy[0] = random.randint(0, screen_width - enemy_width)
                enemy_movement_speed = random.uniform(0.5, 1.5)
                enemy[3] = enemy_movement_speed

            if not player_invincible:
                player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
                enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_width, enemy_height)
                if player_rect.colliderect(enemy_rect):
                    lives -= 1
                    if lives > 0:
                        player_invincible = True
                        invincible_frames = invincible_duration
                        new_life_ship_x = player_x
                        new_life_ship_y = player_y
                    else:
                        game_state = GAME_OVER

        if player_invincible:
            invincible_frames -= 1
            if invincible_frames <= 0:
                player_invincible = False
                new_life_ship_x = -100
                new_life_ship_y = -100

        for enemy in enemies_to_remove:
            enemies.remove(enemy)

        if len(enemies) == 0:
            score += round_bonus
            round_bonus = 0
            current_round += 1
            enemies = generate_enemies(current_round)

            # Update enemy movement pattern
            if current_round % 2 == 0:
                movement_direction *= -1
            for enemy in enemies:
                enemy[0] += movement_direction * movement_amplitude

        screen.fill(black)
        screen.blit(background_image, (0, 0))
        screen.blit(ship_image, (player_x, player_y))

        for enemy in enemies:
            screen.blit(enemy_image, (enemy[0], enemy[1]))

        if projectile:
            pygame.draw.circle(screen, red, (projectile[0], projectile[1]), 5)

        display_text("Score: " + str(score), 10, 10)
        display_text("Streak: " + str(streak), 10, 50)
        display_text("Round Bonus: " + str(round_bonus), 10, 90)
        display_text("Round: " + str(current_round), 10, 130)
        display_text("Lives: " + str(lives), screen_width - 150, 10)


        # Check for enemy projectiles hitting the player
        for proj in enemy_projectiles:
            proj[1] += enemy_projectile_speed
            if not player_invincible and not player_spinning:
                player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
                projectile_rect = pygame.Rect(proj[0], proj[1], 1, 1)
                if player_rect.colliderect(projectile_rect):
                    lives -= 1
                    if lives > 0:
                        player_visible = False
                        player_spinning = True
                        spin_angle = 0
                        spin_direction = 1
                        player_invincible = True
                        invincible_frames = invincible_duration
                        streak = 0
                    else:
                        game_state = GAME_OVER
            if proj[1] > screen_height:
                enemy_projectiles.remove(proj)

        # Enemy ship shooting logic for round 3 onward
        if current_round >= 3:
            for enemy in enemies:
                if random.random() < 0.01:
                    enemy_proj_x = enemy[0] + enemy_width // 2
                    enemy_proj_y = enemy[1] + enemy_height
                    enemy_projectiles.append([enemy_proj_x, enemy_proj_y])

        # ... (Other game logic)

    elif game_state == GAME_OVER:
        screen.fill(black)
        game_over_text = title_font.render("Game Over", True, red)
        initials_prompt = font.render("Enter your initials (3 characters):", True, white)
        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - game_over_text.get_height() // 2))
        screen.blit(initials_prompt, (screen_width // 2 - initials_prompt.get_width() // 2, screen_height // 2 + 30))
        initials_render = font.render(initials_text, True, white)
        screen.blit(initials_render, (screen_width // 2 - initials_render.get_width() // 2, screen_height // 2 + 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(initials_text) == 3:
                    high_scores[initials_text] = score
                    save_high_scores()
                    game_state = LEADERBOARD

                elif event.key == pygame.K_BACKSPACE:
                    initials_text = initials_text[:-1]
                elif len(initials_text) < 3:
                    initials_text += event.unicode
        
    elif game_state == LEADERBOARD:
        screen.fill(black)
        leaderboard_title = title_font.render("High Scores", True, white)
        screen.blit(leaderboard_title, (screen_width // 2 - leaderboard_title.get_width() // 2, 50))
        sorted_scores = sorted(high_scores.items(), key=lambda x: x[1], reverse=True)
        y_position = 150
        for entry in sorted_scores[:10]:
            initials, score = entry
            leaderboard_entry = font.render(initials + " - " + str(score), True, white)
            screen.blit(leaderboard_entry, (screen_width // 2 - leaderboard_entry.get_width() // 2, y_position))
            y_position += 40

        restart_text = font.render("Press C to restart game", True, white)
        screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, y_position + 40))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    game_state = START_SCREEN
                    lives = 3
                    score = 0
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
