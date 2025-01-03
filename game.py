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
# boards, (y, x), 0
def check_double_three(board, move, turn): # make it efficient

    def extract_segment(start, direction): #very unoptimized
        segment = 0
        for i in range(pattern_width): # 0, 1, 2, 3, 4
            current = start + direction * i
            if out_of_bounds(current):
                return -1
            bit_position = coord_to_bit(current)
            if (opponent_board[0] >> bit_position) & 1:
                return -1
            segment |= ((current_board[0] >> bit_position) & 1) << i
        return segment

    def matches_pattern():
        count = 0
        for direction in DIRECTION_MIN: # (0, 1), (1, 0), (1, 1), (1, -1) right, down, right down, right up 
            for offset in range(-pattern_width + 2, 0): # -3, -2, -1
                start = move + direction * offset # (9, 6)
                segment = extract_segment(coordinate(start), direction)
                if segment == pattern_int:
                    count += 1
                    break
        return count

    place_piece(board[turn], move.co) # place piece on the board
    current_board = board[turn] #unnecessary creations
    opponent_board = board[not turn]

    count = 0

    for pattern_int, pattern_width in THREE: # (0b01110, 5)
        count +=  matches_pattern()
        if count > 1:
            place_piece(board[turn], move.co, False)
            return True
    place_piece(board[turn], move.co, False)
    return False


def check_double_three(board, move, turn): # read and check for efficiency!!!!!!!!!!!!!!!!!!!!!11
    BOARD_SIZE = 19  # Adjust as needed
    row, col = move.co
    margin = 4
    DIRECTION_MIN = [(0, 1), (1, 0), (1, 1), (1, -1)]

    row_min = max(0, row - margin)
    row_max = min(BOARD_SIZE - 1, row + margin)
    col_min = max(0, col - margin)
    col_max = min(BOARD_SIZE - 1, col + margin)

    place_piece(board[turn], move.co)
    current_board = board[turn]
    opponent_board = board[not turn]

    def extract_segment(start, direction, pattern_width):
        segment = 0
        for i in range(pattern_width):
            r = start[0] + direction[0] * i
            c = start[1] + direction[1] * i
            if not (row_min <= r <= row_max and col_min <= c <= col_max):
                return -1
            if out_of_bounds((r, c)):
                return -1
            bit_pos = coord_to_bit((r, c))
            if (opponent_board[0] >> bit_pos) & 1:
                return -1
            segment |= ((current_board[0] >> bit_pos) & 1) << i
        return segment

    def matches_pattern(pattern_int, pattern_width):
        count = 0
        for row_dir, col_dir in DIRECTION_MIN:
            for offset in range(-pattern_width + 2, 1):
                start = (row + row_dir * offset, col + col_dir * offset)
                if extract_segment(start, (row_dir, col_dir), pattern_width) == pattern_int:
                    count += 1
                    if count > 1:
                        return count
        return count

    total = 0
    for pattern_int, pattern_width in THREE:
        total += matches_pattern(pattern_int, pattern_width)
        if total > 1:
            place_piece(board[turn], move.co, False)
            return True

    place_piece(board[turn], move.co, False)
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
