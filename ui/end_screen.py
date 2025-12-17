import tkinter as tk
from tkinter import font
from model.board import Board

class EndScreen:
    def __init__(self, root, winner, black_score, white_score, on_restart_callback):
        self.root = root
        self.on_restart = on_restart_callback
        
        self.frame = tk.Frame(self.root, bg='#2c3e50')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Determine Title
        if winner == 0:
            title_text = "IT'S A DRAW!"
            color = "#f39c12" # Orange
        elif winner == Board.BLACK:
            title_text = "BLACK WINS!"
            color = "white" # Since background is dark, White text pops. Or maybe Black if background was light.
            # Let's use a nice Green or just White.
            color = "#2ecc71"
        else:
            title_text = "WHITE WINS!"
            color = "#ecf0f1"
            
        self.title_font = font.Font(family="Helvetica", size=40, weight="bold")
        lbl_title = tk.Label(self.frame, text=title_text, font=self.title_font, fg=color, bg='#2c3e50')
        lbl_title.pack(pady=(50, 20))
        
        # Scores
        score_font = ("Helvetica", 18)
        score_container = tk.Frame(self.frame, bg='#2c3e50')
        score_container.pack(pady=20)
        
        lbl_black = tk.Label(score_container, text=f"Black: {black_score}", font=score_font, fg="white", bg='#2c3e50')
        lbl_black.pack(side=tk.LEFT, padx=30)
        
        lbl_white = tk.Label(score_container, text=f"White: {white_score}", font=score_font, fg="white", bg='#2c3e50')
        lbl_white.pack(side=tk.LEFT, padx=30)
        
        # New Game Button
        self.btn_new = tk.Button(self.frame, text="NEW GAME", font=("Helvetica", 14, "bold"),
                                   command=self._on_restart_click,
                                   bg="#e74c3c", fg="white", width=20, height=2, bd=0)
        self.btn_new.pack(pady=60)
        
        # Hover effects
        self.btn_new.bind("<Enter>", lambda e: self.btn_new.config(bg="#c0392b"))
        self.btn_new.bind("<Leave>", lambda e: self.btn_new.config(bg="#e74c3c"))
        
    def _on_restart_click(self):
        self.frame.destroy()
        self.on_restart()
