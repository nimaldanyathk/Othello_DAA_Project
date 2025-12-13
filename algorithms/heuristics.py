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
    """
    # Weights for each cell (corners high, adjacent to corners low/negative)
    weights = [
        [100, -20, 10,  5,  5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [ 10,  -2, -1, -1, -1, -1,  -2,  10],
        [  5,  -2, -1, -1, -1, -1,  -2,   5],
        [  5,  -2, -1, -1, -1, -1,  -2,   5],
        [ 10,  -2, -1, -1, -1, -1,  -2,  10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10,  5,  5, 10, -20, 100],
    ]
    
    score = 0
    for r in range(8):
        for c in range(8):
            cell = board.grid[r][c]
            if cell == player:
                score += weights[r][c]
            elif cell == -player:
                score -= weights[r][c]
    return score
