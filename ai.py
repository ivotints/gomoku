from board import coordinate, SIZE, out_of_bounds
from game import is_legal, is_occupied, check_capture, place_piece, is_won
import copy
from macro import PATTERN

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

def bitwise_heuristic(boards, turn, capture):
    ROW_SIZE = 19
    WINDOW_SIZE = 5
    ROW_MASK = (1 << ROW_SIZE) - 1
    WINDOW_MASK = (1 << WINDOW_SIZE) - 1
    value = 0

    def scan_window(current_bits, opponent_bits):
        local_value = 0
        for window_shift in range(ROW_SIZE - WINDOW_SIZE + 1):
            window_opponent = (opponent_bits >> window_shift) & WINDOW_MASK
            if window_opponent == 0:
                window_turn = (current_bits >> window_shift) & WINDOW_MASK
                if window_turn != 0:
                    for pattern, pat_value in PATTERN:
                        if window_turn == pattern:
                            local_value += pat_value
                            break
        return local_value

    # Horizontal scan
    for row in range(ROW_SIZE):
        row_shift = row * ROW_SIZE
        current_row = (boards[turn][0] >> row_shift) & ROW_MASK
        current_row_opponent = (boards[not turn][0] >> row_shift) & ROW_MASK
        value += scan_window(current_row, current_row_opponent)

    # Vertical scan .It will go from last 361 position to the top 19. goes from down to up
    for col in range(ROW_SIZE): # 0 to 18
        vertical_bits = 0
        vertical_opponent = 0
        for row in range(ROW_SIZE): # 0 to 18
            bit_pos = row * ROW_SIZE + col
            vertical_bits |= ((boards[turn][0] >> bit_pos) & 1) << row
            vertical_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << row
        value += scan_window(vertical_bits, vertical_opponent)

        # Main diagonal scan (↘)
    for start in range(2 * ROW_SIZE - 1): # 0 to 37
        diagonal_bits = 0
        diagonal_opponent = 0
        start_row = max(0, start - ROW_SIZE + 1)
        start_col = max(0, ROW_SIZE - 1 - start)
        length = min(ROW_SIZE - start_col, ROW_SIZE - start_row)
        
        if length >= WINDOW_SIZE:
            for i in range(length):
                row = start_row + i
                col = start_col + i
                bit_pos = row * ROW_SIZE + col
                diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
            value += scan_window(diagonal_bits, diagonal_opponent)

    # Anti-diagonal scan (↙)
    for start in range(2 * ROW_SIZE - 1):
        anti_diagonal_bits = 0
        anti_diagonal_opponent = 0
        start_row = max(0, start - ROW_SIZE + 1)
        start_col = min(ROW_SIZE - 1, start)
        length = min(start_col + 1, ROW_SIZE - start_row)
        
        if length >= WINDOW_SIZE:
            for i in range(length):
                row = start_row + i
                col = start_col - i
                bit_pos = row * ROW_SIZE + col
                anti_diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
                anti_diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
            value += scan_window(anti_diagonal_bits, anti_diagonal_opponent)

    return 16 * (2 ** capture) + value

# turn is 1
def bot_play(boards, turn, captures):
    moves = generate_legal_moves(boards, turn, captures)
    best_move = None
    best_points = float('-inf')

    for move in moves:
        new_boards = copy.deepcopy(boards)
        result, capture = handle_move_bot(new_boards, turn, move, captures)
        if result:
            return move
        points = bitwise_heuristic(new_boards, turn, capture)
        if points > best_points:
            best_points = points
            best_move = move
    import random
    return best_move # I commented it because with depth it will be not needed #if best_points > 0 else moves[random.randint(0, len(moves) - 1)]

