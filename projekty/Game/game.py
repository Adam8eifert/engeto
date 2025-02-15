import pygame
import random

# Inicializace Pygame
pygame.init()

# Konstanty
WIDTH, HEIGHT = 800, 600
FPS = 60

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Inicializace okna
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fantasy Adventure")
clock = pygame.time.Clock()

# Vytvoření obrázků pro hrdinu a monstrum
hero_img = pygame.Surface((50, 50), pygame.SRCALPHA)
hero_img.fill((0, 0, 255))  # Modrá postava
pygame.image.save(hero_img, "hero.png")

monster_img = pygame.Surface((50, 50), pygame.SRCALPHA)
monster_img.fill((255, 0, 0))  # Červené monstrum
pygame.image.save(monster_img, "monster.png")

# Načtení obrázků
hero_img = pygame.image.load("hero.png")
monster_img = pygame.image.load("monster.png")

# Třída hráče
class Hero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = hero_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.speed = 5
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

# Třída nepřátel
class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = monster_img
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.randint(1, 3)
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-100, -40)
            self.rect.x = random.randint(0, WIDTH)

# Skóre
score = 0
font = pygame.font.Font(None, 36)

def draw_score():
    score_text = font.render(f"Skóre: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

# Skupiny sprite objektů
all_sprites = pygame.sprite.Group()
monsters = pygame.sprite.Group()
hero = Hero()
all_sprites.add(hero)

# Generování nepřátel
for _ in range(5):
    monster = Monster(random.randint(0, WIDTH), random.randint(-100, -40))
    all_sprites.add(monster)
    monsters.add(monster)

# Herní smyčka
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Aktualizace objektů
    all_sprites.update()
    
    # Kontrola kolize
    hits = pygame.sprite.spritecollide(hero, monsters, True)
    for hit in hits:
        score += 1
        new_monster = Monster(random.randint(0, WIDTH), random.randint(-100, -40))
        all_sprites.add(new_monster)
        monsters.add(new_monster)
    
    # Vykreslení objektů
    screen.fill(WHITE)
    all_sprites.draw(screen)
    draw_score()
    pygame.display.flip()

pygame.quit()
