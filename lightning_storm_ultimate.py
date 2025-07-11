import pygame
import random
import math
import time
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Setup window - Ultra HD
WIDTH, HEIGHT = 1600, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lightning Storm Ultimate - 4K Edition")

# Premium Color Palette
COLORS = {
    'WHITE': (255, 255, 255),
    'ELECTRIC_BLUE': (0, 191, 255),
    'PLASMA_PURPLE': (138, 43, 226),
    'NEON_CYAN': (0, 255, 255),
    'GOLDEN_YELLOW': (255, 215, 0),
    'CRIMSON_RED': (220, 20, 60),
    'EMERALD_GREEN': (50, 205, 50),
    'SILVER': (192, 192, 192),
    'DARK_STORM': (25, 25, 112),
    'MIDNIGHT_BLUE': (25, 25, 112)
}

class AdvancedParticle:
    def __init__(self, x, y, color, velocity, life, particle_type='spark'):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = life
        self.max_life = life
        self.size = random.uniform(1, 4)
        self.type = particle_type
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-5, 5)
    
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        self.rotation += self.spin
        
        if self.type == 'spark':
            self.velocity = (self.velocity[0] * 0.95, self.velocity[1] + 0.15)
        elif self.type == 'ember':
            self.velocity = (self.velocity[0] * 0.98, self.velocity[1] + 0.05)
            self.size *= 0.99
    
    def draw(self, surface):
        if self.life > 0:
            alpha_factor = self.life / self.max_life
            if self.type == 'spark':
                # Draw spark with tail
                tail_length = int(self.size * 3)
                for i in range(tail_length):
                    alpha = alpha_factor * (1 - i / tail_length)
                    color = tuple(int(c * alpha) for c in self.color)
                    pos = (int(self.x - self.velocity[0] * i * 0.1), 
                          int(self.y - self.velocity[1] * i * 0.1))
                    pygame.draw.circle(surface, color, pos, max(1, int(self.size - i * 0.1)))

class WeatherSystem:
    def __init__(self):
        self.wind_speed = random.uniform(0.5, 2.0)
        self.rain_intensity = 0
        self.fog_density = 0
        self.temperature = random.randint(-10, 35)
    
    def update(self, storm_level):
        self.rain_intensity = min(100, storm_level * 1.5)
        self.fog_density = min(50, storm_level * 0.8)
        self.wind_speed += random.uniform(-0.1, 0.1)
        self.wind_speed = max(0.2, min(5.0, self.wind_speed))

class LightningBolt:
    def __init__(self, start_pos, end_pos, color, thickness, energy=100):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color
        self.thickness = thickness
        self.energy = energy
        self.max_energy = energy
        self.points = self.generate_path()
        self.branches = []
        self.glow_radius = thickness * 3
        self.create_branches()
    
    def generate_path(self):
        points = [self.start_pos]
        current_pos = list(self.start_pos)
        target_pos = list(self.end_pos)
        
        segments = random.randint(15, 30)
        for i in range(segments):
            progress = i / segments
            
            # Natural lightning path with fractal noise
            noise_x = random.uniform(-80, 80) * (1 - progress * 0.5)
            noise_y = random.uniform(-20, 20)
            
            # Interpolate towards target
            target_x = self.start_pos[0] + (target_pos[0] - self.start_pos[0]) * progress
            target_y = self.start_pos[1] + (target_pos[1] - self.start_pos[1]) * progress
            
            current_pos[0] = target_x + noise_x
            current_pos[1] = target_y + noise_y + random.uniform(20, 60)
            
            # Keep on screen
            current_pos[0] = max(50, min(WIDTH - 50, current_pos[0]))
            current_pos[1] = min(HEIGHT, current_pos[1])
            
            points.append(tuple(current_pos))
            
            if current_pos[1] >= HEIGHT:
                break
        
        return points
    
    def create_branches(self):
        for i in range(2, len(self.points) - 2, 4):
            if random.random() > 0.6:
                branch_start = self.points[i]
                branch_end = (branch_start[0] + random.randint(-100, 100),
                             branch_start[1] + random.randint(50, 150))
                
                branch = LightningBolt(branch_start, branch_end, self.color, 
                                     max(1, self.thickness - 2), self.energy // 2)
                self.branches.append(branch)
    
    def update(self):
        self.energy -= 2
        self.glow_radius = max(0, self.glow_radius - 1)
        
        for branch in self.branches:
            branch.update()
        
        self.branches = [b for b in self.branches if b.energy > 0]
    
    def draw(self, surface):
        if self.energy > 0:
            alpha = self.energy / self.max_energy
            
            # Draw glow effect
            if self.glow_radius > 0:
                for i, point in enumerate(self.points[:-1]):
                    glow_surface = pygame.Surface((self.glow_radius * 4, self.glow_radius * 4))
                    glow_surface.set_alpha(int(30 * alpha))
                    pygame.draw.circle(glow_surface, self.color, 
                                     (self.glow_radius * 2, self.glow_radius * 2), self.glow_radius)
                    surface.blit(glow_surface, 
                               (point[0] - self.glow_radius * 2, point[1] - self.glow_radius * 2))
            
            # Draw main bolt with multiple layers
            for layer in range(3):
                thickness = max(1, self.thickness - layer)
                layer_alpha = alpha * (1 - layer * 0.3)
                layer_color = tuple(int(c * layer_alpha) for c in self.color)
                
                for i in range(len(self.points) - 1):
                    pygame.draw.line(surface, layer_color, self.points[i], self.points[i + 1], thickness)
            
            # Draw branches
            for branch in self.branches:
                branch.draw(surface)

class StormCloud:
    def __init__(self):
        self.x = random.randint(-200, WIDTH + 200)
        self.y = random.randint(30, 200)
        self.size = random.randint(120, 250)
        self.darkness = random.randint(30, 90)
        self.speed = random.uniform(0.3, 1.5)
        self.lightning_charge = random.randint(0, 100)
        self.layers = random.randint(3, 6)
    
    def update(self, weather):
        self.x += self.speed * weather.wind_speed
        if self.x > WIDTH + 300:
            self.x = -300
        
        self.lightning_charge += random.randint(-2, 5)
        self.lightning_charge = max(0, min(100, self.lightning_charge))
    
    def draw(self, surface):
        for layer in range(self.layers):
            layer_size = self.size - layer * 15
            layer_darkness = self.darkness + layer * 10
            color = (layer_darkness, layer_darkness, layer_darkness + 30)
            
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-5, 5)
            
            pygame.draw.circle(surface, color, 
                             (int(self.x + offset_x), int(self.y + offset_y)), 
                             layer_size)

