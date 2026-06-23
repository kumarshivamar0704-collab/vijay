import pygame
import sys
import random
import math
import os

# Pygame Setup
pygame.init()
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("VIJAY - Fast Auto Shoot Edition")
clock = pygame.time.Clock()

# Color Codes (Neon Cyberpunk Theme)
BG_COLOR = (8, 6, 16)
NEON_CYAN = (0, 255, 240)
NEON_MAGENTA = (255, 0, 110)
NEON_GREEN = (50, 255, 50)
WHITE = (255, 255, 255)
RED = (255, 30, 30)

# --- HIGH SCORE STORAGE SYSTEM ---
SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(score):
    try:
        with open(SCORE_FILE, "w") as f:
            f.write(str(score))
    except:
        pass

# --- ANIMATION CLASSES ---

class IntroParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-20, SCREEN_HEIGHT)
        self.speed = random.uniform(2, 4)
        self.length = random.randint(5, 15)
        
    def fall(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, SCREEN_WIDTH)
            
    def draw(self, surface):
        pygame.draw.line(surface, (40, 30, 90), (self.x, self.y), (self.x, self.y + self.length), 2)

class BlastParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.uniform(3.0, 6.0)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.alpha = 255
        self.fade_speed = random.randint(6, 10)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.fade_speed
        if self.radius > 0.2:
            self.radius -= 0.1

    def draw(self, surface):
        if self.alpha > 0 and self.radius > 0:
            p_surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (self.color[0], self.color[1], self.color[2], self.alpha), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(p_surf, (int(self.x - self.radius), int(self.y - self.radius)))

