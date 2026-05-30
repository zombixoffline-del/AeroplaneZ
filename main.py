import pygame
import sys
import random
import os
import time

# Попытка импорта для видео (если нет OpenCV, видео не будет, но звук останется)
try:
    import cv2
    import numpy as np
    VIDEO_AVAILABLE = True
except ImportError:
    VIDEO_AVAILABLE = False
    print("OpenCV не найден, видео не будет, но звук MP3 будет играть")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 480, 800
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (64, 64, 64)
GRAY = (128, 128, 128)
PURPLE = (150, 0, 150)
BUTTON_NORMAL = (70, 130, 200)
BUTTON_PRESSED = (30, 90, 150)

# Игровые параметры
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 40
PLAYER_SPEED = 8
SHOOT_DELAY = 10

BULLET_WIDTH, BULLET_HEIGHT = 5, 15
BULLET_SPEED = -10

ENEMY_WIDTH, ENEMY_HEIGHT = 40, 30
ENEMY_SPEED = 4
ENEMY_SPAWN_DELAY = 30
ENEMY_SHOOT_DELAY = 60
ENEMY_BULLET_SPEED = 5

BOSS_WIDTH, BOSS_HEIGHT = 80, 80
BOSS_HP = 30
BOSS_SPEED_X, BOSS_SPEED_Y = 3, 1
BOSS_SPAWN_SCORE = 200
BOSS_SHOOT_DELAY = 40
BOSS_BULLET_SPEED = 6

BG_SWITCH_INTERVAL = 30 * FPS
BG_FADE_DURATION = 2 * FPS

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Защитник города")
clock = pygame.time.Clock()

# ---------- Функция воспроизведения видео + звука ----------
def play_video_with_audio(video_name, max_duration=30, pause_music=False):
    """
    Воспроизводит видео (если OpenCV есть) и одновременно запускает звук из MP3.
    Имя видео: например 'WIDIO34.mp4' -> звук должен быть 'WIDIO34.mp3'
    Если pause_music=True, фоновая музыка Metallica останавливается на время.
    """
    video_path = os.path.join(BASE_DIR, video_name)
    audio_name = os.path.splitext(video_name)[0] + ".mp3"
    audio_path = os.path.join(BASE_DIR, audio_name)

    # Останавливаем фоновую музыку, если нужно
    music_was_playing = False
    if pause_music and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        music_was_playing = True

    # Запускаем звук MP3 (если есть)
    sound_played = False
    if os.path.exists(audio_path):
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            sound_played = True
        except Exception as e:
            print(f"Не удалось загрузить {audio_path}: {e}")

    # Воспроизводим видео, если OpenCV доступен и файл существует
    cap = None
    if VIDEO_AVAILABLE and os.path.exists(video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            cap = None

    if cap is not None:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0:
            video_fps = 30
        frame_time = 1.0 / video_fps
        target_size = (WIDTH, HEIGHT)
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if time.time() - start_time > max_duration:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)  # поворот для портрета
            frame_surface = pygame.surfarray.make_surface(frame)
            frame_surface = pygame.transform.scale(frame_surface, target_size)

            screen.blit(frame_surface, (0, 0))
            pygame.display.flip()

            time.sleep(frame_time)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        cap.release()
    else:
        # Если видео нет, просто ждём, пока звук играет (или пауза, если звука нет)
        if sound_played:
            # Ждём окончания звука или max_duration
            start_time = time.time()
            while pygame.mixer.music.get_busy() and (time.time() - start_time) < max_duration:
                pygame.time.delay(100)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
        else:
            # Ни видео, ни звука - просто пауза 0.5 сек
            pygame.time.delay(500)

    # Останавливаем звук видео
    pygame.mixer.music.stop()

    # Возобновляем фоновую музыку, если была остановлена
    if music_was_playing:
        try:
            pygame.mixer.music.load(os.path.join(BASE_DIR, "Metallica.mp3"))
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Не удалось загрузить Metallica.mp3: {e}")

    time.sleep(0.5)

# ---------- Загрузка текстур ----------
def load_texture(filename, width, height, fallback_color):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (width, height))
        except Exception as e:
            print(f"Ошибка {filename}: {e}")
    else:
        print(f"Нет {path}, использую заглушку")
    surf = pygame.Surface((width, height))
    surf.fill(fallback_color)
    return surf