# Initialize systems
weather = WeatherSystem()
particles = []
lightning_bolts = []
storm_clouds = [StormCloud() for _ in range(12)]
rain_drops = []

# Create enhanced rain system
for _ in range(500):
    rain_drops.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(-HEIGHT, 0),
        'speed': random.uniform(8, 20),
        'length': random.randint(15, 30),
        'thickness': random.randint(1, 2)
    })

# Game state
running = True
clock = pygame.time.Clock()
storm_intensity = 0
background_flash = 0
time_counter = 0
lightning_colors = list(COLORS.values())[1:8]  # Exclude white and dark colors

# Create thunder sound
def create_enhanced_thunder():
    try:
        duration = random.uniform(1.0, 2.5)
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        # Create complex thunder with multiple frequency layers
        low_freq = np.sin(2 * np.pi * np.linspace(0, 50, frames)) * 0.3
        mid_freq = np.random.normal(0, 0.2, frames)
        high_freq = np.random.normal(0, 0.1, frames) * np.exp(-np.linspace(0, 3, frames))
        
        thunder = low_freq + mid_freq + high_freq
        fade = np.exp(-np.linspace(0, 2, frames))
        thunder *= fade
        
        stereo = np.column_stack((thunder, thunder))
        thunder_array = np.ascontiguousarray((stereo * 16383).astype(np.int16))
        
        return pygame.sndarray.make_sound(thunder_array)
    except:
        return None

