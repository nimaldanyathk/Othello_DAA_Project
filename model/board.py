
class Board:
    """
    Represents the Othello game board.
    The board is an 8x8 grid.
    Cells:
        0: Empty
        1: Black
       -1: White
    """
    SIZE = 8 # Default, but instance variable will override
    EMPTY = 0
    BLACK = 1
    WHITE = -1

    def __init__(self, grid=None, size=8):
        self.SIZE = size
        if grid:
            # Copy existing grid to avoid reference issues
            self.grid = [row[:] for row in grid]
            # Infer size from grid if copied
            self.SIZE = len(grid)
        else:
            self.grid = [[self.EMPTY] * self.SIZE for _ in range(self.SIZE)]
            # Initial setup: Center 4 discs
            mid = self.SIZE // 2
            self.grid[mid-1][mid-1] = self.WHITE
            self.grid[mid][mid] = self.WHITE
            self.grid[mid-1][mid] = self.BLACK
            self.grid[mid][mid-1] = self.BLACK

    def is_on_board(self, r, c):
        return 0 <= r < self.SIZE and 0 <= c < self.SIZE

    def get_valid_moves(self, player):
        """
        Returns a list of (r, c) tuples where 'player' can legally place a disc.
        """
        moves = []
        for r in range(self.SIZE):
            for c in range(self.SIZE):
                if self.is_valid_move(r, c, player):
                    moves.append((r, c))
        return moves

    def is_valid_move(self, r, c, player, return_debug=False):
        """
        Check if placing a disc at (r, c) is valid for 'player'.
        Must be empty and flank opponent discs.
        If return_debug is True, returns (is_valid, debug_log).
        debug_log = list of dicts {'start': (r,c), 'dir': (dr,dc), 'end': (er,ec), 'valid': bool}
        """
        if not self.is_on_board(r, c) or self.grid[r][c] != self.EMPTY:
            return (False, []) if return_debug else False
        
        opponent = -player
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        has_valid_flank = False
        debug_log = []

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            ray_valid = False
            
            if self.is_on_board(nr, nc) and self.grid[nr][nc] == opponent:
                # Potential flank, keep going
                while self.is_on_board(nr, nc) and self.grid[nr][nc] == opponent:
                    nr += dr
                    nc += dc
                
                # If we ended on our own piece, it's a valid flank
                if self.is_on_board(nr, nc) and self.grid[nr][nc] == player:
                    ray_valid = True
                    has_valid_flank = True
            
            if return_debug:
                # Log the ray end point (or the last checked point)
                debug_log.append({
                    'start': (r, c),
                    'dir': (dr, dc),
                    'end': (nr if self.is_on_board(nr, nc) else nr-dr, nc if self.is_on_board(nr, nc) else nc-dc),
                    'valid': ray_valid
                })

        if return_debug:
            return has_valid_flank, debug_log
            
        return has_valid_flank

    def apply_move(self, r, c, player):
        """
        Returns (new_board, flipped_cells)
        flipped_cells is a list of (r, c) tuples that changed color.
        """
        new_board = Board(self.grid, size=self.SIZE)
        new_board.grid[r][c] = player
        
        opponent = -player
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        all_flipped = []

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            to_flip = []
            
            while new_board.is_on_board(nr, nc) and new_board.grid[nr][nc] == opponent:
                to_flip.append((nr, nc))
                nr += dr
                nc += dc
            
            # If we sandwich opponent pieces with our own
            if new_board.is_on_board(nr, nc) and new_board.grid[nr][nc] == player:
                for fr, fc in to_flip:
                    new_board.grid[fr][fc] = player
                all_flipped.extend(to_flip)
                    
        return new_board, all_flipped

    def get_counts(self):
        black = sum(row.count(self.BLACK) for row in self.grid)
        white = sum(row.count(self.WHITE) for row in self.grid)
        return black, white

    def is_full(self):
        return all(cell != self.EMPTY for row in self.grid for cell in row)