player_img = load_texture("player.png", PLAYER_WIDTH, PLAYER_HEIGHT, BLUE)
bullet_img = load_texture("bullet.png", BULLET_WIDTH, BULLET_HEIGHT, YELLOW)
enemy_img = load_texture("enemy.png", ENEMY_WIDTH, ENEMY_HEIGHT, GREEN)
enemy_bullet_img = load_texture("enemy_bullet.png", 6, 12, RED)
boss_img = load_texture("boss.png", BOSS_WIDTH, BOSS_HEIGHT, PURPLE)
bg1 = load_texture("background.png", WIDTH, HEIGHT, (30,30,50))
bg2 = load_texture("background2.png", WIDTH, HEIGHT, (50,30,70))
bg3 = load_texture("background3.png", WIDTH, HEIGHT, (70,50,90))

# fallback если файлы отсутствуют
if bg2.get_at((0,0)) == (50,30,70) and not os.path.exists(os.path.join(BASE_DIR, "background2.png")):
    bg2 = bg1
if bg3.get_at((0,0)) == (70,50,90) and not os.path.exists(os.path.join(BASE_DIR, "background3.png")):
    bg3 = bg1

# ---------- Классы ----------
class Player:
    def __init__(self):
        self.x = WIDTH//2 - PLAYER_WIDTH//2
        self.y = HEIGHT - 130
        self.speed = PLAYER_SPEED
        self.shoot_timer = 0
        self.image = player_img
        self.width, self.height = PLAYER_WIDTH, PLAYER_HEIGHT
    def update(self, left, right):
        if left and self.x > 0:
            self.x -= self.speed
        if right and self.x < WIDTH - self.width:
            self.x += self.speed
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
    def shoot(self):
        if self.shoot_timer == 0:
            self.shoot_timer = SHOOT_DELAY
            return Bullet(self.x + self.width//2 - BULLET_WIDTH//2, self.y - 10)
        return None
    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = BULLET_WIDTH, BULLET_HEIGHT
        self.speed = BULLET_SPEED
        self.image = bullet_img
    def update(self):
        self.y += self.speed
    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def is_off_screen(self):
        return self.y + self.height < 0

class EnemyBullet:
    def __init__(self, x, y, speed):
        self.x, self.y = x, y
        self.width, self.height = 6, 12
        self.speed = speed
        self.image = enemy_bullet_img
    def update(self):
        self.y += self.speed
    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def is_off_screen(self):
        return self.y > HEIGHT

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = ENEMY_WIDTH, ENEMY_HEIGHT
        self.speed = ENEMY_SPEED
        self.shoot_timer = random.randint(0, ENEMY_SHOOT_DELAY)
        self.image = enemy_img
    def update(self):
        self.y += self.speed
        self.shoot_timer -= 1
    def shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = ENEMY_SHOOT_DELAY
            return EnemyBullet(self.x + self.width//2 - 3, self.y + self.height, ENEMY_BULLET_SPEED)
        return None
    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def is_off_screen(self):
        return self.y > HEIGHT

class Boss:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.width, self.height = BOSS_WIDTH, BOSS_HEIGHT
        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.speed_x, self.speed_y = BOSS_SPEED_X, BOSS_SPEED_Y
        self.shoot_timer = 0
        self.image = boss_img
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.speed_x = -self.speed_x
        if self.y <= 0 or self.y + self.height >= HEIGHT//2:
            self.speed_y = -self.speed_y
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
    def shoot(self):
        if self.shoot_timer == 0:
            self.shoot_timer = BOSS_SHOOT_DELAY
            bullets = []
            for offset in (-10, 0, 10):
                b = EnemyBullet(self.x + self.width//2 - 3 + offset, self.y + self.height//2, BOSS_BULLET_SPEED)
                b.x += offset
                bullets.append(b)
            return bullets
        return []
    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))
        bar_w = self.width
        bar_h = 8
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, RED, (self.x, self.y-12, bar_w, bar_h))
        pygame.draw.rect(surf, GREEN, (self.x, self.y-12, bar_w * ratio, bar_h))
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def hit(self):
        self.hp -= 1
        return self.hp <= 0

