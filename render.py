import pygame.draw as pyd
from macro import BLACK
from board import SIZE, WIDTH
from game import is_occupied

def draw_board(win):
    win.fill((235,173,100))
    square = WIDTH / SIZE
    for i in range(1, SIZE):
        pyd.line(win, BLACK, (i * square, square), (i * square, WIDTH - square), width=2)
        pyd.line(win, BLACK, (square, i * square), (WIDTH - square, i * square), width=2)

def find_mouse_pos(pos):
    x, y = pos
    w = WIDTH / SIZE
    if x < w - w / 3 or x > WIDTH - w + w / 3 or y < w - w / 3 or y > WIDTH - w + w / 3:
        return None
    x = round(x / w)
    y = round(y / w)
    return ((x - 1, y - 1))

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