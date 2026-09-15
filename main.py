import base64
import io
import pygame


pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Platformer")
clock = pygame.time.Clock()

# Bigger player: width 60, height 75.
# Start with the feet just above the ground platform.
player = pygame.Rect(50, 275, 60, 75)
player_velocity_y = 0
on_ground = False

# Sprite image.
# Paste the complete data:image/png;base64,... text into sprite_data.txt.
# This loader removes the "data:image/png;base64," label, decodes the
# Base64 text, and turns the PNG bytes into a Pygame image.
try:
    with open("sprite_data.txt", "r", encoding="utf-8") as sprite_file:
        sprite_data = sprite_file.read().strip()

    if sprite_data.startswith("data:"):
        sprite_data = sprite_data.split(",", 1)[1]

    image_bytes = base64.b64decode(sprite_data)
    player_image = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
    player_image = pygame.transform.scale(player_image, player.size)
except (pygame.error, FileNotFoundError, ValueError, base64.binascii.Error):
    # The red rectangle keeps the game working if the sprite is missing.
    player_image = None

# The ground has a small hole from x=280 to x=340.
platforms = [
    pygame.Rect(0, 350, 280, 50),
    pygame.Rect(340, 350, WIDTH - 340, 50),
    pygame.Rect(100, 270, 150, 20),
    pygame.Rect(350, 220, 150, 20),
]

GRAVITY = 0.5
JUMP_SPEED = -10
MOVE_SPEED = 5

running = True
move_left = False
move_right = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                move_left = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                move_right = True
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                move_left = False
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                move_right = False

    keys = pygame.key.get_pressed()

    player_velocity_x = 0
    if move_left or keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_velocity_x -= MOVE_SPEED
    if move_right or keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_velocity_x += MOVE_SPEED

    if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and on_ground:
        player_velocity_y = JUMP_SPEED
        on_ground = False

    # Move horizontally. The player can move across the hole.
    player.x += player_velocity_x
    player.x = max(0, min(player.x, WIDTH - player.width))

    # Move vertically, then resolve collisions with platforms.
    previous_bottom = player.bottom
    player_velocity_y += GRAVITY
    player.y += round(player_velocity_y)
    on_ground = False

    for platform in platforms:
        falling_onto_platform = (
            player_velocity_y >= 0
            and previous_bottom <= platform.top
            and player.bottom >= platform.top
            and player.right > platform.left
            and player.left < platform.right
        )
        if falling_onto_platform:
            player.bottom = platform.top
            player_velocity_y = 0
            on_ground = True

    screen.fill((135, 206, 235))

    for platform in platforms:
        pygame.draw.rect(screen, (100, 180, 100), platform)

    if player_image:
        screen.blit(player_image, player)
    else:
        pygame.draw.rect(screen, (220, 80, 80), player)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
