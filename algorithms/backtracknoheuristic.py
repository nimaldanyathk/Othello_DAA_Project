from model.board import Board
from model.game_state import GameState

def scorer(board,player):
    s=0
    
    for row in board.grid:
        for cell in row:
            if cell == player:
                s+=1
            elif cell == -player:
                s-=1
    
    return s 

def evaluatemove(board, moves, depth, playerturn, rootplayer, ismax):
    res = []
    
    for m in moves:
        newboard, _ = board.apply_move(m[0],m[1],playerturn)
        if depth == 0 or newboard.is_full():
            score = scorer(newboard,rootplayer)
            res.append((score,m))
            continue
        opponent = -playerturn
        opponentm = newboard.get_valid_moves(opponent)
        if not opponentm:
            score = scorer(newboard,rootplayer)
            res.append((score,m))
            continue
        opponentres = evaluatemove(newboard,opponentm,depth-1,opponent,rootplayer,not ismax)
        scores = [s for s, m in opponentres]

        if ismax:
            bests = min(scores)
        else:
            bests = max(scores)
        
        res.append((bests,m))
    return res


def evaluatemovevisual(board, moves, depth, playerturn, rootplayer, ismax):

    viewstate = GameState(board, playerturn)
    yield {'type': 'search_node', 'state': viewstate, 'depth': depth}

    results = []

    for move in moves:

        newboard, _ = board.apply_move(move[0], move[1], playerturn)

        if depth == 0 or newboard.is_full():

            score = scorer(newboard, rootplayer)

            leafstate = GameState(newboard, -playerturn)
            yield {'type': 'leaf', 'state': leafstate, 'depth': depth, 'score': score}

            results.append((score, move))
            continue

        opponent = -playerturn
        opponentmoves = newboard.get_valid_moves(opponent)

        if not opponentmoves:

            score = scorer(newboard, rootplayer)

            leafstate = GameState(newboard, -playerturn)
            yield {'type': 'leaf', 'state': leafstate, 'depth': depth, 'score': score}

            results.append((score, move))
            continue

        opponentresults = yield from evaluatemovevisual(
            newboard, opponentmoves, depth-1, opponent, rootplayer, not ismax
        )

        scores = [s for s, m in opponentresults]

        if ismax:
            bestscore = min(scores)
        else:
            bestscore = max(scores)

        results.append((bestscore, move))

    return results

def choosebestmove(board,player,depth=3):
    moves = board.get_valid_move(player)
    if not moves:
        return None 
    scmoves = evaluatemove(board, moves, depth, player, player, True)
    scmoves.sort(key=lambda x:x[0], reverse=True)
    bestscore, bestmove = scmoves[0]
    
    return bestmove

def choosebestmovevisual(board, player, depth=3):

    moves = board.get_valid_moves(player)

    if not moves:
        return

    scoredmoves = yield from evaluatemovevisual(board, moves, depth, player, player, True)

    scoredmoves.sort(key=lambda x: x[0], reverse=True)

    bestscore, bestmove = scoredmoves[0]

    newboard, _ = board.apply_move(bestmove[0], bestmove[1], player)

    nextplayer = -player

    resultstate = GameState(newboard, nextplayer)

    yield {'type': 'result', 'state': resultstate}
