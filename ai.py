from board import coordinate, SIZE, out_of_bounds
from game import is_legal, is_occupied, check_capture, place_piece, is_won
import copy
from macro import PAIR_PATTERNS, THREE_PATTERNS, FOUR_PATTERNS, PATTERN

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


def is_occupied(board, pos):
    bit_position = coord_to_bit(pos)
    return (board[0] >> bit_position) & 1

def coord_to_bit(move):
    row, col = move
    return row * (SIZE - 1) + col

# i is y and j is x
def evaluate_board_1(boards, turn, capture, result):
    def count_patterns(board):
        masks = {length: (1 << length) - 1 for length in range(2, 7)}
        
        #smarter
        def get_line_bits(start_i, start_j, di, dj):                
            bits = 0
            for k in range(6):
                i, j = start_i + k*di, start_j + k*dj
                if i < 0 or i >= SIZE - 1 or j < 0 or j >= SIZE - 1:
                    return -1
                #pos = board[not turn]  (i * (SIZE - 1) + j)
                if is_occupied(boards[not turn], (i, j)): #take whole segment if segment == 0 return -1
                    return -1
                bits |= (is_occupied(board, (i, j)) << k) # take whole segment directly from bitboard
            return bits
        
        def get_line_bits(start_i, start_j, di, dj):                
            bits = 0
            for k in range(6):
                i, j = start_i + k*di, start_j + k*dj
                if i < 0 or i >= SIZE - 1 or j < 0 or j >= SIZE - 1:
                    return -1
                if is_occupied(boards[not turn], (i, j)):
                    return -1
                bits |= (is_occupied(board, (i, j)) << k)
            return bits
        
        # #faster and worser
        # def get_line_bits(start_i, start_j, di, dj):
        #     # Pre-calculate end coordinates
        #     end_i = start_i + 5*di
        #     end_j = start_j + 5*dj
            
        #     # Quick boundary check for entire segment
        #     if (start_i < 0 or end_i >= SIZE - 1 or 
        #         start_j < 0 or end_j >= SIZE - 1):
        #         return -1
                
        #     # Check opponent pieces first (early return)
        #     for k in range(6):
        #         i, j = start_i + k*di, start_j + k*dj
        #         if is_occupied(boards[not turn], (i, j)):
        #             return -1
                    
        #     # Get all bits in one pass
        #     bits = 0
        #     for k in range(6):
        #         i, j = start_i + k*di, start_j + k*dj
        #         bits |= (is_occupied(board, (i, j)) << k)
                
        #     return bits

        pairs = threes = fours = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        # for i in range(SIZE - 1):
        #     for j in range(SIZE - 1):
        #         for di, dj in directions:
        #             window = get_line_bits(i, j, di, dj)
        #             if window == -1:
        #                 continue
        #             current_pairs = 0
        #             current_threes = 0
                        
        #             # Check all patterns with single window scan
        #             for pattern, length in PAIR_PATTERNS:
        #                 if (window & masks[length]) == pattern:
        #                     current_pairs += 1
                            
        #             if current_pairs:
        #                 for pattern, length in THREE_PATTERNS:
        #                     if (window & masks[length]) == pattern:
        #                         current_threes += 1
        #                 if current_threes:
        #                     for pattern, length in FOUR_PATTERNS:
        #                         if (window & masks[length]) == pattern:
        #                             fours += 1
        #             pairs += current_pairs
        #             threes += current_threes

        # return pairs, threes, fours

        for i in range(SIZE - 1):
            for j in range(SIZE - 1):
                for di, dj in directions:
                    window = get_line_bits(i, j, di, dj)
                    if window == -1:
                        continue
                        
                    for pattern, length in PAIR_PATTERNS:
                        if (window & masks[length]) == pattern:
                            pairs += 1
                            
                    for pattern, length in THREE_PATTERNS:
                        if (window & masks[length]) == pattern:
                            threes += 1
                    for pattern, length in FOUR_PATTERNS:
                        if (window & masks[length]) == pattern:
                            fours += 1

        return pairs, threes, fours
        
    pairs, threes, fours = count_patterns(boards[turn])
    capture_reward = 50 * (2 ** capture) if capture > 0 else 0
    return pairs + 10 * threes + 100 * fours + 1000 * result + capture_reward

# boards[turn] is the board of the player
def evaluate_board_2(boards, turn, capture):
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
    for start in range(2 * ROW_SIZE - 1):
        diagonal_bits = 0
        diagonal_opponent = 0
        start_row = max(0, start - ROW_SIZE + 1)
        start_col = max(0, ROW_SIZE - 1 - start)
        length = min(ROW_SIZE - start_col, ROW_SIZE - start_row)
        
        for i in range(length):
            row = start_row + i
            col = start_col + i
            bit_pos = row * ROW_SIZE + col
            diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
            diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
        if length >= WINDOW_SIZE:
            value += scan_window(diagonal_bits, diagonal_opponent)

    # Anti-diagonal scan (↙)
    for start in range(2 * ROW_SIZE - 1):
        anti_diagonal_bits = 0
        anti_diagonal_opponent = 0
        start_row = max(0, start - ROW_SIZE + 1)
        start_col = min(ROW_SIZE - 1, start)
        length = min(start_col + 1, ROW_SIZE - start_row)
        
        for i in range(length):
            row = start_row + i
            col = start_col - i
            bit_pos = row * ROW_SIZE + col
            anti_diagonal_bits |= ((boards[turn][0] >> bit_pos) & 1) << i
            anti_diagonal_opponent |= ((boards[not turn][0] >> bit_pos) & 1) << i
        if length >= WINDOW_SIZE:
            value += scan_window(anti_diagonal_bits, anti_diagonal_opponent)


    return 16 * (2 ** capture) + value - 16

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
        # points = evaluate_board_1(new_boards, turn, capture, result)
        points = evaluate_board_2(new_boards, turn, capture)
        if points > best_points:
            best_points = points
            best_move = move
    import random
    return best_move if best_points > 0 else moves[random.randint(0, len(moves) - 1)]

