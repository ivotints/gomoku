import pygame.draw as pyd
from macro import BLACK
from board import SIZE, WIDTH
from game import is_occupied

# can we store somewhere this image of board not to create it every time?
def draw_board(win):
    win.fill((235,173,100))
    square = WIDTH / SIZE # 47.6
    for i in range(1, SIZE):
        # vertical lines      x           y         x               y
        pyd.line(win, BLACK, (i * square, square), (i * square, WIDTH - square), width=2)
        # horizontal lines    x           y         x               y
        pyd.line(win, BLACK, (square, i * square), (WIDTH - square, i * square), width=2)

def find_mouse_pos(pos):
    x, y = pos
    w = WIDTH / SIZE # 47.6
    if x < w - w / 3 or x > WIDTH - w + w / 3 or y < w - w / 3 or y > WIDTH - w + w / 3:
        return None
    x = round(x / w)
    y = round(y / w)
    return ((x - 1, y - 1))

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

def update_board(boards, win):
    draw_board(win) # this will again create image of board, can we store it somewhere?
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