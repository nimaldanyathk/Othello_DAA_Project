
class Board:
    """
    Represents the Othello game board.
    The board is an 8x8 grid.
    Cells:
        0: Empty
        1: Black
       -1: White
    """
    SIZE = 8
    EMPTY = 0
    BLACK = 1
    WHITE = -1

    def __init__(self, grid=None):
        if grid:
            # Copy existing grid to avoid reference issues
            self.grid = [row[:] for row in grid]
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

    def is_valid_move(self, r, c, player):
        """
        Check if placing a disc at (r, c) is valid for 'player'.
        Must be empty and flank opponent discs.
        """
        if not self.is_on_board(r, c) or self.grid[r][c] != self.EMPTY:
            return False
        
        opponent = -player
        
        # Directions: valid move must flip at least one opponent disc in some direction
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if self.is_on_board(nr, nc) and self.grid[nr][nc] == opponent:
                # Potential flank, keep going
                while self.is_on_board(nr, nc) and self.grid[nr][nc] == opponent:
                    nr += dr
                    nc += dc
                
                # If we ended on our own piece, it's a valid flank
                if self.is_on_board(nr, nc) and self.grid[nr][nc] == player:
                    return True
        return False

    def apply_move(self, r, c, player):
        """
        Returns a NEW Board instance with the move applied and discs flipped.
        Does NOT modify the current instance (immutability helper for state search).
        """
        new_board = Board(self.grid)
        new_board.grid[r][c] = player
        
        opponent = -player
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

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
                    
        return new_board

    def get_counts(self):
        black = sum(row.count(self.BLACK) for row in self.grid)
        white = sum(row.count(self.WHITE) for row in self.grid)
        return black, white

    def is_full(self):
        return all(cell != self.EMPTY for row in self.grid for cell in row)
