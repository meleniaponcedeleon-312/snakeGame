import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game window size
width = 600
height = 400

# Create game window
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game')

# Clock for controlling speed
clock = pygame.time.Clock()

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Snake properties
block_size = 20
initial_speed = 10  # Starting speed

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# Helper Functions
def score_display(score):
    value = score_font.render("Score: " + str(score), True, black)
    screen.blit(value, [10, 10])

def draw_snake(block_size, snake_list):
    for block in snake_list:
        pygame.draw.rect(screen, green, [block[0], block[1], block_size, block_size])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [width / 6, height / 3])

# Game loop
def game_loop():
    game_over = False
    game_close = False

    # Starting position
    x = width / 2
    y = height / 2

    x_change = 0
    y_change = 0

    snake_list = []
    length_of_snake = 1
    snake_speed = initial_speed  # Start speed

    # Random food coordinates
    food_x = round(random.randrange(0, width - block_size) / block_size) * block_size
    food_y = round(random.randrange(0, height - block_size) / block_size) * block_size

    while not game_over:
        while game_close:
            screen.fill(blue)
            message("You lost! Press Q-Quit or C-Play Again", red)
            score_display(length_of_snake - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()  # Restart the game

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = block_size
                    x_change = 0

        # Wall collision
        if x >= width or x < 0 or y >= height or y < 0:
            game_close = True

        # Move snake
        x += x_change
        y += y_change
        screen.fill(blue)

        # Draw food
        pygame.draw.rect(screen, red, [food_x, food_y, block_size, block_size])

        # Update snake
        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check self-collision
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        draw_snake(block_size, snake_list)
        score_display(length_of_snake - 1)
        pygame.display.update()

        # Check if snake eats food
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, width - block_size) / block_size) * block_size
            food_y = round(random.randrange(0, height - block_size) / block_size) * block_size
            length_of_snake += 1

            # Increase speed slightly each time food is eaten
            snake_speed = min(snake_speed + 1, 25)  # Cap max speed at 25

        # Control frame rate
        clock.tick(snake_speed)

    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    game_loop()
