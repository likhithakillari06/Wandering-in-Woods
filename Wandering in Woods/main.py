import pygame
import sys
import os
import matplotlib
matplotlib.use("Agg") 
import matplotlib.backends.backend_agg as agg
import pylab
import threading
from settings import *
from logic import GameSession, run_headless_simulation
from ui import Button, SmallButton, draw_text
from audio import AudioEngine

class Application:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wandering in the Woods")
        self.clock = pygame.time.Clock()
        self.audio = AudioEngine()
        
        try:
            self.raw_bg_img = pygame.image.load(os.path.join(IMG_DIR, 'woods_bg.png'))
        except:
            self.raw_bg_img = None

        try:
            self.menu_bg_img = pygame.image.load(os.path.join(IMG_DIR, 'menu_bg.jpg'))
            self.menu_bg_img = pygame.transform.scale(self.menu_bg_img, (WIDTH, HEIGHT))
        except:
            self.menu_bg_img = None

        # Start the game on the new Welcome Screen
        self.state = "WELCOME"
        self.session = None
        self.placements = []
        
        self.global_stats = {
            "K-2": [], "3-5": [], "6-8": [], "User Play": []
        }
        
        self.setup_cols = 10
        self.setup_rows = 8
        self.setup_players = 4
        self.algo_mode = "random"

        self.graph_surf = None
        self.is_loading_graph = False
        self.graph_data = None 

        # --- UI BUTTONS ---
        # Welcome Screen Button (Orange with Yellow hover)
        self.btn_start = Button(WIDTH//2 - 150, HEIGHT//2, 300, 60, "Let's Play the Game")
        self.btn_start.color = (255, 140, 0) # Deep Orange
        self.btn_start.hover_color = (255, 215, 0) # Gold/Yellow

        # Main Menu Buttons
        self.btn_k2 = Button(WIDTH//2 - 100, 150, 200, 50, "Grades K-2")
        self.btn_35 = Button(WIDTH//2 - 100, 220, 200, 50, "Grades 3-5")
        self.btn_68 = Button(WIDTH//2 - 100, 290, 200, 50, "Grades 6-8")
        self.btn_user = Button(WIDTH//2 - 100, 360, 200, 50, "User Play Mode")
        self.btn_stats = Button(WIDTH//2 - 100, 480, 200, 50, "View Statistics")
        
        # In-Game Buttons
        self.btn_back = Button(20, 20, 100, 40, "Main Menu")
        self.btn_restart = Button(WIDTH - 280, HEIGHT - 80, 240, 50, "Restart Round")
        self.btn_graph = Button(WIDTH - 280, HEIGHT - 150, 240, 50, "Run Big Data")
        self.btn_toggle_algo = Button(WIDTH - 280, HEIGHT - 220, 240, 50, "Algo: Random")
        
        self.btn_play_again = Button(WIDTH - 280, HEIGHT - 80, 240, 50, "Play Again!")
        self.btn_play_again.color = (0, 184, 148)
        self.btn_play_again.hover_color = (85, 239, 196)

        self.btn_col_up = SmallButton(WIDTH - 80, 150, 30, 30, "+")
        self.btn_col_dn = SmallButton(WIDTH - 280, 150, 30, 30, "-")
        self.btn_row_up = SmallButton(WIDTH - 80, 200, 30, 30, "+")
        self.btn_row_dn = SmallButton(WIDTH - 280, 200, 30, 30, "-")
        self.btn_ply_up = SmallButton(WIDTH - 80, 250, 30, 30, "+")
        self.btn_ply_dn = SmallButton(WIDTH - 280, 250, 30, 30, "-")

    def create_graph_thread(self):
        self.is_loading_graph = True
        self.audio.speak(f"Simulating 50 times using {self.algo_mode} algorithm.")
        def background_task():
            results = run_headless_simulation(50, self.setup_cols, self.setup_rows, self.setup_players, self.algo_mode)
            fig = pylab.figure(figsize=[3.5, 3], dpi=100)
            ax = fig.gca()
            ax.hist(results, bins=12, color='skyblue', edgecolor='black')
            ax.set_title(f"50 Runs ({self.algo_mode.title()})")
            canvas = agg.FigureCanvasAgg(fig)
            canvas.draw()
            raw_data = canvas.buffer_rgba().tobytes()
            size = canvas.get_width_height()
            self.graph_data = (raw_data, size) 
            pylab.close(fig)
            self.is_loading_graph = False
        threading.Thread(target=background_task, daemon=True).start()

    def run(self):
        while True:
            self.screen.fill(BG_COLOR)
            
            # --- MENU/WELCOME BACKGROUND RENDERING ---
            if self.state in ["WELCOME", "MENU"] and self.menu_bg_img:
                self.screen.blit(self.menu_bg_img, (0, 0))
            
            # --- DYNAMIC GAMEPLAY BACKGROUND RENDERING ---
            elif self.raw_bg_img and self.state not in ["WELCOME", "MENU", "STATS"]:
                if self.state == "SETUP":
                    c, r = self.setup_cols, self.setup_rows
                elif self.session:
                    c, r = self.session.grid.cols, self.session.grid.rows
                else:
                    c, r = 0, 0
                    
                if c > 0 and r > 0:
                    grid_w = c * CELL_SIZE
                    grid_h = r * CELL_SIZE
                    off_x = ((WIDTH - 300) - grid_w) // 2
                    off_y = (HEIGHT - grid_h) // 2
                    scaled_bg = pygame.transform.scale(self.raw_bg_img, (grid_w, grid_h))
                    self.screen.blit(scaled_bg, (off_x, off_y))

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            # State routing
            if self.state == "WELCOME": self.draw_welcome(events)
            elif self.state == "MENU": self.draw_menu(events)
            elif self.state == "STATS": self.draw_stats(events)
            elif self.state == "SETUP": self.run_setup(events)
            elif self.state == "K-2": self.run_game(events, "K-2")
            elif self.state == "3-5": self.run_game(events, "3-5")
            elif self.state == "6-8": self.run_game(events, "6-8")
            elif self.state == "USER": self.run_user(events)

            pygame.display.flip()
            self.clock.tick(FPS)

    def draw_welcome(self, events):
        # Yellow personalized welcome text
        draw_text(self.screen, "Welcome Likhita Killari", WIDTH//2 - 270, HEIGHT//2 - 120, 50, (255, 140, 0))
        self.btn_start.draw(self.screen)
        
        for event in events:
            if self.btn_start.is_clicked(event):
                self.audio.play_click()
                self.state = "MENU"

    def draw_menu(self, events):
        # Title updated to Orange color
        draw_text(self.screen, "Wandering in the Woods", WIDTH//2 - 270, 50, 48, (255, 180, 0))
        
        buttons = [(self.btn_k2, "K-2"), (self.btn_35, "SETUP"), (self.btn_68, "SETUP"), 
                   (self.btn_user, "SETUP"), (self.btn_stats, "STATS")]
        for btn, state in buttons:
            btn.draw(self.screen)
            for event in events:
                if btn.is_clicked(event):
                    self.audio.play_click()
                    self.graph_surf = None
                    self.session = None 
                    if state == "K-2":
                        self.state = "K-2"
                        self.session = GameSession(8, 8, 2, WIDTH - 300)
                        self.audio.speak("Welcome to K-2! Watch them wander.")
                    elif state == "SETUP":
                        self.state = "SETUP"
                        self.next_state = btn.text.split()[1] if "Grades" in btn.text else "USER"
                        self.placements = []
                        self.setup_players = 2 if self.next_state == "USER" else 4
                        self.audio.speak("Configure your grid and place your players!")
                    elif state == "STATS":
                        self.state = "STATS"

    def draw_stats(self, events):
        self.btn_back.draw(self.screen)
        draw_text(self.screen, "Global Statistics", WIDTH//2 - 150, 50, 40, (255,255,255))
        
        y = 150
        for mode, data in self.global_stats.items():
            draw_text(self.screen, f"--- {mode} Mode ---", 200, y, 28, (116, 185, 255))
            if data:
                draw_text(self.screen, f"Games: {len(data)} | Best: {min(data)} | Worst: {max(data)} | Avg: {sum(data)//len(data)}", 200, y+40, 24, (255,255,255))
            else:
                draw_text(self.screen, "No games played yet.", 200, y+40, 24, (150,150,150))
            y += 100

        for event in events:
            if self.btn_back.is_clicked(event):
                self.state = "MENU"

    def run_setup(self, events):
        self.draw_ui_panel()
        self.btn_back.draw(self.screen)
        
        draw_text(self.screen, "Grid Settings", WIDTH - 260, 100, 24)
        
        self.btn_col_dn.draw(self.screen); self.btn_col_up.draw(self.screen)
        draw_text(self.screen, f"Cols: {self.setup_cols}", WIDTH - 210, 150, 20)
        
        self.btn_row_dn.draw(self.screen); self.btn_row_up.draw(self.screen)
        draw_text(self.screen, f"Rows: {self.setup_rows}", WIDTH - 210, 200, 20)
        
        if self.next_state != "USER":
            self.btn_ply_dn.draw(self.screen); self.btn_ply_up.draw(self.screen)
            draw_text(self.screen, f"Players: {self.setup_players}", WIDTH - 210, 250, 20)

        draw_text(self.screen, f"Click Grid to Place: {len(self.placements)}/{self.setup_players}", WIDTH - 280, 320, 20, (0, 150, 0))

        temp_grid = GameSession(self.setup_cols, self.setup_rows, 0, WIDTH - 300).grid
        temp_grid.draw(self.screen)

        for event in events:
            if self.btn_back.is_clicked(event): self.state = "MENU"
            if self.btn_col_up.is_clicked(event) and self.setup_cols < 15: self.setup_cols += 1
            if self.btn_col_dn.is_clicked(event) and self.setup_cols > 5: self.setup_cols -= 1
            if self.btn_row_up.is_clicked(event) and self.setup_rows < 12: self.setup_rows += 1
            if self.btn_row_dn.is_clicked(event) and self.setup_rows > 5: self.setup_rows -= 1
            if self.next_state != "USER":
                if self.btn_ply_up.is_clicked(event) and self.setup_players < 4: self.setup_players += 1
                if self.btn_ply_dn.is_clicked(event) and self.setup_players > 2: self.setup_players -= 1

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if mx < WIDTH - 300: 
                    gx = (mx - temp_grid.offset_x) // CELL_SIZE
                    gy = (my - temp_grid.offset_y) // CELL_SIZE
                    if 0 <= gx < self.setup_cols and 0 <= gy < self.setup_rows:
                        self.placements.append((gx, gy))
                        self.audio.play_click()
                        if len(self.placements) == self.setup_players:
                            self.state = self.next_state
                            self.session = GameSession(self.setup_cols, self.setup_rows, self.setup_players, WIDTH - 300, self.placements)
                            self.audio.speak("Game starting!")

        for i, (gx, gy) in enumerate(self.placements):
            px = temp_grid.offset_x + gx * CELL_SIZE
            py = temp_grid.offset_y + gy * CELL_SIZE
            pygame.draw.circle(self.screen, (255,0,0), (px + CELL_SIZE//2, py + CELL_SIZE//2), CELL_SIZE//2 - 5)

    def run_game(self, events, mode_name):
        if not self.session.is_finished:
            self.session.step(self.algo_mode if mode_name == "6-8" else "random")
        else:
            stats_list = self.global_stats[mode_name]
            if len(stats_list) == 0 or self.session.steps != getattr(self, 'last_recorded_step', -1):
                stats_list.append(self.session.steps)
                self.last_recorded_step = self.session.steps
                self.audio.play_win()
                self.audio.speak(f"Finished in {self.session.steps} steps!")

        self.session.grid.draw(self.screen)
        for p in self.session.players: p.draw(self.screen, self.session.grid.offset_x, self.session.grid.offset_y)
        
        self.draw_ui_panel()
        self._handle_controls(events)

        if mode_name == "6-8":
            self.btn_toggle_algo.text = f"Algo: {self.algo_mode.title()}"
            self.btn_toggle_algo.draw(self.screen)
            if self.graph_data:
                raw_data, size = self.graph_data
                self.graph_surf = pygame.image.frombytes(raw_data, size, "RGBA")
                self.graph_data = None 
                self.audio.speak("Big data analysis complete!")

            if not self.is_loading_graph: self.btn_graph.draw(self.screen)
            else: draw_text(self.screen, "Generating Big Data...", WIDTH - 280, HEIGHT - 130, 20, (200, 0, 0))

            if self.graph_surf: self.screen.blit(self.graph_surf, (WIDTH - 325, 360))

            for event in events:
                if self.btn_toggle_algo.is_clicked(event):
                    self.algo_mode = "smart" if self.algo_mode == "random" else "random"
                    self.audio.play_click()
                if self.btn_graph.is_clicked(event) and not self.is_loading_graph:
                    self.audio.play_click()
                    self.create_graph_thread()

    def run_user(self, events):
        if not self.session.is_finished:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    p1 = self.session.players[0] if len(self.session.players) > 0 else None
                    p2 = self.session.players[1] if len(self.session.players) > 1 else None
                    
                    if p1 and p1.active:
                        if event.key == pygame.K_UP: p1.manual_move(0, -1, self.setup_cols, self.setup_rows)
                        if event.key == pygame.K_DOWN: p1.manual_move(0, 1, self.setup_cols, self.setup_rows)
                        if event.key == pygame.K_LEFT: p1.manual_move(-1, 0, self.setup_cols, self.setup_rows)
                        if event.key == pygame.K_RIGHT: p1.manual_move(1, 0, self.setup_cols, self.setup_rows)
                    
                    if p2 and p2.active:
                        if event.key == pygame.K_u: p2.manual_move(0, -1, self.setup_cols, self.setup_rows)
                        if event.key == pygame.K_d: p2.manual_move(0, 1, self.setup_cols, self.setup_rows)
                        if event.key == pygame.K_l: p2.manual_move(-1, 0, self.setup_cols, self.setup_rows)
                        if event.key == pygame.K_r: p2.manual_move(1, 0, self.setup_cols, self.setup_rows)
                    
                    self.session.steps += 1
                    self.session.check_collisions()
        else:
            stats_list = self.global_stats["User Play"]
            if len(stats_list) == 0 or self.session.steps != getattr(self, 'last_recorded_step', -1):
                stats_list.append(self.session.steps)
                self.last_recorded_step = self.session.steps
                self.audio.play_win()
                self.audio.speak("You found each other!")

        self.session.grid.draw(self.screen)
        for p in self.session.players: p.draw(self.screen, self.session.grid.offset_x, self.session.grid.offset_y)
        
        self.draw_ui_panel()
        self._handle_controls(events)
        
        if not self.session.is_finished:
            draw_text(self.screen, "P1: Arrows | P2: U,D,L,R", WIDTH - 280, 200, 20, (0,0,200))

    def _handle_controls(self, events):
        self.btn_back.draw(self.screen)
        
        is_finished = self.session and self.session.is_finished
        
        if is_finished:
            self.btn_play_again.draw(self.screen)
        else:
            self.btn_restart.draw(self.screen)
            
        for event in events:
            if self.btn_back.is_clicked(event):
                self.audio.play_click()
                self.state = "MENU"
                
            wants_restart = False
            if not is_finished and self.btn_restart.is_clicked(event):
                wants_restart = True
            elif is_finished and self.btn_play_again.is_clicked(event):
                wants_restart = True

            if wants_restart:
                self.audio.play_click()
                self.graph_surf = None
                if self.state == "K-2":
                    self.session = GameSession(8, 8, 2, WIDTH - 300)
                else:
                    self.session = GameSession(self.setup_cols, self.setup_rows, self.setup_players, WIDTH - 300, self.placements)

    def draw_ui_panel(self):
        ui_rect = pygame.Rect(WIDTH - 300, 0, 300, HEIGHT)
        pygame.draw.rect(self.screen, UI_BG, ui_rect)
        draw_text(self.screen, f"Mode: {self.state}", WIDTH - 280, 20, 28)
        
        if self.session and self.state != "SETUP":
            draw_text(self.screen, f"Live Steps: {self.session.steps}", WIDTH - 280, 80, 24)
            if self.session.is_finished:
                draw_text(self.screen, "FINISHED!", WIDTH - 280, 110, 24, (0, 150, 0))
            
            stats = self.global_stats.get(self.state, [])
            if stats:
                draw_text(self.screen, "--- Mode Stats ---", WIDTH - 280, 300, 22)
                draw_text(self.screen, f"Shortest Run: {min(stats)}", WIDTH - 280, 340, 20)
                draw_text(self.screen, f"Longest Run: {max(stats)}", WIDTH - 280, 380, 20)
                draw_text(self.screen, f"Average Run: {sum(stats)//len(stats)}", WIDTH - 280, 420, 20)

if __name__ == "__main__":
    app = Application()
    app.run()