import pygame.draw as pyd
import pygame as py
from macro import BLACK, WHITE, WIDTH, SIZE


def draw_board(win, captures=[0, 0]):
    win.fill((235,173,100))
    square = WIDTH / SIZE
    for i in range(1, SIZE):
        pyd.line(win, BLACK, (i * square, square), (i * square, WIDTH - square), width=2)
        pyd.line(win, BLACK, (square, i * square), (WIDTH - square, i * square), width=2)
    font = py.font.Font(None, 24)
    text = font.render(f"Captures:     {captures[0]}", True, BLACK)
    text_rect = text.get_rect(center=(80, 20))
    win.blit(text, text_rect)
    text = font.render(str(captures[1]), True, WHITE)
    text_rect = text.get_rect(center=(180, 20))
    win.blit(text, text_rect)

def find_mouse_pos(pos):
    x, y = pos
    w = WIDTH / SIZE
    if x < w - w / 3 or x > WIDTH - w + w / 3 or y < w - w / 3 or y > WIDTH - w + w / 3:
        return None
    x = round(x / w)
    y = round(y / w)
    return ((x - 1, y - 1))

def update_board(boards, win, captures):
    draw_board(win, captures)
    # draw_captures(win, captures)
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