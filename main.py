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
    
    from ui.end_screen import EndScreen

    def show_start_screen():
        # Clear
        for widget in root.winfo_children():
            widget.destroy()
        start = StartScreen(root, start_game_logic)

    def start_game_logic(player_color):
        for widget in root.winfo_children():
            widget.destroy()
        app = OthelloGUI(root, human_player=player_color, on_game_over=show_end_screen)

    def show_end_screen(winner, black_score, white_score):
        # We need to wait a tiny bit or just clear immediately? 
        # Usually good to see the board for a split second, but GUI handles 'on_game_over' call.
        # Let's clean up
        for widget in root.winfo_children():
            widget.destroy()
        
        end = EndScreen(root, winner, black_score, white_score, show_start_screen)

    show_start_screen()
    root.mainloop()

if __name__ == "__main__":
    main()
