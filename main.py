import tkinter as tk
from ui.gui import OthelloGUI
from ui.start_screen import StartScreen

def main():
    root = tk.Tk()
    # Center the window
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    w = 600
    h = 600
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    def start_game(player_color):
        # Clear start screen
        for widget in root.winfo_children():
            widget.destroy()
            
        app = OthelloGUI(root, human_player=player_color)
    
    start_screen = StartScreen(root, start_game)
    root.mainloop()

if __name__ == "__main__":
    main()
