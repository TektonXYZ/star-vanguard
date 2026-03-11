"""
Star Vanguard — Deep Space Recovery

Year 2197. The Andromeda Expeditionary Force has sent you, Commander, 
to recover lost resources from the debris field of the fallen Titan Station.

Your mission: Extract quantum crystals from asteroids, collect repair 
nanites from damaged supply drones, and survive the automated defense 
drones that still patrol the wreckage.

The Vanguard-7 is humanity's last hope for the journey home.
"""

import pygame
import random
import math
from enum import Enum

pygame.init()

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# World settings (fixed map)
WORLD_WIDTH = 3000
WORLD_HEIGHT = 3000

# Colors
STAR_WHITE = (255, 255, 255)
ENGINE_BLUE = (0, 150, 255)
ENGINE_CORE = (100, 200, 255)
HULL_GREEN = (0, 255, 100)
SHIELD_CYAN = (0, 255, 255)
ASTEROID_GRAY = (120, 120, 130)
ASTEROID_DARK = (80, 80, 90)
HEALING_GREEN = (0, 255, 150)
HEALING_GLOW = (100, 255, 200)
ENEMY_RED = (255, 50, 50)
ENEMY_CORE = (255, 100, 100)
CRYSTAL_GOLD = (255, 215, 0)
BACKGROUND = (5, 5, 10)
GRID_COLOR = (20, 20, 30)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Star Vanguard — Deep Space Recovery")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        # Ship starts in center of world
        self.ship = {
            'x': WORLD_WIDTH // 2,
            'y': WORLD_HEIGHT // 2,
            'angle': 0,
            'vx': 0,
            'vy': 0,
            'radius': 15,
            'hull': 100,
            'max_hull': 100,
            'crystals': 0,
            'alive': True
        }
        
        # Camera follows ship (offset from ship position)
        self.camera = {
            'x': self.ship['x'] - SCREEN_WIDTH // 2,
            'y': self.ship['y'] - SCREEN_HEIGHT // 2
        }
        
        # Game objects
        self.asteroids = []
        self.healing_drones = []
        self.enemies = []
        self.projectiles = []
        self.particles = []
        self.stars = []
        
        # Generate stars for parallax
        for _ in range(200):
            self.stars.append({
                'x': random.randint(0, WORLD_WIDTH),
                'y': random.randint(0, WORLD_HEIGHT),
                'size': random.uniform(1, 3),
                'brightness': random.uniform(0.3, 1.0),
                'parallax': random.uniform(0.1, 0.5)
            })
        
        # Spawn initial objects
        self.spawn_asteroids(15)
        self.spawn_healing_drones(5)
        self.spawn_enemies(3)
        
        self.wave = 1
        self.score = 0
        
    def spawn_asteroids(self, count):
        for _ in range(count):
            self.asteroids.append({
                'x': random.uniform(100, WORLD_WIDTH - 100),
                'y': random.uniform(100, WORLD_HEIGHT - 100),
                'radius': random.uniform(20, 50),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'angle': random.uniform(0, 360),
                'rot_speed': random.uniform(-1, 1),
                'crystals': random.randint(10, 30)
            })
    
    def spawn_healing_drones(self, count):
        for _ in range(count):
            self.healing_drones.append({
                'x': random.uniform(200, WORLD_WIDTH - 200),
                'y': random.uniform(200, WORLD_HEIGHT - 200),
                'radius': 12,
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(-0.3, 0.3),
                'heal_amount': 25,
                'pulse': 0
            })
    
    def spawn_enemies(self, count):
        # Spawn away from ship
        for _ in range(count):
            angle = random.uniform(0, 360)
            dist = 400
            self.enemies.append({
                'x': self.ship['x'] + math.cos(math.radians(angle)) * dist,
                'y': self.ship['y'] + math.sin(math.radians(angle)) * dist,
                'radius': 12,
                'vx': 0,
                'vy': 0,
                'angle': 0,
                'speed': 1.5 + self.wave * 0.2,
                'hull': 2,
                'fire_timer': 0
            })
    
    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        return (x - self.camera['x'], y - self.camera['y'])
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Rotation (50% less sensitive - 0.04 instead of 0.08)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.ship['angle'] -= 0.04
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.ship['angle'] += 0.04
        
        # Thrust (30% slower - 0.21 instead of 0.3)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            thrust = 0.21
            self.ship['vx'] += math.cos(self.ship['angle']) * thrust
            self.ship['vy'] += math.sin(self.ship['angle']) * thrust
            
            # Engine particles
            for _ in range(3):
                self.particles.append({
                    'x': self.ship['x'] - math.cos(self.ship['angle']) * 20,
                    'y': self.ship['y'] - math.sin(self.ship['angle']) * 20,
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 2),
                    'life': 20,
                    'color': ENGINE_BLUE,
                    'size': random.randint(2, 5)
                })
        
        # Reverse thrust
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.ship['vx'] *= 0.95
            self.ship['vy'] *= 0.95
        
        # Fire
        if keys[pygame.K_SPACE]:
            self.fire_projectile()
        
        # Friction
        self.ship['vx'] *= 0.98
        self.ship['vy'] *= 0.98
        
        # Max speed cap
        speed = math.sqrt(self.ship['vx']**2 + self.ship['vy']**2)
        if speed > 6:  # Max speed
            self.ship['vx'] = (self.ship['vx'] / speed) * 6
            self.ship['vy'] = (self.ship['vy'] / speed) * 6
    
    def fire_projectile(self):
        # Check cooldown
        if not hasattr(self, 'last_fire'):
            self.last_fire = 0
        
        if pygame.time.get_ticks() - self.last_fire > 200:  # 200ms cooldown
            self.projectiles.append({
                'x': self.ship['x'] + math.cos(self.ship['angle']) * 20,
                'y': self.ship['y'] + math.sin(self.ship['angle']) * 20,
                'vx': math.cos(self.ship['angle']) * 12,
                'vy': math.sin(self.ship['angle']) * 12,
                'life': 60
            })
            self.last_fire = pygame.time.get_ticks()
    
    def update(self):
        if not self.ship['alive']:
            return
        
        self.handle_input()
        
        # Update ship position
        self.ship['x'] += self.ship['vx']
        self.ship['y'] += self.ship['vy']
        
        # Keep ship in world bounds
        self.ship['x'] = max(50, min(WORLD_WIDTH - 50, self.ship['x']))
        self.ship['y'] = max(50, min(WORLD_HEIGHT - 50, self.ship['y']))
        
        # Update camera (follow ship)
        self.camera['x'] = self.ship['x'] - SCREEN_WIDTH // 2
        self.camera['y'] = self.ship['y'] - SCREEN_HEIGHT // 2
        
        # Clamp camera to world bounds
        self.camera['x'] = max(0, min(WORLD_WIDTH - SCREEN_WIDTH, self.camera['x']))
        self.camera['y'] = max(0, min(WORLD_HEIGHT - SCREEN_HEIGHT, self.camera['y']))
        
        # Update asteroids
        for ast in self.asteroids:
            ast['x'] += ast['vx']
            ast['y'] += ast['vy']
            ast['angle'] += ast['rot_speed']
            
            # Bounce off world bounds
            if ast['x'] < ast['radius'] or ast['x'] > WORLD_WIDTH - ast['radius']:
                ast['vx'] *= -1
            if ast['y'] < ast['radius'] or ast['y'] > WORLD_HEIGHT - ast['radius']:
                ast['vy'] *= -1
        
        # Update healing drones
        for drone in self.healing_drones:
            drone['x'] += drone['vx']
            drone['y'] += drone['vy']
            drone['pulse'] += 0.05
            
            # Gentle bounce
            if drone['x'] < 100 or drone['x'] > WORLD_WIDTH - 100:
                drone['vx'] *= -1
            if drone['y'] < 100 or drone['y'] > WORLD_HEIGHT - 100:
                drone['vy'] *= -1
        
        # Update enemies
        for enemy in self.enemies:
            # Move toward ship
            dx = self.ship['x'] - enemy['x']
            dy = self.ship['y'] - enemy['y']
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                enemy['vx'] = (dx / dist) * enemy['speed']
                enemy['vy'] = (dy / dist) * enemy['speed']
            
            enemy['x'] += enemy['vx']
            enemy['y'] += enemy['vy']
            enemy['angle'] = math.atan2(enemy['vy'], enemy['vx'])
        
        # Update projectiles
        for proj in self.projectiles[:]:
            proj['x'] += proj['vx']
            proj['y'] += proj['vy']
            proj['life'] -= 1
            if proj['life'] <= 0:
                self.projectiles.remove(proj)
        
        # Update particles
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
        
        # Check collisions
        self.check_collisions()
    
    def check_collisions(self):
        ship = self.ship
        
        # Ship vs asteroids
        for ast in self.asteroids[:]:
            dist = math.sqrt((ship['x'] - ast['x'])**2 + (ship['y'] - ast['y'])**2)
            if dist < ship['radius'] + ast['radius']:
                ship['hull'] -= 15
                self.create_explosion(ast['x'], ast['y'], ASTEROID_GRAY, 10)
                self.asteroids.remove(ast)
                if ship['hull'] <= 0:
                    ship['alive'] = False
        
        # Ship vs healing drones
        for drone in self.healing_drones[:]:
            dist = math.sqrt((ship['x'] - drone['x'])**2 + (ship['y'] - drone['y'])**2)
            if dist < ship['radius'] + drone['radius']:
                ship['hull'] = min(ship['max_hull'], ship['hull'] + drone['heal_amount'])
                self.create_explosion(drone['x'], drone['y'], HEALING_GREEN, 15)
                self.healing_drones.remove(drone)
        
        # Ship vs enemies
        for enemy in self.enemies[:]:
            dist = math.sqrt((ship['x'] - enemy['x'])**2 + (ship['y'] - enemy['y'])**2)
            if dist < ship['radius'] + enemy['radius']:
                ship['hull'] -= 20
                self.create_explosion(enemy['x'], enemy['y'], ENEMY_RED, 15)
                self.enemies.remove(enemy)
                if ship['hull'] <= 0:
                    ship['alive'] = False
        
        # Projectiles vs asteroids
        for proj in self.projectiles[:]:
            for ast in self.asteroids[:]:
                dist = math.sqrt((proj['x'] - ast['x'])**2 + (proj['y'] - ast['y'])**2)
                if dist < ast['radius']:
                    self.ship['crystals'] += ast['crystals']
                    self.score += ast['crystals']
                    self.create_explosion(ast['x'], ast['y'], CRYSTAL_GOLD, 20)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    self.asteroids.remove(ast)
                    break
        
        # Projectiles vs enemies
        for proj in self.projectiles[:]:
            for enemy in self.enemies[:]:
                dist = math.sqrt((proj['x'] - enemy['x'])**2 + (proj['y'] - enemy['y'])**2)
                if dist < enemy['radius'] + 5:
                    enemy['hull'] -= 1
                    if enemy['hull'] <= 0:
                        self.score += 50
                        self.create_explosion(enemy['x'], enemy['y'], ENEMY_RED, 20)
                        self.enemies.remove(enemy)
                    if proj in self.projectiles:
                        self.projectiles.remove(proj)
                    break
    
    def create_explosion(self, x, y, color, count):
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(2, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(math.radians(angle)) * speed,
                'vy': math.sin(math.radians(angle)) * speed,
                'life': random.randint(20, 40),
                'color': color,
                'size': random.randint(2, 6)
            })
    
    def draw(self):
        # Clear screen
        self.screen.fill(BACKGROUND)
        
        # Draw stars (parallax)
        for star in self.stars:
            px = star['x'] - self.camera['x'] * star['parallax']
            py = star['y'] - self.camera['y'] * star['parallax']
            # Wrap stars for infinite effect
            px = px % WORLD_WIDTH
            py = py % WORLD_HEIGHT
            screen_x = px - self.camera['x']
            screen_y = py - self.camera['y']
            
            if 0 <= screen_x <= SCREEN_WIDTH and 0 <= screen_y <= SCREEN_HEIGHT:
                brightness = int(255 * star['brightness'])
                pygame.draw.circle(self.screen, (brightness, brightness, brightness), 
                                 (int(screen_x), int(screen_y)), int(star['size']))
        
        # Draw world boundary
        boundary_rect = pygame.Rect(
            -self.camera['x'], -self.camera['y'],
            WORLD_WIDTH, WORLD_HEIGHT
        )
        pygame.draw.rect(self.screen, SHIELD_CYAN, boundary_rect, 3)
        
        if not self.ship['alive']:
            # Game over screen
            go_text = self.font.render("MISSION FAILED - Press R to Restart", True, ENEMY_RED)
            text_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(go_text, text_rect)
            pygame.display.flip()
            return
        
        # Draw asteroids
        for ast in self.asteroids:
            sx, sy = self.world_to_screen(ast['x'], ast['y'])
            if -100 < sx < SCREEN_WIDTH + 100 and -100 < sy < SCREEN_HEIGHT + 100:
                points = []
                for i in range(8):
                    angle = math.radians(ast['angle'] + i * 45)
                    r = ast['radius'] * (0.8 + 0.2 * math.sin(i * 3))
                    px = sx + math.cos(angle) * r
                    py = sy + math.sin(angle) * r
                    points.append((px, py))
                pygame.draw.polygon(self.screen, ASTEROID_GRAY, points)
                pygame.draw.polygon(self.screen, ASTEROID_DARK, points, 2)
                
                # Crystal indicator
                crystal_text = self.small_font.render(str(ast['crystals']), True, CRYSTAL_GOLD)
                self.screen.blit(crystal_text, (sx - 10, sy - 10))
        
        # Draw healing drones
        for drone in self.healing_drones:
            sx, sy = self.world_to_screen(drone['x'], drone['y'])
            if -50 < sx < SCREEN_WIDTH + 50 and -50 < sy < SCREEN_HEIGHT + 50:
                # Pulsing glow
                pulse_size = drone['radius'] + abs(math.sin(drone['pulse'])) * 10
                pygame.draw.circle(self.screen, HEALING_GLOW, (int(sx), int(sy)), int(pulse_size))
                pygame.draw.circle(self.screen, HEALING_GREEN, (int(sx), int(sy)), int(drone['radius']))
                pygame.draw.circle(self.screen, (255, 255, 255), (int(sx), int(sy)), 5)
                
                # Plus sign
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (sx - 5, sy), (sx + 5, sy), 2)
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (sx, sy - 5), (sx, sy + 5), 2)
        
        # Draw enemies
        for enemy in self.enemies:
            sx, sy = self.world_to_screen(enemy['x'], enemy['y'])
            if -50 < sx < SCREEN_WIDTH + 50 and -50 < sy < SCREEN_HEIGHT + 50:
                pygame.draw.circle(self.screen, ENEMY_RED, (int(sx), int(sy)), int(enemy['radius']))
                pygame.draw.circle(self.screen, ENEMY_CORE, (int(sx), int(sy)), 6)
        
        # Draw projectiles
        for proj in self.projectiles:
            sx, sy = self.world_to_screen(proj['x'], proj['y'])
            pygame.draw.circle(self.screen, ENGINE_BLUE, (int(sx), int(sy)), 4)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(sx), int(sy)), 2)
        
        # Draw particles
        for p in self.particles:
            sx, sy = self.world_to_screen(p['x'], p['y'])
            alpha = p['life'] / 40
            color = tuple(int(c * alpha) for c in p['color'])
            pygame.draw.circle(self.screen, color, (int(sx), int(sy)), p['size'])
        
        # Draw ship (center of screen)
        sx = SCREEN_WIDTH // 2
        sy = SCREEN_HEIGHT // 2
        
        # Engine trail
        if math.sqrt(self.ship['vx']**2 + self.ship['vy']**2) > 0.5:
            for i in range(5):
                trail_x = sx - math.cos(self.ship['angle']) * (20 + i * 8)
                trail_y = sy - math.sin(self.ship['angle']) * (20 + i * 8)
                alpha = 150 - i * 25
                pygame.draw.circle(self.screen, ENGINE_BLUE, (int(trail_x), int(trail_y)), 6 - i)
        
        # Ship body
        ship_points = []
        for angle_offset in [0, 140, 180, 220]:
            angle = self.ship['angle'] + math.radians(angle_offset)
            if angle_offset == 0:
                r = 20
            else:
                r = 12
            px = sx + math.cos(angle) * r
            py = sy + math.sin(angle) * r
            ship_points.append((px, py))
        
        pygame.draw.polygon(self.screen, HULL_GREEN, ship_points)
        pygame.draw.polygon(self.screen, (255, 255, 255), ship_points, 2)
        
        # Cockpit
        pygame.draw.circle(self.screen, (0, 100, 200), (int(sx), int(sy)), 5)
        
        # UI
        # Hull bar
        hull_width = 200
        hull_height = 20
        hull_x = 20
        hull_y = 20
        pygame.draw.rect(self.screen, (50, 50, 50), (hull_x, hull_y, hull_width, hull_height))
        current_hull_width = int((self.ship['hull'] / self.ship['max_hull']) * hull_width)
        hull_color = HULL_GREEN if self.ship['hull'] > 50 else ENEMY_RED
        pygame.draw.rect(self.screen, hull_color, (hull_x, hull_y, current_hull_width, hull_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (hull_x, hull_y, hull_width, hull_height), 2)
        
        hull_text = self.small_font.render(f"HULL: {int(self.ship['hull'])}/{self.ship['max_hull']}", True, (255, 255, 255))
        self.screen.blit(hull_text, (hull_x + 5, hull_y + 2))
        
        # Crystals
        crystal_text = self.font.render(f"CRYSTALS: {self.ship['crystals']}", True, CRYSTAL_GOLD)
        self.screen.blit(crystal_text, (20, 50))
        
        # Score
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 80))
        
        # Wave
        wave_text = self.font.render(f"WAVE: {self.wave}", True, ENGINE_BLUE)
        self.screen.blit(wave_text, (20, 110))
        
        # Controls hint
        hint_text = self.small_font.render("WASD/ARROWS: Move | SPACE: Fire", True, (150, 150, 150))
        self.screen.blit(hint_text, (20, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_r and not self.ship['alive']:
                        self.reset_game()
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    print("=" * 60)
    print("STAR VANGUARD — Deep Space Recovery")
    print("=" * 60)
    print("\nMission: Collect crystals from asteroids")
    print("         Destroy healing drones for repairs")
    print("         Survive enemy patrols")
    print("\nControls: WASD/Arrows = Move")
    print("          SPACE = Fire")
    print("          R = Restart (when dead)")
    print("=" * 60)
    
    game = Game()
    game.run()
