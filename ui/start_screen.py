import tkinter as tk
from tkinter import font
from model.board import Board

class StartScreen:
    def __init__(self, root, on_start_callback):
        self.root = root
        self.on_start = on_start_callback
        self.selected_color = None
        
        self.frame = tk.Frame(self.root, bg='#2c3e50')
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        self.title_font = font.Font(family="Helvetica", size=36, weight="bold")
        lbl_title = tk.Label(self.frame, text="OTHELLO", font=self.title_font, fg="#ecf0f1", bg='#2c3e50')
        lbl_title.pack(pady=(40, 10))
        
        lbl_sub = tk.Label(self.frame, text="Choose your side", font=("Helvetica", 16), fg="#bdc3c7", bg='#2c3e50')
        lbl_sub.pack(pady=(0, 40))
        
        # Selection Container
        self.selection_frame = tk.Frame(self.frame, bg='#2c3e50')
        self.selection_frame.pack()
        
        # Cards
        self.card_black = self._create_card(self.selection_frame, "Black", Board.BLACK)
        self.card_white = self._create_card(self.selection_frame, "White", Board.WHITE)
        
        self.card_black.pack(side=tk.LEFT, padx=20)
        self.card_white.pack(side=tk.LEFT, padx=20)
        
        # Start Button
        self.btn_start = tk.Button(self.frame, text="START GAME", font=("Helvetica", 14, "bold"),
                                   state=tk.DISABLED, command=self._on_start_click,
                                   bg="#95a5a6", fg="white", width=20, height=2, bd=0)
        self.btn_start.pack(pady=50)
        
    def _create_card(self, parent, label_text, color_val):
        # A Canvas acting as a button
        card = tk.Canvas(parent, width=150, height=180, bg="#34495e", highlightthickness=2, highlightbackground="#7f8c8d")
        
        # Draw Text
        card.create_text(75, 30, text=label_text, fill="white", font=("Arial", 16, "bold"))
        
        # Draw Disc
        fill_col = "black" if color_val == Board.BLACK else "white"
        outline = "white" if color_val == Board.BLACK else "black"
        card.create_oval(35, 60, 115, 140, fill=fill_col, outline=outline, width=2)
        
        # Bindings
        card.bind("<Button-1>", lambda e, c=color_val, w=card: self._select_side(c, w))
        card.bind("<Enter>", lambda e, w=card: self._on_hover(w, True))
        card.bind("<Leave>", lambda e, w=card: self._on_hover(w, False))
        
        return card

    def _on_hover(self, widget, is_hovering):
        if self.selected_color is None or (widget != self.card_black if self.selected_color == Board.WHITE else widget != self.card_white):
             # Only effect if not strictly handling selection highlight override
             # But here we just want subtle hover unless selected
             pass

    def _select_side(self, color, widget):
        self.selected_color = color
        
        # Reset styles
        self.card_black.config(bg="#34495e", highlightbackground="#7f8c8d", highlightthickness=2)
        self.card_white.config(bg="#34495e", highlightbackground="#7f8c8d", highlightthickness=2)
        
        # Highlight Selected (Green)
        widget.config(bg="#2ecc71", highlightbackground="#27ae60", highlightthickness=4)
        
        # Enable Start
        self.btn_start.config(state=tk.NORMAL, bg="#2ecc71", cursor="hand2")
        
    def _on_start_click(self):
        if self.selected_color:
            self.frame.destroy()
            self.on_start(self.selected_color)
