import pygame as py
import pygame.draw as pyd

WIDTH = 1000
SIZE = 21
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class coordinate:
    def __init__(self, pos):
        self.co = pos
    def __add__(self, other):
        result = []
        if isinstance(other, tuple):
            for i, j in zip(self.co, other):
                result.append(i + j)
            return tuple(result)
        if isinstance(other, coordinate):
            for i, j in zip(self.co, other.co):
                result.append(i + j)
            return tuple(result)
        return NotImplemented

    def __mul__(self, other):
        result = []
        if isinstance(other, int):
            for i in self.co:
                result.append(i * other)
            return tuple(result)
        return NotImplemented

    def __sub__(self, other):
        result = []
        if isinstance(other, tuple):
            for i, j in zip(self.co, other):
                result.append(i - j)
            return tuple(result)
        if isinstance(other, coordinate):
            for i, j in zip(self.co, other.co):
                result.append(i - j)
            return tuple(result)
        return NotImplemented

DIRECTIONS = [
    coordinate((0, 1)),  
    coordinate((1, 0)),  
    coordinate((1, 1)),  
    coordinate((1, -1)), 
    coordinate((0, -1)), 
    coordinate((-1, 0)), 
    coordinate((-1, -1)),
    coordinate((-1, 1))  
]

class gomoku:
    def __init__(self):
        self.boards = [[0], [0]]
        self.turn = 0
        self.win = py.display.set_mode((WIDTH, WIDTH))
        self.captures = [0, 0]
        self.running = True

        py.display.set_caption("Gomoku")
        draw_board(self.win)
        py.display.update()

def out_of_bounds(move):
    return move[0] < 0 or move[0] >= 17 or move[1] < 0 or move[1] >= 17

def check_capture(boards, move, turn, captures, clear=True):
    capture = 0
    for pos in DIRECTIONS:
        if out_of_bounds(move + pos * 3):
            continue
        if not is_occupied(boards[turn], move + pos * 3):
            continue
        if is_occupied(boards[not turn], move + pos * 2) and is_occupied(boards[not turn], move + pos):
            capture += 1
            if clear:
                place_piece(boards[not turn], move + pos * 2, False)
                place_piece(boards[not turn], move + pos, False)
    captures[turn] += capture
    return capture


def find_mouse_pos(pos):
    x, y = pos
    w = WIDTH / SIZE
    if x < w - 15 or x > WIDTH - w + 15 or y < w - 15 or y > WIDTH - w + 15:
        return None
    x = round(x / w)
    y = round(y / w)
    return ((x - 1, y - 1))

def draw_board(win):
    win.fill((163, 112, 23))
    square = WIDTH / SIZE
    for i in range(1, SIZE):
        pyd.line(win, (0, 0, 0), (i * square, square), (i * square, WIDTH - square), width=2)
        pyd.line(win, (0, 0, 0), (square, i * square), (WIDTH - square, i * square), width=2)

def is_occupied(board, pos):
    bit_position = coord_to_bit(pos)
    return (board[0] >> bit_position) & 1

def coord_to_bit(move):
    row, col = move
    return row * (SIZE - 1) + col

def bit_to_coord(bit):
    return divmod(bit, SIZE - 1)

def place_piece(bitboard, move, set_bit=True):
    bit_position = coord_to_bit(move)
    if set_bit:
        bitboard[0] |= (1 << bit_position)
    else:
        bitboard[0] &= ~(1 << bit_position)

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

def winning_line(board):
    directions = [
        [(0, 1), (1, 0), (1, 1), (1, -1)],
        [((SIZE - 1), SIZE - 5), (SIZE - 5, (SIZE - 1)), (SIZE - 5, SIZE - 5), (SIZE - 5, SIZE - 5)]
    ]
    
    for d, bounds in zip(directions[0], directions[1]):
        di, dj = d
        bound_i, bound_j = bounds
        
        for i in range(bound_i):
            j = 0
            while j < bound_j:
                if all(is_occupied(board, (i + k*di, j + k*dj)) 
                      for k in range(5)):
                    return ((i,j), (i + 1*di, j + 1*dj), (i + 2*di, j + 2*dj), (i + 3*di, j + 3*dj), (i + 4*di, j + 4*dj))
                j += 1
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

def handle_move(boards, turn, move, captures, true_move=True):
    capture = check_capture(boards, move, turn, captures)
    if captures[turn] == 4 and not capture and winning_line(boards[not turn]):
        return None, capture
    place_piece(boards[turn], move.co)
    if captures[turn] > 4 or is_won(boards, turn, captures[not turn]):
        return True, capture
    return False, capture

def update_board(boards, win):
    draw_board(win)
    for player, board in enumerate(boards):
        b = board.copy()
        pos = 0
        while b[0]:
            if b[0] & 1:

                x = pos % (SIZE - 1)
                y = pos // (SIZE - 1)

                px = (x + 1) * WIDTH / SIZE
                py = (y + 1) * WIDTH / SIZE
                color = (0, 0, 0) if player == 0 else (255, 255, 255)
                pyd.circle(win, color, (px, py), WIDTH / SIZE / 3)
            b[0] >>= 1
            pos += 1

def main():
    py.init()
    game = gomoku()
    while game.running:
        for event in py.event.get():
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    game.running = False
            if event.type == py.MOUSEBUTTONDOWN:
                pos = find_mouse_pos(py.mouse.get_pos())
                if pos is None:
                    continue
                move = coordinate((pos[1], pos[0]))
                if not is_occupied(game.boards[0], move.co) and not is_occupied(game.boards[1], move.co):
                    result, update = handle_move(game.boards, game.turn, move, game.captures)
                    if result is None:
                        continue
                    if result:
                        print("GG")
                        exit(0)
                    if update:
                        update_board(game.boards, game.win)
                    else:
                        pyd.circle(game.win, BLACK if not game.turn else WHITE, ((pos[0] + 1) * WIDTH / SIZE , (pos[1] + 1) * WIDTH / SIZE), WIDTH / SIZE / 3)
                    # print(game.captures)
                    # display_board(game.boards[0], game.boards[1])
                    game.turn = not game.turn
                    py.display.update()



if __name__ == '__main__':
    main()

