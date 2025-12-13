import pygame
import sys
from model.board import Board
from model.game_state import GameState
from algorithms.graph import get_best_move

class PyGameUI:
    # Constants
    SCREEN_SIZE = 600
    BOARD_SIZE = 600
    CELL_SIZE = BOARD_SIZE // 8
    
    # Colors
    COLOR_BG = (34, 139, 34) # Forest Green
    COLOR_LINE = (0, 0, 0)
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_HINT = (50, 205, 50, 100) # Transparent-ish hint

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_SIZE, self.SCREEN_SIZE))
        pygame.display.set_caption("Othello - DAA Graph Project")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 32)
        
        self.game_state = GameState()
        self.human_player = Board.BLACK
        self.ai_player = Board.WHITE
        
        self.running = True

    def draw_board(self):
        self.screen.fill(self.COLOR_BG)
        
        # Grid lines
        for i in range(9):
            pos = i * self.CELL_SIZE
            pygame.draw.line(self.screen, self.COLOR_LINE, (pos, 0), (pos, self.BOARD_SIZE), 2)
            pygame.draw.line(self.screen, self.COLOR_LINE, (0, pos), (self.BOARD_SIZE, pos), 2)
            
        # Discs
        for r in range(8):
            for c in range(8):
                cell = self.game_state.board.grid[r][c]
                if cell != Board.EMPTY:
                    x = c * self.CELL_SIZE + self.CELL_SIZE // 2
                    y = r * self.CELL_SIZE + self.CELL_SIZE // 2
                    radius = self.CELL_SIZE // 2 - 5
                    color = self.COLOR_BLACK if cell == Board.BLACK else self.COLOR_WHITE
                    pygame.draw.circle(self.screen, color, (x, y), radius)

        # Hints for human
        if self.game_state.player == self.human_player:
            moves = self.game_state.board.get_valid_moves(self.human_player)
            for r, c in moves:
                x = c * self.CELL_SIZE + self.CELL_SIZE // 2
                y = r * self.CELL_SIZE + self.CELL_SIZE // 2
                pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 5) # Small dot hint

    def handle_click(self, pos):
        if self.game_state.player != self.human_player:
            return
            
        c = pos[0] // self.CELL_SIZE
        r = pos[1] // self.CELL_SIZE
        
        if self.game_state.board.is_valid_move(r, c, self.human_player):
            self._apply_move_transition(r, c)

    def _apply_move_transition(self, r, c):
        # find successor
        target_board = self.game_state.board.apply_move(r, c, self.game_state.player)
        successors = self.game_state.get_successors()
        for s in successors:
            if s.board.grid == target_board.grid:
                self.game_state = s
                return

    def ai_move(self):
        if self.game_state.is_terminal():
            return
            
        # Draw "Thinking" text maybe?
        pygame.display.set_caption("Othello - AI Thinking...")
        pygame.display.update()
        
        next_state = get_best_move(self.game_state, depth=3)
        if next_state:
            self.game_state = next_state
        else:
            # Pass turn if no moves
            pass_successors = self.game_state.get_successors()
            if pass_successors:
                 self.game_state = pass_successors[0]
        
        pygame.display.set_caption("Othello - DAA Graph Project")

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state.player == self.human_player:
                        self.handle_click(pygame.mouse.get_pos())

            self.draw_board()
            pygame.display.flip()
            
            # Game Over check
            if self.game_state.is_terminal():
                # End screen?
               pass 
            elif self.game_state.player == self.ai_player:
                # Add small delay so it doesn't feel instant
                pygame.time.delay(500)
                self.ai_move()

            self.clock.tick(60)

        pygame.quit()
