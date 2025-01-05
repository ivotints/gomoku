from macro import DIRECTIONS, THREE, DIRECTION_MIN
from board import coordinate, out_of_bounds, coord_to_bit, SIZE
BOARD_SIZE = SIZE - 1

def display_board(player1, player2):
    for row in range(SIZE - 1):
        row_display = []
        for col in range(SIZE - 1):
            if is_occupied(player1, (row, col)):
                row_display.append('X')
            elif is_occupied(player2, (row, col)):
                row_display.append('O')
            else:
                row_display.append('.')
        print(' '.join(row_display))
    print("---------------")

# boards, (y, x), 0
def check_capture(boards, move, turn):
    capture = 0
    capture_positions = []
    for pos in DIRECTIONS:
        # check for out of bounds
        if out_of_bounds(move + pos * 3):
            continue
        # check for players piece if present
        if not is_occupied(boards[turn], move + pos * 3):
            continue
        # check for opponent piece to eat
        if is_occupied(boards[not turn], move + pos * 2) and is_occupied(boards[not turn], move + pos):
            capture += 1
            capture_positions.append(move + pos * 2)
            capture_positions.append(move + pos)

    return capture, capture_positions

def place_piece(bitboard, move, set_bit=True):
    bit_position = coord_to_bit(move)
    if set_bit:
        bitboard[0] |= (1 << bit_position)
    else:
        bitboard[0] &= ~(1 << bit_position)

def is_occupied(board, pos): # y, x
    y, x = pos
    bit_position = y * BOARD_SIZE + x # y * 19 + x
    return (board[0] >> bit_position) & 1

def winning_line(board):
    size = BOARD_SIZE

    for i in range(size):
        for j in range(size):
            pos = (i, j)
            if not is_occupied(board, pos):
                continue
            for direction in DIRECTION_MIN:
                di, dj = direction.co
                if all(0 <= i + k*di < size and 0 <= j + k*dj < size and is_occupied(board, (i + k*di, j + k*dj)) for k in range(5)):
                    return ((i, j), (i + 1*di, j + 1*dj), (i + 2*di, j + 2*dj), (i + 3*di, j + 3*dj), (i + 4*di, j + 4*dj))
    return None

def is_eatable(boards, pos, direction, turn):
    if not is_occupied(boards[turn], pos + direction):
        return False
    if is_occupied(boards[not turn], pos - direction) and not (is_occupied(boards[not turn], pos + direction * 2) or is_occupied(boards[turn], pos + direction * 2)):
        return True
    if is_occupied(boards[not turn], pos + direction * 2) and not (is_occupied(boards[not turn], pos - direction) or is_occupied(boards[turn], pos - direction)):
        return True
    return False

def is_line_capture(boards, line, turn):
    for pos in line:
        pos = coordinate(pos)
        for direction in DIRECTIONS:
            if out_of_bounds(pos + direction * 2) or out_of_bounds(pos - direction):
                continue
            if is_eatable(boards, pos, direction, turn):
                return True
    return False

def is_won(boards, turn, capture):
    line = winning_line(boards[turn])
    if line is None or (capture == 4 and is_line_capture(boards, line, turn)):
        return False
    return True

# # boards, (y, x), 0
# def check_double_three(board, move, turn): # make it efficient

#     def extract_segment(start, direction): #very unoptimized
#         segment = 0
#         for i in range(pattern_width): # 0, 1, 2, 3, 4
#             current = start + direction * i
#             if out_of_bounds(current):
#                 return -1
#             bit_position = coord_to_bit(current)
#             if (opponent_board[0] >> bit_position) & 1:
#                 return -1
#             segment |= ((current_board[0] >> bit_position) & 1) << i
#         return segment

#     def matches_pattern():
#         count = 0
#         for direction in DIRECTION_MIN: # (0, 1), (1, 0), (1, 1), (1, -1) right, down, right down, right up 
#             for offset in range(-pattern_width + 2, 0): # -3, -2, -1
#                 start = move + direction * offset # (9, 6)
#                 segment = extract_segment(coordinate(start), direction)
#                 if segment == pattern_int:
#                     count += 1
#                     break
#         return count

#     place_piece(board[turn], move.co) # place piece on the board
#     current_board = board[turn] #unnecessary creations
#     opponent_board = board[not turn]

#     count = 0

#     for pattern_int, pattern_width in THREE: # (0b01110, 5)
#         count +=  matches_pattern()
#         if count > 1:
#             place_piece(board[turn], move.co, False)
#             return True
#     place_piece(board[turn], move.co, False)
#     return False