class BackgroundFader:
    def __init__(self, bg1, bg2, bg3):
        self.bg1 = bg1
        self.bg2 = bg2
        self.bg3 = bg3
        self.current = 1          # текущий фон (1, 2 или 3)
        self.alpha = 255
        self.fading = False
        self.fade_counter = 0
        self.switch_timer = 0
        self.switch_interval = BG_SWITCH_INTERVAL

    def update(self):
        # Если все фоны одинаковы (например, отсутствуют файлы) — ничего не делаем
        if self.bg1 is self.bg2 is self.bg3:
            return
        if not self.fading:
            self.switch_timer += 1
            if self.switch_timer >= self.switch_interval:
                self.switch_timer = 0
                self.start_fade()
        else:
            self.fade_counter += 1
            self.alpha = max(0, 255 - int(255 * self.fade_counter / BG_FADE_DURATION))
            if self.fade_counter >= BG_FADE_DURATION:
                # Переключаем на следующий фон: 1→2, 2→3, 3→1
                self.current = self.current % 3 + 1
                self.fading = False
                self.fade_counter = 0
                self.alpha = 255

    def start_fade(self):
        if not self.fading:
            self.fading = True
            self.fade_counter = 0
            self.alpha = 255

    def draw(self, screen):
        # Получаем текущий и следующий фоны
        if self.current == 1:
            bg_current = self.bg1
            bg_next = self.bg2
        elif self.current == 2:
            bg_current = self.bg2
            bg_next = self.bg3
        else:  # current == 3
            bg_current = self.bg3
            bg_next = self.bg1

        # Рисуем следующий фон полностью
        screen.blit(bg_next, (0, 0))
        # Поверх него — текущий с прозрачностью (если идёт затухание)
        if self.fading:
            temp = bg_current.copy()
            temp.set_alpha(self.alpha)
            screen.blit(temp, (0, 0))
        else:
            screen.blit(bg_current, (0, 0))

# ---------- Кнопки ----------
class AnimatedButton:
    def __init__(self, rect, text, normal_color, pressed_color, text_color=WHITE):
        self.rect = rect
        self.text = text
        self.normal_color = normal_color
        self.pressed_color = pressed_color
        self.text_color = text_color
        self.pressed = False
        self.shadow_offset = 3
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                return True
            self.pressed = False
        return False
    def draw(self, screen):
        shadow_rect = self.rect.inflate(0, 0)
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=12)
        color = self.pressed_color if self.pressed else self.normal_color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=12)
        text_surf = small_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

def draw_text(text, font, color, x, y, center=True):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

