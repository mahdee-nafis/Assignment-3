import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = 12
PROJECTILE_SPEED = 10
ENEMY_SPEED = 2
COLLECTIBLE_SIZE = 20
BOSS_HEALTH = 200

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Animal Hero Adventure")
clock = pygame.time.Clock()

# Font for score and health
font = pygame.font.SysFont("Arial", 30)

# Player Class (Hero)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (100, SCREEN_HEIGHT - 100)
        self.speed = PLAYER_SPEED
        self.velocity = 0
        self.health = 100
        self.lives = 3
        self.is_jumping = False
        self.jump_count = 10

    def update(self):
        keys = pygame.key.get_pressed()

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Jumping
        if not self.is_jumping:
            if keys[pygame.K_SPACE]:
                self.velocity = -JUMP_STRENGTH
                self.is_jumping = True
        else:
            self.velocity += GRAVITY
            self.rect.y += self.velocity

        # Prevent player from going out of screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.is_jumping = False
            self.velocity = 0

    def shoot(self):
        projectile = Projectile(self.rect.centerx, self.rect.top)
        return projectile

# Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = PROJECTILE_SPEED

    def update(self):
        self.rect.x += self.speed
        if self.rect.right > SCREEN_WIDTH:
            self.kill()

# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 50
        self.speed = ENEMY_SPEED

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

# Collectible Class
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        self.image = pygame.Surface((COLLECTIBLE_SIZE, COLLECTIBLE_SIZE))
        if self.type == 'health':
            self.image.fill(GREEN)
        else:
            self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.rect.x -= 2
        if self.rect.right < 0:
            self.kill()

# Level class with Boss Enemy
class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.Surface((100, 100))
        self.image.fill((255, 165, 0))  # Orange boss color
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = BOSS_HEALTH
        self.speed = 1

# Game Over Screen
def game_over():
    game_over_text = font.render("GAME OVER! Press R to Restart", True, (255, 255, 255))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()

# Main Game Loop
def main():
    # Create sprite groups
    player = Player()
    all_sprites = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    collectibles = pygame.sprite.Group()

    all_sprites.add(player)

    score = 0
    level = 1
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Shoot projectile
                    projectile = player.shoot()
                    all_sprites.add(projectile)
                    projectiles.add(projectile)

        # Update all sprites
        all_sprites.update()
        projectiles.update()
        enemies.update()
        collectibles.update()

        # Collision detection
        for projectile in projectiles:
            for enemy in enemies:
                if projectile.rect.colliderect(enemy.rect):
                    enemy.take_damage(25)
                    score += 10
                    projectile.kill()

        # Spawn enemies and collectibles
        if random.randint(1, 100) < 2:
            enemy = Enemy(SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT - 100))
            all_sprites.add(enemy)
            enemies.add(enemy)

        if random.randint(1, 100) < 3:
            collectible = Collectible(SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT - 100), 'health')
            all_sprites.add(collectible)
            collectibles.add(collectible)

        # Drawing
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(10, 10, 200, 20))  # Health bar
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(10, 10, player.health * 2, 20))  # Player health
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 10, 10))

        pygame.display.update()

        clock.tick(FPS)

# Start the game
main()
