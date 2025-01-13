from game import has_winning_line
import copy
from macro import DEPTH
from wrapper import heuristic, generate_legal_moves_cpp, check_capture, is_won, minimax

# do not return anything
def handle_move_bot_void(boards, turn, move, captures) -> None:
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards[turn][0], boards[not turn][0], y, x)
    boards[turn][0] |= (1 << move)
    if capture: # here it will delete opponent's pieces
        captures[turn] += capture
        for p in pos:
            boards[not turn][0] &= ~(1 << p)

def handle_move_bot(boards, turn, move, captures):
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards[turn][0], boards[not turn][0], y, x)
    boards[turn][0] |= (1 << move)
    if capture: # here it will delete opponent's pieces
        captures[turn] += capture
        for p in pos:
            boards[not turn][0] &= ~(1 << p)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True
    return False

def minimax_py(boards, depth, alpha, beta, maximizing_player, turn, captures):
    if depth == 1:
        value = heuristic(boards[turn][0], boards[not turn][0],captures[turn],captures[not turn])
        return value
    moves = generate_legal_moves_cpp(boards[turn][0], boards[not turn][0], captures[turn])

    if maximizing_player:
        max_eval = -2147483648
        for move in moves:
            new_boards = copy.deepcopy(boards)
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            if result:
                return 2147483647
            eval = minimax_py(new_boards, depth - 1, alpha, beta, False, not turn, captures)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = 2147483647
        for move in moves:
            new_boards = copy.deepcopy(boards)
            result = handle_move_bot(new_boards, turn, move, [captures[0], captures[1]])
            if result:
                return -2147483648
            eval = minimax_py(new_boards, depth - 1, alpha, beta, True, not turn, captures)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def is_winning_move(boards, turn, move, captures):
    y = move // 19
    x = move % 19
    capture, pos = check_capture(boards[turn][0], boards[not turn][0], y, x)
    if capture + captures[turn] > 4:
        return True
    boards[turn][0] |= (1 << move)
    if has_winning_line(boards[turn][0]):
        return True
    boards[turn][0] &= ~(1 << move)
    return False

def bot_play(boards, turn, captures):
    t = [0]
    moves = generate_legal_moves_cpp(boards[turn][0], boards[not turn][0], captures[turn])

    for move in moves:
        if is_winning_move(boards, turn, move, captures):
            return move

    best_move = moves[0]  # Default to first move
    best_eval = -2147483648
    alpha = -2147483648
    beta = 2147483647

    for move in moves:
        new_boards = copy.deepcopy(boards)
        handle_move_bot_void(new_boards, turn, move, [captures[0], captures[1]])

        eval = minimax(new_boards, DEPTH, alpha, beta, False, not turn, captures)
        if eval > best_eval:
            best_eval = eval
            best_move = move
        alpha = max(alpha, eval)

    return best_move