class SmoothGun:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 120 
        self.vx = 0          
        self.accel = 0.8     
        self.friction = 0.85  
        self.max_speed = 9
        self.width = 46
        self.height = 20

    def update(self, move_dir):
        if move_dir != 0:
            self.vx += move_dir * self.accel
            if self.vx > self.max_speed: self.vx = self.max_speed
            if self.vx < -self.max_speed: self.vx = -self.max_speed
        else:
            self.vx *= self.friction
            if abs(self.vx) < 0.1: self.vx = 0

        self.x += self.vx

        if self.x < self.width // 2 + 10:
            self.x = self.width // 2 + 10
            self.vx = 0
        if self.x > SCREEN_WIDTH - self.width // 2 - 10:
            self.x = SCREEN_WIDTH - self.width // 2 - 10
            self.vx = 0

    def draw(self, surface):
        pygame.draw.rect(surface, (30, 35, 60), (self.x - self.width//2, self.y, self.width, self.height), border_radius=6)
        pygame.draw.rect(surface, NEON_CYAN, (self.x - self.width//2, self.y, self.width, self.height), 2, border_radius=6)
        pygame.draw.circle(surface, (20, 24, 45), (int(self.x), self.y), 14)
        pygame.draw.circle(surface, NEON_CYAN, (int(self.x), self.y), 14, 2)
        pygame.draw.line(surface, NEON_CYAN, (int(self.x), self.y), (int(self.x), self.y - 28), 6)
        pygame.draw.circle(surface, WHITE, (int(self.x), self.y - 28), 3)

class LaserBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = -14  # Original Steady Bullet Speed
        self.vx = random.uniform(-1.5, 1.5) 

    def update(self):
        self.y += self.speed
        self.x += self.vx

    def draw(self, surface):
        pygame.draw.line(surface, NEON_GREEN, (int(self.x), int(self.y)), (int(self.x), int(self.y + 15)), 4)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)

class AnimatedTarget:
    def __init__(self):
        self.time = 0
        self.base_radius = 24
        self.radius = 24
        self.color = NEON_MAGENTA
        self.reset()

    def reset(self):
        self.x = random.randint(60, SCREEN_WIDTH - 60)
        self.y = random.randint(80, SCREEN_HEIGHT // 3 + 40)
        self.vx = random.choice([-4.0, -2.5, 2.5, 4.0])
        self.vy = random.choice([-1.5, -0.8, 0.8, 1.5])

    def update(self):
        self.time += 0.08
        self.radius = self.base_radius + math.sin(self.time) * 4
        self.x += self.vx
        self.y += self.vy

        if self.x < 30 or self.x > SCREEN_WIDTH - 30:
            self.vx *= -1
        if self.y < 50 or self.y > SCREEN_HEIGHT // 2:
            self.vy *= -1

    def draw(self, surface):
        x_int, y_int = int(self.x), int(self.y)
        pygame.draw.circle(surface, (50, 0, 30), (x_int, y_int), int(self.radius))
        pygame.draw.circle(surface, self.color, (x_int, y_int), int(self.radius), 3)
        pygame.draw.circle(surface, WHITE, (x_int, y_int), int(self.radius * 0.6), 2)
        pygame.draw.circle(surface, NEON_CYAN, (x_int, y_int), int(self.radius * 0.25))

# --- TEXT HELPER ENGINE ---
def render_text(surface, text, size, x, y, color, center=True):
    font = pygame.font.SysFont("Impact", size)
    txt_surf = font.render(text, True, color)
    rect = txt_surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    
    glow_surf = font.render(text, True, (25, 15, 50))
    surface.blit(glow_surf, (rect.x + 2, rect.y + 2))
    surface.blit(txt_surf, rect)

# --- INITIALIZATION ---
gun = SmoothGun()
target = AnimatedTarget()
bullets = []
blast_particles = []
bg_particles = [IntroParticle() for _ in range(25)]

# State Control Flags
game_state = 0  
is_paused = False  

loading_progress = 0
bar_w = 240
intro_alpha = 0
scale_pulse = 0

last_shot_time = 0 
SHOT_COOLDOWN = 150  # UPDATED: 200ms Cooldown for Rapid-Fire Action!

score = 0
high_score = load_high_score()  
shake_intensity = 0

# Anti-Camping Setup
last_movement_time = pygame.time.get_ticks()
STATIONARY_LIMIT = 3000  

# On-Screen Touch HUD Buttons Configuration
btn_y = SCREEN_HEIGHT - 80
btn_w = 120
btn_h = 60
left_btn_rect = pygame.Rect(30, btn_y, btn_w, btn_h)
right_btn_rect = pygame.Rect(SCREEN_WIDTH - 30 - btn_w, btn_y, btn_w, btn_h)
pause_btn_rect = pygame.Rect(SCREEN_WIDTH - 70, 15, 55, 35)

# --- MAIN LOOP ---
game_active = True
while game_active:
    
    current_time = pygame.time.get_ticks()

    offset_x = 0
    offset_y = 0
    if shake_intensity > 0 and not is_paused:
        offset_x = random.randint(-shake_intensity, shake_intensity)
        offset_y = random.randint(-shake_intensity, shake_intensity)
        shake_intensity -= 1

    game_canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    game_canvas.fill(BG_COLOR)

    # --- INPUT EVENT LOOP ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_active = False
            
        # Keyboard Setup
        if event.type == pygame.KEYDOWN:
            if game_state == 1 and event.key == pygame.K_p:
                is_paused = not is_paused
                if not is_paused:
                    last_movement_time = pygame.time.get_ticks()
            elif game_state == 2 and event.key == pygame.K_SPACE:
                # Reset & Restart
                score = 0
                bullets.clear()
                blast_particles.clear()
                gun = SmoothGun()
                target.reset()
                last_movement_time = pygame.time.get_ticks()
                is_paused = False
                game_state = 1

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Pause click logic
            if game_state == 1 and pause_btn_rect.collidepoint(mouse_pos):
                is_paused = not is_paused
                if not is_paused:
                    last_movement_time = pygame.time.get_ticks()
            
            # Restart screen tap trigger
            elif game_state == 2 or game_state == 0:
                if game_state == 2:
                    score = 0
                    bullets.clear()
                    blast_particles.clear()
                    gun = SmoothGun()
                    target.reset()
                    last_movement_time = pygame.time.get_ticks()
                    is_paused = False
                    game_state = 1

    # --- STATE 0: LOADING SCREEN ---
    if game_state == 0:
        for p in bg_particles:
            p.fall()
            p.draw(game_canvas)

        if intro_alpha < 255:
            intro_alpha += 8
            if intro_alpha > 255: intro_alpha = 255

        scale_pulse += 0.05
        size_offset = math.sin(scale_pulse) * 4

        text_canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        render_text(text_canvas, "VIJAY", int(65 + size_offset), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, NEON_CYAN)
        render_text(text_canvas, "RAPID AUTO-SHOOT", 18, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15, WHITE)
        text_canvas.set_alpha(intro_alpha)
        game_canvas.blit(text_canvas, (0, 0))

        loading_progress += 4.5
        bx = (SCREEN_WIDTH - bar_w) // 2
        by = SCREEN_HEIGHT // 2 + 80
        
        pygame.draw.rect(game_canvas, (25, 20, 45), (bx, by, bar_w, 6), border_radius=3)
        current_w = min(loading_progress, bar_w)
        if current_w > 0:
            pygame.draw.rect(game_canvas, NEON_MAGENTA, (bx, by, current_w, 6), border_radius=3)

        if loading_progress >= bar_w:
            game_state = 1
            last_movement_time = pygame.time.get_ticks()

    # --- STATE 1: ACTIVE CORE GAMEPLAY ---
    elif game_state == 1:
        direction = 0
        
        # PC Keyboard Check
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction = 1
            
        # Mobile Touch Button Hold Check
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0] and not is_paused:
            curr_mouse_pos = pygame.mouse.get_pos()
            if left_btn_rect.collidepoint(curr_mouse_pos):
                direction = -1
            elif right_btn_rect.collidepoint(curr_mouse_pos):
                direction = 1

        if direction != 0:
            last_movement_time = current_time  

        time_since_move = current_time - last_movement_time

        if time_since_move > STATIONARY_LIMIT and not is_paused:
            game_state = 2  

        if not is_paused:
            gun.update(direction)
            target.update()

            # 🔥 AUTOMATIC BULLET FIRING AT 200MS SPEED 🔥
            if current_time - last_shot_time > SHOT_COOLDOWN:
                bullets.append(LaserBullet(gun.x, gun.y - 28))
                last_shot_time = current_time

            for b in bullets[:]:
                b.update()
                if b.y < 0:
                    bullets.remove(b)
                    continue

                dist = math.hypot(b.x - target.x, b.y - target.y)
                if dist < target.radius + 3:  
                    score += 1
                    if score > high_score: 
                        high_score = score
                        save_high_score(high_score)
                        
                    shake_intensity = 8  
                    for _ in range(35):
                        blast_particles.append(BlastParticle(target.x, target.y, target.color))
                    bullets.remove(b)
                    target.reset()

            for p in blast_particles[:]:
                p.update()
                if p.alpha <= 0:
                    blast_particles.remove(p)

        # Drawing Assets
        for b in bullets: b.draw(game_canvas)
        for p in blast_particles: p.draw(game_canvas)
        target.draw(game_canvas)
        gun.draw(game_canvas)

        # Draw Touch controls panels
        pygame.draw.rect(game_canvas, (20, 25, 50), left_btn_rect, border_radius=10)
        pygame.draw.rect(game_canvas, NEON_CYAN, left_btn_rect, 2, border_radius=10)
        render_text(game_canvas, "<<", 22, left_btn_rect.centerx, left_btn_rect.centery, NEON_CYAN)

        pygame.draw.rect(game_canvas, (20, 25, 50), right_btn_rect, border_radius=10)
        pygame.draw.rect(game_canvas, NEON_CYAN, right_btn_rect, 2, border_radius=10)
        render_text(game_canvas, ">>", 22, right_btn_rect.centerx, right_btn_rect.centery, NEON_CYAN)

        # Pause Control
        pygame.draw.rect(game_canvas, (30, 20, 45), pause_btn_rect, border_radius=6)
        pygame.draw.rect(game_canvas, NEON_MAGENTA, pause_btn_rect, 1, border_radius=6)
        render_text(game_canvas, "PAUSE" if not is_paused else "PLAY", 14, pause_btn_rect.centerx, pause_btn_rect.centery, NEON_MAGENTA)

        # Display Scores
        render_text(game_canvas, f"SCORE: {score}", 20, 75, 30, NEON_GREEN)
        render_text(game_canvas, f"HIGH: {high_score}", 20, SCREEN_WIDTH - 120, 30, NEON_CYAN)

        # Camping Warning Display UI
        if time_since_move > 1000 and not is_paused:
            remaining_time = max(0, (STATIONARY_LIMIT - time_since_move) / 1000)
            warning_color = RED if current_time % 200 < 100 else WHITE
            render_text(game_canvas, f"MOVE OR DIE: {remaining_time:.1f}s", 22, SCREEN_WIDTH // 2, 100, warning_color)

        if is_paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 8, 22, 220))
            game_canvas.blit(overlay, (0, 0))
            render_text(game_canvas, "GAME PAUSED", 42, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, NEON_CYAN)
            render_text(game_canvas, "PRESS 'P' OR TAP TOP BUTTON", 16, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, WHITE)

    # --- STATE 2: GAME OVER SCREEN ---
    elif game_state == 2:
        render_text(game_canvas, "GAME OVER", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80, RED)
        render_text(game_canvas, "REASON: DON'T CAMP! STAY MOVING!", 18, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, WHITE)
        render_text(game_canvas, f"YOUR SCORE: {score}", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, NEON_GREEN)
        render_text(game_canvas, f"HIGH SCORE: {high_score}", 24, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, NEON_CYAN)
        
        if current_time % 1000 < 500:
            render_text(game_canvas, "PRESS SPACE OR TAP TO RESTART", 18, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130, NEON_CYAN)

    screen.blit(game_canvas, (offset_x, offset_y))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
