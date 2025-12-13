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

def depth_limited_dfs(state, depth, player, heuristic_func):
    """
    Depth-Limited DFS (Minimax) to find the best move.
    Returns (best_score, best_move_state).
    
    This effectively uses the graph structure to perform a lookahead.
    """
    if depth == 0 or state.is_terminal():
        return heuristic_func(state.board, player), state

    successors = state.get_successors()
    if not successors:
        # Pass turn
        return depth_limited_dfs(state, depth-1, player, heuristic_func)

    best_score = float('-inf') if state.player == player else float('inf')
    best_op = None # The resulting state after the best move

    for successor in successors:
        score, _ = depth_limited_dfs(successor, depth - 1, player, heuristic_func)
        
        if state.player == player: # Maximize
            if score > best_score:
                best_score = score
                best_op = successor
        else: # Minimize (Opponent's turn)
            if score < best_score:
                best_score = score
                best_op = successor
                
    return best_score, best_op

def get_best_move(state, depth=3):
    """
    Wrapper for the decision making process.
    """
    # Note: 'state' is the current node. We want the edge (move) that leads to the best child node.
    # The depth_limited_dfs returns the best leaf score and the immediate successor that leads there (wait, recursive logic needs verify)
    
    # Actually standard Minimax returns value. The root call needs the move.
    # My implementation above returns 'best_op' which is the successor state node.
    # So we simply find which successor matches that board.
    
    _, best_state = depth_limited_dfs(state, depth, state.player, weighted_heuristic)
    return best_state
