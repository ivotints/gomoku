import pygame as py
import pygame.draw as pyd

SIZE = 1080
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def find_mouse_pos(pos):
    x, y = pos
    size = SIZE / 19
    x = round(x / size)
    y = round(y / size)
    if x == 0 or x == 19 or y == 0 or y == 19:
        return None
    return ((x - 1, y - 1))

def draw_board(win):
    win.fill((163, 112, 23))
    for i in range(0, 18):
        pyd.line(win, (0, 0, 0), (i * SIZE / 19, 0), (i * SIZE / 19, SIZE), width=2)
        pyd.line(win, (0, 0, 0), (0, i * SIZE / 19), (SIZE, i * SIZE / 19), width=2)
    pyd.line(win, (0, 0, 0), (18 * SIZE / 19 - 2, 0), (18 * SIZE / 19 - 2, SIZE), width=2)
    pyd.line(win, (0, 0, 0), (0, 18 * SIZE / 19 - 2), (SIZE, 18 * SIZE / 19 - 2), width=2)

def is_occupied(boards, pos):
    y, x = pos
    bit_position = coord_to_bit(x, y)
    for board in boards:
        if (board >> bit_position) & 1:
            return True
    return False

def coord_to_bit(row, col):
    return row * 17 + col

def bit_to_coord(bit):
    return divmod(bit, 17)

def place_piece(bitboard, row, col):
    bit_position = coord_to_bit(row, col)
    return bitboard | (1 << bit_position)

def display_board(player1, player2):
    for row in range(17):
        row_display = []
        for col in range(17):
            if is_occupied([player1], (row, col)):
                row_display.append('X')
            elif is_occupied([player2], (row, col)):
                row_display.append('O')
            else:
                row_display.append('.')
        print(' '.join(row_display))
        print("---------------")

def main():
    py.init()
    turn = 0
    win = py.display.set_mode((SIZE, SIZE))
    py.display.set_caption("Gomoku")
    draw_board(win)
    py.display.update()
    running = True
    boards = [0, 0]
    while running:
        for event in py.event.get():
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    running = False
            if event.type == py.MOUSEBUTTONDOWN:
                pos = find_mouse_pos(py.mouse.get_pos())
                if pos and not is_occupied(boards, (pos[1], pos[0])):
                    boards[turn] = place_piece(boards[turn], pos[0], pos[1])
                    display_board(boards[0], boards[1])
                    pyd.circle(win, BLACK if not turn else WHITE, ((pos[0] + 1) * SIZE / 19 , (pos[1] + 1) * SIZE / 19), SIZE / 19 / 3)
                    turn = not turn
                    py.display.update()



if __name__ == '__main__':
    main()

