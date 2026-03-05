from model.board import Board
from model.game_state import GameState

def classifier(board, moves):
    A = [] 
    B = []  
    C = []  
    D = []  
    size = len(board.grid)
    corners = [(0,0),(0,size-1),(size-1,0),(size-1,size-1)]
    cedges = [
        (0,1),(1,0),(1,1),
        (0,size-2),(1,size-2),(1,size-1),
        (size-2,0),(size-2,1),(size-1,1),
        (size-2,size-1),(size-1,size-2),(size-2,size-2)
    ]

    for r,c in moves:
        if (r,c) in corners:
            A.append((r,c))
        elif (r,c) in cedges:
            D.append((r,c))
        elif r==0 or r==size-1 or c==0 or c==size-1:
            B.append((r,c))
        else:
            C.append((r,c))

    return A,B,C,D


def quaddom(board, player, r0, c0, size):

    if size <= 2:
        cpu = 0
        human = 0

        for r in range(r0, min(r0 + size, len(board.grid))):
            for c in range(c0, min(c0 + size, len(board.grid))):

                if board.grid[r][c] == player:
                    cpu += 1
                elif board.grid[r][c] == -player:
                    human += 1

        return 1 if cpu > human else 0

    half = size // 2

    q1 = quaddom(board, player, r0, c0, half)
    q2 = quaddom(board, player, r0, c0 + half, half)
    q3 = quaddom(board, player, r0 + half, c0, half)
    q4 = quaddom(board, player, r0 + half, c0 + half, half)

    return q1 + q2 + q3 + q4

def evalmove(board, move, player):
    newboard,_ = board.apply_move(move[0], move[1], player)
    size = len(newboard.grid)
    res = quaddom(newboard, player, 0, 0, size)
    score = res
    return score

def choosebestmove(board, player):

    moves = board.get_valid_moves(player)
    if not moves:
        return None  

    A,B,C,D = classifier(board, moves)
    if A:
        bucket = A
    elif B:
        bucket = B
    elif C:
        bucket = C
    else:
        bucket = D

    bestm = None
    bests = -1
    for move in bucket:
        score = evalmove(board, move, player)
        if score > bests:
            bests = score
            bestm = move
    return bestm

def choosebestmovevisual(board, player):
    moves = board.get_valid_moves(player)
    if not moves:
        return

    A,B,C,D = classifier(board, moves)
    if A:
        bucket = A
    elif B:
        bucket = B
    elif C:
        bucket = C
    else:
        bucket = D
    bestmove = None
    bestscore = -1


    for move in bucket:

        newboard,_ = board.apply_move(move[0], move[1], player)

        viewstate = GameState(newboard, -player)

        yield {'type':'search_node','state':viewstate}

        score = evalmove(board, move, player)

        if score > bestscore:
            bestscore = score
            bestmove = move


    newboard,_ = board.apply_move(bestmove[0], bestmove[1], player)
    resultstate = GameState(newboard, -player)
    yield {'type':'result','state':resultstate}
