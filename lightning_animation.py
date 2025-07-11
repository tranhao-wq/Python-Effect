import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Setup window
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Epic Lightning Storm - Premium Edition")

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 150, 255)
PURPLE = (200, 100, 255)
DARK_BLUE = (20, 30, 60)
GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)

# Particle class for advanced effects
class Particle:
    def __init__(self, x, y, color, velocity, life):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = life
        self.max_life = life
        self.size = random.randint(1, 3)
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] + 0.1)
    
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color[:3], alpha)
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# Rain drop class
class RainDrop:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(5, 15)
        self.length = random.randint(10, 20)
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = random.randint(-50, 0)
            self.x = random.randint(0, WIDTH)
    
    def draw(self, surface):
        pygame.draw.line(surface, (100, 150, 200), 
                        (self.x, self.y), (self.x - 2, self.y + self.length), 1)

# Cloud class
class Cloud:
    def __init__(self):
        self.x = random.randint(-100, WIDTH + 100)
        self.y = random.randint(50, 200)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(80, 150)
        self.darkness = random.randint(40, 80)
    
    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 200:
            self.x = -200
    
    def draw(self, surface):
        color = (self.darkness, self.darkness, self.darkness + 20)
        for i in range(5):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-10, 10)
            pygame.draw.circle(surface, color, 
                             (int(self.x + offset_x), int(self.y + offset_y)), 
                             self.size // (i + 1))

# Initialize particle systems
particles = []
rain_drops = [RainDrop() for _ in range(200)]
clouds = [Cloud() for _ in range(8)]

# Create simple thunder sound effect
def create_thunder_sound():
    try:
        import numpy as np
        duration = 0.8
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Create white noise for thunder
        noise = np.random.normal(0, 0.1, frames)
        
        # Apply fade out
        fade = np.exp(-np.linspace(0, 5, frames))
        thunder = noise * fade
        
        # Ensure array is contiguous and correct format
        thunder_stereo = np.column_stack((thunder, thunder))
        thunder_int = np.ascontiguousarray((thunder_stereo * 32767).astype(np.int16))
        
        return pygame.sndarray.make_sound(thunder_int)
    except:
        return None

# Create thunder sound
thunder_sound = create_thunder_sound()
print("Thunder sound created:", thunder_sound is not None)

# Main loop variables
running = True
clock = pygame.time.Clock()
thunder_timer = 0
background_flash = 0
storm_intensity = 0
time_counter = 0
lightning_strikes = []

# Lightning strike class for persistence
class LightningStrike:
    def __init__(self, points, color, thickness):
        self.points = points
        self.color = color
        self.thickness = thickness
        self.life = 10
        self.glow_radius = 20
    
    def update(self):
        self.life -= 1
        self.glow_radius -= 2
    
    def draw(self, surface):
        if self.life > 0:
            # Draw glow effect
            for i, point in enumerate(self.points[:-1]):
                if self.glow_radius > 0:
                    glow_surface = pygame.Surface((self.glow_radius * 2, self.glow_radius * 2))
                    glow_surface.set_alpha(30)
                    pygame.draw.circle(glow_surface, self.color, 
                                     (self.glow_radius, self.glow_radius), self.glow_radius)
                    surface.blit(glow_surface, 
                               (point[0] - self.glow_radius, point[1] - self.glow_radius))
            
            # Draw main lightning
            alpha = int(255 * (self.life / 10))
            for i in range(len(self.points) - 1):
                pygame.draw.line(surface, self.color, self.points[i], self.points[i + 1], 
                               max(1, self.thickness - (10 - self.life)))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                storm_intensity = min(storm_intensity + 20, 100)
    
    time_counter += 1
    storm_intensity = max(0, storm_intensity - 0.2)
    
    # Dynamic background with storm clouds
    if background_flash > 0:
        bg_color = (min(50 + background_flash, 100), min(50 + background_flash, 100), min(80 + background_flash, 120))
        background_flash -= 5
    else:
        bg_color = (10 + int(storm_intensity * 0.3), 15 + int(storm_intensity * 0.2), 30 + int(storm_intensity * 0.4))
    
    screen.fill(bg_color)
    
    # Draw and update clouds
    for cloud in clouds:
        cloud.update()
        cloud.draw(screen)
    
    # Draw and update rain
    if storm_intensity > 20:
        for drop in rain_drops[:int(storm_intensity * 2)]:
            drop.update()
            drop.draw(screen)

    # Create epic lightning with higher probability during storms
    lightning_chance = 0.05 + (storm_intensity * 0.002)
    if random.random() < lightning_chance:
        num_bolts = random.randint(1, 3 + int(storm_intensity / 30))
        
        for bolt in range(num_bolts):
            # More dynamic starting positions
            start_x = random.randint(WIDTH//6, 5*WIDTH//6)
            start_y = random.randint(0, 100)
            points = [(start_x, start_y)]
            
            segments = random.randint(12, 25)
            for _ in range(segments):
                # More realistic lightning path
                deviation = random.randint(-50, 50)
                if len(points) > 3:
                    # Tendency to continue in same direction
                    prev_direction = points[-1][0] - points[-2][0]
                    deviation += prev_direction * 0.3
                
                x = points[-1][0] + deviation
                y = points[-1][1] + random.randint(20, 70)
                
                # Keep lightning on screen
                x = max(50, min(WIDTH - 50, x))
                if y > HEIGHT:
                    y = HEIGHT
                
                points.append((x, y))
                if y >= HEIGHT:
                    break
            
            # Premium color selection
            colors = [YELLOW, WHITE, CYAN, GOLD, LIGHT_BLUE]
            color = random.choice(colors)
            thickness = random.randint(3, 8)
            
            # Create persistent lightning strike
            lightning_strikes.append(LightningStrike(points, color, thickness))
            
            # Create particle explosion at strike points
            for i in range(0, len(points), 3):
                for _ in range(random.randint(5, 15)):
                    particle_color = color
                    velocity = (random.uniform(-5, 5), random.uniform(-5, 5))
                    particles.append(Particle(points[i][0], points[i][1], 
                                            particle_color, velocity, random.randint(20, 40)))
            
            # Add multiple branches with fractal-like patterns
            if random.random() > 0.4:
                for i in range(2, len(points) - 2, 3):
                    if random.random() > 0.5:
                        # Main branch
                        branch_points = [points[i]]
                        branch_segments = random.randint(3, 8)
                        
                        for _ in range(branch_segments):
                            bx = branch_points[-1][0] + random.randint(-60, 60)
                            by = branch_points[-1][1] + random.randint(15, 40)
                            branch_points.append((bx, by))
                        
                        lightning_strikes.append(LightningStrike(branch_points, color, thickness - 2))
                        
                        # Sub-branches
                        if random.random() > 0.7 and len(branch_points) > 2:
                            sub_branch = [branch_points[1]]
                            for _ in range(random.randint(2, 4)):
                                sx = sub_branch[-1][0] + random.randint(-30, 30)
                                sy = sub_branch[-1][1] + random.randint(10, 25)
                                sub_branch.append((sx, sy))
                            lightning_strikes.append(LightningStrike(sub_branch, color, thickness - 3))
            
            # Trigger background flash and particles
            background_flash = random.randint(30, 60)
            storm_intensity = min(100, storm_intensity + random.randint(5, 15))
    
    # Update and draw persistent lightning strikes
    lightning_strikes = [strike for strike in lightning_strikes if strike.life > 0]
    for strike in lightning_strikes:
        strike.update()
        strike.draw(screen)
    
    # Update and draw particles
    particles = [p for p in particles if p.life > 0]
    for particle in particles:
        particle.update()
        particle.draw(screen)
    
    # Epic screen flash with multiple layers
    if background_flash > 40:
        # Multiple flash layers for depth
        for i in range(3):
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            alpha = max(0, (background_flash - 40) * (3 - i) * 2)
            flash_surface.set_alpha(min(alpha, 100))
            colors = [WHITE, LIGHT_BLUE, YELLOW]
            flash_surface.fill(colors[i])
            screen.blit(flash_surface, (0, 0))
        
        # Play thunder sound with intensity
        if thunder_timer <= 0 and thunder_sound:
            thunder_sound.set_volume(min(1.0, storm_intensity / 100))
            thunder_sound.play()
            thunder_timer = random.randint(20, 60)
    
    # Ground illumination effect
    if background_flash > 20:
        ground_glow = pygame.Surface((WIDTH, 100))
        ground_glow.set_alpha(background_flash)
        ground_glow.fill((100, 150, 255))
        screen.blit(ground_glow, (0, HEIGHT - 100))
    
    # Storm intensity indicator
    if storm_intensity > 0:
        intensity_bar = pygame.Rect(10, 10, int(storm_intensity * 2), 10)
        pygame.draw.rect(screen, (255, int(255 - storm_intensity * 2), 0), intensity_bar)
        font = pygame.font.Font(None, 24)
        text = font.render(f"Storm Intensity: {int(storm_intensity)}% (Press SPACE to intensify)", 
                          True, WHITE)
        screen.blit(text, (10, 30))
    
    if thunder_timer > 0:
        thunder_timer -= 1

    pygame.display.flip()
    clock.tick(60)  # 60 FPS for smooth premium experience

pygame.quit()