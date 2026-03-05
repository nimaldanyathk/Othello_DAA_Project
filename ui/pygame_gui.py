import pygame
import sys
import subprocess
import time
from model.board import Board
from model.game_state import GameState
from algorithms.graph import get_best_move_generator, weighted_heuristic
from algorithms.heuristics import get_cell_weight
from algorithms.greedy import get_greedy_move, get_greedy_move_generator
from algorithms.divide_and_conquer import choosebestmovevisual
from algorithms.dp import get_dp_move_generator
from algorithms.backtracking import get_backtracking_move_generator
from algorithms.backtracknoheuristic import evaluatemovevisual as noheur_evaluatemovevisual

import os


def get_backtracking_move_generator_noheur(game_state, depth=4):
    player = game_state.player
    board = game_state.board
    
    moves = board.get_valid_moves(player)
    
    if not moves:
        yield {'type': 'result', 'state': game_state}
        return
        
    scoredmoves = yield from noheur_evaluatemovevisual(board, moves, depth, player, player, True)
    
    scoredmoves.sort(key=lambda x: x[0], reverse=True)
    bestscore, bestmove = scoredmoves[0]
    
    newboard, _ = board.apply_move(bestmove[0], bestmove[1], player)
    nextplayer = -player
    
    resultstate = GameState(newboard, nextplayer)
    yield {'type': 'result', 'state': resultstate, 'score': bestscore}


# Enums
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

# Game Modes
MODE_PvCPU = 0
MODE_PvP = 1

# CPU Strategies
STRAT_GREEDY = 0
STRAT_DNC = 1
STRAT_DP = 2
STRAT_BT = 3
STRAT_BT_NO_HEURISTIC = 4


