from game import has_winning_line
import copy
from macro import DEPTH
from wrapper import generate_legal_moves_cpp, check_capture, minimax

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
