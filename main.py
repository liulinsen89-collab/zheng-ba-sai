import pygame
import random
import sys
import os

# Configuration
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 40)
FIGHTER1_COLOR = (50, 150, 255)
FIGHTER2_COLOR = (255, 100, 100)
HEALTH_BG = (60, 60, 60)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')
F1_IMG = os.path.join(ASSETS_DIR, 'fighter1.png')
F2_IMG = os.path.join(ASSETS_DIR, 'fighter2.png')
BG_IMG = os.path.join(ASSETS_DIR, 'background.png')

class Fighter:
    def __init__(self, x, y, facing=1, img_path=None, color=(255,255,255)):
        self.x = x
        self.y = y
        self.w = 64
        self.h = 96
        self.vx = 0
        self.vy = 0
        self.speed = 3
        self.on_ground = True
        self.facing = facing  # 1 = right, -1 = left
        self.max_hp = 100
        self.hp = self.max_hp
        self.color = color
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60  # frames
        self.attack_range = 60
        self.attack_damage = 8
        self.hit_flash = 0

        self.image = None
        if img_path and os.path.exists(img_path):
            try:
                img = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(img, (self.w, self.h))
            except Exception:
                self.image = None

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self):
        # apply velocity
        self.x += self.vx
        # keep inside screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.w))

        # cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def ai_step(self, opponent):
        # Simple AI: approach opponent, sometimes jump (not implemented), and occasionally attack
        if opponent.x > self.x + 10:
            self.vx = self.speed
            self.facing = 1
        elif opponent.x < self.x - 10:
            self.vx = -self.speed
            self.facing = -1
        else:
            self.vx = 0

        # Randomly pause or backstep
        r = random.random()
        if r < 0.02:
            self.vx = 0
        elif r < 0.04:
            # small backstep
            self.vx = -self.facing * self.speed

        # Attack if in range
        dist = abs((self.x + self.w/2) - (opponent.x + opponent.w/2))
        if dist <= self.attack_range and self.attack_cooldown == 0:
            self.perform_attack(opponent)

    def perform_attack(self, opponent):
        # attack lands immediately if in range
        dist = abs((self.x + self.w/2) - (opponent.x + opponent.w/2))
        if dist <= self.attack_range:
            opponent.hp -= self.attack_damage
            opponent.hit_flash = 6
        self.attack_cooldown = self.attack_cooldown_max

    def draw(self, surface):
        r = self.rect()
        if self.image:
            img = self.image
            if self.facing == -1:
                img = pygame.transform.flip(self.image, True, False)
            surface.blit(img, r)
        else:
            col = self.color
            if self.hit_flash > 0:
                # flash white when hit
                col = (255,255,255)
            pygame.draw.rect(surface, col, r)

        # HP bar
        bar_w = 120
        bar_h = 10
        bar_x = r.centerx - bar_w//2
        bar_y = r.top - 18
        pygame.draw.rect(surface, HEALTH_BG, (bar_x, bar_y, bar_w, bar_h))
        hp_w = max(0, int(bar_w * (self.hp / self.max_hp)))
        pygame.draw.rect(surface, (200,30,30), (bar_x, bar_y, hp_w, bar_h))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Zheng-Ba-Sai (AI vs AI)')
        self.clock = pygame.time.Clock()
        self.running = True

        # load background if available
        self.background = None
        if os.path.exists(BG_IMG):
            try:
                bg = pygame.image.load(BG_IMG).convert()
                self.background = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception:
                self.background = None

        # fighters
        f1_img = F1_IMG if os.path.exists(F1_IMG) else None
        f2_img = F2_IMG if os.path.exists(F2_IMG) else None
        self.f1 = Fighter(100, SCREEN_HEIGHT - 160, facing=1, img_path=f1_img, color=FIGHTER1_COLOR)
        self.f2 = Fighter(SCREEN_WIDTH-200, SCREEN_HEIGHT - 160, facing=-1, img_path=f2_img, color=FIGHTER2_COLOR)

        self.round_time = 60 * FPS  # 60 seconds
        self.timer = self.round_time
        self.winner = None
        self.post_end_timer = 0

    def reset(self):
        self.f1.x = 100
        self.f1.hp = self.f1.max_hp
        self.f1.vx = 0
        self.f1.attack_cooldown = 0
        self.f2.x = SCREEN_WIDTH-200
        self.f2.hp = self.f2.max_hp
        self.f2.vx = 0
        self.f2.attack_cooldown = 0
        self.timer = self.round_time
        self.winner = None
        self.post_end_timer = 0

    def update(self):
        if self.winner:
            self.post_end_timer += 1
            if self.post_end_timer > FPS * 4:
                self.reset()
            return

        # AI steps
        self.f1.ai_step(self.f2)
        self.f2.ai_step(self.f1)

        # update fighters (movement and simple collision)
        self.f1.update()
        self.f2.update()

        # prevent overlap: simple separation
        if self.f1.rect().colliderect(self.f2.rect()):
            # push them apart
            if self.f1.x < self.f2.x:
                self.f1.x -= 1
                self.f2.x += 1
            else:
                self.f1.x += 1
                self.f2.x -= 1

        # timer
        self.timer -= 1
        if self.timer <= 0:
            # time up: decide by HP
            if self.f1.hp > self.f2.hp:
                self.winner = 'Fighter 1'
            elif self.f2.hp > self.f1.hp:
                self.winner = 'Fighter 2'
            else:
                self.winner = 'Draw'
            return

        # check HP
        if self.f1.hp <= 0 or self.f2.hp <= 0:
            if self.f1.hp <= 0 and self.f2.hp <= 0:
                self.winner = 'Draw'
            elif self.f1.hp <= 0:
                self.winner = 'Fighter 2'
            else:
                self.winner = 'Fighter 1'

    def draw(self):
        if self.background:
            self.screen.blit(self.background, (0,0))
        else:
            self.screen.fill(BG_COLOR)

        # ground line
        pygame.draw.rect(self.screen, (40,40,50), (0, SCREEN_HEIGHT-60, SCREEN_WIDTH, 60))

        # fighters
        self.f1.draw(self.screen)
        self.f2.draw(self.screen)

        # timer
        font = pygame.font.Font(None, 36)
        secs = max(0, self.timer // FPS)
        t_surf = font.render(f"Time: {secs}s", True, WHITE)
        self.screen.blit(t_surf, (SCREEN_WIDTH//2 - 50, 10))

        # winner
        if self.winner:
            big = pygame.font.Font(None, 64)
            text = big.render(f"{self.winner}", True, (240,240,80))
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 40))

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    Game().run()
