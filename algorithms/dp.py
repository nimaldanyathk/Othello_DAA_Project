from algorithms.heuristics import weighted_heuristic
from model.board import Board

# Transposition Table Constants
FLAG_EXACT = 0
FLAG_LOWERBOUND = 1
FLAG_UPPERBOUND = 2

def dp_minimax_generator(state, depth, player, heuristic_func, alpha, beta, memo):
    """
    Minimax generator with Alpha-Beta pruning and Memoization (Dynamic Programming).
    
    This function demonstrates the two key properties of Dynamic Programming:
    1. Overlapping Subproblems: The same game state can be reached via different 
       sequences of moves (transpositions). We store these in 'memo'.
    2. Optimal Substructure: The value of a state is determined by the optimal 
       values of its successor states.
    """
    
    # 1. Create a hashable key for the state
    # We need board configuration, player, and depth to uniquely identify the subproblem.
    # Note: Depth is included because a search at depth 1 is different from depth 3.
    # However, if we have a stored result for depth D, it is valid for any search with depth <= D.
    # For simplicity here, we use exact depth as part of the key.
    
    grid_tuple = tuple(tuple(row) for row in state.board.grid)
    state_key = (grid_tuple, state.player, depth)

    # 2. Check Transposition Table (Memoization)
    if state_key in memo:
        stored_val, flag = memo[state_key]
        
        # Check if the stored value is useful for the current alpha-beta window
        hit = False
        if flag == FLAG_EXACT:
            hit = True
        elif flag == FLAG_LOWERBOUND and stored_val >= beta:
            hit = True
        elif flag == FLAG_UPPERBOUND and stored_val <= alpha:
            hit = True
             
        if hit:
            # Visualize the DP Hit!
            yield {'type': 'dp_hit', 'state': state, 'score': stored_val, 'depth': depth}
            return stored_val, None

    # Visualization: Exploring this node
    yield {'type': 'search_node', 'state': state, 'depth': depth, 'alpha': alpha, 'beta': beta}

    # 3. Base Case
    if depth == 0 or state.is_terminal():
        score = heuristic_func(state.board, player)
        
        # Store exact value in memo
        # Base cases are always exact
        memo[state_key] = (score, FLAG_EXACT)
        
        yield {'type': 'leaf', 'state': state, 'depth': depth, 'score': score}
        return score, None

    successors = state.get_successors()
    
    # If no moves (Pass)
    if not successors:
        val, _ = yield from dp_minimax_generator(state, depth-1, player, heuristic_func, alpha, beta, memo)
        return val, None

    best_op = None
    original_alpha = alpha

    # 4. Recursive Step (Conquer)
    if state.player == player: 
        # Maximizing Player
        max_eval = float('-inf')
        for successor in successors:
            eval_score, _ = yield from dp_minimax_generator(successor, depth - 1, player, heuristic_func, alpha, beta, memo)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_op = successor
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break # Beta Prune

        # 5. Store in Transposition Table
        flag = FLAG_EXACT
        if max_eval <= original_alpha:
            flag = FLAG_UPPERBOUND
        elif max_eval >= beta:
            flag = FLAG_LOWERBOUND
            
        memo[state_key] = (max_eval, flag)
        
        return max_eval, best_op

    else: 
        # Minimizing Player
        min_eval = float('inf')
        for successor in successors:
            eval_score, _ = yield from dp_minimax_generator(successor, depth - 1, player, heuristic_func, alpha, beta, memo)
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_op = successor
                
            beta = min(beta, eval_score)
            if beta <= alpha:
                break # Alpha Prune
        
        # 5. Store in Transposition Table
        flag = FLAG_EXACT
        if min_eval <= original_alpha:
            flag = FLAG_UPPERBOUND
        elif min_eval >= beta:
            flag = FLAG_LOWERBOUND
            
        memo[state_key] = (min_eval, flag)

        return min_eval, best_op

def get_dp_move_generator(state, depth=3):
    """
    Entry point for the DP-enhanced Minimax generator.
    Initializes the memoization table (transposition table).
    """
    # The memoization table persists only for one full move calculation 
    # (or could be shared across moves if we implemented iterative deepening)
    memo = {} 
    
    score, best_state = yield from dp_minimax_generator(
        state, depth, state.player, weighted_heuristic, 
        float('-inf'), float('inf'), memo
    )
    
    yield {'type': 'result', 'state': best_state, 'score': score}
