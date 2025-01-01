from board import coordinate, SIZE
from game import is_legal, is_occupied, check_capture, place_piece, is_won
import copy
from macro import PAIR_PATTERNS, THREE_PATTERNS, FOUR_PATTERNS

def handle_move_bot(boards, turn, move, captures):
    capture, pos = check_capture(boards, move, turn)
    captures[turn] += capture
    place_piece(boards[turn], move.co)
    if capture:
        for p in pos:
            place_piece(boards[not turn], p, False)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True, capture
    return False, capture

def generate_legal_moves(boards, turn, capture):
    legal_moves = []
    for row in range(SIZE - 1):
        for col in range(SIZE - 1):
            move = coordinate((row, col))
            if is_occupied(boards[0], move.co) or is_occupied(boards[1], move.co):
                continue
            legal, _, _ = is_legal(capture, boards, move, turn)
            if legal:
                legal_moves.append(move)
    return legal_moves

def evaluate_board(boards, turn, capture, result):
    def count_patterns(board):
        def get_line_bits(start_i, start_j, di, dj, length):
            bits = 0
            for k in range(length):
                i, j = start_i + k*di, start_j + k*dj
                if i < 0 or i >= SIZE - 1 or j < 0 or j >= SIZE - 1:
                    return -1
                if is_occupied(boards[not turn], (i, j)):
                    return -1
                bits |= (is_occupied(board, (i, j)) << k)
            return bits

        pairs = 0
        threes = 0
        fours = 0
        size = SIZE - 1

        # Check patterns in all directions
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for i in range(size):
            for j in range(size):
                for di, dj in directions:
                    # Check for 5-window patterns
                    window = get_line_bits(i, j, di, dj, 5)
                    if window == -1:
                        continue
                    
                    # Check pair patterns (4-bit window)
                    pair_window = window & 0b11111
                    if pair_window in PAIR_PATTERNS:
                        pairs += 1
                    
                    # Check three patterns (5-bit window)
                    if window in THREE_PATTERNS:
                        threes += 1
                    
                    # Check four patterns (5-bit window)
                    if window in FOUR_PATTERNS:
                        fours += 1

        return pairs, threes, fours

    current_board = boards[turn]
    pairs, threes, fours = count_patterns(current_board)
    capture_reward = 50 * (2 ** capture) if capture > 0 else 0
    return pairs + 10 * threes + 100 * fours + 1000 * result + capture_reward

def bot_play(boards, turn, captures):
    moves = generate_legal_moves(boards, turn, captures)
    best_move = None
    best_points = float('-inf')

    for move in moves:
        # Create a deep copy of the boards to simulate the move
        new_boards = copy.deepcopy(boards)
        result, capture = handle_move_bot(new_boards, turn, move, captures)
        
        # Evaluate the board after the move
        points = evaluate_board(new_boards, turn, capture, result)
        
        # Select the move with the highest heuristic score
        if points > best_points:
            best_points = points
            best_move = move

    return best_move