def check_double_three(board, move, turn): # read and check for efficiency!!!!!!!!!!!!!!!!!!!!!11
    BOARD_SIZE = 19  # Adjust as needed
    y, x = move.co # 9, 9
    margin = 4

    y_min = max(0, y - margin) # 5
    y_max = min(BOARD_SIZE - 1, y + margin) # 13
    x_min = max(0, x - margin) # 5
    x_max = min(BOARD_SIZE - 1, x + margin) # 13

    place_piece(board[turn], move.co)
    current_board = board[turn]
    opponent_board = board[not turn]

    def extract_segment(y_start, x_start, y_dir, x_dir):
        segment = 0
        for i in range(pattern_width): # 0, 1, 2, 3, 4
            r = y_start + y_dir * i
            c = x_start + x_dir * i
            if not (y_min <= r <= y_max and x_min <= c <= x_max): # this checks for out of bounds
                return -1
            # if out_of_bounds((r, c)):
            #     return -1
            bit_pos = r * BOARD_SIZE + c
            if (opponent_board[0] >> bit_pos) & 1:
                return -1
            segment |= ((current_board[0] >> bit_pos) & 1) << i
        return segment

    def matches_pattern():
        count = 0
        for y_dir, x_dir in [(0, 1), (1, 0), (1, 1), (1, -1)]: # right, down, right down, left down
            for offset in range(-pattern_width + 2, 1): # -3, -2, -1, 0
                y_start, x_start = (y + y_dir * offset, x + x_dir * offset)
                if extract_segment(y_start, x_start, y_dir, x_dir) == pattern_int:
                    count += 1
                    if count > 1:
                       return count
        return count

    total = 0
    for pattern_int, pattern_width in THREE:
        total += matches_pattern()
        if total > 1:
            place_piece(board[turn], move.co, False)
            return True

    place_piece(board[turn], move.co, False)
    return False

# now i want to start check_double_three() from beginning. lets for now check only horizontal direction for pattern 0b01110. your goal is to extract from map 5 to 7 bits,  (pattern size is 5) depends on a how close to border we are. if we are on it we dont even check on nothing. We first calculate bits_space which is 5 to 7 bits depends on how close we to the border. than we take mask of that size and check if there is a opponent point in thet area. if result is != 0, we stop. then we take mask of  bits_space bits and apply it to current map. then we take its first  5 bits with mask and we compare it to pattern PATTERN_1. if it is same, we stop and do count as 1. if not, we continue by shifting one bit and



def check_double_three(board, move, turn):
    y, x = move.co # 3, 3
    BOARD_SIZE = 19
    PATTERN_1 = 0b01110
    MASK_5 = 0b11111
    PATTERN_1_LEN = 5
    MAX_EXTRA = 3

    place_piece(board[turn], move.co) ## later change it on piece of code.

    count = 0
    
    # Calculate horizontal space
    left_space = min(x, MAX_EXTRA) # 3
    right_space = min((BOARD_SIZE - 1) - x, MAX_EXTRA) # 3
    bits_space = left_space + right_space + 1
    if bits_space >= PATTERN_1_LEN:
        # Build mask
        mask = 0
        if bits_space == 7:
            mask = 0b1111111
        elif bits_space == 6:
            mask = 0b111111
        elif bits_space == 5:
            mask = 0b11111
        start_col = x - left_space # 0
        # Get full row data for both players
        current_row = (board[turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)
        opponent_row = (board[not turn][0] >> (y * BOARD_SIZE)) & ((1 << BOARD_SIZE) - 1)

        # Extract bits_space bits
        extracted_self = (current_row >> start_col) & mask
        extracted_opp  = (opponent_row >> start_col) & mask
        while bits_space >= PATTERN_1_LEN:
            if extracted_opp & MASK_5 == 0:
                if extracted_self & MASK_5 == PATTERN_1:
                    count += 1
                    break
            bits_space -= 1
            extracted_self >>= 1
            extracted_opp >>= 1
    
    # vertical direction
    top_space = min(y, MAX_EXTRA)
    bottom_space = min((BOARD_SIZE - 1) - y, MAX_EXTRA)
    v_bits_space = top_space + bottom_space + 1
    start_row = y - top_space
    extracted_self_v = 0
    extracted_opp_v = 0
    
    for i in range(v_bits_space):
        bit_pos = (start_row + i) * BOARD_SIZE + x
        extracted_self_v |= ((board[turn][0] >> bit_pos) & 1) << i
        extracted_opp_v |= ((board[not turn][0] >> bit_pos) & 1) << i
    
    while v_bits_space >= PATTERN_1_LEN:
        if (extracted_opp_v & MASK_5) == 0:
            if (extracted_self_v & MASK_5) == PATTERN_1:
                count += 1
                break
        v_bits_space -= 1
        extracted_self_v >>= 1
        extracted_opp_v >>= 1
        

    place_piece(board[turn], move.co, False)
    return count > 1


# 0, boards, (y, x), 0
def is_legal(captures, boards, move, turn):
    capture, pos = check_capture(boards, move, turn) # will return 0, [] if no capture otherwise 1, [pos1, pos2] where pos1 and pos2 are the positions to remove (y, x)
    if not capture and ((captures == 4 and winning_line(boards[not turn])) or check_double_three(boards, move, turn)):
        return False, capture, pos
    return True, capture, pos

# our 2 boards
# which turn
# move that was made
# current captures for both players
def handle_move(boards, turn, move, captures):
    # turbn is 0 for black
    # 0, boards, (y, x), 0
    legal, capture, pos = is_legal(captures[turn], boards, move, turn)
    if not legal:
        return None, capture
    captures[turn] += capture
    place_piece(boards[turn], move.co)
    if capture:
        for p in pos:
            place_piece(boards[not turn], p, False)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True, capture
    return False, capture
