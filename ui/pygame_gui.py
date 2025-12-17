import pygame
import sys
from model.board import Board
from model.game_state import GameState
from algorithms.graph import get_best_move_generator, weighted_heuristic
from algorithms.heuristics import get_cell_weight
import os

# Enums
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# Game Modes
MODE_PvCPU = 0
MODE_PvP = 1

class PyGameUI:
    # Constants
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 700
    BOARD_AREA_SIZE = 700
    
    # Colors - Distinct Palettes
    COLOR_BG = (34, 139, 34) # Green Board
    COLOR_BG_MENU = (40, 44, 52)
    COLOR_LINE = (0, 0, 0)
    COLOR_BLACK = (20, 20, 20)
    COLOR_WHITE = (240, 240, 240)
    
    COLOR_BTN_NORMAL = (100, 100, 200)
    COLOR_BTN_HOVER = (120, 120, 220)
    COLOR_BTN_SELECTED = (50, 200, 50) # Green for selected mode
    
    # Visualization
    COLOR_RAY_VALID = (0, 255, 0)
    COLOR_RAY_INVALID = (255, 0, 0)
    COLOR_NODE_SEARCH = (255, 0, 255)
    COLOR_NODE_LEAF = (0, 255, 255)
    
    def __init__(self):
        pygame.init()
        
        self.sound_enabled = False
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except (NotImplementedError, pygame.error) as e:
            print(f"Warning: Audio system unavailable - {e}")
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Othello - DAA Algorithm Visualization")
        
        # Load Sounds
        self.sounds = {}
        if self.sound_enabled:
            try:
                self.sounds['move'] = pygame.mixer.Sound('assets/sounds/move.wav')
                self.sounds['flip'] = pygame.mixer.Sound('assets/sounds/flip.wav')
                self.sounds['win'] = pygame.mixer.Sound('assets/sounds/win.wav')
            except Exception as e:
                print(f"Warning: Sound loading failed - {e}")
                self.sound_enabled = False # Disable if loading fails
        
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont('Arial', 40, bold=True)
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # App State
        self.app_state = STATE_MENU
        self.grid_size = 8
        self.game_mode = MODE_PvCPU
        
        # Menu State
        self.selected_mode_option = MODE_PvCPU # Default
        
        # Game State
        self.game_state = None
        self.human_player = Board.BLACK
        self.ai_player = Board.WHITE
        
        # Algo Mode
        self.algo_mode = False
        self.heatmap_mode = False
        self.ai_generator = None
        self.current_vis_data = None
        self.last_eval_score = 0
        
        self.running = True

    def start_game(self, size):
        self.grid_size = size
        self.game_mode = self.selected_mode_option
        
        # Re-initialize Board
        initial_board = Board(size=size)
        self.game_state = GameState(board=initial_board, player=Board.BLACK)
        self.app_state = STATE_PLAYING
        self.current_vis_data = None
        self.ai_generator = None
        self.last_eval_score = 0
        self.play_sound('move')
        
        # Recalculate cell size
        self.CELL_SIZE = self.BOARD_AREA_SIZE // self.grid_size

    def draw_menu(self):
        self.screen.fill(self.COLOR_BG_MENU)
        center_x = self.SCREEN_WIDTH // 2
        
        # Title
        title = self.font_title.render("OTHELLO - DAA PROJECT", True, self.COLOR_WHITE)
        self.screen.blit(title, (center_x - title.get_width()//2, 80))
        
        # --- 1. Select Game Mode ---
        lbl_mode = self.font.render("1. Select Game Mode:", True, (200, 200, 200))
        self.screen.blit(lbl_mode, (center_x - lbl_mode.get_width()//2, 180))
        
        modes = [("1 Player (CPU)", MODE_PvCPU), ("2 Players (PvP)", MODE_PvP)]
        self.menu_buttons_mode = []
        
        mode_btn_width = 200
        start_x_mode = center_x - (len(modes) * (mode_btn_width + 20)) // 2
        
        for i, (label, mode_val) in enumerate(modes):
            x = start_x_mode + i * (mode_btn_width + 20)
            y = 220
            rect = pygame.Rect(x, y, mode_btn_width, 50)
            
            # Highlight selected
            color = self.COLOR_BTN_SELECTED if self.selected_mode_option == mode_val else (200, 100, 100)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            # Text
            txt = self.font.render(label, True, self.COLOR_WHITE)
            self.screen.blit(txt, (x + mode_btn_width//2 - txt.get_width()//2, y + 25 - txt.get_height()//2))
            
            self.menu_buttons_mode.append((rect, mode_val))

        # --- 2. Select Grid Size (Starts Game) ---
        lbl_size = self.font.render("2. Start Game (Select Size):", True, (200, 200, 200))
        self.screen.blit(lbl_size, (center_x - lbl_size.get_width()//2, 350))
        
        sizes = [4, 6, 8, 10]
        self.menu_buttons_size = []
        start_x = center_x - ((len(sizes)*100)//2)
        
        for i, s in enumerate(sizes):
            x = start_x + i * 100
            y = 390
            rect = pygame.Rect(x, y, 80, 50)
            pygame.draw.rect(self.screen, self.COLOR_BTN_NORMAL, rect, border_radius=5)
            
            txt = self.font.render(f"{s}x{s}", True, self.COLOR_WHITE)
            self.screen.blit(txt, (x + 40 - txt.get_width()//2, y + 25 - txt.get_height()//2))
            
            self.menu_buttons_size.append((rect, s))

    def handle_menu_click(self, pos):
        # Check Mode Selection (Toggle)
        for rect, mode_val in self.menu_buttons_mode:
            if rect.collidepoint(pos):
                self.selected_mode_option = mode_val
                self.play_sound('flip')
                return

        # Check Size Selection (Start Game)
        for rect, size in self.menu_buttons_size:
            if rect.collidepoint(pos):
                self.start_game(size)
                return

    def play_sound(self, name):
        if self.sound_enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass

    def draw_board(self):
        self.screen.fill(self.COLOR_BG)
        
        # Grid
        for i in range(self.grid_size + 1):
            pos = i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.COLOR_LINE, (pos, 0), (pos, self.BOARD_AREA_SIZE), 2)
            pygame.draw.line(self.screen, self.COLOR_LINE, (0, pos), (self.BOARD_AREA_SIZE, pos), 2)

        # Heatmap Overlay
        if self.heatmap_mode:
            self._draw_heatmap()
            
        # Discs
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                cell = self.game_state.board.grid[r][c]
                if cell != Board.EMPTY:
                    self._draw_disc(r, c, cell, 255)

        # Visualization: CPU
        if self.algo_mode and self.current_vis_data and self.game_mode == MODE_PvCPU:
            self._draw_ai_visualization()

        # Visualization: Raycasting (User)
        # Show for current player if it's a human turn logic
        is_human_turn = False
        if self.game_mode == MODE_PvP:
            is_human_turn = True
        elif self.game_mode == MODE_PvCPU and self.game_state.player == self.human_player:
            is_human_turn = True
            
        if self.algo_mode and is_human_turn:
            self._draw_user_visualization()
            
        # Side Panel
        self._draw_side_panel()
        
    def _draw_heatmap(self):
        s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                w = get_cell_weight(r, c, self.grid_size)
                if w > 1:
                     # Greenish for good
                     color = (0, 255, 0, 100) if w == 100 else (100, 255, 100, 50)
                elif w < 1:
                     # Reddish for bad
                     color = (255, 0, 0, 150) if w == -50 else (255, 100, 100, 50)
                else:
                     continue
                
                pygame.draw.rect(s, color, s.get_rect())
                self.screen.blit(s, (c*self.CELL_SIZE, r*self.CELL_SIZE))

    def _draw_disc(self, r, c, player, alpha):
        x = c * self.CELL_SIZE + self.CELL_SIZE // 2
        y = r * self.CELL_SIZE + self.CELL_SIZE // 2
        radius = self.CELL_SIZE // 2 - 5
        color = self.COLOR_BLACK if player == Board.BLACK else self.COLOR_WHITE
        
        if alpha < 255:
            s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(s, color + (alpha,), (self.CELL_SIZE//2, self.CELL_SIZE//2), radius)
            self.screen.blit(s, (c*self.CELL_SIZE, r*self.CELL_SIZE))
        else:
            pygame.draw.circle(self.screen, color, (x, y), radius)

    def _draw_user_visualization(self):
        mx, my = pygame.mouse.get_pos()
        if mx < self.BOARD_AREA_SIZE:
             c, r = mx // self.CELL_SIZE, my // self.CELL_SIZE
             valid, logs = self.game_state.board.is_valid_move(r, c, self.game_state.player, return_debug=True)
             
             center = (c * self.CELL_SIZE + self.CELL_SIZE//2, r * self.CELL_SIZE + self.CELL_SIZE//2)
             for log in logs:
                end_r, end_c = log['end']
                end_pos = (end_c * self.CELL_SIZE + self.CELL_SIZE//2, end_r * self.CELL_SIZE + self.CELL_SIZE//2)
                color = self.COLOR_RAY_VALID if log['valid'] else self.COLOR_RAY_INVALID
                pygame.draw.line(self.screen, color, center, end_pos, 4)
                pygame.draw.circle(self.screen, color, end_pos, 6)

    def _draw_ai_visualization(self):
        s = pygame.Surface((self.BOARD_AREA_SIZE, self.BOARD_AREA_SIZE))
        s.set_alpha(40)
        s.fill((50, 0, 50))
        self.screen.blit(s, (0,0))
        
        data = self.current_vis_data
        if data['type'] in ('search_node', 'leaf'):
             state = data['state']
             if state:
                 for r in range(self.grid_size):
                    for c in range(self.grid_size):
                        if state.board.grid[r][c] != Board.EMPTY:
                             self._draw_disc(r, c, state.board.grid[r][c], 100)
                             
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0)]
        depth = data.get('depth', 0)
        col = colors[depth % len(colors)]
        pygame.draw.rect(self.screen, col, (0, 0, self.BOARD_AREA_SIZE, self.BOARD_AREA_SIZE), 5)
        txt = self.font.render(f"SIMULATING DEPTH {depth}", True, col)
        self.screen.blit(txt, (20, 20))
        
        # Pruning Visualization
        if data['type'] == 'prune':
            p_state = data['state']
            if p_state:
                 # Just flash a red border or text
                 pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, self.BOARD_AREA_SIZE, self.BOARD_AREA_SIZE), 10)
                 t = self.font_title.render("PRUNED!", True, (255, 0, 0))
                 self.screen.blit(t, (self.BOARD_AREA_SIZE//2 - t.get_width()//2, self.BOARD_AREA_SIZE//2))

    def _draw_eval_bar(self, x, y, width, height):
        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, width, height))
        
        # Normalized score: -100 (White winning) to +100 (Black winning)
        # Clamped
        score = max(-500, min(500, self.last_eval_score))
        
        # Center is 0
        center_y = y + height // 2
        
        # Height of bar per score unit
        # Full height (height/2) represents 100 points roughly for visual
        pixels_per_point = (height/2) / 100
        bar_h = abs(score) * pixels_per_point
        
        if score > 0:
            # Black advantage (Bottom up from center? Or Top? Usually Black is bottom in Othello/Chess conventions varies. Let's say Black is positive/Up)
            # Actually standard Evaluation bar: Top is usually Advantage White if White is top player.
            # Visual: Black is positive (Up from center)
            rect = pygame.Rect(x, center_y - bar_h, width, bar_h)
            pygame.draw.rect(self.screen, (0, 0, 0), rect) # Black bar
        else:
            # White advantage (Down from center)
            rect = pygame.Rect(x, center_y, width, bar_h)
            pygame.draw.rect(self.screen, (255, 255, 255), rect) # White bar
            
        # Center Line
        pygame.draw.line(self.screen, (100, 100, 100), (x, center_y), (x + width, center_y), 1)

    def _draw_side_panel(self):
        panel_x = self.BOARD_AREA_SIZE
        pygame.draw.rect(self.screen, (60, 60, 60), (panel_x, 0, self.SCREEN_WIDTH-panel_x, self.SCREEN_HEIGHT))
        x = panel_x + 20
        y = 20
        
        mode_str = "1 PLAYER (CPU)" if self.game_mode == MODE_PvCPU else "2 PLAYERS (PvP)"
        self.screen.blit(self.small_font.render(mode_str, True, (200, 200, 100)), (x, y))
        y += 40
        
        turn_str = "BLACK" if self.game_state.player == Board.BLACK else "WHITE"
        turn_col = (0,0,0) if self.game_state.player == Board.BLACK else (255,255,255)
        lbl = self.font_title.render(turn_str, True, turn_col, (100,100,100))
        self.screen.blit(lbl, (x, y))
        y += 60
        
        b, w = self.game_state.board.get_counts()
        self.screen.blit(self.font.render(f"Black: {b}", True, self.COLOR_WHITE), (x, y))
        y += 30
        self.screen.blit(self.font.render(f"White: {w}", True, self.COLOR_WHITE), (x, y))
        y += 60
        
        mode_txt = "ON" if self.algo_mode else "OFF"
        mode_col = (0, 255, 0) if self.algo_mode else (100, 100, 100)
        mode_txt = "ON" if self.algo_mode else "OFF"
        mode_col = (0, 255, 0) if self.algo_mode else (100, 100, 100)
        self.screen.blit(self.font.render("Algo View (A)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(mode_txt, True, mode_col), (x + 140, y - 5))
        y += 40
        
        hm_txt = "ON" if self.heatmap_mode else "OFF"
        hm_col = (0, 255, 0) if self.heatmap_mode else (100, 100, 100)
        self.screen.blit(self.font.render("Heatmap (H)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(hm_txt, True, hm_col), (x + 140, y - 5))
        y += 50

        # Eval Bar
        self._draw_eval_bar(x, y, 40, 150)
        # Text
        sc = self.last_eval_score
        col = (0, 255, 0) if sc > 0 else (255, 0, 0)
        self.screen.blit(self.small_font.render(f"Eval: {sc}", True, col), (x + 50, y + 70))
        y += 170
        
        if self.game_state.is_terminal():
            winner = self.game_state.get_winner()
            t = "Black Wins!" if winner==1 else "White Wins!" if winner==-1 else "Draw!"
            self.screen.blit(self.font_title.render(t, True, (255,255,0)), (x, y))
            self.play_sound('win')

        # Restart
        self.btn_restart = pygame.Rect(x, self.SCREEN_HEIGHT - 80, 160, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_restart, border_radius=5)
        oms = self.font.render("MENU", True, self.COLOR_WHITE)
        self.screen.blit(oms, (self.btn_restart.centerx - oms.get_width()//2, self.btn_restart.centery - oms.get_height()//2))

    def update_ai(self):
        if not self.ai_generator:
            self.ai_generator = get_best_move_generator(self.game_state, depth=3)
        try:
            vis = next(self.ai_generator)
            if vis['type'] == 'result':
                self.game_state = vis['state']
                
                # Update Score for Eval Bar
                self.last_eval_score = weighted_heuristic(self.game_state.board, Board.BLACK)
                
                self.ai_generator = None
                self.current_vis_data = None
                self.play_sound('move')
            else:
                self.current_vis_data = vis
                # Optional: Play ticking sound for search?
                if vis['type'] == 'prune':
                     # self.play_sound('flip') # Maybe too annoying
                     pass
        except StopIteration:
            self.ai_generator = None

    def run(self):
        while self.running:
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if self.app_state == STATE_MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                         self.handle_menu_click((mx, my))
                         
                elif self.app_state == STATE_PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            self.algo_mode = not self.algo_mode
                        if event.key == pygame.K_h:
                            self.heatmap_mode = not self.heatmap_mode
                            self.play_sound('flip')
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # Human Move Logic
                        can_move = False
                        if self.game_mode == MODE_PvP:
                            can_move = True # Always human in PvP
                        elif self.game_mode == MODE_PvCPU:
                            if self.game_state.player == self.human_player:
                                can_move = True
                                
                        if can_move:
                             if mx < self.BOARD_AREA_SIZE:
                                 c, r = mx // self.CELL_SIZE, my // self.CELL_SIZE
                                 if self.game_state.board.is_valid_move(r, c, self.game_state.player):
                                     new_board, _ = self.game_state.board.apply_move(r, c, self.game_state.player)
                                     self.play_sound('move')
                                     
                                     # Match successor
                                     successors = self.game_state.get_successors()
                                     for s in successors:
                                         if s.board.grid == new_board.grid:
                                             self.game_state = s
                                             # Update Eval
                                             self.last_eval_score = weighted_heuristic(self.game_state.board, Board.BLACK)
                                             break
                        
                        # Restart Button
                        if hasattr(self, 'btn_restart') and self.btn_restart.collidepoint((mx, my)):
                             self.app_state = STATE_MENU
                             self.play_sound('flip')

            # Render
            if self.app_state == STATE_MENU:
                self.draw_menu()
            elif self.app_state == STATE_PLAYING:
                self.draw_board()
                
                # AI Logic
                if self.game_mode == MODE_PvCPU and self.game_state.player == self.ai_player and not self.game_state.is_terminal():
                    if self.algo_mode:
                        self.update_ai()
                    else:
                        for _ in range(20): 
                            if self.game_state.player == self.ai_player:
                                self.update_ai()
                            else:
                                break

            pygame.display.flip()
            self.clock.tick(30 if self.algo_mode else 60)

        pygame.quit()
