from model.board import Board
from algorithms.heuristics import weighted_heuristic
from model.game_state import GameState


def evaluatemove(board, moves, depth, playerturn, rootplayer, ismax):

    res = []
    for move in moves:
        newboard, _ = board.apply_move(move[0], move[1], playerturn)
        if depth == 0 or newboard.is_full():
            score = weighted_heuristic(newboard, rootplayer)
            res.append((score, move))
            continue
        opponent = -playerturn
        opponentmoves = newboard.get_valid_moves(opponent)
        if not opponentmoves:
            score = weighted_heuristic(newboard, rootplayer)
            res.append((score, move))
            continue
        opponentresults = evaluatemove(
            newboard, opponentmoves, depth-1, opponent, rootplayer, not ismax
        )
        scores = [s for s, m in opponentresults]

        if ismax:
            bestscore = min(scores)
        else:
            bestscore = max(scores)
        res.append((bestscore, move))
    return res


def evaluatemovevisual(board, moves, depth, playerturn, rootplayer, ismax):

    viewstate = GameState(board, playerturn)
    yield {'type': 'search_node', 'state': viewstate, 'depth': depth}

    results = []

    for move in moves:

        newboard, _ = board.apply_move(move[0], move[1], playerturn)

        if depth == 0 or newboard.is_full():
            score = weighted_heuristic(newboard, rootplayer)

            leafstate = GameState(newboard, -playerturn)
            yield {'type': 'leaf', 'state': leafstate, 'depth': depth, 'score': score}

            results.append((score, move))
            continue

        opponent = -playerturn
        opponentmoves = newboard.get_valid_moves(opponent)

        if not opponentmoves:
            score = weighted_heuristic(newboard, rootplayer)

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


def choosebestmove(board, player, depth=3):

    moves = board.get_valid_moves(player)
    if not moves:
        return None
    scmoves = evaluatemove(board, moves, depth, player, player, True)
    scmoves.sort(key=lambda x: x[0], reverse=True)
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
