from model.game_state import GameState

def get_greedy_move(game_state):
    """
    Selects the move that flips the maximum number of pieces.
    Returns the resulting GameState after making that move.
    """
    board = game_state.board
    player = game_state.player
    
    # 1. Get all legal moves
    valid_moves = board.get_valid_moves(player)
    
    if not valid_moves:
        # No moves available. 
        # Check if pass is possible (opponent has moves) or terminal.
        # GameState.get_successors handles this logic usually, 
        # but here we need to return a State.
        # Let's rely on get_successors for the edge case of passing, 
        # or return None if no moves (caller handles).
        
        # If we just return None, the GUI might not know if it's a pass or end.
        # Let's see what get_successors does.
        successors = game_state.get_successors()
        if successors:
            # If there are successors but no valid moves, it implies a pass.
            return successors[0]
        return None

    best_move_count = -1
    best_successor = None
    
    # 2. Evaluate each move
    for r, c in valid_moves:
        # 3. Handle physics (flip pieces) & Count flips
        # board.apply_move returns (new_board, flipped_list)
        new_board, flipped_list = board.apply_move(r, c, player)
        
        flip_count = len(flipped_list)
        
        # 4. Greedy Choice: Maximize flips
        if flip_count > best_move_count:
            best_move_count = flip_count
            best_successor = GameState(new_board, -player)
            
    return best_successor
