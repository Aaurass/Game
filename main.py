import pygame
import random
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bounce Through")

# Clock for frame rate
clock = pygame.time.Clock()

# Game variables
gravity = 0.7  # Increased gravity for faster fall
bird_x, bird_y = 50, HEIGHT // 2
bird_velocity = 0
bird_size = 30
pipe_width = 80
initial_pipe_gap = 150  # Initial gap size
pipe_speed = 6
pipe_spacing = 300  # Space between pipes
pipes = []
score = 0
highscore = 0
game_over = False
countdown = 0
mode = "easy"  # Default mode is "easy"
lives = 3  # Default lives for "easy" mode

# Load highscore from file
try:
    with open("highscore.json", "r") as file:
        highscore = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    highscore = 0

# Fonts
font = pygame.font.SysFont("Arial", 30)
big_font = pygame.font.SysFont("Arial", 50)

# Function to draw the bird
def draw_bird():
    pygame.draw.circle(screen, BLUE, (bird_x, int(bird_y)), bird_size // 2)

# Function to draw pipes
def draw_pipes():
    for pipe in pipes:
        pygame.draw.rect(screen, GREEN, (pipe["x"], 0, pipe_width, pipe["top"]))
        pygame.draw.rect(screen, GREEN, (pipe["x"], pipe["bottom"], pipe_width, HEIGHT - pipe["bottom"]))

# Function to detect collision
def detect_collision():
    global game_over, lives
    for pipe in pipes:
        if bird_x + bird_size // 2 > pipe["x"] and bird_x - bird_size // 2 < pipe["x"] + pipe_width:
            if bird_y - bird_size // 2 < pipe["top"] or bird_y + bird_size // 2 > pipe["bottom"]:
                if mode == "easy":
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                    return False  # Only end the game if lives are zero
                else:
                    game_over = True
                    return True
    if bird_y - bird_size // 2 <= 0 or bird_y + bird_size // 2 >= HEIGHT:
        if mode == "easy":
            lives -= 1
            if lives <= 0:
                game_over = True
            return False  # Only end the game if lives are zero
        else:
            game_over = True
            return True
    return False

# Function to show a button
def draw_button(text, x, y, width, height, color, text_color):
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

# Function to display the mode selection screen
def show_mode_selection():
    screen.fill(BLACK)
    draw_button("Easy Mode", WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, GRAY, BLACK)
    draw_button("Hard Mode", WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, GRAY, BLACK)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    
    if mouse_click[0] == 1:  # Left mouse button click
        if (WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and
            HEIGHT // 2 - 60 <= mouse_y <= HEIGHT // 2 - 10):
            return "easy"
        elif (WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and
              HEIGHT // 2 + 20 <= mouse_y <= HEIGHT // 2 + 70):
            return "hard"
    
    pygame.display.flip()
    clock.tick(30)

# Show mode selection at the start
mode = show_mode_selection()
lives = 3 if mode == "easy" else 1

# Add initial pipes
for i in range(3):
    top_height = random.randint(50, HEIGHT - initial_pipe_gap - 50)
    pipes.append({"x": WIDTH + i * pipe_spacing, "top": top_height, "bottom": top_height + initial_pipe_gap})

# Game loop
running = True
while running:
    screen.fill(BLACK)  # Set background color to black

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                bird_velocity = -12  # Reduced upward movement for each tap
            elif game_over:  # Restart game on tap after game over
                bird_y = HEIGHT // 2
                bird_velocity = 0
                pipes.clear()
                for i in range(3):
                    top_height = random.randint(50, HEIGHT - initial_pipe_gap - 50)
                    pipes.append({"x": WIDTH + i * pipe_spacing, "top": top_height, "bottom": top_height + initial_pipe_gap})
                score = 0
                game_over = False
                lives = 3 if mode == "easy" else 1

    if not game_over:
        # Bird movement
        bird_velocity += gravity
        bird_y += bird_velocity

        # Move pipes
        for pipe in pipes:
            pipe["x"] -= pipe_speed

        # Check for pipe removal and adding new pipes
        if pipes[0]["x"] < -pipe_width:
            pipes.pop(0)
            new_x_position = pipes[-1]["x"] + pipe_spacing
            top_height = random.randint(50, HEIGHT - initial_pipe_gap - 50)
            pipes.append({"x": new_x_position, "top": top_height, "bottom": top_height + initial_pipe_gap})
            score += 1  # Increase score when a pipe is passed

            # Increase difficulty as score increases
            if score % 5 == 0:  # Increase difficulty every 5 points
                pipe_speed += 1  # Increase pipe speed
                initial_pipe_gap = max(100, initial_pipe_gap - 10)  # Reduce gap size but keep it above 100

            # Update highscore if necessary
            if score > highscore:
                highscore = score
                with open("highscore.json", "w") as file:
                    json.dump(highscore, file)

        # Collision detection
        if detect_collision():
            if mode == "hard" or (mode == "easy" and lives <= 0):
                game_over = True

    # Draw game elements
    draw_bird()
    draw_pipes()

    # Draw score and highscore
    score_text = font.render(f"Score: {score}", True, WHITE)  # Change color to white for better visibility
    screen.blit(score_text, (10, 10))
    highscore_text = font.render(f"Highscore: {highscore}", True, WHITE)  # Change color to white for better visibility
    screen.blit(highscore_text, (WIDTH - 150, 10))

    if game_over:
        game_over_text = big_font.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        draw_button("Tap to Restart", WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50, GRAY, BLACK)

    # Refresh screen
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