thunder_sound = create_enhanced_thunder()

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                storm_intensity = min(storm_intensity + 25, 100)
            elif event.key == pygame.K_r:
                # Reset storm
                storm_intensity = 0
                particles.clear()
                lightning_bolts.clear()
    
    time_counter += 1
    storm_intensity = max(0, storm_intensity - 0.15)
    weather.update(storm_intensity)
    
    # Dynamic background
    if background_flash > 0:
        bg_intensity = min(background_flash, 80)
        bg_color = (20 + bg_intensity, 25 + bg_intensity, 60 + bg_intensity)
        background_flash -= 8
    else:
        storm_factor = int(storm_intensity * 0.4)
        bg_color = (15 + storm_factor, 20 + storm_factor, 45 + storm_factor)
    
    screen.fill(bg_color)
    
    # Update and draw storm clouds
    for cloud in storm_clouds:
        cloud.update(weather)
        cloud.draw(screen)
    
    # Enhanced rain system
    if weather.rain_intensity > 10:
        rain_count = int(weather.rain_intensity * 3)
        for i, drop in enumerate(rain_drops[:rain_count]):
            drop['y'] += drop['speed'] * (1 + weather.wind_speed * 0.1)
            drop['x'] += weather.wind_speed
            
            if drop['y'] > HEIGHT:
                drop['y'] = random.randint(-100, 0)
                drop['x'] = random.randint(0, WIDTH)
            
            # Draw rain with varying opacity
            alpha = min(255, int(weather.rain_intensity * 2))
            rain_color = (100, 150, 200, alpha)
            pygame.draw.line(screen, rain_color[:3], 
                           (drop['x'], drop['y']), 
                           (drop['x'] - weather.wind_speed * 2, drop['y'] + drop['length']), 
                           drop['thickness'])
    
    # Epic lightning generation
    lightning_probability = 0.02 + (storm_intensity * 0.003)
    if random.random() < lightning_probability:
        num_bolts = random.randint(1, 4 + int(storm_intensity / 25))
        
        for _ in range(num_bolts):
            start_x = random.randint(WIDTH // 8, 7 * WIDTH // 8)
            start_y = random.randint(0, 150)
            end_x = start_x + random.randint(-200, 200)
            end_y = HEIGHT + random.randint(-100, 100)
            
            color = random.choice(lightning_colors)
            thickness = random.randint(4, 12)
            energy = random.randint(80, 150)
            
            bolt = LightningBolt((start_x, start_y), (end_x, end_y), color, thickness, energy)
            lightning_bolts.append(bolt)
            
            # Create particle explosion
            for _ in range(random.randint(20, 50)):
                particle_type = random.choice(['spark', 'ember'])
                velocity = (random.uniform(-8, 8), random.uniform(-8, 8))
                life = random.randint(30, 80)
                particles.append(AdvancedParticle(start_x, start_y, color, velocity, life, particle_type))
            
            # Trigger effects
            background_flash = random.randint(60, 120)
            storm_intensity = min(100, storm_intensity + random.randint(8, 20))
    
    # Update and draw lightning bolts
    lightning_bolts = [bolt for bolt in lightning_bolts if bolt.energy > 0]
    for bolt in lightning_bolts:
        bolt.update()
        bolt.draw(screen)
    
    # Update and draw particles
    particles = [p for p in particles if p.life > 0]
    for particle in particles:
        particle.update()
        particle.draw(screen)
    
    # Multi-layer screen flash
    if background_flash > 60:
        for layer in range(4):
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            alpha = max(0, (background_flash - 60) * (4 - layer) * 3)
            flash_surface.set_alpha(min(alpha, 120))
            flash_colors = [COLORS['WHITE'], COLORS['ELECTRIC_BLUE'], COLORS['NEON_CYAN'], COLORS['GOLDEN_YELLOW']]
            flash_surface.fill(flash_colors[layer])
            screen.blit(flash_surface, (0, 0))
        
        # Enhanced thunder
        if thunder_sound and random.random() > 0.7:
            volume = min(1.0, storm_intensity / 80)
            thunder_sound.set_volume(volume)
            thunder_sound.play()
    
    # Ground illumination with reflection
    if background_flash > 30:
        ground_height = 150
        glow_intensity = background_flash - 30
        
        # Ground glow
        ground_surface = pygame.Surface((WIDTH, ground_height))
        ground_surface.set_alpha(glow_intensity)
        ground_surface.fill(COLORS['ELECTRIC_BLUE'])
        screen.blit(ground_surface, (0, HEIGHT - ground_height))
        
        # Water reflection effect
        reflection_surface = pygame.Surface((WIDTH, 50))
        reflection_surface.set_alpha(glow_intensity // 2)
        reflection_surface.fill(COLORS['NEON_CYAN'])
        screen.blit(reflection_surface, (0, HEIGHT - 50))
    
    # Advanced UI
    if storm_intensity > 0:
        # Storm intensity bar with gradient
        bar_width = int(storm_intensity * 4)
        bar_height = 15
        
        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), (20, 20, 400, bar_height))
        
        # Gradient intensity bar
        for i in range(bar_width):
            color_ratio = i / 400
            r = int(255 * color_ratio)
            g = int(255 * (1 - color_ratio))
            b = 0
            pygame.draw.rect(screen, (r, g, b), (20 + i, 20, 1, bar_height))
        
        # Text overlay
        font = pygame.font.Font(None, 28)
        text = font.render(f"Storm Power: {int(storm_intensity)}% | Weather: {weather.temperature}°C | Wind: {weather.wind_speed:.1f}m/s", 
                          True, COLORS['WHITE'])
        screen.blit(text, (20, 45))
        
        controls_text = font.render("SPACE: Intensify Storm | R: Reset | ESC: Exit", True, COLORS['SILVER'])
        screen.blit(controls_text, (20, 75))
    
    # Performance counter
    fps = clock.get_fps()
    fps_text = pygame.font.Font(None, 24).render(f"FPS: {fps:.1f} | Particles: {len(particles)} | Bolts: {len(lightning_bolts)}", 
                                                True, COLORS['WHITE'])
    screen.blit(fps_text, (WIDTH - 300, 20))
    
    pygame.display.flip()
    clock.tick(75)  # 75 FPS for ultra-smooth experience

pygame.quit()