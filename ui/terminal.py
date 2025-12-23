import sys
from model.board import Board
from model.game_state import GameState
from algorithms.graph import get_best_move

class TerminalUI:
    def __init__(self):
        self.game_state = GameState()
        self.ai_player = Board.WHITE 
        self.human_player = Board.BLACK

    def print_board(self):
        print("\n  " + " ".join([str(i) for i in range(8)]))
        for r in range(8):
            row_str = f"{r} "
            for c in range(8):
                cell = self.game_state.board.grid[r][c]
                symbol = "."
                if cell == Board.BLACK: symbol = "B"
                elif cell == Board.WHITE: symbol = "W"
                row_str += symbol + " "
            print(row_str)
        
        b, w = self.game_state.board.get_counts()
        print(f"\nScore => Black: {b} | White: {w}")
        turn = "Black" if self.game_state.player == Board.BLACK else "White"
        print(f"Turn: {turn}")

    def run(self):
        print("\033[H\033[J") # ANSI Clear Screen
        print("=== OTHELLO TERMINAL VERSION ===")
        print("Instructions:")
        print(" - Enter moves as 'row col' (e.g., '3 2')")
        print(" - Row 0 is top, Col 0 is left.")
        print(" - You are BLACK (B). CPU is WHITE (W).")
        print("---------------------------------------")
        
        while not self.game_state.is_terminal():
            self.print_board()
            
            if self.game_state.player == self.human_player:
                # Human Turn
                moves = self.game_state.board.get_valid_moves(self.human_player)
                if not moves:
                    print("\nNo valid moves! Passing...")
                    input("Press Enter to continue...")
                    self._pass_turn()
                    continue
                
                print(f"\nValid Moves: {moves}")
                try:
                    inp = input("Enter move (row col): ")
                    parts = inp.strip().split()
                    if len(parts) != 2:
                        print("Invalid format.")
                        continue
                    r, c = int(parts[0]), int(parts[1])
                    if (r, c) not in moves:
                        print("Invalid move. Try again.")
                        continue
                    
                    # Apply move
                    self._apply_move(r, c)
                    
                except ValueError:
                    print("Invalid input.")
            else:
                # AI Turn
                print("AI is thinking...")
                next_state = get_best_move(self.game_state, depth=3)
                if next_state:
                    self.game_state = next_state
                else:
                    print("AI has no moves. Passing...")
                    self._pass_turn()

        self.print_board()
        self._declare_winner()

    def _apply_move(self, r, c):
        # In our graph model, we just find the successor
        successors = self.game_state.get_successors()
        target_board, _ = self.game_state.board.apply_move(r, c, self.game_state.player)
        for s in successors:
            if s.board.grid == target_board.grid:
                self.game_state = s
                return
        print("Critical Error: Move not found in graph edges.")

    def _pass_turn(self):
        # Force a pass creation
        # The graph model returns a swapped player state if no moves
        successors = self.game_state.get_successors()
        if successors:
            self.game_state = successors[0]

    def _declare_winner(self):
        winner = self.game_state.get_winner()
        if winner == Board.BLACK:
            print("GAME OVER. BLACK WINS!")
        elif winner == Board.WHITE:
            print("GAME OVER. WHITE WINS!")
        else:
            print("GAME OVER. DRAW!")
