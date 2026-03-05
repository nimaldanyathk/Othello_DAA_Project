from model.board import Board
from algorithms.heuristics import weighted_heuristic
from model.game_state import GameState 

def evaluatemove(board, moves, depth, playerturn, rootplayer, ismax):
    if len(moves) > 1:
        mid = len(moves) // 2
        leftmoves = moves[:mid]
        rightmoves = moves[mid:]
        leftresults = evaluatemove(board, leftmoves, depth, playerturn, rootplayer, ismax)
        rightresults = evaluatemove(board, rightmoves, depth, playerturn, rootplayer, ismax)
        
        return leftresults + rightresults

    move = moves[0]
    newboard, _ = board.apply_move(move[0], move[1], playerturn)

    if depth == 0 or newboard.is_full():
        score = weighted_heuristic(newboard, rootplayer)
        return [(score, move)]
    opponent = -playerturn
    opponentmoves = newboard.get_valid_moves(opponent)
    if not opponentmoves:
        score = weighted_heuristic(newboard, rootplayer)
        return [(score, move)]
    opponentresults = evaluatemove(newboard, opponentmoves, depth - 1, opponent, rootplayer, not ismax)
    opponentscores = [s for s, m in opponentresults]
    if ismax:
        bestscore = min(opponentscores)
    else:
        bestscore = max(opponentscores)
    return [(bestscore, move)]

def evaluatemovevisual(board, moves, depth, playerturn, rootplayer, ismax):
    viewstate = GameState(board, playerturn)
    yield {'type': 'search_node', 'state': viewstate, 'depth': depth}
    
    if len(moves) > 1:
        mid = len(moves) // 2
        leftmoves = moves[:mid]
        rightmoves = moves[mid:]
        
        leftresults = yield from evaluatemovevisual(board, leftmoves, depth, playerturn, rootplayer, ismax)
        rightresults = yield from evaluatemovevisual(board, rightmoves, depth, playerturn, rootplayer, ismax)
        
        return leftresults + rightresults
    move = moves[0]
    newboard, _ = board.apply_move(move[0], move[1], playerturn)
    if depth == 0 or newboard.is_full():
        score = weighted_heuristic(newboard, rootplayer)
        leafstate = GameState(newboard, -playerturn)
        yield {'type': 'leaf', 'state': leafstate, 'depth': depth, 'score': score}
        return [(score, move)]
        
    opponent = -playerturn
    opponentmoves = newboard.get_valid_moves(opponent)
    if not opponentmoves:
        score = weighted_heuristic(newboard, rootplayer)
        leafstate = GameState(newboard, -playerturn)
        yield {'type': 'leaf', 'state': leafstate, 'depth': depth, 'score': score}
        return [(score, move)]
    opponentresults = yield from evaluatemovevisual(newboard, opponentmoves, depth - 1, opponent, rootplayer, not ismax)
    opponentscores = [s for s, m in opponentresults]
    if ismax:
        bestscore = min(opponentscores)
    else:
        bestscore = max(opponentscores)
    return [(bestscore, move)]

def choosebestmove(board, player, depth=3):
    moves = board.get_valid_moves(player)
    if not moves:
        return None
    scoredmoves = evaluatemove(board, moves, depth, player, player, ismax=True)
    
    def mergesort(arr):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        left = mergesort(arr[:mid])
        right = mergesort(arr[mid:])

        return merge(left, right)
    def merge(left, right):
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i][0] > right[j][0]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result
    scoredmoves = mergesort(scoredmoves)
    if not scoredmoves:
        return None        
    bestscore, bestmove = scoredmoves[0]
    return bestmove

def choosebestmovevisual(board, player, depth=3):

    moves = board.get_valid_moves(player)
    
    if not moves:
        return
    
    scoredmoves = yield from evaluatemovevisual(board, moves, depth, player, player, ismax=True)
    
    scoredmoves.sort(key=lambda x: x[0], reverse=True)
    
    if not scoredmoves:
        return
        
    bestscore, bestmove = scoredmoves[0]
    newboard, _ = board.apply_move(bestmove[0], bestmove[1], player)
    
    from model.game_state import GameState
    nextplayer = -player
    resultstate = GameState(newboard, nextplayer)
    
    yield {'type': 'result', 'state': resultstate}

