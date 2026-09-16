import asyncio
import base64
import io

import pygame


WIDTH, HEIGHT = 600, 400
PLAYER_SIZE = (116, 64)
GRAVITY = 0.5
JUMP_SPEED = -10
MOVE_SPEED = 5
SPAWN_POSITION = (50, 350 - PLAYER_SIZE[1])
CUPCAKE_SIZE = 24


def draw_cupcake(surface, rect):
    """Draw a small cupcake collectible."""
    pygame.draw.rect(surface, (190, 115, 70), (rect.x + 3, rect.y + 9, rect.width - 6, rect.height - 9))
    pygame.draw.polygon(
        surface,
        (255, 150, 190),
        [(rect.x + 2, rect.y + 10), (rect.centerx, rect.y + 2), (rect.right - 2, rect.y + 10)],
    )
    pygame.draw.circle(surface, (255, 210, 225), (rect.centerx, rect.y + 6), 3)


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
    font = pygame.font.Font(None, 28)

    player = pygame.Rect(*SPAWN_POSITION, *PLAYER_SIZE)
    score = 0
    cupcakes = [
        pygame.Rect(180, 245, CUPCAKE_SIZE, CUPCAKE_SIZE),
        pygame.Rect(410, 195, CUPCAKE_SIZE, CUPCAKE_SIZE),
        pygame.Rect(520, 320, CUPCAKE_SIZE, CUPCAKE_SIZE),
    ]
    player_velocity_y = 0
    on_ground = True
    player_image = load_player_image(player.size)

    platforms = [
        pygame.Rect(0, 350, 240, 50),
        pygame.Rect(360, 350, WIDTH - 360, 50),
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

        player.x += player_velocity_x
        player.x = max(0, min(player.x, WIDTH - player.width))


        previous_bottom = player.bottom
        player_velocity_y += GRAVITY
        player.y += round(player_velocity_y)
        on_ground = False

        # Respawn the sprite if it falls below the level.
        if player.top > HEIGHT:
            player.topleft = SPAWN_POSITION
            player_velocity_y = 0
            on_ground = True

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

        # Collect cupcakes when the player touches them.
        collected_cupcakes = [cupcake for cupcake in cupcakes if player.colliderect(cupcake)]
        for cupcake in collected_cupcakes:
            cupcakes.remove(cupcake)
            score += 1

        screen.fill((135, 206, 235))

        for platform in platforms:
            pygame.draw.rect(screen, (100, 180, 100), platform)

        for cupcake in cupcakes:
            draw_cupcake(screen, cupcake)

        score_text = font.render(f"Cupcakes: {score}", True, (40, 40, 40))
        screen.blit(score_text, (10, 10))

        if player_image is not None:
            screen.blit(player_image, player)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
