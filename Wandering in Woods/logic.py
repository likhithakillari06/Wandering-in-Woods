import random
import pygame
import os
from settings import *

class Player:
    def __init__(self, pid, x, y):
        self.id = pid
        self.x = x
        self.y = y
        self.active = True 
        self.group_size = 1 
        
        try:
            img_path = os.path.join(IMG_DIR, f'player{pid+1}.png')
            self.image = pygame.image.load(img_path)
            self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))
        except:
            self.image = None 

    def manual_move(self, dx, dy, cols, rows):
        if not self.active: return
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < cols and 0 <= ny < rows:
            self.x = nx
            self.y = ny

    def move(self, cols, rows, mode="random"):
        if not self.active: return
        moves = []
        if self.x > 0: moves.append((-1, 0))
        if self.x < cols - 1: moves.append((1, 0))
        if self.y > 0: moves.append((0, -1))
        if self.y < rows - 1: moves.append((0, 1))
        
        if mode == "random":
            dx, dy = random.choice(moves)
            self.x += dx
            self.y += dy
        elif mode == "smart":
            # Smart Protocol: Tend to move toward the center of the grid
            cx, cy = cols // 2, rows // 2
            best_move = moves[0]
            min_dist = 9999
            for dx, dy in moves:
                dist = abs((self.x + dx) - cx) + abs((self.y + dy) - cy)
                if dist < min_dist:
                    min_dist = dist
                    best_move = (dx, dy)
            # 80% chance to move smart, 20% random to prevent getting stuck
            if random.random() < 0.8:
                self.x += best_move[0]
                self.y += best_move[1]
            else:
                dx, dy = random.choice(moves)
                self.x += dx
                self.y += dy

    def draw(self, surface, offset_x, offset_y):
        if not self.active: return
        px = offset_x + (self.x * CELL_SIZE)
        py = offset_y + (self.y * CELL_SIZE)
        
        if self.image:
            surface.blit(self.image, (px, py))
        else:
            colors = [(255, 118, 117), (85, 239, 196), (253, 203, 110), (162, 155, 254)]
            pygame.draw.circle(surface, colors[self.id % 4], (px + CELL_SIZE//2, py + CELL_SIZE//2), CELL_SIZE//2 - 5)
        
        if self.group_size > 1:
            font = pygame.font.SysFont(None, 36)
            txt = font.render(str(self.group_size), True, (255, 255, 255))
            pygame.draw.circle(surface, (200, 0, 0), (px + 10, py + 10), 12)
            surface.blit(txt, (px + 3, py + 0))

class Grid:
    def __init__(self, cols, rows, available_width):
        self.cols = cols
        self.rows = rows
        self.grid_pixel_width = cols * CELL_SIZE
        self.grid_pixel_height = rows * CELL_SIZE
        self.offset_x = (available_width - self.grid_pixel_width) // 2
        self.offset_y = (HEIGHT - self.grid_pixel_height) // 2

    def draw(self, surface):
        border_rect = pygame.Rect(self.offset_x, self.offset_y, self.grid_pixel_width, self.grid_pixel_height)
        pygame.draw.rect(surface, (255, 255, 255), border_rect, 2)

class GameSession:
    def __init__(self, cols, rows, num_players, layout_width, manual_placements=None):
        self.grid = Grid(cols, rows, layout_width)
        self.players = []
        self.steps = 0
        self.is_finished = False
        
        if manual_placements:
            for i, (cx, cy) in enumerate(manual_placements):
                self.players.append(Player(i, cx, cy))
        else:
            corners = [(0,0), (cols-1, rows-1), (0, rows-1), (cols-1, 0)]
            for i in range(num_players):
                cx, cy = corners[i]
                self.players.append(Player(i, cx, cy))

    def check_collisions(self):
        active_players = [p for p in self.players if p.active]
        for i in range(len(active_players)):
            for j in range(i + 1, len(active_players)):
                p1, p2 = active_players[i], active_players[j]
                if p1.active and p2.active and p1.x == p2.x and p1.y == p2.y:
                    p1.group_size += p2.group_size
                    p2.active = False 
        if len([p for p in self.players if p.active]) <= 1:
            self.is_finished = True

    def step(self, mode="random"):
        if self.is_finished: return
        self.steps += 1
        for p in self.players:
            p.move(self.grid.cols, self.grid.rows, mode)
            self.check_collisions() 

def run_headless_simulation(runs, cols, rows, num_players, mode="random"):
    results = []
    for _ in range(runs):
        sim = GameSession(cols, rows, num_players, 800)
        while not sim.is_finished and sim.steps < 3000:
            sim.step(mode)
        results.append(sim.steps)
    return results