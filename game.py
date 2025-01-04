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
    BOARD_SIZE = 19
    y, x = move.co
    PATTERN_1 = 0b01110
    PATTERN_2 = 0b010110
    PATTERN_3 = 0b011010
    PATTERN_1_L = 5
    PATTERN_2_3_L = 6
    MASK_5 = 0b11111
    MASK_6 = 0b111111
    MASK_7 = 0b1111111
    MASK_8 = 0b11111111




    return False

def check_double_three(board, move, turn):
    BOARD_SIZE = 19
    y, x = move.co
    
    PATTERN_1 = 0b01110
    PATTERN_1_LEN = 5
    MASK_5 = 0b11111
    MAX_EXTRA = 3


    # Calculate horizontal space
    left_space = min(x, MAX_EXTRA)
    right_space = min((BOARD_SIZE - 1) - x, MAX_EXTRA)
    bits_space = left_space + right_space + 1
    if bits_space < PATTERN_1_LEN:
        return False

    # Build mask ##complete shit from that moment. FIX IT!!!!!!!!!!!!
    start_col = x - left_space
    mask = 0
    for i in range(bits_space): # 0, 1, 2, 3, 4, 5, 6, 7
        bit_pos = y * BOARD_SIZE + (start_col + i)
        mask |= 1 << bit_pos

    # # Build mask
    # start_col = x - left_space # 0
    # mask = 0
    # for i in range(bits_space + 1 - PATTERN_1_LEN): # 5, 6, 7
    #     bit_pos = y * BOARD_SIZE + start_col + i
    #     segment = (board[turn][0] >> bit_pos) & MASK_5
    #     if segment == PATTERN_1:
            

    # Check if opponent occupies any bit in this range
    if board[not turn][0] & mask:
        return False

    # Extract this horizontal slice
    current_bits = (board[turn][0] & mask) >> (y * BOARD_SIZE + start_col)

    # Slide a 5-bit window to detect PATTERN_1
    for shift in range(bits_space - PATTERN_1_LEN + 1):
        segment = (current_bits >> shift) & 0b11111
        if segment == PATTERN_1:
            return True

    return False


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