# ---------- Меню ----------
def menu():
    start_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2, 160, 50)
    start_button = AnimatedButton(start_rect, "СТАРТ", BUTTON_NORMAL, BUTTON_PRESSED)
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if start_button.handle_event(event):
                # Стартовое видео + звук (WIDIO34.mp4 и WIDIO34.mp3)
                play_video_with_audio("WIDIO34.mp4")
                # Запускаем фоновую музыку
                try:
                    pygame.mixer.music.load(os.path.join(BASE_DIR, "Metallica.mp3"))
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Не удалось загрузить Metallica.mp3: {e}")
                return
        screen.blit(bg1, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        draw_text("ЗАЩИТНИК ГОРОДА", font, YELLOW, WIDTH//2, HEIGHT//3)
        draw_text("Сбейте инопланетные корабли!", small_font, WHITE, WIDTH//2, HEIGHT//2 - 50)
        start_button.draw(screen)
        pygame.display.flip()

# ---------- Экран Game Over ----------
def game_over(score):
    pygame.mixer.music.stop()
    restart_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2, 160, 50)
    menu_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 80, 120, 40)
    restart_btn = AnimatedButton(restart_rect, "ЗАНОВО", BUTTON_NORMAL, BUTTON_PRESSED)
    menu_btn = AnimatedButton(menu_rect, "МЕНЮ", GRAY, DARK_GRAY)
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if restart_btn.handle_event(event):
                return True
            if menu_btn.handle_event(event):
                return False
        screen.blit(bg1, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        draw_text("GAME OVER", font, RED, WIDTH//2, HEIGHT//3)
        draw_text(f"Счёт: {score}", font, WHITE, WIDTH//2, HEIGHT//2 - 50)
        restart_btn.draw(screen)
        menu_btn.draw(screen)
        pygame.display.flip()

# ---------- Основной игровой цикл ----------
def run_game():
    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = []
    score = 0
    spawn_timer = 0
    boss = None
    boss_spawned = False
    video_played_1000 = False

    left = right = False
    fader = BackgroundFader(bg1, bg2, bg3)

    btn_h = 60
    btn_y = HEIGHT - btn_h - 10
    left_btn = AnimatedButton(pygame.Rect(10, btn_y, 100, btn_h), "<<", BUTTON_NORMAL, BUTTON_PRESSED)
    right_btn = AnimatedButton(pygame.Rect(WIDTH - 110, btn_y, 100, btn_h), ">>", BUTTON_NORMAL, BUTTON_PRESSED)
    shoot_btn = AnimatedButton(pygame.Rect(WIDTH//2 - 50, btn_y, 100, btn_h), "ОГОНЬ", RED, (180, 0, 0))

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if left_btn.handle_event(event):
                left = event.type == pygame.MOUSEBUTTONDOWN
            if right_btn.handle_event(event):
                right = event.type == pygame.MOUSEBUTTONDOWN
            if shoot_btn.handle_event(event) and event.type == pygame.MOUSEBUTTONDOWN:
                b = player.shoot()
                if b:
                    bullets.append(b)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            b = player.shoot()
            if b:
                bullets.append(b)
        if keys[pygame.K_LEFT]:
            left = True
        elif keys[pygame.K_RIGHT]:
            right = True
        else:
            if not (pygame.mouse.get_pressed()[0] and left_btn.rect.collidepoint(pygame.mouse.get_pos())):
                left = False
            if not (pygame.mouse.get_pressed()[0] and right_btn.rect.collidepoint(pygame.mouse.get_pos())):
                right = False

        player.update(left, right)

        for b in bullets[:]:
            b.update()
            if b.is_off_screen():
                bullets.remove(b)

        for eb in enemy_bullets[:]:
            eb.update()
            if eb.is_off_screen():
                enemy_bullets.remove(eb)

        if boss is None:
            if spawn_timer <= 0:
                ex = random.randint(20, WIDTH - ENEMY_WIDTH - 20)
                enemies.append(Enemy(ex, -ENEMY_HEIGHT))
                spawn_timer = ENEMY_SPAWN_DELAY
            else:
                spawn_timer -= 1

        for e in enemies[:]:
            e.update()
            shot = e.shoot()
            if shot:
                enemy_bullets.append(shot)
            if e.is_off_screen():
                enemies.remove(e)

        for b in bullets[:]:
            br = b.get_rect()
            for e in enemies[:]:
                if br.colliderect(e.get_rect()):
                    bullets.remove(b)
                    enemies.remove(e)
                    score += 10
                    break

        if not boss_spawned and score >= BOSS_SPAWN_SCORE:
            boss = Boss(WIDTH//2 - BOSS_WIDTH//2, 50)
            boss_spawned = True
            enemies.clear()

        if boss:
            boss.update()
            boss_shots = boss.shoot()
            if boss_shots:
                enemy_bullets.extend(boss_shots)
            for b in bullets[:]:
                if b.get_rect().colliderect(boss.get_rect()):
                    bullets.remove(b)
                    if boss.hit():
                        boss = None
                        score += 100
                    break
            if boss and player.get_rect().colliderect(boss.get_rect()):
                running = False

        pr = player.get_rect()
        for e in enemies:
            if pr.colliderect(e.get_rect()):
                running = False
                break
        for eb in enemy_bullets:
            if pr.colliderect(eb.get_rect()):
                running = False
                break

        # Достижение 1000 очков: видео + звук, затем выход в меню
        if score >= 1000 and not video_played_1000:
            video_played_1000 = True
            play_video_with_audio("WIDIO.mp4", pause_music=True)
            return False

        fader.update()
        fader.draw(screen)
        draw_text(f"Счёт: {score}", font, WHITE, 70, 30, center=False)

        player.draw(screen)
        for b in bullets:
            b.draw(screen)
        for eb in enemy_bullets:
            eb.draw(screen)
        for e in enemies:
            e.draw(screen)
        if boss:
            boss.draw(screen)

        left_btn.draw(screen)
        right_btn.draw(screen)
        shoot_btn.draw(screen)

        pygame.display.flip()

    return game_over(score)

# ---------- Запуск ----------
def main():
    while True:
        menu()
        restart = run_game()
        if not restart:
            continue

if __name__ == "__main__":
    main()