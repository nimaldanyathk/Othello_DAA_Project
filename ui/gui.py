import tkinter as tk
from tkinter import messagebox
from model.game_state import GameState
from model.board import Board
from algorithms.graph import get_best_move, bfs_explore

class OthelloGUI:
    CELL_SIZE = 60
    BOARD_SIZE = 8 * CELL_SIZE
    OFFSET = 10

    def __init__(self, root, human_player=Board.BLACK, on_game_over=None):
        self.root = root
        self.root.title("Othello - DAA Graph Project")
        self.on_game_over = on_game_over
        
        self.game_state = GameState()
        self.human_player = human_player
        self.ai_player = -human_player
        
        self._setup_ui()
        self._draw_board()

    def _setup_ui(self):
        # SIMPLIFIED LAYOUT: Direct packing to root
        
        # 1. Controls on the Right
        self.frame_info = tk.Frame(self.root)
        self.frame_info.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Force text color to black to handle potential Dark Mode conflicts
        self.lbl_turn = tk.Label(self.frame_info, text="Turn: Black", font=("Arial", 14), fg="black")
        self.lbl_turn.pack(pady=10)
        
        self.lbl_score = tk.Label(self.frame_info, text="Black: 2  White: 2", font=("Arial", 12), fg="black")
        self.lbl_score.pack(pady=10)
        
        self.btn_reset = tk.Button(self.frame_info, text="New Game", command=self._reset_game)
        self.btn_reset.pack(pady=20)
        
        self.btn_ai_move = tk.Button(self.frame_info, text="Force AI Move", command=self._ai_move_step)
        self.btn_ai_move.pack(pady=5)

        # 2. Board on the Left
        # Using explicit dimensions and background
        self.canvas = tk.Canvas(self.root, width=self.BOARD_SIZE, height=self.BOARD_SIZE, bg='green', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)
        
        # Force an update to ensure geometry is calculated
        self.root.update()
        print(f"UI Layout Refreshed. Canvas mapped: {self.canvas.winfo_ismapped()}")

    def _reset_game(self):
        self.game_state = GameState()
        self._update_display()

    def _draw_board(self):
        print("Drawing board...")
        self.canvas.delete("all")
        # Draw grid lines
        for i in range(1, 8):
            self.canvas.create_line(i*self.CELL_SIZE, 0, i*self.CELL_SIZE, self.BOARD_SIZE, fill="black")
            self.canvas.create_line(0, i*self.CELL_SIZE, self.BOARD_SIZE, i*self.CELL_SIZE, fill="black")
            
        # Draw discs
        for r in range(8):
            for c in range(8):
                cell = self.game_state.board.grid[r][c]
                if cell != Board.EMPTY:
                    x = c * self.CELL_SIZE + self.CELL_SIZE // 2
                    y = r * self.CELL_SIZE + self.CELL_SIZE // 2
                    r_rad = self.CELL_SIZE // 2 - 5
                    color = "black" if cell == Board.BLACK else "white"
                    self.canvas.create_oval(x-r_rad, y-r_rad, x+r_rad, y+r_rad, fill=color, outline="black")
        
        # Highlight valid moves for human
        if self.game_state.player == self.human_player:
            moves = self.game_state.board.get_valid_moves(self.human_player)
            for r, c in moves:
                x = c * self.CELL_SIZE + self.CELL_SIZE // 2
                y = r * self.CELL_SIZE + self.CELL_SIZE // 2
                # Valid Move Hint: Semi-transparent look using stipple (if supported) or just outline
                self.canvas.create_oval(x-8, y-8, x+8, y+8, fill="green", outline="green", width=2)

    def _update_display(self):
        self._draw_board()
        b, w = self.game_state.board.get_counts()
        self.lbl_score.config(text=f"Black: {b}  White: {w}")
        
        current = "Black" if self.game_state.player == Board.BLACK else "White"
        self.lbl_turn.config(text=f"Turn: {current}")

        if self.game_state.is_terminal():
            winner = self.game_state.get_winner()
            if self.on_game_over:
                b, w = self.game_state.board.get_counts()
                self.on_game_over(winner, b, w)
            else:
                t = "Black Wins!" if winner == 1 else "White Wins!" if winner == -1 else "Draw!"
                messagebox.showinfo("Game Over", t)
        elif self.game_state.player == self.ai_player:
            # Schedule AI move
            self.root.after(500, self._ai_move_step)
        
        else:
             # Human turn check
             moves = self.game_state.board.get_valid_moves(self.game_state.player)
             if not moves:
                 # No moves, but not terminal -> Pass Turn
                 messagebox.showinfo("Pass Turn", "No valid moves available. Passing turn.")
                 successors = self.game_state.get_successors()
                 if successors:
                     self.game_state = successors[0]
                     # Schedule update to avoid recursion depth issues or immediate re-check
                     self.root.after(100, self._update_display)

    def _on_click(self, event):
        if self.game_state.player != self.human_player:
            return
            
        c = event.x // self.CELL_SIZE
        r = event.y // self.CELL_SIZE
        
        if self.game_state.board.is_valid_move(r, c, self.human_player):
            # Apply move logic
            # Since our graph model generates NEW states, we find the successor matching this move
            successors = self.game_state.get_successors()
            
            # Simple apply for human (we know the move is valid, so we can just apply it directly to get state)
            # But to strictly test the graph:
            found_next = None
            target_board, _ = self.game_state.board.apply_move(r, c, self.human_player)
            
            for s in successors:
                if s.board.grid == target_board.grid:
                    found_next = s
                    break
            
            if found_next:
                self.game_state = found_next
                self._update_display()
            else:
                # Should not happen if logic is correct
                print("Error: Successor not found for valid move!")

    def _ai_move_step(self):
        if self.game_state.is_terminal():
            return
            
        if self.game_state.player != self.ai_player:
            # If it's human turn but no moves, the rules say pass. 
            # get_successors handles pass automatically.
            # If get_successors returns a pass state, we should take it.
            pass
        
        # Calculate best move
        # Using Greedy Algorithm
        from algorithms.greedy import get_greedy_move
        next_state = get_greedy_move(self.game_state)
        
        if next_state:
            self.game_state = next_state
            self._update_display()
        else:
            # No moves (should be handled by is_terminal or pass logic)
            pass
