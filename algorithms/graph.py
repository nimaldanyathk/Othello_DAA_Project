from collections import deque
from algorithms.heuristics import weighted_heuristic

def bfs_explore(start_state, max_nodes=1000):
    """
    Breadth-First Search traversal generator.
    Explores the game graph layer by layer.
    Useful for analyzing immediate move possibilities.
    """
    queue = deque([start_state])
    visited = set()
    visited.add(start_state)
    count = 0
    
    while queue and count < max_nodes:
        state = queue.popleft()
        yield state
        count += 1
        
        if not state.is_terminal():
            for successor in state.get_successors():
                if successor not in visited:
                    visited.add(successor)
                    queue.append(successor)

def dfs_explore(start_state, max_depth=3):
    """
    Depth-First Search traversal generator.
    Explores deep into one variation before backtracking.
    """
    stack = [(start_state, 0)]
    visited = set()
    visited.add(start_state)
    
    while stack:
        state, depth = stack.pop()
        yield state
        
        if depth < max_depth and not state.is_terminal():
            for successor in state.get_successors():
                if successor not in visited:
                    visited.add(successor)
                    stack.append((successor, depth + 1))

def alpha_beta_generator(state, depth, alpha, beta, player, heuristic_func):
    """
    Generator version of Minimax with Alpha-Beta Pruning.
    Yields:
        {'type': 'search_node', ...} for visiting
        {'type': 'leaf', ...} for evaluation
        {'type': 'prune', ...} for cutoff events
    """
    # Yield current state visiting
    yield {'type': 'search_node', 'state': state, 'depth': depth, 'score': None, 'alpha': alpha, 'beta': beta}

    if depth == 0 or state.is_terminal():
        score = heuristic_func(state.board, player)
        yield {'type': 'leaf', 'state': state, 'depth': depth, 'score': score}
        return score, state

    successors = state.get_successors()
    if not successors:
        # Pass turn
        # Recurse with same alpha/beta
        val = yield from alpha_beta_generator(state, depth-1, alpha, beta, player, heuristic_func)
        return val

    best_op = None

    if state.player == player: # Maximizer
        value = float('-inf')
        for successor in successors:
            score, _ = yield from alpha_beta_generator(successor, depth - 1, alpha, beta, player, heuristic_func)
            
            if score > value:
                value = score
                best_op = successor
                
            alpha = max(alpha, value)
            if value >= beta:
                # PRUNING
                yield {'type': 'prune', 'state': successor, 'depth': depth, 'score': value}
                break # Beta Cutoff
        return value, best_op
    
    else: # Minimizer (Opponent)
        value = float('inf')
        for successor in successors:
            score, _ = yield from alpha_beta_generator(successor, depth - 1, alpha, beta, player, heuristic_func)
            
            if score < value:
                value = score
                best_op = successor
                
            beta = min(beta, value)
            if value <= alpha:
                 # PRUNING
                yield {'type': 'prune', 'state': successor, 'depth': depth, 'score': value}
                break # Alpha Cutoff
        return value, best_op

def get_best_move_generator(state, depth=3):
    """
    Generator wrapper.
    Yields visualization data.
    Finally yields {'type': 'result', 'state': best_state}
    """
    # Use yield from to capture the return value (best_score, best_op)
    # while propagating all visualization dicts up.
    # Start with full alpha-beta window [-inf, +inf]
    _, best_op = yield from alpha_beta_generator(state, depth, float('-inf'), float('inf'), state.player, weighted_heuristic)
            
    yield {'type': 'result', 'state': best_op}

def get_best_move(state, depth=3):
    """
    Backward compatibility wrapper.
    Consumes the generator and returns the final result.
    """
    gen = get_best_move_generator(state, depth)
    result_state = None
    for item in gen:
        if item['type'] == 'result':
            result_state = item['state']
    return result_state
