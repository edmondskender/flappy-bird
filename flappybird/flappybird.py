import pygame
import random
from sys import exit

class FlappyBird:
    def __init__(self):
        pygame.init()

        # Skalierungsfaktor festlegen (z.B. 2 für doppelte Größe)
        self.scale_factor = 2

        # Bildschirmgröße anpassen
        self.original_width = 551
        self.original_height = 720
        self.screen_width = int(self.original_width * self.scale_factor)
        self.screen_height = int(self.original_height * self.scale_factor)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        pygame.display.set_caption("Flappy Bird")

        self.clock = pygame.time.Clock()

        self.running = True
        self.game_state = "START"

        # Hintergrund
        self.background = pygame.image.load('graphics/background.png').convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        self.background_rect = self.background.get_rect()

        # Boden
        self.ground_velocity = 2 * self.scale_factor

        self.ground1 = pygame.image.load('graphics/ground.png')
        self.ground1 = pygame.transform.scale(self.ground1, (int(self.ground1.get_width() * self.scale_factor), int(self.ground1.get_height() * self.scale_factor)))
        self.ground1_rect = self.ground1.get_rect()
        self.ground1_rect.midtop = (self.screen_width // 2, self.screen_height - self.ground1_rect.height)

        self.ground2 = pygame.image.load('graphics/ground.png')
        self.ground2 = pygame.transform.scale(self.ground2, (int(self.ground2.get_width() * self.scale_factor), int(self.ground2.get_height() * self.scale_factor)))
        self.ground2_rect = self.ground2.get_rect()
        self.ground2_rect.topleft = (self.ground1_rect.right, self.screen_height - self.ground1_rect.height)

        # Startbutton
        self.start = pygame.image.load('graphics/start.png')
        self.start = pygame.transform.scale(self.start, (int(self.start.get_width() * self.scale_factor), int(self.start.get_height() * self.scale_factor)))
        self.start_rect = self.start.get_rect()
        self.start_rect.midbottom = (self.screen_width // 2, self.screen_height // 2)

        # Game Over
        self.game_over = pygame.image.load('graphics/game_over.png')
        self.game_over = pygame.transform.scale(self.game_over, (int(self.game_over.get_width() * self.scale_factor), int(self.game_over.get_height() * self.scale_factor)))
        self.game_over_rect = self.game_over.get_rect()
        self.game_over_rect.center = (self.screen_width // 2, self.screen_height // 2)

        # Animationseinstellungen für Start
        self.start_y_pos = self.start_rect.y
        self.start_movement = 0
        self.start_direction = 1
        self.start_speed = 0.5 * self.scale_factor
        self.start_range = 10 * self.scale_factor

        # Animationseinstellungen für Game Over
        self.game_over_y_pos = self.game_over_rect.y
        self.gameover_movement = 0
        self.gameover_direction = 1
        self.gameover_speed = 0.5 * self.scale_factor
        self.gameover_range = 10 * self.scale_factor

        # Player
        self.player = Player(scale_factor=self.scale_factor)

        # Pipes
        self.pipes = pygame.sprite.Group()
        self.pipe_spawn_time = pygame.time.get_ticks()
        self.pipe_spawn_interval = 3000  # Intervall in Millisekunden

        # Score
        self.alpha_font = pygame.font.Font('fonts/FlappybirdyRegular-KaBW.ttf', int(100 * self.scale_factor))
        self.font = pygame.font.Font('fonts/flappy-bird-font.ttf', int(64 * self.scale_factor))
        self.score = 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()
        exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == "PLAYING":
                        self.player.jump()
                    elif self.game_state == "START":
                        self.game_state = "PLAYING"
                        self.player.reset()
                        self.pipes.empty()
                        self.pipe_spawn_time = pygame.time.get_ticks()
                elif event.key == pygame.K_r:
                    if self.game_state == "GAME_OVER":
                        self.game_state = "PLAYING"
                        self.score = 0
                        self.player.reset()
                        self.pipes.empty()
                        self.pipe_spawn_time = pygame.time.get_ticks()

    def update(self):
        if self.game_state == "START":
            self.start_movement += self.start_direction * self.start_speed
            self.start_rect.y = self.start_y_pos + self.start_movement
            if abs(self.start_movement) >= self.start_range:
                self.start_direction *= -1

        elif self.game_state == "PLAYING":
            self.ground1_rect.x -= self.ground_velocity
            self.ground2_rect.x -= self.ground_velocity
            if self.ground1_rect.right <= 0:
                self.ground1_rect.left = self.ground2_rect.right
            elif self.ground2_rect.right <= 0:
                self.ground2_rect.left = self.ground1_rect.right

            self.player.update()

            self.pipes.update()

            for pipe in self.pipes:
                # Kollisionen überprüfen
                if self.player.bird_rect.colliderect(pipe.top_rect) or self.player.bird_rect.colliderect(pipe.bottom_rect):
                    self.game_state = "GAME_OVER"
                # Pipes entfernen, die aus dem Bildschirm kommen
                if pipe.top_rect.right <= 0:
                    pipe.kill()
                # Score erhöhen
                if not pipe.passed and pipe.top_rect.right < self.player.bird_rect.left:
                    pipe.passed = True
                    self.score += 1

            current_time = pygame.time.get_ticks()
            if current_time - self.pipe_spawn_time > self.pipe_spawn_interval:
                new_pipe = Pipe(self.screen_width, scale_factor=self.scale_factor)
                self.pipes.add(new_pipe)
                self.pipe_spawn_time = current_time

            # Kollisionen mit Boden oder Bildschirmrand überprüfen
            if self.player.bird_rect.colliderect(self.ground1_rect) or self.player.bird_rect.colliderect(self.ground2_rect) or self.player.bird_rect.top <= 0:
                self.game_state = "GAME_OVER"

        elif self.game_state == "GAME_OVER":
            self.gameover_movement += self.gameover_direction * self.gameover_speed
            self.game_over_rect.y = self.game_over_y_pos + self.gameover_movement
            if abs(self.gameover_movement) >= self.gameover_range:
                self.gameover_direction *= -1

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.ground1, self.ground1_rect)
        self.screen.blit(self.ground2, self.ground2_rect)

        if self.game_state == "START":
            self.screen.blit(self.start, self.start_rect)

        elif self.game_state == "PLAYING":
            self.player.draw(self.screen)
            for pipe in self.pipes:
                pipe.draw(self.screen)
            score_surface = self.font.render(f'{self.score}', True, (0, 0, 0))
            self.screen.blit(score_surface, (20 * self.scale_factor, 20 * self.scale_factor))

        elif self.game_state == "GAME_OVER":
            endscore_text = self.alpha_font.render(f'Your Score ', True, (0, 0, 0))
            endscore_text_rect = endscore_text.get_rect(center=(self.screen_width // 2, int(180 * self.scale_factor)))

            endscore = self.font.render(f'{self.score}', True, (0, 0, 0))
            endscore_rect = endscore.get_rect(center=(self.screen_width // 2, int(250 * self.scale_factor)))
            self.screen.blit(endscore, endscore_rect)
            self.screen.blit(endscore_text, endscore_text_rect)
            self.screen.blit(self.game_over, self.game_over_rect)

class Player:
    def __init__(self, start_x=50, start_y=250, scale_factor=1):
        self.scale_factor = scale_factor

        self.bird_frames = [
            pygame.image.load('graphics/bird_mid.png'),
            pygame.image.load('graphics/bird_down.png'),
            pygame.image.load('graphics/bird_up.png')
        ]
        # Bilder skalieren
        self.bird_frames = [pygame.transform.scale(img, (int(img.get_width() * self.scale_factor), int(img.get_height() * self.scale_factor))) for img in self.bird_frames]

        self.current_frame = 0
        self.bird = self.bird_frames[self.current_frame]
        self.bird_rect = self.bird.get_rect()
        self.bird_rect.center = (int(start_x * self.scale_factor), int(start_y * self.scale_factor))

        self.velocity = 0
        self.gravity = 0.27
        self.start_position_y = self.bird_rect.y

    def update(self):
        self.velocity += self.gravity
        self.bird_rect.y += self.velocity

    def draw(self, screen):
        if self.velocity < 0:  # Vogel springt
            self.bird = self.bird_frames[2]
        elif self.velocity > 0:  # Vogel fällt
            self.bird = self.bird_frames[1]
        screen.blit(self.bird, self.bird_rect)

    def jump(self):
        self.velocity = -6.25

    def reset(self):
        self.velocity = 0
        self.bird_rect.y = self.start_position_y

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x_pos, scale_factor=1):
        super().__init__()

        self.scale_factor = scale_factor

        self.gap = random.randint(int(95 * self.scale_factor), int(120 * self.scale_factor))
        self.speed = 2 * self.scale_factor

        self.height = random.randint(int(110 * self.scale_factor), int(420 * self.scale_factor))

        self.pipe_top = pygame.image.load('graphics/pipe_top.png').convert_alpha()
        self.pipe_top = pygame.transform.scale(self.pipe_top, (int(self.pipe_top.get_width() * self.scale_factor), int(self.pipe_top.get_height() * self.scale_factor)))
        self.top_rect = self.pipe_top.get_rect(midbottom=(x_pos + int(50 * self.scale_factor), self.height - self.gap // 2))

        self.pipe_bottom = pygame.image.load('graphics/pipe_bottom.png').convert_alpha()
        self.pipe_bottom = pygame.transform.scale(self.pipe_bottom, (int(self.pipe_bottom.get_width() * self.scale_factor), int(self.pipe_bottom.get_height() * self.scale_factor)))
        self.bottom_rect = self.pipe_bottom.get_rect(midtop=(x_pos + int(50 * self.scale_factor), self.height + self.gap // 2))

        self.passed = False

    def update(self):
        self.top_rect.x -= self.speed
        self.bottom_rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.pipe_top, self.top_rect)
        screen.blit(self.pipe_bottom, self.bottom_rect)

Game = FlappyBird()
Game.run()
