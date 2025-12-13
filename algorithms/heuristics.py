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

def weighted_heuristic(board, player):
    """
    Heuristic considering board position weights (corners are valuable).
    Dynamically handles different board sizes.
    """
    size = board.SIZE
    score = 0
    
    # Corner coordinates
    corners = {(0,0), (0, size-1), (size-1, 0), (size-1, size-1)}
    
    # Simple dynamic weighting:
    # Corner: 100
    # Edge: 10
    # Adjacent to corner (danger zone): -20
    # Other: 1
    
    for r in range(size):
        for c in range(size):
            cell = board.grid[r][c]
            if cell == Board.EMPTY:
                continue
                
            val = 1
            if (r,c) in corners:
                val = 100
            elif (r == 0 or r == size-1 or c == 0 or c == size-1):
                # Edge but not corner
                # Check if it's adjacent to corner (Risk)
                is_risky = False
                for cr, cc in corners:
                    if abs(r-cr) <= 1 and abs(c-cc) <= 1:
                        is_risky = True
                        break
                val = -20 if is_risky else 10
            else:
                 # Inner board
                 # Check 'C-squares' (diagonal from corner)
                 is_c_square = False
                 for cr, cc in corners:
                     if abs(r-cr) == 1 and abs(c-cc) == 1:
                         is_c_square = True
                         break
                 val = -50 if is_c_square else 1
                 
            if cell == player:
                score += val
            else:
                score -= val
                
    return score