class PyGameUI:
    # Constants
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 700
    BOARD_AREA_SIZE = 700
    
    # Colors - Distinct Palettes
    COLOR_BG = (24, 119, 64) # Richer Green Board
    COLOR_BG_MENU = (30, 34, 42)
    COLOR_LINE = (10, 50, 20)
    COLOR_BLACK = (15, 15, 15)
    COLOR_WHITE = (245, 245, 245)
    
    COLOR_BTN_NORMAL = (100, 100, 200)
    COLOR_BTN_HOVER = (120, 120, 220)
    COLOR_BTN_SELECTED = (50, 200, 50) # Green for selected mode
    
    # Visualization
    COLOR_RAY_VALID = (0, 255, 0)
    COLOR_RAY_INVALID = (255, 0, 0)
    COLOR_NODE_SEARCH = (255, 0, 255)
    COLOR_NODE_LEAF = (0, 255, 255)
    
    def __init__(self):
        # Pre-initialize mixer for better MP3 support
        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
        except:
            pass
            
        pygame.init()
        
        self.sound_enabled = False
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except (NotImplementedError, pygame.error) as e:
            print(f"Warning: Audio system unavailable - {e}")
        
        self.screen_width = 900
        self.screen_height = 700
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Othello - DAA Algorithm Visualization")
        
        self.board_area_size = 700
        self.cell_size = 80
        self.font_scale = 1.0
        
        self.calculate_layout(self.screen_width, self.screen_height)
        
        self.sounds = {}
        if self.sound_enabled:
            # We wrap the loading in a try block and check for path existence
            # to prevent silent failures that disable the whole sound system.
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                bgm_path = os.path.join(base_dir, 'assets', 'sounds', 'Background Music.mp3')
                
                if os.path.exists(bgm_path):
                    pygame.mixer.music.load(bgm_path)
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
                
                sound_files = {
                    'move': os.path.join(base_dir, 'assets', 'sounds', 'Moves click.mp3'),
                    'win': os.path.join(base_dir, 'assets', 'sounds', 'Won.mp3'),
                    'loss': os.path.join(base_dir, 'assets', 'sounds', 'LOST.mp3'),
                    'capture_more': os.path.join(base_dir, 'assets', 'sounds', 'Captured More.mp3'),
                    'opp_capture_more': os.path.join(base_dir, 'assets', 'sounds', 'Opp captured more.mp3')
                }
                
                for key, path in sound_files.items():
                    if os.path.exists(path):
                        self.sounds[key] = pygame.mixer.Sound(path)
                    else:
                        print(f"Warning: Missing sound file {path}")
                        
            except Exception as e:
                print(f"Warning: Secondary sound loading failed - {e}")
        
        self.clock = pygame.time.Clock()
        
        self.app_state = STATE_MENU
        self.grid_size = 8
        self.game_mode = MODE_PvCPU
        
        self.selected_mode_option = MODE_PvCPU
        self.cpu_strategy = STRAT_DNC
        self.selected_grid_size = 8
        
        self.game_state = None
        self.human_player = Board.BLACK
        self.ai_player = Board.WHITE
        
        self.algo_mode = False
        self.heatmap_mode = False
        self.ai_generator = None
        self.current_vis_data = None
        self.is_comparing = False
        self.defer_benchmark = False
        self.dropdown_open = False
        self.dropdown_rect = pygame.Rect(0, 0, 0, 0)
        self.show_eval_bar = True
        
        self.running = True

    def calculate_layout(self, w, h):
        self.screen_width = w
        self.screen_height = h
        
        # Board takes up maximum square space possible, leaving room for panel
        min_panel_width = 200
        available_board_w = w - min_panel_width
        
        if available_board_w < h:
            self.board_area_size = available_board_w
        else:
            self.board_area_size = h
            
        if self.board_area_size < 300:
            self.board_area_size = 300
            
        if hasattr(self, 'grid_size') and self.grid_size > 0:
            self.cell_size = self.board_area_size // self.grid_size
        else:
            self.cell_size = self.board_area_size // 8
            
        # Dynamic Font Sizing
        title_size = int(min(w, h) * 0.05) if min(w,h) * 0.05 > 20 else 20
        text_size = int(min(w, h) * 0.03) if min(w,h) * 0.03 > 14 else 14
        small_size = int(min(w, h) * 0.025) if min(w,h) * 0.025 > 12 else 12
        
        self.font_title = pygame.font.SysFont('Arial', title_size, bold=True)
        self.font = pygame.font.SysFont('Arial', text_size)
        self.small_font = pygame.font.SysFont('Arial', small_size)

    def start_game(self, size):
        self.grid_size = size
        self.game_mode = self.selected_mode_option
        
        initial_board = Board(size=size)
        
        mid = size // 2
        initial_board.grid[mid-1][mid-1] = Board.WHITE
        initial_board.grid[mid][mid] = Board.WHITE
        initial_board.grid[mid-1][mid] = Board.BLACK
        initial_board.grid[mid][mid-1] = Board.BLACK
        
        self.game_state = GameState(board=initial_board, player=Board.BLACK)
        self.app_state = STATE_PLAYING
        self.current_vis_data = None
        self.ai_generator = None
        self.last_eval_score = 0
        self.play_sound('move')
        
        self.calculate_layout(self.screen_width, self.screen_height)

    def draw_menu(self):
        self.screen.fill(self.COLOR_BG_MENU)
        center_x = self.screen_width // 2
        
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

        # --- 2. Select CPU Strategy (If 1 Player) ---
        is_1player = self.selected_mode_option == MODE_PvCPU
        lbl_color = (200, 200, 200) if is_1player else (80, 80, 80)
        lbl_strat = self.font.render("2. Select CPU Strategy (If 1 Player):", True, lbl_color)
        self.screen.blit(lbl_strat, (center_x - lbl_strat.get_width()//2, 300))
        
        self.strats = [("Greedy", STRAT_GREEDY), ("Divide & Conquer", STRAT_DNC), ("DP", STRAT_DP), ("Backtracking", STRAT_BT), ("Backtracking (No Heur)", STRAT_BT_NO_HEURISTIC)]
        
        # Dropdown closed state rendering
        dd_width = 250
        dd_x = center_x - dd_width // 2
        dd_y = 340
        self.btn_dropdown = pygame.Rect(dd_x, dd_y, dd_width, 50)
        
        color = self.COLOR_BTN_NORMAL if is_1player else (60, 60, 60)
        pygame.draw.rect(self.screen, color, self.btn_dropdown, border_radius=5)
        
        current_name = next((name for name, val in self.strats if val == self.cpu_strategy), "Unknown")
        txt_color = self.COLOR_WHITE if is_1player else (120, 120, 120)
        txt = self.font.render(current_name + " \u25BC", True, txt_color)
        self.screen.blit(txt, (dd_x + dd_width//2 - txt.get_width()//2, dd_y + 25 - txt.get_height()//2))
        
        # Removed dropdown open render from here to draw at the end
        # "N/A" overlay text when in PvP mode
        if not is_1player:
            na = self.font.render("(Not applicable in 2 Player mode)", True, (100, 100, 100))
            self.screen.blit(na, (center_x - na.get_width()//2, 400))

        # --- 3. Select Grid Size ---
        lbl_size = self.font.render("3. Select Size:", True, (200, 200, 200))
        self.screen.blit(lbl_size, (center_x - lbl_size.get_width()//2, 430))
        
        sizes = [4, 6, 8, 10]
        self.menu_buttons_size = []
        start_x = center_x - ((len(sizes)*100)//2)
        
        for i, s in enumerate(sizes):
            x = start_x + i * 100
            y = 470
            rect = pygame.Rect(x, y, 80, 50)
            color = self.COLOR_BTN_SELECTED if getattr(self, 'selected_grid_size', 8) == s else self.COLOR_BTN_NORMAL
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            txt = self.font.render(f"{s}x{s}", True, self.COLOR_WHITE)
            self.screen.blit(txt, (x + 40 - txt.get_width()//2, y + 25 - txt.get_height()//2))
            
            self.menu_buttons_size.append((rect, s))

        # --- 4. Start Game Button ---
        self.btn_start = pygame.Rect(center_x - 125, 560, 250, 50)
        pygame.draw.rect(self.screen, (50, 200, 50), self.btn_start, border_radius=5)
        txt = self.font.render("START GAME", True, self.COLOR_BLACK)
        self.screen.blit(txt, (self.btn_start.centerx - txt.get_width()//2, self.btn_start.centery - txt.get_height()//2))

        # Render open dropdown on top of everything else
        self.menu_buttons_strat = []
        if self.dropdown_open and is_1player:
            # Recreate variables since we moved this to end
            dd_width = 250
            dd_x = center_x - dd_width // 2
            dd_y = 340
            
            self.dropdown_rect = pygame.Rect(dd_x, dd_y + 50, dd_width, len(self.strats) * 40)
            
            # Solid background with a slight shadow effect
            shadow_rect = pygame.Rect(dd_x + 5, dd_y + 55, dd_width, len(self.strats) * 40)
            pygame.draw.rect(self.screen, (20, 20, 30), shadow_rect, border_radius=5)
            
            pygame.draw.rect(self.screen, (40, 40, 60), self.dropdown_rect, border_radius=5)
            pygame.draw.rect(self.screen, self.COLOR_WHITE, self.dropdown_rect, width=2, border_radius=5)
            
            for i, (label, strat_val) in enumerate(self.strats):
                rect = pygame.Rect(dd_x, dd_y + 50 + i * 40, dd_width, 40)
                
                # Hover effect for dropdown items
                mx, my = pygame.mouse.get_pos()
                item_color = (70, 70, 100) if rect.collidepoint((mx, my)) else (40, 40, 60)
                item_color = self.COLOR_BTN_SELECTED if self.cpu_strategy == strat_val else item_color
                pygame.draw.rect(self.screen, item_color, rect)
                
                txt = self.small_font.render(label, True, self.COLOR_WHITE)
                self.screen.blit(txt, (dd_x + 10, dd_y + 50 + i * 40 + 20 - txt.get_height()//2))
                self.menu_buttons_strat.append((rect, strat_val))



    def handle_menu_click(self, pos):
        # Handle dropdown open state first
        if self.dropdown_open:
            if self.selected_mode_option == MODE_PvCPU:
                for rect, strat_val in self.menu_buttons_strat:
                    if rect.collidepoint(pos):
                        self.cpu_strategy = strat_val
                        self.dropdown_open = False
                        self.play_sound('flip')
                        return
            self.dropdown_open = False
            return
            
        for rect, mode_val in self.menu_buttons_mode:
            if rect.collidepoint(pos):
                self.selected_mode_option = mode_val
                self.play_sound('flip')
                return

        if self.selected_mode_option == MODE_PvCPU and hasattr(self, 'btn_dropdown'):
            if self.btn_dropdown.collidepoint(pos):
                self.dropdown_open = not self.dropdown_open
                self.play_sound('flip')
                return

        for rect, size in self.menu_buttons_size:
            if rect.collidepoint(pos):
                self.selected_grid_size = size
                self.play_sound('flip')
                return

        if hasattr(self, 'btn_start') and self.btn_start.collidepoint(pos):
            self.start_game(getattr(self, 'selected_grid_size', 8))
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
            pos = i * self.cell_size
            pygame.draw.line(self.screen, self.COLOR_LINE, (pos, 0), (pos, self.board_area_size), 2)
            pygame.draw.line(self.screen, self.COLOR_LINE, (0, pos), (self.board_area_size, pos), 2)

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
        s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
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
                self.screen.blit(s, (c*self.cell_size, r*self.cell_size))

    def _draw_disc(self, r, c, player, alpha):
        x = c * self.cell_size + self.cell_size // 2
        y = r * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 2 - 5
        color = self.COLOR_BLACK if player == Board.BLACK else self.COLOR_WHITE
        
        if alpha == 255:
            # Draw shadow
            pygame.draw.circle(self.screen, (10, 40, 20), (x + 3, y + 3), radius)
        
        if alpha < 255:
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            pygame.draw.circle(s, color + (alpha,), (self.cell_size//2, self.cell_size//2), radius)
            self.screen.blit(s, (c*self.cell_size, r*self.cell_size))
        else:
            pygame.draw.circle(self.screen, color, (x, y), radius)
            # Add highlight for 3D effect
            highlight = (60, 60, 60) if player == Board.BLACK else (255, 255, 255)
            pygame.draw.circle(self.screen, highlight, (int(x - radius*0.3), int(y - radius*0.3)), int(radius*0.2))

    def draw_game_over(self):
        # Draw the base board first under the overlay
        self.draw_board()
        
        # Semi-transparent overlay
        s = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 190)) # Dark overlay
        self.screen.blit(s, (0, 0))
        
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        winner = self.game_state.get_winner()
        b, w = self.game_state.board.get_counts()
        
        # Determine title text based on mode and winner
        if winner == Board.BLACK:
            if self.game_mode == MODE_PvCPU and self.human_player == Board.BLACK:
                title_txt = "YOU WIN!"
                color = (50, 255, 50)
            elif self.game_mode == MODE_PvCPU:
                title_txt = "CPU WINS!"
                color = (255, 70, 70)
            else:
                title_txt = "BLACK WINS!"
                color = (150, 150, 150)
        elif winner == Board.WHITE:
            if self.game_mode == MODE_PvCPU and self.human_player == Board.WHITE:
                title_txt = "YOU WIN!"
                color = (50, 255, 50)
            elif self.game_mode == MODE_PvCPU:
                title_txt = "CPU WINS!"
                color = (255, 70, 70)
            else:
                title_txt = "WHITE WINS!"
                color = (255, 255, 255)
        else:
            title_txt = "DRAW!"
            color = (255, 255, 100)
            
        # Draw Title
        title = self.font_title.render(title_txt, True, color)
        # Add text shadow
        shadow = self.font_title.render(title_txt, True, (0, 0, 0))
        self.screen.blit(shadow, (center_x - title.get_width()//2 + 2, center_y - 120 + 2))
        self.screen.blit(title, (center_x - title.get_width()//2, center_y - 120))
        
        # Draw Score
        score_txt = self.font.render(f"Final Score - Black: {b} | White: {w}", True, self.COLOR_WHITE)
        self.screen.blit(score_txt, (center_x - score_txt.get_width()//2, center_y - 40))
        
        # Play Again button
        self.btn_play_again = pygame.Rect(center_x - 110, center_y + 30, 220, 50)
        pygame.draw.rect(self.screen, (50, 200, 50), self.btn_play_again, border_radius=8)
        txt = self.font.render("PLAY AGAIN", True, self.COLOR_BLACK)
        self.screen.blit(txt, (self.btn_play_again.centerx - txt.get_width()//2, self.btn_play_again.centery - txt.get_height()//2))
        
        # Quit to Menu button
        self.btn_quit = pygame.Rect(center_x - 110, center_y + 100, 220, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_quit, border_radius=8)
        txt = self.font.render("QUIT TO MENU", True, self.COLOR_WHITE)
        self.screen.blit(txt, (self.btn_quit.centerx - txt.get_width()//2, self.btn_quit.centery - txt.get_height()//2))


    def _draw_user_visualization(self):
        mx, my = pygame.mouse.get_pos()
        if mx < self.board_area_size:
             c, r = mx // self.cell_size, my // self.cell_size
             valid, logs = self.game_state.board.is_valid_move(r, c, self.game_state.player, return_debug=True)
             
             center = (c * self.cell_size + self.cell_size//2, r * self.cell_size + self.cell_size//2)
             for log in logs:
                end_r, end_c = log['end']
                end_pos = (end_c * self.cell_size + self.cell_size//2, end_r * self.cell_size + self.cell_size//2)
                color = self.COLOR_RAY_VALID if log['valid'] else self.COLOR_RAY_INVALID
                pygame.draw.line(self.screen, color, center, end_pos, 4)
                pygame.draw.circle(self.screen, color, end_pos, 6)

    def _draw_ai_visualization(self):
        s = pygame.Surface((self.board_area_size, self.board_area_size))
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
        pygame.draw.rect(self.screen, col, (0, 0, self.board_area_size, self.board_area_size), 5)
        txt = self.font.render(f"SIMULATING DEPTH {depth}", True, col)
        self.screen.blit(txt, (20, 20))
        
        # Pruning Visualization
        if data['type'] == 'prune':
            p_state = data['state']
            if p_state:
                 # Just flash a red border or text
                 pygame.draw.rect(self.screen, (255, 0, 0), (0, 0, self.board_area_size, self.board_area_size), 10)
                 t = self.font_title.render("PRUNED!", True, (255, 0, 0))
                 self.screen.blit(t, (self.board_area_size//2 - t.get_width()//2, self.board_area_size//2))

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
            # Black advantage
            rect = pygame.Rect(x, center_y - bar_h, width, bar_h)
            pygame.draw.rect(self.screen, (0, 0, 0), rect) # Black bar
        else:
            # White advantage
            rect = pygame.Rect(x, center_y, width, bar_h)
            pygame.draw.rect(self.screen, (255, 255, 255), rect) # White bar
            
        # Center Line
        pygame.draw.line(self.screen, (100, 100, 100), (x, center_y), (x + width, center_y), 1)

    def _draw_side_panel(self):
        panel_x = self.board_area_size
        pygame.draw.rect(self.screen, (60, 60, 60), (panel_x, 0, self.screen_width-panel_x, self.screen_height))
        x = panel_x + 20
        y = 20
        
        mode_str = "1 PLAYER (CPU)" if self.game_mode == MODE_PvCPU else "2 PLAYERS (PvP)"
        if self.game_mode == MODE_PvCPU:
            if self.cpu_strategy == STRAT_GREEDY:
                mode_str += " - GREEDY"
            elif self.cpu_strategy == STRAT_DNC:
                mode_str += " - D&C"
            elif self.cpu_strategy == STRAT_DP:
                mode_str += " - DP"
            elif self.cpu_strategy == STRAT_BT:
                mode_str += " - BACKTRACKING"
            elif self.cpu_strategy == STRAT_BT_NO_HEURISTIC:
                mode_str += " - BACKTRACK (NO HEUR)"

        
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
        self.screen.blit(self.font.render("Algo View (A)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(mode_txt, True, mode_col), (x + 140, y - 5))
        y += 40
        
        hm_txt = "ON" if self.heatmap_mode else "OFF"
        hm_col = (0, 255, 0) if self.heatmap_mode else (100, 100, 100)
        self.screen.blit(self.font.render("Heatmap (H)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(hm_txt, True, hm_col), (x + 140, y - 5))
        y += 40
        
        ev_txt = "ON" if self.show_eval_bar else "OFF"
        ev_col = (0, 255, 0) if self.show_eval_bar else (100, 100, 100)
        self.screen.blit(self.font.render("Eval Bar (E)", True, (200,200,200)), (x, y))
        self.screen.blit(self.font_title.render(ev_txt, True, ev_col), (x + 140, y - 5))
        y += 50

        # Eval Bar
        if self.show_eval_bar:
            self._draw_eval_bar(x, y, 40, 150)
            # Text
            sc = self.last_eval_score
            col = (0, 255, 0) if sc > 0 else (255, 0, 0)
            self.screen.blit(self.small_font.render(f"Eval: {sc}", True, col), (x + 50, y + 70))
        
        y += 170
        # Surrender
        self.btn_restart = pygame.Rect(x, self.screen_height - 80, 160, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_restart, border_radius=5)
        oms = self.font.render("SURRENDER", True, self.COLOR_WHITE)
        self.screen.blit(oms, (self.btn_restart.centerx - oms.get_width()//2, self.btn_restart.centery - oms.get_height()//2))


    def update_ai(self):
        if not self.ai_generator:
            if self.cpu_strategy == STRAT_GREEDY:
                # Greedy Strategy doesn't have an iterative generator, make move immediately
                best_state = get_greedy_move(self.game_state)
                # Create a simple generator that yields the result
                def greedy_gen():
                    yield {'type': 'result', 'state': best_state}
                self.ai_generator = greedy_gen()
            elif self.cpu_strategy == STRAT_DNC:
                self.ai_generator = choosebestmovevisual(self.game_state.board, self.game_state.player)
            elif self.cpu_strategy == STRAT_DP:
                self.ai_generator = get_dp_move_generator(self.game_state, depth=3)
            elif self.cpu_strategy == STRAT_BT:
                # Pass a copy so the in-place algorithm does not mutate the live game state
                from model.game_state import GameState
                bt_board = Board(self.game_state.board.grid, size=self.game_state.board.SIZE)
                bt_state = GameState(board=bt_board, player=self.game_state.player)
                self.ai_generator = get_backtracking_move_generator(bt_state, depth=4)
            elif self.cpu_strategy == STRAT_BT_NO_HEURISTIC:
                from model.game_state import GameState
                bt_board = Board(self.game_state.board.grid, size=self.game_state.board.SIZE)
                bt_state = GameState(board=bt_board, player=self.game_state.player)
                self.ai_generator = get_backtracking_move_generator_noheur(bt_state, depth=4)

            else:
                self.ai_generator = get_best_move_generator(self.game_state, depth=3)
        try:
            vis = next(self.ai_generator)
            if vis['type'] == 'result':
                # Force a copy of the board to prevent in-place algorithms from mutating the final state
                final_state = vis['state']
                final_board = Board(final_state.board.grid, size=final_state.board.SIZE)
                
                # Check flipped count
                ai = self.game_state.player
                ai_before = sum(row.count(ai) for row in self.game_state.board.grid)
                ai_after = sum(row.count(ai) for row in final_board.grid)
                flipped_count = ai_after - ai_before - 1
                
                if flipped_count >= 8:
                    self.play_sound('opp_capture_more')
                else:
                    self.play_sound('move')

                from model.game_state import GameState
                self.game_state = GameState(final_board, final_state.player)
                
                # Update Score for Eval Bar
                self.last_eval_score = weighted_heuristic(self.game_state.board, Board.BLACK)
                
                self.ai_generator = None
                self.current_vis_data = None
            elif vis['type'] == 'dp_hit':
                 # Flash a message simply if needed or let data show it
                 self.current_vis_data = vis
                 # self.play_sound('flip')
            else:
                self.current_vis_data = vis
                # Optional: Play ticking sound for search?
                if vis['type'] == 'prune':
                     # self.play_sound('flip') # Maybe too annoying
                     pass
        except StopIteration:
            self.ai_generator = None
            self.current_vis_data = None

    def run(self):
        while self.running:
            mx, my = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        pygame.display.toggle_fullscreen()

                if event.type == pygame.VIDEORESIZE:
                    self.calculate_layout(event.w, event.h)

                if self.app_state == STATE_MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                         self.handle_menu_click((mx, my))

                elif self.app_state == STATE_GAME_OVER:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                         if hasattr(self, 'btn_play_again') and self.btn_play_again.collidepoint((mx, my)):
                             self.start_game(self.grid_size)
                         elif hasattr(self, 'btn_quit') and self.btn_quit.collidepoint((mx, my)):
                             self.app_state = STATE_MENU
                             self.play_sound('flip')
                         
                elif self.app_state == STATE_PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_a:
                            self.algo_mode = not self.algo_mode
                        if event.key == pygame.K_h:
                            self.heatmap_mode = not self.heatmap_mode
                            self.play_sound('flip')
                        if event.key == pygame.K_e:
                            self.show_eval_bar = not self.show_eval_bar
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
                             if mx < self.board_area_size:
                                 c, r = mx // self.cell_size, my // self.cell_size
                                 if self.game_state.board.is_valid_move(r, c, self.game_state.player):
                                     new_board, flipped = self.game_state.board.apply_move(r, c, self.game_state.player)
                                     
                                     if len(flipped) >= 8:
                                         if self.game_state.player == self.human_player:
                                             self.play_sound('capture_more')
                                         else:
                                             self.play_sound('opp_capture_more')
                                     elif self.game_state.player != self.human_player:
                                         self.play_sound('move')
                                     
                                     from model.game_state import GameState
                                     self.game_state = GameState(new_board, -self.game_state.player)
                                     self.last_eval_score = weighted_heuristic(self.game_state.board, Board.BLACK)
                                     self.ai_generator = None  # Cancel any in-progress AI generator
                        
                        # Restart Button
                        if hasattr(self, 'btn_restart') and self.btn_restart.collidepoint((mx, my)):
                             self.app_state = STATE_MENU
                             self.play_sound('flip')

            if self.app_state == STATE_MENU:
                self.draw_menu()
            elif self.app_state == STATE_PLAYING:
                self.draw_board()
                
                # AI Logic
                if self.game_mode == MODE_PvCPU and self.game_state.player == self.ai_player and not self.game_state.is_terminal():
                    if self.algo_mode:
                        self.update_ai()
                    else:
                        # Speed up calculation significantly for Classical BT to prevent UI freezing
                        steps_per_frame = 1000 if self.cpu_strategy == STRAT_BT else 20
                        for _ in range(steps_per_frame): 
                            if self.game_state.player == self.ai_player:
                                self.update_ai()
                            else:
                                break

                # --- AUTO PASS LOGIC (HUMAN) ---
                if self.game_mode == MODE_PvP or (self.game_mode == MODE_PvCPU and self.game_state.player == self.human_player):
                     if not self.game_state.is_terminal():
                         if not self.game_state.board.get_valid_moves(self.game_state.player):
                             # No moves -> Pass
                             succ = self.game_state.get_successors()
                             if succ:
                                 # Render PASS notification
                                 t = self.font_title.render("PASS!", True, (255, 0, 0))
                                 self.screen.blit(t, (self.board_area_size//2 - t.get_width()//2, self.board_area_size//2))
                                 pygame.display.flip()
                                 pygame.time.delay(1000)
                                 
                                 self.game_state = succ[0]
                                 self.current_vis_data = None
                                 
                if self.game_state.is_terminal() and self.app_state == STATE_PLAYING:
                     self.app_state = STATE_GAME_OVER
                     
                     black_count = sum(row.count(Board.BLACK) for row in self.game_state.board.grid)
                     white_count = sum(row.count(Board.WHITE) for row in self.game_state.board.grid)
                     
                     if self.game_mode == MODE_PvCPU:
                         human_score = black_count if self.human_player == Board.BLACK else white_count
                         cpu_score = white_count if self.human_player == Board.BLACK else black_count
                         if human_score > cpu_score:
                             self.play_sound('win')
                         elif cpu_score > human_score:
                             self.play_sound('loss')
                     else:
                         self.play_sound('win')

            elif self.app_state == STATE_GAME_OVER:
                self.draw_game_over()


            pygame.display.flip()
            self.clock.tick(30 if self.algo_mode else 60)

        pygame.quit()
