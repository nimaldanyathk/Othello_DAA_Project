from model.board import Board

def basic_heuristic(board, player):
    """
    Simple heuristic: Coin difference.
    Returns +ve if player is winning, -ve if losing.
    """
    black, white = board.get_counts()
    diff = black - white
    if player == Board.WHITE:
        diff = -diff
    return diff

def get_cell_weight(r, c, size):
    """
    Returns the strategic weight of a cell.
    Positive = Good, Negative = Bad.
    """
    # Corner coordinates
    corners = {(0,0), (0, size-1), (size-1, 0), (size-1, size-1)}
    
    if (r,c) in corners:
        return 100
        
    # Check edges
    if (r == 0 or r == size-1 or c == 0 or c == size-1):
        # Edge but not corner
        # Check if it's adjacent to corner (Risk)
        is_risky = False
        for cr, cc in corners:
            if abs(r-cr) <= 1 and abs(c-cc) <= 1:
                is_risky = True
                break
        return -20 if is_risky else 10
    
    # Inner board
    # Check 'C-squares' (diagonal from corner)
    is_c_square = False
    for cr, cc in corners:
        if abs(r-cr) == 1 and abs(c-cc) == 1:
            is_c_square = True
            break
            
    return -50 if is_c_square else 1

def weighted_heuristic(board, player):
    """
    Heuristic considering board position weights (corners are valuable).
    Dynamically handles different board sizes.
    """
    size = board.SIZE
    score = 0
    
    for r in range(size):
        for c in range(size):
            cell = board.grid[r][c]
            if cell == Board.EMPTY:
                continue
                
            val = get_cell_weight(r, c, size)
                 
            if cell == player:
                score += val
            else:
                score -= val
                
    return score
