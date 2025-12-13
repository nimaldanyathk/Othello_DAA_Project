import pygame
import sys
from model.board import Board
from model.game_state import GameState
from algorithms.graph import get_best_move_generator

# Enums
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

class PyGameUI:
    # Constants
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 700
    BOARD_AREA_SIZE = 700
    
    # Colors - Distinct Palettes
    # User / Board
    COLOR_BG = (34, 139, 34) # Green Board
    COLOR_BG_MENU = (40, 44, 52)
    COLOR_LINE = (0, 0, 0)
    COLOR_BLACK = (20, 20, 20)
    COLOR_WHITE = (240, 240, 240)
    
    # Visualization - User
    COLOR_RAY_VALID = (0, 255, 0)
    COLOR_RAY_INVALID = (255, 0, 0)
    
    # Visualization - CPU Search Tree
    # Magenta/Cyan for high contrast tech/algo feel
    COLOR_NODE_SEARCH = (255, 0, 255) # Magenta
    COLOR_NODE_LEAF = (0, 255, 255)   # Cyan
    COLOR_EDGE_TREE = (255, 215, 0)   # Gold lines
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Othello - DAA Algorithm Visualization")
        
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont('Arial', 40, bold=True)
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Game State
        self.app_state = STATE_MENU
        self.grid_size = 8
        self.game_state = None
        
        # Players
        self.human_player = Board.BLACK
        self.ai_player = Board.WHITE
        
        # Algo Mode
        self.algo_mode = False
        self.ai_generator = None
        self.current_vis_data = None
        self.vis_history = [] # To draw tree lines [(parent_pos, child_pos), ...] logic needs state tracking
        
        self.running = True

    def start_game(self, size):
        self.grid_size = size
        # Re-initialize Board with new size
        initial_board = Board(size=size)
        self.game_state = GameState(board=initial_board, player=Board.BLACK)
        self.app_state = STATE_PLAYING
        self.vis_history = []
        self.current_vis_data = None
        self.ai_generator = None
        
        # Recalculate cell size
        self.CELL_SIZE = self.BOARD_AREA_SIZE // self.grid_size

    def draw_menu(self):
        self.screen.fill(self.COLOR_BG_MENU)
        
        # Title
        title = self.font_title.render("OTHELLO - DAA PROJECT", True, self.COLOR_WHITE)
        self.screen.blit(title, (self.SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Options
        info = self.font.render("Select Grid Size:", True, (200, 200, 200))
        self.screen.blit(info, (self.SCREEN_WIDTH//2 - info.get_width()//2, 250))
        
        sizes = [4, 6, 8, 10]
        # Buttons logic (simple rects)
        self.menu_buttons = []
        start_x = self.SCREEN_WIDTH//2 - ((len(sizes)*100)//2)
        for i, s in enumerate(sizes):
            x = start_x + i * 100
            y = 300
            rect = pygame.Rect(x, y, 80, 50)
            pygame.draw.rect(self.screen, (100, 100, 200), rect, border_radius=5)
            
            txt = self.font.render(f"{s}x{s}", True, self.COLOR_WHITE)
            self.screen.blit(txt, (x + 40 - txt.get_width()//2, y + 25 - txt.get_height()//2))
            
            self.menu_buttons.append((rect, s))

    def handle_menu_click(self, pos):
        for rect, size in self.menu_buttons:
            if rect.collidepoint(pos):
                self.start_game(size)

    def draw_board(self):
        self.screen.fill(self.COLOR_BG)
        
        # 1. Grid
        for i in range(self.grid_size + 1):
            pos = i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.COLOR_LINE, (pos, 0), (pos, self.BOARD_AREA_SIZE), 2)
            pygame.draw.line(self.screen, self.COLOR_LINE, (0, pos), (self.BOARD_AREA_SIZE, pos), 2)
            
        # 2. Discs
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                cell = self.game_state.board.grid[r][c]
                if cell != Board.EMPTY:
                    self._draw_disc(r, c, cell, 255)

        # 3. Visualization: Ghost States (AI)
        if self.algo_mode and self.current_vis_data:
            self._draw_ai_visualization()

        # 4. Visualization: Raycasting (User)
        if self.algo_mode and self.game_state.player == self.human_player:
            self._draw_user_visualization()
            
        # 5. Side Panel
        self._draw_side_panel()

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
             valid, logs = self.game_state.board.is_valid_move(r, c, self.human_player, return_debug=True)
             
             center = (c * self.CELL_SIZE + self.CELL_SIZE//2, r * self.CELL_SIZE + self.CELL_SIZE//2)
             for log in logs:
                end_r, end_c = log['end']
                end_pos = (end_c * self.CELL_SIZE + self.CELL_SIZE//2, end_r * self.CELL_SIZE + self.CELL_SIZE//2)
                color = self.COLOR_RAY_VALID if log['valid'] else self.COLOR_RAY_INVALID
                pygame.draw.line(self.screen, color, center, end_pos, 4)
                pygame.draw.circle(self.screen, color, end_pos, 6)

    def _draw_ai_visualization(self):
        # Tint board
        s = pygame.Surface((self.BOARD_AREA_SIZE, self.BOARD_AREA_SIZE))
        s.set_alpha(40)
        s.fill((50, 0, 50)) # Dark Purple tint
        self.screen.blit(s, (0,0))
        
        data = self.current_vis_data
        
        # Draw Ghost State
        if data['type'] in ('search_node', 'leaf'):
             state = data['state']
             if state:
                 for r in range(self.grid_size):
                    for c in range(self.grid_size):
                        if state.board.grid[r][c] != Board.EMPTY:
                             self._draw_disc(r, c, state.board.grid[r][c], 100) # Ghost opacity
                             
        # Tree Edge Visualization
        # We assume the AI is traversing. We can draw a line from center to current node if we tracked parent.
        # Simplified: Draw a border indicating depth Color
        colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0)] # Depth colors
        depth = data.get('depth', 0)
        col = colors[depth % len(colors)]
        pygame.draw.rect(self.screen, col, (0, 0, self.BOARD_AREA_SIZE, self.BOARD_AREA_SIZE), 5)
        
        # Info text overlay on board
        txt = self.font.render(f"SIMULATING DEPTH {depth}", True, col)
        self.screen.blit(txt, (20, 20))

    def _draw_side_panel(self):
        panel_x = self.BOARD_AREA_SIZE
        pygame.draw.rect(self.screen, (60, 60, 60), (panel_x, 0, self.SCREEN_WIDTH-panel_x, self.SCREEN_HEIGHT))
        
        # Padding
        x = panel_x + 20
        y = 20
        
        # Turn Info
        turn_str = "BLACK" if self.game_state.player == Board.BLACK else "WHITE"
        turn_col = (0,0,0) if self.game_state.player == Board.BLACK else (255,255,255)
        lbl = self.font_title.render(turn_str, True, turn_col, (100,100,100))
        self.screen.blit(lbl, (x, y))
        y += 60
        
        # Scores
        b, w = self.game_state.board.get_counts()
        self.screen.blit(self.font.render(f"Black: {b}", True, self.COLOR_WHITE), (x, y))
        y += 30
        self.screen.blit(self.font.render(f"White: {w}", True, self.COLOR_WHITE), (x, y))
        y += 60
        
        # Algo Mode Toggle
        mode_txt = "ON" if self.algo_mode else "OFF"
        mode_col = (0, 255, 0) if self.algo_mode else (100, 100, 100)
        self.screen.blit(self.font.render("Algo View (Press A)", True, (200,200,200)), (x, y))
        y += 30
        self.screen.blit(self.font_title.render(mode_txt, True, mode_col), (x, y))
        y += 60
        
        # Restart
        self.btn_restart = pygame.Rect(x, self.SCREEN_HEIGHT - 80, 160, 50)
        pygame.draw.rect(self.screen, (200, 50, 50), self.btn_restart, border_radius=5)
        oms = self.font.render("NEW GAME", True, self.COLOR_WHITE)
        self.screen.blit(oms, (self.btn_restart.centerx - oms.get_width()//2, self.btn_restart.centery - oms.get_height()//2))

    def update_ai(self):
        if not self.ai_generator:
            self.ai_generator = get_best_move_generator(self.game_state, depth=3)
        
        try:
            # FRAME DELAY logic for smoother visualization
            # Just do 1 yield per frame update
            vis = next(self.ai_generator)
            
            if vis['type'] == 'result':
                self.game_state = vis['state']
                result_state = vis['state']
                self.ai_generator = None
                self.current_vis_data = None
                
                # Check game over after move
                if result_state.is_terminal():
                     # self.app_state = STATE_GAME_OVER
                     pass
            else:
                self.current_vis_data = vis
                
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
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        # User move
                         if self.game_state.player == self.human_player:
                             if mx < self.BOARD_AREA_SIZE:
                                 c, r = mx // self.CELL_SIZE, my // self.CELL_SIZE
                                 if self.game_state.board.is_valid_move(r, c, self.human_player):
                                     new_board, _ = self.game_state.board.apply_move(r, c, self.human_player)
                                     # Match successor
                                     successors = self.game_state.get_successors()
                                     for s in successors:
                                         if s.board.grid == new_board.grid:
                                             self.game_state = s
                                             break
                        
                        # Restart Button
                         if hasattr(self, 'btn_restart') and self.btn_restart.collidepoint((mx, my)):
                             self.app_state = STATE_MENU

            # Render
            if self.app_state == STATE_MENU:
                self.draw_menu()
            elif self.app_state == STATE_PLAYING:
                self.draw_board()
                
                if self.game_state.player == self.ai_player and not self.game_state.is_terminal():
                    # AI logic
                    # If algo mode is ON, we rely on the loop's consistent tick. 
                    # If OFF, we might want to speed it up, but for consistency let's keep it same or process multiple.
                    if self.algo_mode:
                        self.update_ai()
                    else:
                        # Process multiple steps to be faster
                        for _ in range(20): 
                            if self.game_state.player == self.ai_player:
                                self.update_ai()
                            else:
                                break

            pygame.display.flip()
            self.clock.tick(30 if self.algo_mode else 60)

        pygame.quit()
