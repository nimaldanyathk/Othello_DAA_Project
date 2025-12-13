import tkinter as tk
from ui.gui import OthelloGUI

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
    
    app = OthelloGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
