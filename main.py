import asyncio
import base64
import io

import pygame


WIDTH, HEIGHT = 600, 400
# Keep the player narrower than the 60-pixel hole so they can fall through it.
PLAYER_SIZE = (55, 75)
GRAVITY = 0.5
JUMP_SPEED = -10
MOVE_SPEED = 5


def load_player_image(player_size):
    """Load the Base64 PNG from sprite_data.txt, if available."""
    try:
        with open("sprite_data.txt", "r", encoding="utf-8") as sprite_file:
            sprite_data = sprite_file.read().strip()

        if sprite_data.startswith("data:"):
            sprite_data = sprite_data.split(",", 1)[1]

        image_bytes = base64.b64decode(sprite_data)
        image = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
        return pygame.transform.scale(image, player_size)
    except (OSError, ValueError, base64.binascii.Error, pygame.error):
        return None


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rehans trip to the store")
    clock = pygame.time.Clock()

    # Start on the left platform: its top is y=350.
    player = pygame.Rect(50, 350 - PLAYER_SIZE[1], *PLAYER_SIZE)
    player_velocity_y = 0
    on_ground = True
    player_image = load_player_image(player.size)

    # The gap between x=280 and x=340 is a hole the player can fall through.
    platforms = [
        pygame.Rect(0, 350, 280, 50),
        pygame.Rect(340, 350, WIDTH - 340, 50),
        pygame.Rect(100, 270, 150, 20),
        pygame.Rect(350, 220, 150, 20),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player_velocity_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_velocity_x -= MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_velocity_x += MOVE_SPEED

        if (
            keys[pygame.K_UP]
            or keys[pygame.K_w]
            or keys[pygame.K_SPACE]
        ) and on_ground:
            player_velocity_y = JUMP_SPEED
            on_ground = False

        # Move horizontally and keep the player inside the screen.
        player.x += player_velocity_x
        player.x = max(0, min(player.x, WIDTH - player.width))

        # Move vertically and resolve landing collisions.
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

        if player_image is not None:
            screen.blit(player_image, player)
        else:
            pygame.draw.rect(screen, (220, 80, 80), player)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
